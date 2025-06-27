#!/usr/bin/env python3
"""
Simple Whisper Service for Digital Twin Voice Intelligence
Provides local speech-to-text transcription using OpenAI Whisper
"""

import os
import io
import time
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Whisper Service", version="1.0.0")

# Enable CORS for web app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
whisper_model = None
model_name = "base"  # Start with base model for speed

class TranscriptionResponse(BaseModel):
    text: str
    confidence: float
    language: Optional[str] = None
    duration: Optional[float] = None
    model_used: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    timestamp: str

def load_whisper_model():
    """Load Whisper model on startup"""
    global whisper_model
    try:
        import whisper
        logger.info(f"🤖 Loading Whisper model: {model_name}")
        whisper_model = whisper.load_model(model_name)
        logger.info(f"✅ Whisper model '{model_name}' loaded successfully")
        return True
    except ImportError:
        logger.error("❌ Whisper not installed. Install with: pip install openai-whisper")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to load Whisper model: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize Whisper on startup"""
    success = load_whisper_model()
    if success:
        logger.info("🚀 Simple Whisper Service started successfully")
    else:
        logger.warning("⚠️ Whisper Service started without model (install requirements)")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=whisper_model is not None,
        model_name=model_name,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: Optional[str] = None
):
    """Transcribe audio file using Whisper"""
    
    if whisper_model is None:
        raise HTTPException(
            status_code=503, 
            detail="Whisper model not loaded. Please install openai-whisper: pip install openai-whisper"
        )
    
    start_time = time.time()
    
    try:
        # Read audio data
        audio_data = await audio_file.read()
        logger.info(f"📊 Received audio file: {len(audio_data)} bytes")
        
        # Save to temporary file (Whisper needs file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            # Transcribe with Whisper
            logger.info("🎙️ Transcribing audio with Whisper...")
            
            if language:
                result = whisper_model.transcribe(temp_path, language=language)
            else:
                result = whisper_model.transcribe(temp_path)
            
            duration = time.time() - start_time
            
            # Extract results
            text = result["text"].strip()
            detected_language = result.get("language", "unknown")
            
            # Calculate confidence (Whisper doesn't provide this directly)
            # We'll use segment-level confidence if available
            segments = result.get("segments", [])
            if segments:
                # Average confidence from segments
                confidences = []
                for segment in segments:
                    if "avg_logprob" in segment:
                        # Convert log probability to confidence (rough approximation)
                        conf = min(1.0, max(0.0, (segment["avg_logprob"] + 1.0)))
                        confidences.append(conf)
                
                confidence = sum(confidences) / len(confidences) if confidences else 0.8
            else:
                confidence = 0.8  # Default confidence for Whisper
            
            logger.info(f"✅ Transcription completed in {duration:.2f}s: '{text[:50]}...'")
            
            return TranscriptionResponse(
                text=text,
                confidence=confidence,
                language=detected_language,
                duration=duration,
                model_used=model_name
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    except Exception as e:
        logger.error(f"❌ Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/models")
async def list_models():
    """List available Whisper models"""
    models = ["tiny", "base", "small", "medium", "large"]
    return {
        "available_models": models,
        "current_model": model_name,
        "model_loaded": whisper_model is not None,
        "recommendations": {
            "tiny": "Fastest, lower accuracy",
            "base": "Good balance of speed and accuracy",
            "small": "Better accuracy, moderate speed",
            "medium": "High accuracy, slower",
            "large": "Best accuracy, slowest"
        }
    }

@app.post("/switch_model/{new_model}")
async def switch_model(new_model: str):
    """Switch to a different Whisper model"""
    global whisper_model, model_name
    
    valid_models = ["tiny", "base", "small", "medium", "large"]
    if new_model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {valid_models}")
    
    try:
        import whisper
        logger.info(f"🔄 Switching to Whisper model: {new_model}")
        whisper_model = whisper.load_model(new_model)
        model_name = new_model
        logger.info(f"✅ Successfully switched to '{new_model}' model")
        
        return {
            "status": "success",
            "previous_model": model_name,
            "new_model": new_model,
            "message": f"Successfully switched to {new_model} model"
        }
    except Exception as e:
        logger.error(f"❌ Failed to switch model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to switch model: {str(e)}")

if __name__ == "__main__":
    print("🎙️ Starting Simple Whisper Service...")
    print("📋 Requirements:")
    print("   pip install openai-whisper fastapi uvicorn python-multipart")
    print("")
    print("🚀 Starting server on http://localhost:8001")
    print("📖 API docs will be available at http://localhost:8001/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )