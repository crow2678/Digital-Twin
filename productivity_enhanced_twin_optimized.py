#!/usr/bin/env python3
"""
Optimized Productivity Enhanced Digital Twin Controller
Faster response times with async processing and caching.
"""

import os
import re
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import uuid
from functools import lru_cache
import time

# Import the existing enhanced twin
from enhanced_twin_controller import EnhancedDigitalTwin

# Response cache for identical queries
RESPONSE_CACHE = {}
CACHE_TIMEOUT = 300  # 5 minutes

@dataclass
class ActionItem:
    id: str
    task: str
    assignee: str
    due_date: Optional[str]
    priority: str  # high, medium, low
    context: str
    estimated_time: Optional[int]  # minutes
    status: str = "pending"  # pending, in_progress, completed
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class SmartQuestion:
    question: str
    category: str
    reasoning: str
    urgency: str  # high, medium, low
    target_person: Optional[str] = None
    context: str = ""

@dataclass
class EmailDraft:
    to: str
    subject: str
    body: str
    tone: str
    priority: str
    context: str

class OptimizedProductivityTwin(EnhancedDigitalTwin):
    """Optimized Digital Twin with faster response times"""
    
    def __init__(self):
        print("⚡ Initializing Optimized Productivity Twin...")
        start_time = time.time()
        
        # Initialize parent class
        super().__init__()
        
        # Initialize collections
        self.action_items = []
        self.pending_questions = []
        self.document_insights = {}
        self.meeting_summaries = {}
        self.email_drafts = []
        self.productivity_mode = True
        
        # Performance optimizations
        self._analysis_cache = {}
        self._batch_operations = []
        
        # Expose memory manager for web app compatibility
        self.memory_manager = getattr(self, 'hybrid_manager', None)
        
        init_time = time.time() - start_time
        print(f"✅ Optimized twin ready in {init_time:.2f}s!")
        self._print_features()
    
    def _print_features(self):
        """Print features without blocking"""
        features = [
            "📄 Fast document analysis",
            "🎤 Optimized meeting processing", 
            "✉️ Cached email drafting",
            "📅 Smart calendar suggestions",
            "🧠 Intelligent questions",
            "⚡ Response caching"
        ]
        for feature in features:
            print(f"   {feature}")
    
    # === CACHING UTILITIES ===
    
    def _get_cache_key(self, content: str, operation: str) -> str:
        """Generate cache key for content"""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{operation}_{content_hash}"
    
    def _is_cache_valid(self, cache_entry: dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
        timestamp = cache_entry.get('timestamp', 0)
        return time.time() - timestamp < CACHE_TIMEOUT
    
    def _cache_response(self, key: str, response: Any) -> Any:
        """Cache response with timestamp"""
        RESPONSE_CACHE[key] = {
            'response': response,
            'timestamp': time.time()
        }
        return response
    
    # === OPTIMIZED DOCUMENT ANALYSIS ===
    
    def analyze_document(self, content: str, doc_type: str = "general", filename: str = None) -> Dict[str, Any]:
        """Optimized document analysis with caching"""
        
        print(f"⚡ Analyzing: {filename or 'document'} ({len(content)} chars)")
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(content, "doc_analysis")
        if cache_key in RESPONSE_CACHE and self._is_cache_valid(RESPONSE_CACHE[cache_key]):
            print(f"📋 Using cached analysis ({time.time() - start_time:.2f}s)")
            return RESPONSE_CACHE[cache_key]['response']
        
        # Chunk large documents for faster processing
        if len(content) > 4000:
            content = self._smart_chunk_content(content)
            print(f"📝 Content chunked to {len(content)} chars")
        
        # Process with optimized analysis
        if self.llm_available:
            analysis = self._optimized_llm_analysis(content, doc_type)
        else:
            analysis = self._fast_basic_analysis(content, doc_type)
        
        # Store the analysis
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        self.document_insights[doc_id] = {
            "filename": filename,
            "type": doc_type,
            "content": content[:500] + "..." if len(content) > 500 else content,
            "analysis": analysis,
            "created_at": datetime.now().isoformat()
        }
        
        # Add action items and questions
        if "action_items" in analysis:
            self.action_items.extend(analysis["action_items"])
        if "questions" in analysis:
            self.pending_questions.extend(analysis["questions"])
        
        # Cache and return
        analysis_time = time.time() - start_time
        print(f"✅ Analysis complete ({analysis_time:.2f}s)")
        return self._cache_response(cache_key, analysis)
    
    def _smart_chunk_content(self, content: str, max_chunk: int = 3000) -> str:
        """Intelligently chunk content to preserve context"""
        if len(content) <= max_chunk:
            return content
        
        # Try to break at natural boundaries
        sentences = content.split('. ')
        result = ""
        
        for sentence in sentences:
            if len(result + sentence) > max_chunk:
                break
            result += sentence + ". "
        
        # If no good break point, take first max_chunk chars
        if len(result) < max_chunk // 2:
            result = content[:max_chunk]
        
        return result
    
    def _optimized_llm_analysis(self, content: str, doc_type: str) -> Dict[str, Any]:
        """Streamlined LLM analysis with focused prompts"""
        
        # Shorter, more focused prompt
        prompt = f"""Analyze this {doc_type} document efficiently:

{content}

Provide JSON with:
1. "summary": 1-2 sentences
2. "key_points": Top 3 points only
3. "action_items": Tasks with priority/assignee
4. "questions": 2-3 critical questions only
5. "deadlines": Important dates

Be concise and focus on actionable insights."""
        
        try:
            response = self.llm.invoke(prompt)
            return self._parse_llm_response(response.content, content)
        except Exception as e:
            print(f"⚠️ LLM analysis failed, using fast fallback: {e}")
            return self._fast_basic_analysis(content, doc_type)
    
    def _parse_llm_response(self, response_text: str, content: str) -> Dict[str, Any]:
        """Optimized JSON parsing with fallback"""
        try:
            # Find JSON boundaries
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Quick conversion to objects
                analysis = self._convert_to_objects(analysis, content)
                return analysis
        except Exception:
            pass
        
        # Fast text parsing fallback
        return self._fast_text_parse(response_text, content)
    
    def _convert_to_objects(self, analysis: dict, content: str) -> dict:
        """Convert analysis dict to proper objects efficiently"""
        # Convert action items
        if "action_items" in analysis and isinstance(analysis["action_items"], list):
            action_objects = []
            for item in analysis["action_items"][:5]:  # Limit to 5 items
                if isinstance(item, dict):
                    action_obj = ActionItem(
                        id=f"action_{uuid.uuid4().hex[:8]}",
                        task=item.get("task", "")[:200],  # Limit task length
                        assignee=item.get("assignee", "me"),
                        due_date=item.get("due_date"),
                        priority=item.get("priority", "medium"),
                        context=item.get("context", "")[:100],
                        estimated_time=item.get("estimated_time", 30)
                    )
                    action_objects.append(action_obj)
            analysis["action_items"] = action_objects
        
        # Convert questions
        if "questions" in analysis and isinstance(analysis["questions"], list):
            question_objects = []
            for q in analysis["questions"][:3]:  # Limit to 3 questions
                if isinstance(q, dict):
                    question_obj = SmartQuestion(
                        question=q.get("question", "")[:200],
                        category=q.get("category", "general"),
                        reasoning=q.get("reasoning", "")[:100],
                        urgency=q.get("urgency", "medium"),
                        target_person=q.get("target_person"),
                        context=content[:100] + "..." if len(content) > 100 else content
                    )
                    question_objects.append(question_obj)
            analysis["questions"] = question_objects
        
        return analysis
    
    def _fast_basic_analysis(self, content: str, doc_type: str) -> Dict[str, Any]:
        """Ultra-fast basic analysis without LLM"""
        
        lines = content.split('\n')[:20]  # Limit to first 20 lines
        words = content.lower().split()[:500]  # Limit word processing
        
        # Quick keyword extraction
        action_keywords = ['todo', 'action', 'task', 'must', 'need', 'should']
        action_items = []
        
        for line in lines:
            if any(kw in line.lower() for kw in action_keywords):
                if len(action_items) < 3:  # Limit to 3 items
                    action_items.append(ActionItem(
                        id=f"action_{uuid.uuid4().hex[:8]}",
                        task=line.strip()[:100],
                        assignee="me",
                        due_date=None,
                        priority="medium",
                        context=f"From {doc_type}",
                        estimated_time=30
                    ))
        
        # Quick date extraction
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
        dates = re.findall(date_pattern, content)[:3]
        
        return {
            "summary": f"Document: {len(lines)} lines, {len(words)} words",
            "key_points": [line.strip() for line in lines[:3] if line.strip()],
            "action_items": action_items,
            "questions": [],
            "deadlines": dates,
            "risks": [],
            "opportunities": []
        }
    
    def _fast_text_parse(self, text: str, content: str) -> Dict[str, Any]:
        """Fast text parsing when JSON fails"""
        # Extract basic info from text response
        lines = text.split('\n')
        
        summary = "Analysis completed"
        key_points = []
        
        for line in lines[:10]:
            line = line.strip()
            if line and not line.startswith(('{', '}', '[', ']')):
                if len(key_points) < 3:
                    key_points.append(line[:100])
                if "summary" in line.lower() and not summary:
                    summary = line
        
        return {
            "summary": summary[:200],
            "key_points": key_points,
            "action_items": [],
            "questions": [],
            "deadlines": [],
            "risks": [],
            "opportunities": []
        }
    
    # === OPTIMIZED EMAIL DRAFTING ===
    
    def draft_email_response(self, original_email: str, intent: str, tone: str = "professional") -> EmailDraft:
        """Optimized email drafting with templates"""
        
        print(f"⚡ Drafting {tone} email...")
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(f"{original_email}_{intent}_{tone}", "email")
        if cache_key in RESPONSE_CACHE and self._is_cache_valid(RESPONSE_CACHE[cache_key]):
            print(f"📧 Using cached draft ({time.time() - start_time:.2f}s)")
            return RESPONSE_CACHE[cache_key]['response']
        
        # Use templates for common scenarios
        draft = self._template_email_draft(original_email, intent, tone)
        if not draft and self.llm_available:
            draft = self._quick_llm_email_draft(original_email, intent, tone)
        
        if not draft:
            draft = self._basic_email_draft(original_email, intent, tone)
        
        self.email_drafts.append(draft)
        
        draft_time = time.time() - start_time
        print(f"✅ Email drafted ({draft_time:.2f}s)")
        return self._cache_response(cache_key, draft)
    
    def _template_email_draft(self, original: str, intent: str, tone: str) -> Optional[EmailDraft]:
        """Use templates for common email scenarios"""
        
        intent_lower = intent.lower()
        
        # Meeting request template
        if "meeting" in intent_lower or "schedule" in intent_lower:
            return EmailDraft(
                to="[Recipient]",
                subject="Meeting Request",
                body=f"""Hi,\n\n{intent}\n\nWould you be available for a 30-minute meeting this week?\n\nPlease let me know your availability.\n\nBest regards""",
                tone=tone,
                priority="medium",
                context=intent
            )
        
        # Follow-up template
        elif "follow" in intent_lower or "update" in intent_lower:
            return EmailDraft(
                to="[Recipient]",
                subject="Follow-up",
                body=f"""Hi,\n\nI wanted to follow up on our previous discussion.\n\n{intent}\n\nLooking forward to your response.\n\nBest regards""",
                tone=tone,
                priority="medium",
                context=intent
            )
        
        return None
    
    def _quick_llm_email_draft(self, original: str, intent: str, tone: str) -> EmailDraft:
        """Quick LLM email draft with minimal prompt"""
        
        prompt = f"""Draft a {tone} email response:\n\nOriginal: {original[:200]}...\nIntent: {intent}\n\nProvide JSON: {{"subject": "...", "body": "..."}}"""
        
        try:
            response = self.llm.invoke(prompt)
            # Quick JSON extraction
            if '{' in response.content and '}' in response.content:
                json_start = response.content.find('{')
                json_end = response.content.rfind('}') + 1
                json_str = response.content[json_start:json_end]
                email_data = json.loads(json_str)
                
                return EmailDraft(
                    to="[Recipient]",
                    subject=email_data.get("subject", "Re: Your Email"),
                    body=email_data.get("body", "Draft email body"),
                    tone=tone,
                    priority="medium",
                    context=intent
                )
        except Exception:
            pass
        
        return self._basic_email_draft(original, intent, tone)
    
    def _basic_email_draft(self, original_email: str, intent: str, tone: str) -> EmailDraft:
        """Fast basic email draft"""
        
        subject = "Re: " + (original_email.split('\n')[0][:50] if original_email else "Your Email")
        
        if tone == "professional":
            body = f"""Thank you for your email.\n\n{intent}\n\nPlease let me know if you need any additional information.\n\nBest regards"""
        else:
            body = f"""Hi,\n\nThanks for reaching out. {intent}\n\nLet me know if you have questions!\n\nThanks"""
        
        return EmailDraft(
            to="[Recipient]",
            subject=subject,
            body=body,
            tone=tone,
            priority="medium",
            context=intent
        )
    
    # === OPTIMIZED MEETING PROCESSING ===
    
    def process_meeting_transcript(self, transcript: str, meeting_title: str = None, attendees: List[str] = None) -> Dict[str, Any]:
        """Optimized meeting processing"""
        
        print(f"⚡ Processing meeting: {meeting_title or 'Meeting'} ({len(transcript)} chars)")
        start_time = time.time()
        
        # Process as document first (uses caching)
        doc_analysis = self.analyze_document(transcript, "meeting_transcript", f"{meeting_title}_transcript.txt")
        
        # Quick meeting-specific extraction
        meeting_analysis = self._fast_meeting_analysis(transcript, meeting_title, attendees, doc_analysis)
        
        # Store meeting summary
        meeting_id = f"meeting_{uuid.uuid4().hex[:8]}"
        self.meeting_summaries[meeting_id] = {
            "title": meeting_title or "Meeting",
            "analysis": meeting_analysis,
            "created_at": datetime.now().isoformat()
        }
        
        process_time = time.time() - start_time
        print(f"✅ Meeting processed ({process_time:.2f}s)")
        return meeting_analysis
    
    def _fast_meeting_analysis(self, transcript: str, title: str, attendees: List[str], doc_analysis: Dict) -> Dict[str, Any]:
        """Fast meeting analysis focusing on essential info"""
        
        # Quick action item separation
        my_items = []
        others_items = []
        
        if "action_items" in doc_analysis:
            for item in doc_analysis["action_items"]:
                if hasattr(item, 'assignee') and item.assignee.lower() in ["me", "i"]:
                    my_items.append(item)
                else:
                    others_items.append(item)
        
        # Quick decision extraction
        lines = transcript.lower().split('\n')
        decisions = []
        decision_keywords = ['decided', 'agreed', 'concluded', 'resolved']
        
        for line in lines:
            if any(kw in line for kw in decision_keywords) and len(decisions) < 3:
                decisions.append(line.strip()[:100])
        
        return {
            "my_action_items": my_items,
            "others_action_items": others_items,
            "decisions_made": decisions,
            "questions_to_ask": doc_analysis.get("questions", [])[:3],
            "next_steps": ["Follow up on action items", "Schedule next meeting if needed"],
            "follow_up_emails": [],
            "meeting_effectiveness": 7,
            "next_meeting_needed": len(my_items) > 2
        }
    
    # === OPTIMIZED SMART QUESTIONS ===
    
    @lru_cache(maxsize=50)
    def _cached_smart_questions(self, context_hash: str, domain: str) -> List[SmartQuestion]:
        """Cached smart question generation"""
        # Use generic questions for speed
        generic_questions = [
            SmartQuestion(
                question="What are the key success criteria?",
                category="clarification",
                reasoning="Understanding success metrics is crucial",
                urgency="high",
                context=context_hash[:50]
            ),
            SmartQuestion(
                question="What are the main risks?",
                category="risk",
                reasoning="Risk identification helps with planning",
                urgency="medium",
                context=context_hash[:50]
            ),
            SmartQuestion(
                question="What resources are needed?",
                category="tactical",
                reasoning="Resource planning is essential",
                urgency="medium",
                context=context_hash[:50]
            )
        ]
        return generic_questions
    
    def generate_smart_questions(self, context: str, domain: str = "general") -> List[SmartQuestion]:
        """Optimized smart question generation"""
        
        print(f"⚡ Generating questions for {domain}...")
        
        # Use hash for caching
        import hashlib
        context_hash = hashlib.md5(context.encode()).hexdigest()[:16]
        
        return self._cached_smart_questions(context_hash, domain)
    
    # === PERFORMANCE MONITORING ===
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "cache_size": len(RESPONSE_CACHE),
            "action_items": len(self.action_items),
            "documents_processed": len(self.document_insights),
            "meetings_processed": len(self.meeting_summaries),
            "email_drafts": len(self.email_drafts),
            "llm_available": self.llm_available
        }
    
    def clear_cache(self):
        """Clear response cache"""
        global RESPONSE_CACHE
        RESPONSE_CACHE.clear()
        print("🧹 Cache cleared")
    
    # === ENHANCED INTERACTIVE SESSION ===
    
    def run_productivity_session(self):
        """Run optimized interactive session"""
        
        print("\n" + "="*70)
        print("⚡ OPTIMIZED Productivity Enhanced Digital Twin")
        print("="*70)
        print("Performance Features:")
        print("  ⚡ Response caching (5min TTL)")
        print("  📝 Smart content chunking")
        print("  🎯 Focused analysis")
        print("  📧 Email templates")
        print("  🧠 Cached question generation")
        print("\nCommands:")
        print("  • 'analyze <text>' - Fast document analysis")
        print("  • 'meeting <transcript>' - Quick meeting processing")
        print("  • 'draft_email <original> | <intent>' - Template-based drafting")
        print("  • 'questions <context>' - Cached smart questions")
        print("  • 'stats' - Performance statistics")
        print("  • 'clear_cache' - Clear response cache")
        print("="*70)
        
        # Get user ID
        user_id = input("\n👤 Enter your user ID (or press Enter for default): ").strip()
        if not user_id:
            user_id = "default_user"
        
        self.current_user = user_id
        
        # Try to load previous session
        session_loaded = self.load_recent_session(user_id)
        
        print(f"✅ Optimized session started for: {user_id}")
        if session_loaded:
            print("💾 Previous session restored")
        
        print("\n" + "-"*70)
        
        while True:
            try:
                user_input = input(f"\n{user_id}: ").strip()
                start_time = time.time()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    self.save_session()
                    stats = self.get_performance_stats()
                    print(f"\n👋 Session ended. Processed {stats['documents_processed']} documents, {stats['action_items']} actions tracked.")
                    break
                
                elif user_input.lower().startswith("analyze "):
                    content = user_input[8:].strip()
                    if content:
                        analysis = self.analyze_document(content)
                        self._display_document_analysis(analysis)
                    else:
                        print("Please provide content to analyze")
                
                elif user_input.lower().startswith("meeting "):
                    transcript = user_input[8:].strip()
                    if transcript:
                        meeting_analysis = self.process_meeting_transcript(transcript)
                        self._display_meeting_analysis(meeting_analysis)
                    else:
                        print("Please provide meeting transcript")
                
                elif user_input.lower().startswith("draft_email "):
                    parts = user_input[12:].split("|")
                    if len(parts) >= 2:
                        original = parts[0].strip()
                        intent = parts[1].strip()
                        draft = self.draft_email_response(original, intent)
                        self._display_email_draft(draft)
                    else:
                        print("Format: draft_email <original email> | <your intent>")
                
                elif user_input.lower().startswith("questions "):
                    context = user_input[10:].strip()
                    if context:
                        questions = self.generate_smart_questions(context)
                        self._display_smart_questions(questions)
                    else:
                        print("Please provide context for questions")
                
                elif user_input.lower() == "stats":
                    stats = self.get_performance_stats()
                    print(f"\n📊 PERFORMANCE STATS")
                    print(f"Cache entries: {stats['cache_size']}")
                    print(f"Documents processed: {stats['documents_processed']}")
                    print(f"Meetings processed: {stats['meetings_processed']}")
                    print(f"Action items: {stats['action_items']}")
                    print(f"LLM available: {stats['llm_available']}")
                
                elif user_input.lower() == "clear_cache":
                    self.clear_cache()
                
                elif user_input.lower() == "my_actions":
                    self._display_action_items()
                
                elif user_input.lower() == "daily_brief":
                    self._display_daily_briefing()
                
                else:
                    # Process with regular enhanced twin functionality
                    response = self.process_user_input(user_input, user_id)
                    print(f"\nAssistant: {response}")
                
                # Show response time
                response_time = time.time() - start_time
                print(f"\n⏱️ Response time: {response_time:.2f}s")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    # === DISPLAY METHODS (Optimized) ===
    
    def _display_document_analysis(self, analysis: Dict[str, Any]):
        """Fast display of document analysis"""
        print("\n📄 DOCUMENT ANALYSIS")
        print("-" * 30)
        print(f"📋 {analysis.get('summary', 'No summary')[:100]}")
        
        key_points = analysis.get('key_points', [])
        if key_points:
            print(f"\n🎯 Key Points ({len(key_points)}):")
            for i, point in enumerate(key_points[:3], 1):
                point_text = point if isinstance(point, str) else str(point)
                print(f"  {i}. {point_text[:80]}")
        
        action_items = analysis.get('action_items', [])
        if action_items:
            print(f"\n✅ Actions ({len(action_items)}):")
            for item in action_items[:3]:
                if hasattr(item, 'task'):
                    print(f"  • {item.task[:60]} ({item.priority})")
                else:
                    print(f"  • {str(item)[:60]}")
    
    def _display_meeting_analysis(self, analysis: Dict[str, Any]):
        """Fast display of meeting analysis"""
        print("\n🎤 MEETING ANALYSIS")
        print("-" * 30)
        
        my_items = analysis.get('my_action_items', [])
        if my_items:
            print(f"📋 My Actions ({len(my_items)}):")
            for item in my_items[:3]:
                task_text = item.task if hasattr(item, 'task') else str(item)
                print(f"  • {task_text[:60]}")
        
        decisions = analysis.get('decisions_made', [])
        if decisions:
            print(f"\n✅ Decisions ({len(decisions)}):")
            for decision in decisions[:2]:
                print(f"  → {decision[:60]}")
    
    def _display_email_draft(self, draft: EmailDraft):
        """Fast display of email draft"""
        print("\n✉️ EMAIL DRAFT")
        print("-" * 30)
        print(f"📧 {draft.subject}")
        print(f"📝 {draft.tone.title()} tone")
        print(f"\n{draft.body[:200]}..." if len(draft.body) > 200 else f"\n{draft.body}")
    
    def _display_smart_questions(self, questions: List[SmartQuestion]):
        """Fast display of smart questions"""
        print(f"\n🧠 SMART QUESTIONS ({len(questions)})")
        print("-" * 30)
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q.question[:80]}")
            print(f"   {q.category} | {q.urgency}\n")
    
    def _display_action_items(self):
        """Fast display of action items"""
        print(f"\n📋 ACTION ITEMS ({len(self.action_items)})")
        print("-" * 30)
        if not self.action_items:
            print("No action items yet.")
            return
        
        for item in self.action_items[:5]:
            status_icon = "✅" if item.status == "completed" else "🔄" if item.status == "in_progress" else "⏳"
            print(f"{status_icon} {item.task[:60]}")
            print(f"   {item.priority} priority | {item.status}\n")
    
    def _display_daily_briefing(self):
        """Fast daily briefing"""
        print("\n📊 DAILY BRIEFING")
        print("-" * 30)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
        
        stats = self.get_performance_stats()
        pending = [item for item in self.action_items if item.status == "pending"]
        high_priority = [item for item in pending if item.priority == "high"]
        
        print(f"\n📈 Today's Stats:")
        print(f"  • Documents processed: {stats['documents_processed']}")
        print(f"  • Meetings analyzed: {stats['meetings_processed']}")
        print(f"  • Pending tasks: {len(pending)}")
        print(f"  • High priority: {len(high_priority)}")
        print(f"  • Cache efficiency: {stats['cache_size']} entries")
        
        if high_priority:
            print(f"\n🔥 Top Priority:")
            for item in high_priority[:2]:
                print(f"  • {item.task[:50]}")

def main():
    """Main function to run optimized productivity twin"""
    try:
        print("⚡ Starting Optimized Productivity Twin...")
        twin = OptimizedProductivityTwin()
        twin.run_productivity_session()
    except KeyboardInterrupt:
        print("\n👋 Session interrupted.")
    except Exception as e:
        print(f"❌ Failed to start optimized twin: {e}")
        print("Make sure your .env file is configured with Azure credentials.")

if __name__ == "__main__":
    main()