#!/usr/bin/env python3
"""
Collaboration Intelligence API Server
Handles Slack/Teams integration and AI-powered message analysis
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Collaboration Intelligence API",
    description="AI-powered Slack/Teams integration for digital twin",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
@dataclass
class CollaborationMessage:
    id: str
    platform: str  # "slack" or "teams"
    channel: str
    user: str
    text: str
    timestamp: datetime
    thread_ts: Optional[str] = None
    mentions: List[str] = None
    attachments: List[Dict] = None
    reactions: List[str] = None

@dataclass
class MessageInsight:
    message_id: str
    action_items: List[str]
    deadlines: List[str]
    decisions: List[str]
    questions: List[str]
    priority_score: float
    sentiment: str
    stakeholders: List[str]
    project_tags: List[str]
    suggested_actions: List[Dict[str, Any]]

@dataclass
class SuggestedAction:
    id: str
    type: str  # "create_task", "schedule_meeting", "send_reminder", "auto_reply"
    title: str
    description: str
    confidence: float
    context: Dict[str, Any]
    status: str = "pending"  # "pending", "approved", "executed", "dismissed"

class MonitoringConfig(BaseModel):
    channels: List[str]
    users: List[str]
    keywords: List[str]
    auto_actions_enabled: bool = False
    platforms: List[str] = ["slack", "teams"]

class ActionRequest(BaseModel):
    action_id: str
    approved: bool

# Global storage (in production, use database)
monitored_channels = []
monitored_users = []
monitored_keywords = []
recent_messages: List[CollaborationMessage] = []
message_insights: Dict[str, MessageInsight] = {}
suggested_actions: Dict[str, SuggestedAction] = {}
auto_actions_enabled = False

# Mock data for testing
MOCK_CHANNELS = {
    "slack": ["#general", "#product-updates", "#dev-team", "#marketing", "#q4-planning"],
    "teams": ["Product Planning", "Development Team", "Marketing Strategy", "Executive Updates"]
}

MOCK_USERS = ["sarah.johnson", "mike.chen", "lisa.williams", "john.smith", "alex.kumar"]

MOCK_MESSAGES = [
    {
        "platform": "slack",
        "channel": "#product-updates",
        "user": "sarah.johnson", 
        "text": "We need to finalize the Q4 roadmap by Friday. @mike.chen can you prepare the technical specs?",
        "mentions": ["mike.chen"],
        "urgency": "high"
    },
    {
        "platform": "teams",
        "channel": "Development Team",
        "user": "mike.chen",
        "text": "The API integration is 80% complete. Still need to handle edge cases for the new authentication flow.",
        "urgency": "medium"
    },
    {
        "platform": "slack", 
        "channel": "#general",
        "user": "lisa.williams",
        "text": "Action item from today's meeting: Review legal contracts by Tuesday EOD",
        "urgency": "high"
    },
    {
        "platform": "teams",
        "channel": "Marketing Strategy", 
        "user": "john.smith",
        "text": "Campaign performance is looking good. Should we increase the budget for next month?",
        "urgency": "low"
    },
    {
        "platform": "slack",
        "channel": "#dev-team",
        "user": "alex.kumar",
        "text": "Found a critical bug in the payment system. Need immediate attention!",
        "urgency": "critical"
    }
]

class MessageAnalyzer:
    """AI-powered message analysis engine"""
    
    def __init__(self):
        self.action_patterns = [
            r"(?:need to|should|must|will|action item[:\s]*)\s*([^.!?]+)",
            r"@\w+\s+(?:please|can you)\s+([^.!?]+)",
            r"(?:task|todo|assignment)[:\s]+([^.!?]+)"
        ]
        
        self.deadline_patterns = [
            r"by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"by\s+(today|tomorrow|eod|end of day)",
            r"deadline[:\s]+(.*?)(?:\.|$)",
            r"due\s+(.*?)(?:\.|$)"
        ]
        
        self.decision_patterns = [
            r"(?:decided|decision|approved|confirmed)[:\s]*([^.!?]+)",
            r"(?:we will|let's go with|selected)[:\s]*([^.!?]+)"
        ]
        
        self.question_patterns = [
            r"\?[^?]*\?",
            r"(?:should we|can we|how|what|when|where|why|who)[^.!?]*\?"
        ]
    
    def extract_action_items(self, text: str) -> List[str]:
        """Extract action items from message text"""
        actions = []
        for pattern in self.action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actions.extend([match.strip() for match in matches if match.strip()])
        return actions
    
    def extract_deadlines(self, text: str) -> List[str]:
        """Extract deadlines and time-sensitive information"""
        deadlines = []
        for pattern in self.deadline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            deadlines.extend([match.strip() for match in matches if match.strip()])
        return deadlines
    
    def extract_decisions(self, text: str) -> List[str]:
        """Extract decisions made in conversation"""
        decisions = []
        for pattern in self.decision_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            decisions.extend([match.strip() for match in matches if match.strip()])
        return decisions
    
    def extract_questions(self, text: str) -> List[str]:
        """Extract questions that need answers"""
        questions = []
        # Find sentences ending with question marks
        question_sentences = re.findall(r'[^.!?]*\?', text)
        questions.extend([q.strip() for q in question_sentences if q.strip()])
        return questions
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions and user references"""
        mentions = re.findall(r'@(\w+(?:\.\w+)?)', text)
        return mentions
    
    def calculate_priority(self, text: str, urgency_hint: str = None) -> float:
        """Calculate priority score based on content and context"""
        score = 5.0  # Base score
        
        # Urgency keywords
        urgent_keywords = ["urgent", "critical", "asap", "immediately", "emergency"]
        high_keywords = ["important", "priority", "deadline", "must", "need to"]
        
        text_lower = text.lower()
        
        if urgency_hint == "critical":
            score = 10.0
        elif urgency_hint == "high":
            score = 8.0
        elif any(keyword in text_lower for keyword in urgent_keywords):
            score = 9.0
        elif any(keyword in text_lower for keyword in high_keywords):
            score = 7.0
        
        # Boost score for @mentions
        if "@" in text:
            score += 1.0
            
        # Boost score for questions
        if "?" in text:
            score += 0.5
            
        return min(score, 10.0)
    
    def analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ["good", "great", "excellent", "success", "completed", "done"]
        negative_words = ["problem", "issue", "bug", "error", "failed", "concern"]
        urgent_words = ["urgent", "critical", "asap", "emergency"]
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in urgent_words):
            return "urgent"
        elif any(word in text_lower for word in negative_words):
            return "concerned"
        elif any(word in text_lower for word in positive_words):
            return "positive"
        else:
            return "neutral"
    
    def generate_suggestions(self, insight: MessageInsight) -> List[Dict[str, Any]]:
        """Generate smart action suggestions based on message analysis"""
        suggestions = []
        
        # Suggest task creation for action items
        for action in insight.action_items:
            suggestions.append({
                "type": "create_task",
                "title": f"Create task: {action[:50]}...",
                "description": f"Create task from message: {action}",
                "confidence": 0.8,
                "action_data": {
                    "task_title": action,
                    "assignee": insight.stakeholders[0] if insight.stakeholders else None,
                    "priority": "high" if insight.priority_score > 7 else "medium"
                }
            })
        
        # Suggest meeting for questions with multiple stakeholders
        if insight.questions and len(insight.stakeholders) > 1:
            suggestions.append({
                "type": "schedule_meeting",
                "title": "Schedule discussion meeting",
                "description": f"Multiple questions raised with {len(insight.stakeholders)} people involved",
                "confidence": 0.7,
                "action_data": {
                    "attendees": insight.stakeholders,
                    "subject": "Discussion: " + insight.questions[0][:30] + "...",
                    "duration": 30
                }
            })
        
        # Suggest reminder for deadlines
        for deadline in insight.deadlines:
            suggestions.append({
                "type": "send_reminder",
                "title": f"Set reminder for: {deadline}",
                "description": f"Create reminder for deadline: {deadline}",
                "confidence": 0.9,
                "action_data": {
                    "reminder_text": f"Deadline reminder: {deadline}",
                    "target_users": insight.stakeholders
                }
            })
        
        return suggestions
    
    async def analyze_message(self, message: CollaborationMessage) -> MessageInsight:
        """Main analysis function"""
        
        action_items = self.extract_action_items(message.text)
        deadlines = self.extract_deadlines(message.text)
        decisions = self.extract_decisions(message.text)
        questions = self.extract_questions(message.text)
        stakeholders = self.extract_mentions(message.text)
        if message.user not in stakeholders:
            stakeholders.append(message.user)
        
        priority_score = self.calculate_priority(message.text)
        sentiment = self.analyze_sentiment(message.text)
        
        # Generate project tags based on channel and content
        project_tags = [message.channel]
        if "q4" in message.text.lower():
            project_tags.append("q4-planning")
        if "product" in message.text.lower():
            project_tags.append("product")
        if "api" in message.text.lower():
            project_tags.append("api")
        
        insight = MessageInsight(
            message_id=message.id,
            action_items=action_items,
            deadlines=deadlines,
            decisions=decisions,
            questions=questions,
            priority_score=priority_score,
            sentiment=sentiment,
            stakeholders=stakeholders,
            project_tags=project_tags,
            suggested_actions=[]
        )
        
        # Generate action suggestions
        suggestions = self.generate_suggestions(insight)
        insight.suggested_actions = suggestions
        
        return insight

# Initialize analyzer
analyzer = MessageAnalyzer()

@app.on_event("startup")
async def startup():
    """Initialize the collaboration intelligence system"""
    logger.info("🚀 Starting Collaboration Intelligence API Server")
    logger.info("🤝 Slack/Teams Integration Ready")
    logger.info("🧠 AI Message Analysis Enabled")
    logger.info("🌐 Server running on http://localhost:8001")
    
    # Generate some initial mock data
    await generate_mock_messages()

async def generate_mock_messages():
    """Generate realistic mock messages for testing"""
    global recent_messages, message_insights, suggested_actions
    
    for i, mock_msg in enumerate(MOCK_MESSAGES):
        message = CollaborationMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            platform=mock_msg["platform"],
            channel=mock_msg["channel"],
            user=mock_msg["user"],
            text=mock_msg["text"],
            timestamp=datetime.now() - timedelta(minutes=30-i*5),
            mentions=mock_msg.get("mentions", [])
        )
        
        recent_messages.append(message)
        
        # Analyze message
        insight = await analyzer.analyze_message(message)
        message_insights[message.id] = insight
        
        # Create suggested actions
        for suggestion in insight.suggested_actions:
            action = SuggestedAction(
                id=f"action_{uuid.uuid4().hex[:8]}",
                type=suggestion["type"],
                title=suggestion["title"],
                description=suggestion["description"],
                confidence=suggestion["confidence"],
                context={
                    "message_id": message.id,
                    "channel": message.channel,
                    "platform": message.platform,
                    **suggestion["action_data"]
                }
            )
            suggested_actions[action.id] = action
    
    logger.info(f"📝 Generated {len(recent_messages)} mock messages")
    logger.info(f"💡 Created {len(suggested_actions)} suggested actions")

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "collaboration_intelligence",
        "timestamp": datetime.now().isoformat(),
        "monitored_channels": len(monitored_channels),
        "recent_messages": len(recent_messages),
        "pending_actions": len([a for a in suggested_actions.values() if a.status == "pending"])
    }

@app.get("/platforms/status")
async def get_platform_status():
    """Get connection status for different platforms"""
    return {
        "slack": {
            "connected": True,  # Mock: always connected
            "channels": MOCK_CHANNELS["slack"],
            "last_message": datetime.now() - timedelta(minutes=2),
            "rate_limit_remaining": 100
        },
        "teams": {
            "connected": True,  # Mock: always connected  
            "channels": MOCK_CHANNELS["teams"],
            "last_message": datetime.now() - timedelta(minutes=5),
            "rate_limit_remaining": 150
        }
    }

@app.get("/channels")
async def get_available_channels():
    """Get available channels for monitoring"""
    return {
        "slack": MOCK_CHANNELS["slack"],
        "teams": MOCK_CHANNELS["teams"],
        "users": MOCK_USERS
    }

@app.post("/monitoring/config")
async def update_monitoring_config(config: MonitoringConfig):
    """Update monitoring configuration"""
    global monitored_channels, monitored_users, monitored_keywords, auto_actions_enabled
    
    monitored_channels = config.channels
    monitored_users = config.users  
    monitored_keywords = config.keywords
    auto_actions_enabled = config.auto_actions_enabled
    
    logger.info(f"📊 Updated monitoring config: {len(config.channels)} channels, {len(config.users)} users")
    
    return {
        "status": "updated",
        "monitoring": {
            "channels": monitored_channels,
            "users": monitored_users,
            "keywords": monitored_keywords,
            "auto_actions": auto_actions_enabled
        }
    }

@app.get("/monitoring/config")
async def get_monitoring_config():
    """Get current monitoring configuration"""
    return {
        "channels": monitored_channels,
        "users": monitored_users,
        "keywords": monitored_keywords,
        "auto_actions_enabled": auto_actions_enabled
    }

@app.get("/messages/recent")
async def get_recent_messages(limit: int = 20):
    """Get recent messages with analysis"""
    recent = sorted(recent_messages, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    result = []
    for msg in recent:
        insight = message_insights.get(msg.id)
        result.append({
            "message": asdict(msg),
            "analysis": asdict(insight) if insight else None
        })
    
    return {"messages": result, "total": len(recent_messages)}

@app.get("/suggestions/pending")
async def get_pending_suggestions():
    """Get pending action suggestions"""
    pending = [asdict(action) for action in suggested_actions.values() if action.status == "pending"]
    return {
        "suggestions": pending,
        "count": len(pending)
    }

@app.post("/suggestions/{suggestion_id}/execute")
async def execute_suggestion(suggestion_id: str, request: ActionRequest):
    """Execute or dismiss a suggested action"""
    if suggestion_id not in suggested_actions:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    action = suggested_actions[suggestion_id]
    
    if request.approved:
        action.status = "approved"
        # Here we would execute the actual action
        result = await execute_action(action)
        action.status = "executed"
        
        logger.info(f"✅ Executed action: {action.title}")
        return {
            "status": "executed",
            "action": asdict(action),
            "result": result
        }
    else:
        action.status = "dismissed"
        logger.info(f"❌ Dismissed action: {action.title}")
        return {
            "status": "dismissed",
            "action": asdict(action)
        }

async def execute_action(action: SuggestedAction) -> Dict[str, Any]:
    """Execute a suggested action"""
    
    if action.type == "create_task":
        # Mock task creation
        return {
            "task_id": f"task_{uuid.uuid4().hex[:8]}",
            "title": action.context.get("task_title"),
            "assignee": action.context.get("assignee"),
            "created": True
        }
    
    elif action.type == "schedule_meeting":
        # Mock meeting scheduling
        return {
            "meeting_id": f"meeting_{uuid.uuid4().hex[:8]}",
            "subject": action.context.get("subject"),
            "attendees": action.context.get("attendees"),
            "scheduled": True
        }
    
    elif action.type == "send_reminder":
        # Mock reminder creation
        return {
            "reminder_id": f"reminder_{uuid.uuid4().hex[:8]}",
            "text": action.context.get("reminder_text"),
            "targets": action.context.get("target_users"),
            "sent": True
        }
    
    return {"status": "executed", "type": action.type}

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get collaboration analytics summary"""
    
    # Calculate insights from recent messages
    total_messages = len(recent_messages)
    total_action_items = sum(len(insight.action_items) for insight in message_insights.values())
    total_questions = sum(len(insight.questions) for insight in message_insights.values())
    
    platform_breakdown = {}
    for msg in recent_messages:
        platform_breakdown[msg.platform] = platform_breakdown.get(msg.platform, 0) + 1
    
    urgency_breakdown = {}
    for insight in message_insights.values():
        if insight.priority_score >= 8:
            urgency = "high"
        elif insight.priority_score >= 6:
            urgency = "medium"
        else:
            urgency = "low"
        urgency_breakdown[urgency] = urgency_breakdown.get(urgency, 0) + 1
    
    return {
        "summary": {
            "total_messages": total_messages,
            "action_items_identified": total_action_items,
            "questions_raised": total_questions,
            "suggestions_generated": len(suggested_actions),
            "actions_executed": len([a for a in suggested_actions.values() if a.status == "executed"])
        },
        "breakdown": {
            "by_platform": platform_breakdown,
            "by_urgency": urgency_breakdown
        },
        "top_stakeholders": list(set(user for insight in message_insights.values() for user in insight.stakeholders))[:5]
    }

# Development endpoints for testing

@app.post("/dev/simulate-message")
async def simulate_message(platform: str, channel: str, user: str, text: str):
    """Simulate a new message for testing (development only)"""
    
    message = CollaborationMessage(
        id=f"msg_{uuid.uuid4().hex[:8]}",
        platform=platform,
        channel=channel,
        user=user,
        text=text,
        timestamp=datetime.now(),
        mentions=re.findall(r'@(\w+(?:\.\w+)?)', text)
    )
    
    recent_messages.append(message)
    
    # Analyze the message
    insight = await analyzer.analyze_message(message)
    message_insights[message.id] = insight
    
    # Create suggested actions
    for suggestion in insight.suggested_actions:
        action = SuggestedAction(
            id=f"action_{uuid.uuid4().hex[:8]}",
            type=suggestion["type"],
            title=suggestion["title"],
            description=suggestion["description"],
            confidence=suggestion["confidence"],
            context={
                "message_id": message.id,
                "channel": message.channel,
                "platform": message.platform,
                **suggestion["action_data"]
            }
        )
        suggested_actions[action.id] = action
    
    logger.info(f"📨 Simulated message from {user} in {channel}")
    
    return {
        "message": asdict(message),
        "analysis": asdict(insight),
        "suggestions_created": len(insight.suggested_actions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)