#!/usr/bin/env python3
"""
Behavioral API Server - Universal Digital Twin Integration (CLEAN VERSION)
AI-driven pattern discovery for any life domain, with suppressed verbose logging
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json
import logging
import uvicorn
import sys
import os
from pathlib import Path

# === SUPPRESS ALL VERBOSE LOGGING ===
# Silence uvicorn access logs and other verbose loggers
logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
logging.getLogger("uvicorn").setLevel(logging.ERROR)
logging.getLogger("fastapi").setLevel(logging.ERROR)

# Configure minimal logging - only show critical events
logging.basicConfig(
    level=logging.ERROR,
    format='%(message)s'
)

# Create a clean logger for essential events only
class CleanAPILogger:
    def info(self, message):
        # Only show essential startup/shutdown messages
        if any(keyword in message for keyword in ["Starting", "Shutting down", "initialized"]):
            print(f"🌐 {message}")
    
    def error(self, message):
        print(f"❌ {message}")
    
    def warning(self, message):
        # Suppress warnings unless critical
        if "Critical" in message:
            print(f"⚠️ {message}")

logger = CleanAPILogger()

# Add the current directory to the path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Try to import Digital Twin components (silently)
digital_twin_available = False
try:
    from hybrid_memory_manager import HybridMemoryManager
    digital_twin_available = True
    # Silent import success
except ImportError as e:
    # Only show if critical
    digital_twin_available = False
    HybridMemoryManager = None

# Pydantic models for request validation
class BehavioralEventData(BaseModel):
    type: str
    timestamp: int
    domain: Optional[str] = None
    url: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class BehavioralDataRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    event_data: BehavioralEventData = Field(..., description="Behavioral event data")
    timestamp: str = Field(..., description="ISO timestamp")
    source: str = Field(default="digital_tracking", description="Data source")

class SyncBehavioralDataRequest(BaseModel):
    user_id: str
    events: List[BehavioralEventData]
    sync_timestamp: str

# Lightweight session tracking
user_sessions = {}
hybrid_memory_manager = None

def initialize_digital_twin():
    """Initialize Universal Digital Twin system if available"""
    global hybrid_memory_manager
    
    if not digital_twin_available:
        return False
    
    try:
        # Load environment variables for Azure configuration
        from dotenv import load_dotenv
        load_dotenv()
        
        azure_config = {
            "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
            "search_key": os.getenv("AZURE_SEARCH_KEY"),
            "index_name": os.getenv("AZURE_SEARCH_INDEX")
        }
        
        if all(azure_config.values()):
            hybrid_memory_manager = HybridMemoryManager(azure_config)
            logger.info("Universal Digital Twin system initialized successfully")
            return True
        else:
            return False
            
    except Exception as e:
        return False

# Create FastAPI app
app = FastAPI(
    title="Universal Digital Twin API",
    description="AI-driven behavioral intelligence for any life domain",
    version="3.0.0"
)

# Comprehensive CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "http://localhost:*",
        "https://localhost:*",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize Digital Twin on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Universal Digital Twin API Server")
    twin_available = initialize_digital_twin()
    
    if twin_available:
        print("🧠 Digital Twin ready - behavioral learning active")
    else:
        print("📊 API ready - data collection mode")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Universal Digital Twin API Server")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Universal Digital Twin API",
        "status": "running",
        "version": "3.0.0",
        "digital_twin_available": digital_twin_available,
        "digital_twin_connected": hybrid_memory_manager is not None,
        "continuous_learning": hybrid_memory_manager is not None,
        "universal_intelligence": True,
        "active_users": len(user_sessions),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "digital_twin_available": digital_twin_available,
        "digital_twin_connected": hybrid_memory_manager is not None,
        "continuous_learning": hybrid_memory_manager is not None,
        "universal_intelligence": True,
        "active_users": len(user_sessions),
        "cors_enabled": True,
        "uptime": datetime.now(timezone.utc).isoformat()
    }

# Proper OPTIONS handling for CORS preflight
@app.options("/behavioral-data")
async def options_behavioral_data():
    """Handle CORS preflight for behavioral-data endpoint"""
    return {"message": "CORS preflight successful"}

@app.options("/sync-behavioral-data")
async def options_sync_behavioral_data():
    """Handle CORS preflight for sync-behavioral-data endpoint"""
    return {"message": "CORS preflight successful"}

def format_event_for_twin(event_data: BehavioralEventData) -> str:
    """Convert behavioral event to natural language memory"""
    event_type = event_data.type
    domain = event_data.domain or "unknown"
    
    # Universal behavioral insights
    if "work_balance" in event_type:
        work_pct = event_data.data.get("work_percentage", 0) if event_data.data else 0
        return f"Digital productivity session with {work_pct}% focused work engagement"
    
    elif "focus_session" in event_type:
        duration = event_data.data.get("focus_time_ms", 0) // 60000 if event_data.data else 0
        return f"Sustained attention period: {duration} minutes of concentrated digital work"
    
    elif "page_visit" in event_type:
        return f"Digital content engagement: explored and interacted with {domain}"
    
    elif "time_tracking" in event_type:
        time_spent = event_data.data.get("active_time_ms", 0) // 60000 if event_data.data else 0
        return f"Active engagement: spent {time_spent} minutes working with {domain}"
    
    elif "rapid_switching" in event_type:
        return f"Multitasking behavior: dynamic context switching between digital tasks"
    
    elif "navigation" in event_type:
        return f"Platform navigation: explored features and functionality within {domain}"
    
    elif "email" in event_type:
        return f"Digital communication: engaged in email correspondence and messaging"
    
    elif "research" in event_type:
        return f"Information gathering: conducted research and knowledge acquisition"
    
    elif "manual_input" in event_type:
        meeting_outcome = event_data.data.get("meeting_outcome") if event_data.data else None
        energy_level = event_data.data.get("energy_level") if event_data.data else None
        quick_note = event_data.data.get("quick_note") if event_data.data else None
        
        parts = ["Manual activity log:"]
        if meeting_outcome:
            parts.append(f"meeting result was {meeting_outcome}")
        if energy_level:
            parts.append(f"energy level was {energy_level}/5")
        if quick_note:
            parts.append(f"noted: {quick_note}")
        
        return " ".join(parts)
    
    elif "test_event" in event_type:
        return "System test: verified digital twin behavioral tracking connectivity"
    
    else:
        return f"Digital activity: {event_type.replace('_', ' ')} on {domain}"

async def process_with_digital_twin(user_id: str, event_data: BehavioralEventData) -> Dict[str, Any]:
    """Process behavioral event with Digital Twin"""
    if not hybrid_memory_manager:
        return {"success": False, "reason": "Digital Twin not available"}
    
    try:
        memory_content = format_event_for_twin(event_data)
        
        user_context = {
            "user_id": user_id,
            "tenant_id": "universal_behavioral_tracking",
            "session_id": event_data.session_id or "digital_session",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "chrome_extension_behavioral_tracking"
        }
        
        memory, report = hybrid_memory_manager.process_and_store_memory(
            memory_content, user_context
        )
        
        # Show clean memory creation event
        if memory and report.get('success'):
            print(f"💾 Learned: {memory.semantic_summary[:60]}...")
        
        return {
            "success": True,
            "memory_id": memory.id if memory else None,
            "ontology_domain": report.get('ontology_domain'),
            "ai_confidence": report.get('ai_confidence', 0),
            "semantic_summary": report.get('semantic_summary'),
            "processing_time": report.get('processing_time_seconds', 0),
            "memory_content": memory_content
        }
        
    except Exception as e:
        logger.error(f"Digital Twin processing error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/behavioral-data")
async def receive_behavioral_data(request: BehavioralDataRequest):
    """Receive and process behavioral data"""
    try:
        user_id = request.user_id
        event_data = request.event_data
        
        # Silent processing - no verbose logs
        
        # Process with Digital Twin if available
        processing_result = None
        if hybrid_memory_manager:
            try:
                processing_result = await process_with_digital_twin(user_id, event_data)
                # Silent processing - only show memory creation above
            except Exception as e:
                logger.error(f"Error processing with Digital Twin: {e}")
                processing_result = {"success": False, "error": str(e)}
        
        # Update session tracking silently
        if user_id not in user_sessions:
            user_sessions[user_id] = {"events_processed": 0}
        
        user_sessions[user_id].update({
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "events_processed": user_sessions[user_id].get("events_processed", 0) + 1,
            "last_event_type": event_data.type
        })
        
        return {
            "success": True,
            "message": "Behavioral data received and processed",
            "user_id": user_id,
            "event_type": event_data.type,
            "digital_twin_processed": processing_result.get("success", False) if processing_result else False,
            "memory_id": processing_result.get("memory_id") if processing_result else None,
            "processing_details": processing_result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing behavioral data: {e}")
        return {
            "success": False,
            "message": f"Error processing data: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.post("/sync-behavioral-data")
async def sync_behavioral_data(request: SyncBehavioralDataRequest):
    """Sync multiple behavioral events"""
    try:
        user_id = request.user_id
        events = request.events
        
        # Silent bulk processing
        processed_events = []
        failed_events = []
        
        for event in events:
            try:
                if hybrid_memory_manager:
                    twin_result = await process_with_digital_twin(user_id, event)
                    if twin_result.get("success"):
                        processed_events.append({
                            "event_type": event.type,
                            "memory_id": twin_result.get("memory_id")
                        })
                    else:
                        failed_events.append({
                            "event_type": event.type, 
                            "error": twin_result.get("error", "Unknown error")
                        })
                else:
                    failed_events.append({
                        "event_type": event.type, 
                        "error": "Digital Twin not available"
                    })
                
            except Exception as e:
                failed_events.append({
                    "event_type": event.type, 
                    "error": str(e)
                })
        
        # Show bulk processing result
        if processed_events:
            print(f"💾 Bulk learned: {len(processed_events)} behavioral patterns")
        
        # Update session
        user_sessions[user_id] = {
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "events_processed": user_sessions.get(user_id, {}).get("events_processed", 0) + len(processed_events),
            "last_sync": request.sync_timestamp
        }
        
        return {
            "success": True,
            "message": f"Synced {len(processed_events)} events successfully",
            "user_id": user_id,
            "processed_count": len(processed_events),
            "failed_count": len(failed_events),
            "processed_events": processed_events,
            "failed_events": failed_events,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error syncing behavioral data: {e}")
        return {
            "success": False,
            "message": f"Sync error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.get("/user/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user behavioral statistics"""
    try:
        session_info = user_sessions.get(user_id, {})
        
        if hybrid_memory_manager:
            profile = hybrid_memory_manager.get_user_memory_profile(user_id)
            
            return {
                "user_id": user_id,
                "total_memories": profile.get('total_memories', 0),
                "domain_distribution": profile.get('domain_distribution', {}),
                "recent_activity": profile.get('recent_activity', 0),
                "session_info": session_info,
                "digital_twin_integration": True
            }
        else:
            return {
                "user_id": user_id,
                "session_info": session_info,
                "digital_twin_integration": False,
                "message": "Digital Twin not available"
            }
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return {
            "user_id": user_id,
            "error": str(e),
            "digital_twin_integration": False
        }

@app.get("/analytics/dashboard")
async def get_dashboard_data(user_id: str = "Paresh"):
    """Get dashboard analytics data"""
    try:
        if hybrid_memory_manager:
            profile = hybrid_memory_manager.get_user_memory_profile(user_id)
            
            return {
                "user_id": user_id,
                "dashboard_metrics": {
                    "total_behavioral_memories": profile.get('total_memories', 0),
                    "domain_distribution": profile.get('domain_distribution', {}),
                    "recent_activity": profile.get('recent_activity', 0),
                    "digital_engagement": "AI analyzing patterns",
                    "productivity_insights": "Continuous learning enabled"
                },
                "digital_twin_status": "Active and learning",
                "continuous_learning": True,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "user_id": user_id,
                "message": "Digital Twin integration not available",
                "continuous_learning": False
            }
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {
            "user_id": user_id,
            "error": str(e),
            "continuous_learning": False
        }

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    print("🚀 Universal Digital Twin API Server")
    print("🔇 Clean mode - only essential events shown")
    print("📡 http://localhost:8000")
    
    # Run with suppressed uvicorn logs
    uvicorn.run(
        "behavioral_api_server:app",
        host="0.0.0.0",
        port=8000,
        log_level="error",  # Only show errors
        access_log=False,   # Disable access logs
        reload=True
    )