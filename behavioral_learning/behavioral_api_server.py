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

# Add the project root directory to the path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent  # Go up to digital-twin directory
sys.path.insert(0, str(project_root))

print(f"📁 Looking for Digital Twin components in: {project_root}")
print(f"📁 Project root exists: {project_root.exists()}")

# Try to import Digital Twin components
digital_twin_available = False
digital_twin_connected = False
try:
    # Try connecting to the main digital twin via HTTP API
    import requests
    
    # Test connection to main digital twin API
    response = requests.get('http://localhost:8080/health', timeout=2)
    if response.status_code == 200:
        digital_twin_connected = True
        print("✅ Connected to Digital Twin web API!")
    else:
        print("⚠️ Digital Twin web API not responding")
except Exception as e:
    print(f"⚠️ Warning: Could not connect to Digital Twin API: {e}")
    print("📝 Running in standalone mode - data collection only")

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
    # Test connection to main digital twin API
    try:
        import requests
        response = requests.get('http://localhost:8080/health', timeout=2)
        main_twin_status = response.status_code == 200
    except:
        main_twin_status = False
    
    return {
        "status": "healthy",
        "digital_twin_available": main_twin_status,
        "digital_twin_connected": main_twin_status,
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
            # Process behavioral patterns into learning insights even without full Digital Twin
            try:
                behavioral_insight = generate_behavioral_insight(user_id, event_data, behavioral_data_store.get(user_id, []))
                enriched_event["behavioral_insight"] = behavioral_insight
                logger.info(f"🧠 Generated behavioral insight: {behavioral_insight['pattern_type']}")
                
                # Auto-sync high-confidence insights to web app digital twin
                if behavioral_insight.get('confidence', 0) >= 0.75:
                    try:
                        await sync_to_digital_twin(user_id, behavioral_insight)
                    except Exception as sync_error:
                        logger.warning(f"⚠️ Could not auto-sync to digital twin: {sync_error}")
                        
            except Exception as e:
                logger.error(f"❌ Error generating behavioral insight: {e}")
            logger.info(f"📊 Stored event locally with behavioral analysis")
        
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

# ===================================================================
# WEB INTERFACE INTEGRATION ENDPOINTS
# New endpoints to support web dashboard integration
# ===================================================================

@app.get("/user-stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get comprehensive user statistics for web dashboard integration"""
    
    try:
        # Get user events from behavioral data store
        user_events = behavioral_data_store.get(user_id, [])
        
        # Filter recent events (last 24 hours)
        now = datetime.now(timezone.utc)
        recent_events = []
        
        for event in user_events:
            try:
                # Handle nested event structure
                event_data = event
                if 'original_event' in event:
                    event_data = event['original_event']
                
                # Handle different timestamp formats
                event_time = None
                timestamp = event_data.get('timestamp')
                
                if timestamp:
                    if isinstance(timestamp, str):
                        # Handle ISO format timestamps
                        try:
                            event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except:
                            pass
                    elif isinstance(timestamp, (int, float)):
                        # Convert from milliseconds to seconds if needed
                        if timestamp > 1e12:  # If timestamp is in milliseconds
                            event_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
                        else:
                            event_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                
                # If we have a valid timestamp and it's within 24 hours, include it
                if event_time and (now - event_time).total_seconds() < 86400:  # 24 hours
                    cleaned_event = dict(event_data)  # Create a copy
                    recent_events.append(cleaned_event)
                elif not timestamp:
                    # If no timestamp, include the event anyway (better than losing data)
                    cleaned_event = dict(event_data)
                    recent_events.append(cleaned_event)
                    
            except Exception as e:
                # Include event if we can't parse it (better than losing data)
                logger.debug(f"Could not parse event: {e}")
                if 'original_event' in event:
                    recent_events.append(dict(event['original_event']))
                else:
                    recent_events.append(dict(event))
        
        # Calculate statistics
        stats = calculate_user_statistics(recent_events)
        
        logger.info(f"📊 Returning stats for {user_id}: {len(recent_events)} recent events out of {len(user_events)} total")
        
        return {
            "user_id": user_id,
            "events_count": len(recent_events),
            "total_events": len(user_events),
            "stats": stats,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user stats for {user_id}: {e}")
        return get_default_user_stats(user_id)

@app.get("/realtime-stats/{user_id}")
async def get_realtime_stats(user_id: str):
    """Get real-time user activity stats"""
    
    try:
        # Get recent events (last hour)
        user_events = behavioral_data_store.get(user_id, [])
        now = datetime.now(timezone.utc)
        recent_events = []
        
        for event in user_events:
            try:
                event_time = None
                if 'timestamp' in event:
                    timestamp = event['timestamp']
                    if isinstance(timestamp, str):
                        event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    elif isinstance(timestamp, (int, float)):
                        event_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
                
                if event_time and (now - event_time).total_seconds() < 3600:  # 1 hour
                    recent_events.append(event)
            except:
                continue
        
        # Get current activity
        current_activity = "Unknown"
        if recent_events:
            latest_event = recent_events[-1]  # Most recent
            current_activity = determine_current_activity(latest_event)
        
        # Calculate active time today (all events from today)
        today_events = []
        for event in user_events:
            try:
                event_time = None
                if 'timestamp' in event:
                    timestamp = event['timestamp']
                    if isinstance(timestamp, str):
                        event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    elif isinstance(timestamp, (int, float)):
                        event_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
                
                if event_time and event_time.date() == now.date():
                    today_events.append(event)
            except:
                continue
        
        active_time_ms = sum(event.get('time_spent_ms', 0) for event in today_events)
        active_time_ms += sum(event.get('active_time_ms', 0) for event in today_events)
        active_time_ms += sum(event.get('focus_time_ms', 0) for event in today_events)
        
        return {
            "user_id": user_id,
            "current_activity": current_activity,
            "active_time_ms": active_time_ms,
            "recent_events_count": len(recent_events),
            "today_events_count": len(today_events),
            "last_activity": recent_events[-1].get('timestamp') if recent_events else None,
            "status": "active" if recent_events else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Error getting realtime stats for {user_id}: {e}")
        return {
            "user_id": user_id,
            "current_activity": "Error retrieving data",
            "active_time_ms": 0,
            "recent_events_count": 0,
            "status": "error"
        }

@app.get("/all-events/{user_id}")
async def get_all_events(user_id: str):
    """Get all behavioral events for a user"""
    
    try:
        events = behavioral_data_store.get(user_id, [])
        
        return {
            "user_id": user_id,
            "events": events,
            "total_count": len(events),
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting all events for {user_id}: {e}")
        return {
            "user_id": user_id,
            "events": [],
            "total_count": 0,
            "error": str(e)
        }

@app.get("/learning-memories/{user_id}")
async def get_learning_memories(user_id: str):
    """Get learning memories generated from behavioral patterns for digital twin integration"""
    
    try:
        user_events = behavioral_data_store.get(user_id, [])
        
        # Extract behavioral insights and learning memories
        learning_memories = []
        pattern_insights = []
        
        for event in user_events:
            # Extract behavioral insights
            if 'behavioral_insight' in event:
                insight = event['behavioral_insight']
                learning_memories.append({
                    'memory_text': insight.get('learning_memory', ''),
                    'pattern_type': insight.get('pattern_type', 'unknown'),
                    'context': insight.get('context', ''),
                    'productivity_impact': insight.get('productivity_impact', {}),
                    'predictive_suggestions': insight.get('predictive_suggestions', []),
                    'confidence': insight.get('confidence', 0.0),
                    'timestamp': insight.get('timestamp', ''),
                    'source_event': event.get('original_event', {}).get('type', 'unknown')
                })
                
                pattern_insights.append({
                    'pattern_type': insight.get('pattern_type', 'unknown'),
                    'context': insight.get('context', ''),
                    'productivity_impact': insight.get('productivity_impact', {}),
                    'confidence': insight.get('confidence', 0.0)
                })
        
        # Generate summary insights
        pattern_summary = analyze_pattern_trends(pattern_insights)
        
        return {
            "user_id": user_id,
            "learning_memories": learning_memories,
            "pattern_insights": pattern_insights,
            "pattern_summary": pattern_summary,
            "total_memories": len(learning_memories),
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning memories for {user_id}: {e}")
        return {
            "user_id": user_id,
            "learning_memories": [],
            "pattern_insights": [],
            "pattern_summary": {},
            "total_memories": 0,
            "error": str(e)
        }

def calculate_user_statistics(events: List[Dict]) -> Dict:
    """Calculate comprehensive statistics from user events"""
    
    if not events:
        return get_default_stats()
    
    # Initialize counters
    work_time_ms = 0
    personal_time_ms = 0
    learning_time_ms = 0
    focus_sessions_count = 0
    tab_switches_count = 0
    total_active_time_ms = 0
    engagement_events = 0
    
    logger.info(f"Processing {len(events)} events for statistics")
    
    # Analyze events
    for event in events:
        event_type = event.get('type', '')
        
        if 'work_balance' in event_type or 'general_work_balance' in event_type:
            work_time_ms += event.get('work_time_ms', 0)
            personal_time_ms += event.get('personal_time_ms', 0)
            learning_time_ms += event.get('learning_time_ms', 0)
        
        elif 'focus_session' in event_type or 'general_focus_session' in event_type:
            focus_sessions_count += 1
            total_active_time_ms += event.get('focus_time_ms', 0)
        
        elif 'rapid_switching' in event_type or 'tab_switch' in event_type or 'switching' in event_type:
            tab_switches_count += 1
        
        elif 'engagement' in event_type or 'time_tracking' in event_type:
            engagement_events += 1
            total_active_time_ms += event.get('active_time_ms', 0)
        
        # Add general active time
        total_active_time_ms += event.get('time_spent_ms', 0)
    
    # If we don't have specific work/personal time, estimate from activity
    if work_time_ms == 0 and total_active_time_ms > 0:
        # Estimate work time based on domains and activity
        work_domains = ['localhost', 'salesforce.com', 'outlook.com', 'office.com', 'linkedin.com']
        work_events = [e for e in events if any(domain in e.get('domain', '') for domain in work_domains)]
        
        if len(work_events) > len(events) * 0.5:  # More than 50% work-related
            work_time_ms = int(total_active_time_ms * 0.8)  # Assume 80% work time
            personal_time_ms = total_active_time_ms - work_time_ms
    
    # Calculate productivity score
    total_time = work_time_ms + personal_time_ms + learning_time_ms
    work_percentage = (work_time_ms / max(total_time, 1)) * 100 if total_time > 0 else 0
    
    productivity_score = min(100, int(
        work_percentage * 0.7 +  # Work time weight
        (focus_sessions_count * 10) * 0.2 +  # Focus sessions weight
        max(0, (50 - tab_switches_count)) * 0.1  # Less switching is better
    ))
    
    return {
        'work_time_ms': work_time_ms,
        'personal_time_ms': personal_time_ms,
        'learning_time_ms': learning_time_ms,
        'focus_sessions_count': focus_sessions_count,
        'tab_switches_count': tab_switches_count,
        'total_active_time_ms': total_active_time_ms,
        'productivity_score': productivity_score,
        'most_used_apps': extract_most_used_apps(events),
        'peak_hours': calculate_peak_hours(events)
    }

def get_default_stats() -> Dict:
    """Return default statistics when no events are available"""
    return {
        'work_time_ms': 0,
        'personal_time_ms': 0,
        'learning_time_ms': 0,
        'focus_sessions_count': 0,
        'tab_switches_count': 0,
        'total_active_time_ms': 0,
        'productivity_score': 0,
        'most_used_apps': [],
        'peak_hours': 'No data'
    }

def get_default_user_stats(user_id: str) -> Dict:
    """Return default user stats structure"""
    return {
        "user_id": user_id,
        "events_count": 0,
        "total_events": 0,
        "stats": get_default_stats(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "error": "No behavioral data available"
    }

def determine_current_activity(latest_event: Dict) -> str:
    """Determine current activity from latest event"""
    
    event_type = latest_event.get('type', '')
    domain = latest_event.get('domain', '')
    
    if 'salesforce' in domain.lower():
        return "Working in Salesforce"
    elif 'outlook' in domain.lower() or 'office' in domain.lower():
        return "Managing emails"
    elif 'linkedin' in domain.lower():
        return "Professional networking"
    elif 'focus_session' in event_type:
        return "Deep focus work"
    elif 'switching' in event_type:
        return "Task switching"
    else:
        return f"Active on {domain}" if domain else "General browsing"

def extract_most_used_apps(events: List[Dict]) -> List[str]:
    """Extract most used applications from events"""
    
    domain_counts = {}
    
    for event in events:
        domain = event.get('domain', '')
        if domain and domain != 'unknown':
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Return top 5 domains
    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    return [domain for domain, count in sorted_domains[:5]]

def calculate_peak_hours(events: List[Dict]) -> str:
    """Calculate peak productivity hours from events"""
    
    hour_activity = {}
    
    for event in events:
        try:
            timestamp = event.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    # Parse ISO format
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                elif isinstance(timestamp, (int, float)):
                    # Convert from milliseconds
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    hour = dt.hour
                else:
                    continue
                
                hour_activity[hour] = hour_activity.get(hour, 0) + 1
        except:
            continue
    
    if not hour_activity:
        return "No activity data"
    
    peak_hour = max(hour_activity, key=hour_activity.get)
    return f"{peak_hour:02d}:00-{(peak_hour+1):02d}:00"

def generate_behavioral_insight(user_id: str, current_event: BehavioralEventData, historical_events: List[Dict]) -> Dict[str, Any]:
    """Generate intelligent insights from behavioral patterns for memory enrichment"""
    
    event_type = current_event.type
    domain = current_event.domain or "unknown"
    current_time = datetime.now(timezone.utc)
    
    # Analyze patterns from historical data
    similar_events = []
    domain_events = []
    focus_patterns = []
    work_patterns = []
    
    for event in historical_events[-50:]:  # Last 50 events for pattern analysis
        try:
            event_data = event.get('original_event', event)
            if event_data.get('type') == event_type:
                similar_events.append(event_data)
            if event_data.get('domain') == domain:
                domain_events.append(event_data)
            if 'focus' in event_data.get('type', ''):
                focus_patterns.append(event_data)
            if 'work' in event_data.get('type', '') or domain in ['salesforce.com', 'outlook.com', 'office.com']:
                work_patterns.append(event_data)
        except:
            continue
    
    # Generate contextual insights
    insight = {
        "pattern_type": determine_pattern_type(event_type, domain),
        "context": generate_context_insight(current_event, similar_events, domain_events),
        "productivity_impact": assess_productivity_impact(current_event, work_patterns, focus_patterns),
        "learning_memory": create_learning_memory(user_id, current_event, similar_events),
        "predictive_suggestions": generate_predictive_suggestions(current_event, historical_events),
        "timestamp": current_time.isoformat(),
        "confidence": calculate_insight_confidence(similar_events, domain_events)
    }
    
    return insight

def determine_pattern_type(event_type: str, domain: str) -> str:
    """Determine the type of behavioral pattern"""
    
    if 'focus_session' in event_type:
        return "deep_work_pattern"
    elif 'work_balance' in event_type:
        return "productivity_pattern"
    elif 'research' in event_type or domain in ['linkedin.com', 'company-websites']:
        return "research_pattern"
    elif domain in ['salesforce.com', 'hubspot.com']:
        return "crm_workflow_pattern"
    elif domain in ['outlook.com', 'gmail.com', 'office.com']:
        return "communication_pattern"
    elif 'switching' in event_type:
        return "context_switching_pattern"
    else:
        return "general_activity_pattern"

def generate_context_insight(current_event: BehavioralEventData, similar_events: List[Dict], domain_events: List[Dict]) -> str:
    """Generate contextual understanding of the current activity"""
    
    event_type = current_event.type
    domain = current_event.domain or "unknown"
    
    if 'focus_session' in event_type:
        avg_focus_time = sum(e.get('data', {}).get('focus_time_ms', 0) for e in similar_events) / max(len(similar_events), 1)
        return f"User typically focuses for {int(avg_focus_time/60000)} minutes on {domain}. This suggests deep work capability."
    
    elif 'work_balance' in event_type:
        work_pct = current_event.data.get('work_percentage', 0) if current_event.data else 0
        return f"Current work session is {work_pct}% productive. User shows consistent work patterns on {domain}."
    
    elif 'research' in event_type:
        research_count = len([e for e in domain_events if 'research' in e.get('type', '')])
        return f"User has conducted {research_count} research sessions on {domain}. Shows systematic information gathering."
    
    elif domain in ['salesforce.com', 'hubspot.com']:
        crm_sessions = len(domain_events)
        return f"User has {crm_sessions} CRM sessions, indicating active sales/customer management workflow."
    
    else:
        return f"Regular activity on {domain}. Part of user's established work routine."

def assess_productivity_impact(current_event: BehavioralEventData, work_patterns: List[Dict], focus_patterns: List[Dict]) -> Dict[str, Any]:
    """Assess how this activity impacts overall productivity"""
    
    if 'focus_session' in current_event.type:
        focus_time = current_event.data.get('focus_time_ms', 0) if current_event.data else 0
        avg_focus = sum(e.get('data', {}).get('focus_time_ms', 0) for e in focus_patterns) / max(len(focus_patterns), 1)
        
        return {
            "impact_type": "positive",
            "impact_score": min(100, int((focus_time / max(avg_focus, 1)) * 80)),
            "description": f"Deep focus session contributes significantly to productivity",
            "recommendation": "Schedule more sessions like this during peak energy hours"
        }
    
    elif 'switching' in current_event.type:
        return {
            "impact_type": "negative",
            "impact_score": -30,
            "description": "Context switching reduces focus efficiency",
            "recommendation": "Consider batching similar tasks to reduce switching"
        }
    
    elif current_event.domain in ['salesforce.com', 'linkedin.com']:
        return {
            "impact_type": "positive",
            "impact_score": 70,
            "description": "Core business activity - essential for sales productivity",
            "recommendation": "Track outcomes to measure ROI of time investment"
        }
    
    else:
        return {
            "impact_type": "neutral",
            "impact_score": 50,
            "description": "Standard work activity",
            "recommendation": "Monitor for optimization opportunities"
        }

def create_learning_memory(user_id: str, current_event: BehavioralEventData, similar_events: List[Dict]) -> str:
    """Create a natural language memory that can be stored in the digital twin"""
    
    event_type = current_event.type
    domain = current_event.domain or "unknown"
    current_time = datetime.now(timezone.utc)
    
    if 'focus_session' in event_type:
        focus_time = current_event.data.get('focus_time_ms', 0) if current_event.data else 0
        return f"On {current_time.strftime('%A at %H:%M')}, I had a {int(focus_time/60000)}-minute deep focus session working on {domain}. This was productive time where I could concentrate without interruptions. I should protect more time blocks like this for complex work."
    
    elif 'work_balance' in event_type:
        work_pct = current_event.data.get('work_percentage', 0) if current_event.data else 0
        return f"My work session on {current_time.strftime('%A at %H:%M')} was {work_pct}% focused on productive activities. I spent time on {domain} as part of my core business activities. This helps me understand my productivity patterns."
    
    elif 'research' in event_type:
        target = current_event.data.get('target', 'prospects') if current_event.data else 'information'
        return f"I conducted research on {target} using {domain} on {current_time.strftime('%A at %H:%M')}. This research activity is part of my systematic approach to gathering information for business decisions."
    
    elif domain in ['salesforce.com', 'hubspot.com']:
        return f"I used {domain} for CRM activities on {current_time.strftime('%A at %H:%M')}. This is core business work involving customer relationship management and sales pipeline activities."
    
    else:
        return f"I was active on {domain} on {current_time.strftime('%A at %H:%M')} as part of my regular work routine. This activity contributes to my overall productivity and business objectives."

def generate_predictive_suggestions(current_event: BehavioralEventData, historical_events: List[Dict]) -> List[str]:
    """Generate predictive suggestions based on patterns"""
    
    suggestions = []
    event_type = current_event.type
    domain = current_event.domain or "unknown"
    
    # Analyze time patterns
    current_hour = datetime.now(timezone.utc).hour
    
    if 'focus_session' in event_type:
        suggestions.extend([
            f"Based on your patterns, schedule your next focus session around {(current_hour + 2) % 24}:00",
            "Consider blocking this time slot for similar deep work in your calendar",
            "Your focus sessions are most effective - prioritize them for complex tasks"
        ])
    
    elif domain == 'salesforce.com':
        suggestions.extend([
            "After Salesforce sessions, you typically research prospects on LinkedIn",
            "Consider preparing your next follow-up emails while CRM data is fresh",
            "Update your pipeline status to maintain momentum"
        ])
    
    elif domain == 'linkedin.com' and 'research' in event_type:
        suggestions.extend([
            "Research sessions often lead to outreach - prepare your messaging templates",
            "Add researched prospects to your CRM for systematic follow-up",
            "Consider setting reminders for follow-up actions within 24 hours"
        ])
    
    # Pattern-based suggestions
    if len(historical_events) > 10:
        recent_domains = [e.get('original_event', e).get('domain') for e in historical_events[-10:]]
        if recent_domains.count(domain) >= 3:
            suggestions.append(f"You've been very active on {domain} - consider if this focus is aligned with your priorities")
    
    return suggestions[:3]  # Return top 3 suggestions

def calculate_insight_confidence(similar_events: List[Dict], domain_events: List[Dict]) -> float:
    """Calculate confidence score for the generated insights"""
    
    pattern_strength = min(len(similar_events) / 5.0, 1.0)  # More similar events = higher confidence
    domain_familiarity = min(len(domain_events) / 10.0, 1.0)  # More domain usage = higher confidence
    
    base_confidence = 0.6  # Base confidence for any insight
    pattern_bonus = pattern_strength * 0.3
    domain_bonus = domain_familiarity * 0.1
    
    return min(base_confidence + pattern_bonus + domain_bonus, 0.95)

async def sync_to_digital_twin(user_id: str, behavioral_insight: Dict[str, Any]):
    """Auto-sync high-confidence behavioral insights to web app digital twin"""
    
    try:
        import aiohttp
        
        web_app_url = "http://localhost:8080"
        
        # Prepare the insight for digital twin storage
        insight_data = {
            "memory_text": behavioral_insight.get('learning_memory', ''),
            "pattern_type": behavioral_insight.get('pattern_type', 'unknown'),
            "context": behavioral_insight.get('context', ''),
            "productivity_impact": behavioral_insight.get('productivity_impact', {}),
            "predictive_suggestions": behavioral_insight.get('predictive_suggestions', []),
            "confidence": behavioral_insight.get('confidence', 0.0),
            "timestamp": behavioral_insight.get('timestamp', ''),
            "auto_sync": True
        }
        
        # Send to web app for immediate integration
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{web_app_url}/auto-sync-memory/{user_id}",
                json=insight_data,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Auto-synced behavioral insight to digital twin: {result.get('memory_id', 'unknown')}")
                    return True
                else:
                    logger.warning(f"⚠️ Auto-sync failed with status {response.status}")
                    return False
                    
    except ImportError:
        # Fallback to requests if aiohttp not available
        try:
            import requests
            
            web_app_url = "http://localhost:8080"
            
            insight_data = {
                "memory_text": behavioral_insight.get('learning_memory', ''),
                "pattern_type": behavioral_insight.get('pattern_type', 'unknown'),
                "context": behavioral_insight.get('context', ''),
                "productivity_impact": behavioral_insight.get('productivity_impact', {}),
                "predictive_suggestions": behavioral_insight.get('predictive_suggestions', []),
                "confidence": behavioral_insight.get('confidence', 0.0),
                "timestamp": behavioral_insight.get('timestamp', ''),
                "auto_sync": True
            }
            
            response = requests.post(
                f"{web_app_url}/auto-sync-memory/{user_id}",
                json=insight_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Auto-synced behavioral insight to digital twin: {result.get('memory_id', 'unknown')}")
                return True
            else:
                logger.warning(f"⚠️ Auto-sync failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Auto-sync failed: {e}")
            return False
    
    except Exception as e:
        logger.warning(f"⚠️ Auto-sync failed: {e}")
        return False

def analyze_pattern_trends(pattern_insights: List[Dict]) -> Dict[str, Any]:
    """Analyze trends across behavioral patterns"""
    
    if not pattern_insights:
        return {
            "dominant_patterns": [],
            "productivity_trend": "insufficient_data",
            "recommendations": ["Continue using the system to generate insights"],
            "pattern_strength": 0.0
        }
    
    # Count pattern types
    pattern_counts = {}
    total_confidence = 0
    positive_impacts = 0
    
    for insight in pattern_insights:
        pattern_type = insight.get('pattern_type', 'unknown')
        pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        total_confidence += insight.get('confidence', 0)
        
        impact = insight.get('productivity_impact', {})
        if impact.get('impact_type') == 'positive':
            positive_impacts += 1
    
    # Identify dominant patterns
    sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
    dominant_patterns = [{"pattern": p[0], "frequency": p[1]} for p in sorted_patterns[:3]]
    
    # Calculate overall trend
    avg_confidence = total_confidence / len(pattern_insights)
    productivity_ratio = positive_impacts / len(pattern_insights)
    
    if productivity_ratio >= 0.7:
        productivity_trend = "improving"
    elif productivity_ratio >= 0.4:
        productivity_trend = "stable"
    else:
        productivity_trend = "needs_attention"
    
    # Generate recommendations
    recommendations = []
    
    if 'deep_work_pattern' in pattern_counts:
        recommendations.append("Your deep work patterns are strong - schedule more focus blocks")
    
    if 'context_switching_pattern' in pattern_counts:
        recommendations.append("Reduce context switching by batching similar tasks")
    
    if 'crm_workflow_pattern' in pattern_counts:
        recommendations.append("Your CRM usage shows good customer management habits")
    
    if not recommendations:
        recommendations.append("Continue building behavioral patterns for personalized insights")
    
    return {
        "dominant_patterns": dominant_patterns,
        "productivity_trend": productivity_trend,
        "pattern_strength": avg_confidence,
        "positive_activity_ratio": productivity_ratio,
        "recommendations": recommendations,
        "insights_generated": len(pattern_insights)
    }

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