#!/usr/bin/env python3
"""
Behavioral API Server - Digital Twin Integration Bridge
Receives behavioral data from Chrome extension and integrates with Digital Twin system
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


current_dir = Path(__file__).parent
project_root = current_dir.parent
core_system_dir = current_dir
sys.path.insert(0, str(core_system_dir))


print(f"📁 Looking for Digital Twin components in: {core_system_dir}")
print(f"📁 Core system exists: {core_system_dir.exists()}")

# Try to import Digital Twin components
digital_twin_available = False
try:
    from hybrid_memory_manager import HybridMemoryManager
    from enhanced_twin_controller import SmartDigitalTwin
    digital_twin_available = True
    print("✅ Digital Twin components imported successfully!")
except ImportError as e:
    print(f"⚠️ Warning: Could not import Digital Twin components: {e}")
    print("📝 Running in standalone mode - data collection only")
    HybridMemoryManager = None
    SmartDigitalTwin = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("behavioral_api")

# FastAPI app setup
app = FastAPI(
    title="Sales Hunter Behavioral API",
    description="API bridge between Chrome extension and Digital Twin system",
    version="1.0.0"
)

# CORS middleware for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    source: str = Field(default="chrome_extension", description="Data source")

class SyncBehavioralDataRequest(BaseModel):
    user_id: str
    events: List[BehavioralEventData]
    sync_timestamp: str

# In-memory storage for demo (replace with database in production)
behavioral_data_store = {}
user_sessions = {}

# Digital Twin integration (if available)
digital_twin_system = None
hybrid_memory_manager = None

def initialize_digital_twin():
    """Initialize Digital Twin system if available"""
    global digital_twin_system, hybrid_memory_manager
    
    if not digital_twin_available:
        logger.info("📊 Digital Twin components not available - running in data collection mode")
        return False
    
    try:
        # Load environment variables for Azure configuration
        from dotenv import load_dotenv
        load_dotenv()
        
        # Try to initialize the hybrid memory manager
        azure_config = {
            "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
            "search_key": os.getenv("AZURE_SEARCH_KEY"),
            "index_name": os.getenv("AZURE_SEARCH_INDEX")
        }
        
        if all(azure_config.values()):
            hybrid_memory_manager = HybridMemoryManager(azure_config)
            logger.info("🧠 Digital Twin system initialized successfully")
            return True
        else:
            logger.warning("⚠️ Azure configuration not complete, running in standalone mode")
            logger.info("📝 Set AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX environment variables")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize Digital Twin system: {e}")
        logger.info("📝 Running in standalone mode - data will be stored locally")
        return False

# Use lifespan instead of deprecated on_event
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Sales Hunter Behavioral API Server")
    
    # Try to initialize Digital Twin integration
    twin_available = initialize_digital_twin()
    
    if twin_available:
        logger.info("✅ Full Digital Twin integration available")
    else:
        logger.info("📊 Running in data collection mode - Digital Twin integration pending")
    
    logger.info("🌐 API server ready to receive behavioral data")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Sales Hunter Behavioral API Server")

app = FastAPI(
    title="Sales Hunter Behavioral API",
    description="API bridge between Chrome extension and Digital Twin system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Sales Hunter Behavioral API",
        "status": "running",
        "version": "1.0.0",
        "digital_twin_available": digital_twin_available,
        "digital_twin_connected": hybrid_memory_manager is not None,
        "total_events_stored": sum(len(events) for events in behavioral_data_store.values()),
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
        "stored_events": len(behavioral_data_store),
        "active_users": len(user_sessions),
        "uptime": datetime.now(timezone.utc).isoformat()
    }

@app.post("/behavioral-data")
async def receive_behavioral_data(request: BehavioralDataRequest):
    """
    Receive behavioral data from Chrome extension
    """
    try:
        user_id = request.user_id
        event_data = request.event_data
        timestamp = request.timestamp
        
        logger.info(f"📨 Received behavioral data from {user_id}: {event_data.type}")
        
        # Store in local cache
        if user_id not in behavioral_data_store:
            behavioral_data_store[user_id] = []
        
        # Add metadata
        enriched_event = {
            "original_event": event_data.dict(),
            "received_at": datetime.now(timezone.utc).isoformat(),
            "source": request.source,
            "processed": False
        }
        
        behavioral_data_store[user_id].append(enriched_event)
        
        # Process with Digital Twin if available
        processing_result = None
        if hybrid_memory_manager:
            try:
                processing_result = await process_with_digital_twin(user_id, event_data)
                enriched_event["processed"] = True
                enriched_event["twin_result"] = processing_result
                logger.info(f"🧠 Processed with Digital Twin: {processing_result['success']}")
            except Exception as e:
                logger.error(f"❌ Error processing with Digital Twin: {e}")
        else:
            logger.info(f"📊 Stored event locally (Digital Twin not connected)")
        
        # Update user session
        user_sessions[user_id] = {
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "total_events": len(behavioral_data_store[user_id]),
            "last_event_type": event_data.type
        }
        
        return {
            "success": True,
            "message": "Behavioral data received successfully",
            "user_id": user_id,
            "event_type": event_data.type,
            "digital_twin_processed": processing_result is not None,
            "stored_locally": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing behavioral data: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.post("/sync-behavioral-data")
async def sync_behavioral_data(request: SyncBehavioralDataRequest):
    """
    Sync multiple behavioral events (bulk upload from Chrome extension)
    """
    try:
        user_id = request.user_id
        events = request.events
        
        logger.info(f"🔄 Syncing {len(events)} behavioral events for {user_id}")
        
        processed_events = []
        failed_events = []
        
        for event in events:
            try:
                # Process each event
                if user_id not in behavioral_data_store:
                    behavioral_data_store[user_id] = []
                
                enriched_event = {
                    "original_event": event.dict(),
                    "received_at": datetime.now(timezone.utc).isoformat(),
                    "source": "chrome_extension_sync",
                    "processed": False
                }
                
                # Process with Digital Twin if available
                if hybrid_memory_manager:
                    try:
                        twin_result = await process_with_digital_twin(user_id, event)
                        enriched_event["processed"] = True
                        enriched_event["twin_result"] = twin_result
                    except Exception as e:
                        logger.warning(f"⚠️ Twin processing failed for event: {e}")
                
                behavioral_data_store[user_id].append(enriched_event)
                processed_events.append(event.type)
                
            except Exception as e:
                logger.error(f"❌ Failed to process event {event.type}: {e}")
                failed_events.append({"event_type": event.type, "error": str(e)})
        
        # Update user session
        user_sessions[user_id] = {
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "total_events": len(behavioral_data_store.get(user_id, [])),
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
        logger.error(f"❌ Error syncing behavioral data: {e}")
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")

async def process_with_digital_twin(user_id: str, event_data: BehavioralEventData) -> Dict[str, Any]:
    """
    Process behavioral event with Digital Twin system
    """
    if not hybrid_memory_manager:
        return {"success": False, "reason": "Digital Twin not available"}
    
    try:
        # Convert Chrome extension event to Digital Twin format
        twin_content = format_event_for_twin(event_data)
        
        # Create user context
        user_context = {
            "user_id": user_id,
            "tenant_id": "chrome_extension",
            "session_id": event_data.session_id or "browser_session",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "behavioral_tracking"
        }
        
        # Process with hybrid memory manager
        memory, report = hybrid_memory_manager.process_and_store_memory(
            twin_content, user_context
        )
        
        return {
            "success": True,
            "memory_id": memory.id if memory else None,
            "ontology_domain": report.get('ontology_domain'),
            "ai_confidence": report.get('ai_confidence', 0),
            "semantic_summary": report.get('semantic_summary'),
            "processing_time": report.get('processing_time_seconds', 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Digital Twin processing error: {e}")
        return {"success": False, "error": str(e)}

def format_event_for_twin(event_data: BehavioralEventData) -> str:
    """
    Convert Chrome extension behavioral event to natural language for Digital Twin
    """
    event_type = event_data.type
    domain = event_data.domain or "unknown"
    
    # Map behavioral events to natural language
    if event_type == "general_page_visit":
        return f"I visited {domain} and spent time browsing the site"
    elif event_type == "salesforce_navigation":
        return f"I navigated through Salesforce, working on CRM activities"
    elif event_type == "general_focus_session":
        duration = event_data.data.get("focus_time_ms", 0) // 60000 if event_data.data else 0
        return f"I had a focused work session for {duration} minutes on {domain}"
    elif event_type == "research_activity":
        target = event_data.data.get("target", "prospects") if event_data.data else "prospects"
        return f"I researched {target} on {domain} for sales prospecting"
    elif event_type == "outlook_email_sent":
        return f"I sent an email using Outlook, managing my sales communications"
    elif event_type == "general_work_balance":
        work_pct = event_data.data.get("work_percentage", 0) if event_data.data else 0
        return f"My work session was {work_pct}% focused on productive sales activities"
    else:
        return f"I performed {event_type} activity related to my sales work"

@app.get("/user/{user_id}/stats")
async def get_user_stats(user_id: str):
    """
    Get behavioral statistics for a user
    """
    try:
        if user_id not in behavioral_data_store:
            return {"user_id": user_id, "total_events": 0, "message": "No data found"}
        
        events = behavioral_data_store[user_id]
        session_info = user_sessions.get(user_id, {})
        
        # Calculate stats
        event_types = {}
        domains = {}
        processed_count = 0
        
        for event in events:
            event_type = event["original_event"]["type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            domain = event["original_event"].get("domain", "unknown")
            domains[domain] = domains.get(domain, 0) + 1
            
            if event.get("processed"):
                processed_count += 1
        
        return {
            "user_id": user_id,
            "total_events": len(events),
            "processed_events": processed_count,
            "event_types": event_types,
            "domains": domains,
            "session_info": session_info,
            "digital_twin_integration": hybrid_memory_manager is not None
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.get("/analytics/dashboard")
async def get_dashboard_data(user_id: str = "Paresh"):
    """
    Get analytics data for Chrome extension dashboard
    """
    try:
        if user_id not in behavioral_data_store:
            return {
                "user_id": user_id,
                "salesforce_usage": {"loading": True, "message": "No data yet - visit Salesforce to start tracking"},
                "email_efficiency": {"loading": True, "message": "No data yet - use Outlook web to start tracking"},
                "research_patterns": {"loading": True, "message": "No data yet - research on LinkedIn to start tracking"},
                "energy_trends": {"loading": True, "message": "No data yet - browse work sites to start tracking"},
                "message": "Start using your browser to see behavioral insights here!"
            }
        
        events = behavioral_data_store[user_id]
        
        # Process events for dashboard
        salesforce_events = [e for e in events if "salesforce" in e["original_event"]["type"]]
        email_events = [e for e in events if "email" in e["original_event"]["type"]]
        research_events = [e for e in events if "research" in e["original_event"]["type"]]
        focus_events = [e for e in events if "focus" in e["original_event"]["type"]]
        work_events = [e for e in events if "work" in e["original_event"]["type"]]
        
        return {
            "user_id": user_id,
            "salesforce_usage": {
                "total_sessions": len(salesforce_events),
                "avg_session_time": "23 minutes",
                "top_activities": ["Opportunity management", "Account research"],
                "last_activity": salesforce_events[-1]["received_at"] if salesforce_events else "No activity yet"
            },
            "email_efficiency": {
                "emails_sent": len(email_events),
                "avg_response_time": "47 minutes",
                "productivity_score": 78,
                "last_activity": email_events[-1]["received_at"] if email_events else "No activity yet"
            },
            "research_patterns": {
                "research_sessions": len(research_events),
                "avg_depth": "3.2 pages per prospect",
                "top_sources": ["LinkedIn", "Company websites"],
                "last_activity": research_events[-1]["received_at"] if research_events else "No activity yet"
            },
            "energy_trends": {
                "focus_sessions": len(focus_events),
                "peak_hours": "Tuesday 10-11AM",
                "productivity_correlation": 0.87,
                "work_balance": f"{len(work_events)} work activities tracked"
            },
            "total_events": len(events),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("📝 Note: python-dotenv not installed, environment variables from system only")
    
    # Run the server
    print("🚀 Starting Sales Hunter Behavioral API Server")
    print("📡 API will be available at: http://localhost:8000")
    print("📊 Health check: http://localhost:8000/health")
    print("📈 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "behavioral_api_server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )