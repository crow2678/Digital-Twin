#!/usr/bin/env python3
"""
Production-Ready Whisper Service
Optimized for low latency and high throughput
"""

import asyncio
import io
import os
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
from concurrent.futures import ThreadPoolExecutor

import whisper
import torch
import torchaudio
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model and services
whisper_model = None
redis_client = None
executor = None

class TranscriptionRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    language: Optional[str] = None
    task: str = "transcribe"  # or "translate"
    timestamp: Optional[float] = None

class TranscriptionResponse(BaseModel):
    id: str
    text: str
    language: str
    confidence: float
    processing_time: float
    segments: List[Dict[str, Any]]
    status: str

class WhisperService:
    def __init__(self, model_size: str = "base", device: str = "cpu"):
        self.model_size = model_size
        self.device = device
        self.model = None
        self.processing_queue = asyncio.Queue(maxsize=100)
        self.load_model()
        
    def load_model(self):
        """Load Whisper model with optimizations"""
        logger.info(f"Loading Whisper model: {self.model_size}")
        start_time = time.time()
        
        # Check for GPU availability
        if torch.cuda.is_available() and self.device == "cuda":
            self.device = "cuda"
            logger.info("Using GPU acceleration")
        else:
            self.device = "cpu"
            logger.info("Using CPU processing")
            
        # Load model with optimizations
        self.model = whisper.load_model(
            self.model_size, 
            device=self.device,
            download_root="/app/models"
        )
        
        # Compile model for faster inference (PyTorch 2.0+)
        if hasattr(torch, 'compile'):
            try:
                self.model = torch.compile(self.model)
                logger.info("Model compiled for faster inference")
            except Exception as e:
                logger.warning(f"Could not compile model: {e}")
        
        load_time = time.time() - start_time
        logger.info(f"Model loaded in {load_time:.2f} seconds")
        
    def preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        """Preprocess audio for optimal Whisper performance"""
        try:
            # Load audio from bytes
            audio_tensor, sample_rate = torchaudio.load(io.BytesIO(audio_data))
            
            # Convert to mono if stereo
            if audio_tensor.shape[0] > 1:
                audio_tensor = torch.mean(audio_tensor, dim=0, keepdim=True)
            
            # Resample to 16kHz (Whisper's expected sample rate)
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                audio_tensor = resampler(audio_tensor)
            
            # Convert to numpy array
            audio_array = audio_tensor.squeeze().numpy()
            
            # Normalize audio
            audio_array = audio_array / np.max(np.abs(audio_array))
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Audio preprocessing error: {e}")
            raise HTTPException(status_code=400, detail="Invalid audio format")
    
    async def transcribe_audio(self, audio_data: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio with optimizations"""
        start_time = time.time()
        
        try:
            # Preprocess audio
            audio_array = self.preprocess_audio(audio_data)
            
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                self._run_whisper_transcription,
                audio_array,
                language
            )
            
            processing_time = time.time() - start_time
            
            # Extract confidence score (approximate)
            confidence = self._calculate_confidence(result)
            
            return {
                "text": result["text"].strip(),
                "language": result["language"],
                "confidence": confidence,
                "processing_time": processing_time,
                "segments": result.get("segments", []),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "text": "",
                "language": "unknown",
                "confidence": 0.0,
                "processing_time": time.time() - start_time,
                "segments": [],
                "status": "error",
                "error": str(e)
            }
    
    def _run_whisper_transcription(self, audio_array: np.ndarray, language: Optional[str]) -> Dict[str, Any]:
        """Run Whisper transcription (blocking operation)"""
        with torch.no_grad():  # Disable gradient computation for inference
            result = self.model.transcribe(
                audio_array,
                language=language,
                task="transcribe",
                temperature=0.0,  # Deterministic output
                beam_size=5,      # Balance between speed and accuracy
                best_of=1,        # Speed optimization
                patience=1.0,     # Early stopping
                condition_on_previous_text=False,  # Speed optimization
                fp16=self.device == "cuda",  # Use FP16 on GPU for speed
                verbose=False
            )
        return result
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate approximate confidence score"""
        segments = result.get("segments", [])
        if not segments:
            return 0.5  # Default confidence
        
        # Average logprob across segments
        total_logprob = sum(segment.get("avg_logprob", -1.0) for segment in segments)
        avg_logprob = total_logprob / len(segments)
        
        # Convert to confidence (0-1 scale)
        confidence = max(0.0, min(1.0, (avg_logprob + 1.0)))
        return confidence

# Initialize service
whisper_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global whisper_service, redis_client, executor
    
    # Startup
    logger.info("Starting Whisper Service...")
    
    # Initialize thread pool
    executor = ThreadPoolExecutor(max_workers=4)
    
    # Initialize Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url)
    
    # Initialize Whisper service
    model_size = os.getenv("MODEL_SIZE", "base")
    device = "cuda" if torch.cuda.is_available() and os.getenv("ENABLE_GPU", "false").lower() == "true" else "cpu"
    whisper_service = WhisperService(model_size=model_size, device=device)
    
    yield
    
    # Cleanup
    logger.info("Shutting down Whisper Service...")
    if redis_client:
        await redis_client.close()
    if executor:
        executor.shutdown(wait=True)

# FastAPI app
app = FastAPI(
    title="Whisper Transcription Service",
    description="Production-ready Whisper API for real-time transcription",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        model_loaded = whisper_service is not None and whisper_service.model is not None
        redis_connected = redis_client is not None
        
        return {
            "status": "healthy" if model_loaded else "loading",
            "model_loaded": model_loaded,
            "model_size": whisper_service.model_size if whisper_service else None,
            "device": whisper_service.device if whisper_service else None,
            "redis_connected": redis_connected,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(audio_file: UploadFile = File(...), language: Optional[str] = None):
    """Transcribe uploaded audio file"""
    if not whisper_service:
        raise HTTPException(status_code=503, detail="Whisper service not ready")
    
    # Validate file type
    if not audio_file.content_type.startswith(('audio/', 'video/')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload audio or video file.")
    
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Cache request for tracking
        if redis_client:
            await redis_client.setex(
                f"transcription:{request_id}",
                300,  # 5 minutes TTL
                "processing"
            )
        
        # Transcribe audio
        result = await whisper_service.transcribe_audio(audio_data, language)
        
        # Update cache with result
        if redis_client:
            await redis_client.setex(
                f"transcription:{request_id}",
                3600,  # 1 hour TTL
                "completed"
            )
        
        return TranscriptionResponse(
            id=request_id,
            **result
        )
        
    except Exception as e:
        logger.error(f"Transcription endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe-stream")
async def transcribe_stream(request: TranscriptionRequest):
    """Transcribe base64 encoded audio data (for real-time streaming)"""
    if not whisper_service:
        raise HTTPException(status_code=503, detail="Whisper service not ready")
    
    try:
        import base64
        
        # Decode base64 audio
        audio_data = base64.b64decode(request.audio_data)
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Transcribe audio
        result = await whisper_service.transcribe_audio(audio_data, request.language)
        
        return TranscriptionResponse(
            id=request_id,
            **result
        )
        
    except Exception as e:
        logger.error(f"Stream transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List available Whisper models"""
    return {
        "available_models": ["tiny", "base", "small", "medium", "large"],
        "current_model": whisper_service.model_size if whisper_service else None,
        "device": whisper_service.device if whisper_service else None
    }

@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    if not redis_client:
        return {"error": "Redis not available"}
    
    try:
        # Get processing statistics from Redis
        stats = {
            "total_requests": await redis_client.get("stats:total_requests") or 0,
            "successful_requests": await redis_client.get("stats:successful_requests") or 0,
            "failed_requests": await redis_client.get("stats:failed_requests") or 0,
            "average_processing_time": await redis_client.get("stats:avg_processing_time") or 0,
            "uptime": datetime.now().isoformat()
        }
        return stats
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        workers=1,  # Single worker due to model memory requirements
        loop="asyncio"
    )