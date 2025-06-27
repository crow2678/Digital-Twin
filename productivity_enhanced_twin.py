#!/usr/bin/env python3
"""
Productivity Enhanced Digital Twin Controller
Extends the existing enhanced_twin_controller with document analysis, 
meeting processing, email drafting, and proactive productivity features.
"""

import os
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import uuid

# Import the existing enhanced twin
from enhanced_twin_controller import EnhancedDigitalTwin

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

class ProductivityEnhancedTwin(EnhancedDigitalTwin):
    """Enhanced Digital Twin with Productivity and Research capabilities"""
    
    def __init__(self):
        super().__init__()
        self.action_items = []
        self.pending_questions = []
        self.document_insights = {}
        self.meeting_summaries = {}
        self.email_drafts = []
        self.productivity_mode = True
        
        # Expose memory manager for web app compatibility
        self.memory_manager = getattr(self, 'hybrid_manager', None)
        
        print("🚀 Productivity mode enabled!")
        print("   📄 Document analysis")
        print("   🎤 Meeting processing") 
        print("   ✉️ Email drafting")
        print("   📅 Calendar suggestions")
        print("   🧠 Smart questions")
    
    # === MEMORY MANAGEMENT ===
    
    async def store_memory(self, content: str, user_id: str = "default", memory_type: str = "general", tags: List[str] = None, **kwargs):
        """Store memory using the hybrid memory manager"""
        if self.memory_manager:
            return await self.memory_manager.add_memory(
                content=content,
                user_id=user_id,
                ontology_domain=memory_type,
                source="productivity_twin",
                **kwargs
            )
        else:
            # Fallback: store in local document_insights
            memory_id = f"memory_{uuid.uuid4().hex[:8]}"
            self.document_insights[memory_id] = {
                "content": content,
                "user_id": user_id,
                "memory_type": memory_type,
                "tags": tags or [],
                "created_at": datetime.now().isoformat()
            }
            return {"memory_id": memory_id, "success": True}
    
    # === DOCUMENT ANALYSIS ===
    
    def analyze_document(self, content: str, doc_type: str = "general", filename: str = None) -> Dict[str, Any]:
        """Analyze uploaded document and extract actionable insights"""
        
        print(f"📄 Analyzing document: {filename or 'untitled'} ({doc_type})")
        
        if self.llm_available:
            analysis = self._llm_document_analysis(content, doc_type)
        else:
            analysis = self._basic_document_analysis(content, doc_type)
        
        # Store the analysis
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        self.document_insights[doc_id] = {
            "filename": filename,
            "type": doc_type,
            "content": content[:1000] + "..." if len(content) > 1000 else content,
            "analysis": analysis,
            "created_at": datetime.now().isoformat()
        }
        
        # Add action items if any
        if "action_items" in analysis:
            self.action_items.extend(analysis["action_items"])
        
        # Add questions if any
        if "questions" in analysis:
            self.pending_questions.extend(analysis["questions"])
        
        return analysis
    
    def _llm_document_analysis(self, content: str, doc_type: str) -> Dict[str, Any]:
        """Use LLM for sophisticated document analysis"""
        
        prompt = f"""Analyze this {doc_type} document and provide actionable insights for productivity.

Document Content:
{content}

Please analyze and provide a JSON response with:
1. "summary": Brief 2-3 sentence summary
2. "key_points": List of important points (max 5)
3. "action_items": List of tasks that need to be done, each with:
   - "task": What needs to be done
   - "assignee": Who should do it (use "me" for the user)
   - "due_date": When it's due (if mentioned, format: YYYY-MM-DD)
   - "priority": high/medium/low
   - "context": Additional context
   - "estimated_time": Time needed in minutes (estimate)
4. "questions": Smart questions to ask for clarification, each with:
   - "question": The question text
   - "category": Type of question (clarification/strategic/tactical/risk)
   - "reasoning": Why this question is important
   - "urgency": high/medium/low
   - "target_person": Who to ask (if specific person mentioned)
5. "deadlines": Important dates (format: YYYY-MM-DD)
6. "risks": Potential concerns or issues
7. "opportunities": Things to capitalize on

Focus on actionable insights that will improve productivity and help with follow-up."""
        
        try:
            response = self.llm.invoke(prompt)
            # Try to parse as JSON
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Convert action items to ActionItem objects
                if "action_items" in analysis:
                    action_objects = []
                    for item in analysis["action_items"]:
                        action_obj = ActionItem(
                            id=f"action_{uuid.uuid4().hex[:8]}",
                            task=item.get("task", ""),
                            assignee=item.get("assignee", "me"),
                            due_date=item.get("due_date"),
                            priority=item.get("priority", "medium"),
                            context=item.get("context", ""),
                            estimated_time=item.get("estimated_time")
                        )
                        action_objects.append(action_obj)
                    analysis["action_items"] = action_objects
                
                # Convert questions to SmartQuestion objects
                if "questions" in analysis:
                    question_objects = []
                    for q in analysis["questions"]:
                        question_obj = SmartQuestion(
                            question=q.get("question", ""),
                            category=q.get("category", "general"),
                            reasoning=q.get("reasoning", ""),
                            urgency=q.get("urgency", "medium"),
                            target_person=q.get("target_person"),
                            context=content[:200] + "..." if len(content) > 200 else content
                        )
                        question_objects.append(question_obj)
                    analysis["questions"] = question_objects
                
                return analysis
            else:
                # Fallback if JSON parsing fails
                return self._parse_text_analysis(response.content, doc_type)
                
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}")
            return self._basic_document_analysis(content, doc_type)
    
    def _basic_document_analysis(self, content: str, doc_type: str) -> Dict[str, Any]:
        """Basic document analysis without LLM"""
        
        # Simple keyword-based analysis
        lines = content.split('\n')
        words = content.lower().split()
        
        # Extract potential action items
        action_keywords = ['todo', 'action', 'task', 'must', 'need to', 'should', 'will', 'responsible']
        action_items = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in action_keywords):
                action_items.append(ActionItem(
                    id=f"action_{uuid.uuid4().hex[:8]}",
                    task=line.strip(),
                    assignee="me",
                    due_date=None,
                    priority="medium",
                    context=f"From {doc_type} document",
                    estimated_time=30
                ))
        
        # Extract dates
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b'
        dates = re.findall(date_pattern, content)
        
        return {
            "summary": f"Document contains {len(lines)} lines with {len(words)} words",
            "key_points": lines[:3] if len(lines) >= 3 else lines,
            "action_items": action_items,
            "questions": [],
            "deadlines": dates,
            "risks": [],
            "opportunities": []
        }
    
    # === MEETING PROCESSING ===
    
    def process_meeting_transcript(self, transcript: str, meeting_title: str = None, attendees: List[str] = None) -> Dict[str, Any]:
        """Process meeting transcript to extract action items and insights"""
        
        print(f"🎤 Processing meeting: {meeting_title or 'Untitled Meeting'}")
        
        # First analyze as a document
        doc_analysis = self.analyze_document(transcript, "meeting_transcript", f"{meeting_title}_transcript.txt")
        
        # Extract meeting-specific insights
        if self.llm_available:
            meeting_analysis = self._llm_meeting_analysis(transcript, meeting_title, attendees, doc_analysis)
        else:
            meeting_analysis = self._basic_meeting_analysis(transcript, meeting_title, attendees, doc_analysis)
        
        # Store meeting summary
        meeting_id = f"meeting_{uuid.uuid4().hex[:8]}"
        self.meeting_summaries[meeting_id] = {
            "title": meeting_title or "Meeting",
            "transcript": transcript,
            "analysis": meeting_analysis,
            "created_at": datetime.now().isoformat()
        }
        
        return meeting_analysis
    
    def _llm_meeting_analysis(self, transcript: str, title: str, attendees: List[str], doc_analysis: Dict) -> Dict[str, Any]:
        """LLM-powered meeting analysis"""
        
        attendee_list = ", ".join(attendees) if attendees else "Not specified"
        
        prompt = f"""Analyze this meeting transcript and provide specific meeting insights.

Meeting: {title or 'Untitled'}
Attendees: {attendee_list}

Transcript:
{transcript}

Provide JSON response with:
1. "my_action_items": Tasks assigned to me/the user
2. "others_action_items": Tasks assigned to other people  
3. "decisions_made": Key decisions from the meeting
4. "questions_to_ask": Follow-up questions I should ask specific people
5. "next_steps": What should happen next
6. "follow_up_emails": Suggested emails to send with:
   - "to": Recipient
   - "subject": Email subject
   - "key_points": Main points to include
7. "calendar_events": Meetings/deadlines to schedule
8. "meeting_effectiveness": How productive was this meeting (1-10)
9. "missing_attendees": People who should have been there
10. "next_meeting_needed": Should we schedule a follow-up?

Focus on actionable items that help me be productive after this meeting."""
        
        try:
            response = self.llm.invoke(prompt)
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            print(f"⚠️ Meeting analysis failed: {e}")
        
        return self._basic_meeting_analysis(transcript, title, attendees, doc_analysis)
    
    def _basic_meeting_analysis(self, transcript: str, title: str, attendees: List[str], doc_analysis: Dict) -> Dict[str, Any]:
        """Basic meeting analysis without LLM"""
        
        # Extract action items assigned to user vs others
        my_items = []
        others_items = []
        
        if "action_items" in doc_analysis:
            for item in doc_analysis["action_items"]:
                if item.assignee.lower() in ["me", "i"]:
                    my_items.append(item)
                else:
                    others_items.append(item)
        
        return {
            "my_action_items": my_items,
            "others_action_items": others_items,
            "decisions_made": ["Key decisions would be extracted here"],
            "questions_to_ask": doc_analysis.get("questions", []),
            "next_steps": ["Follow up on action items"],
            "follow_up_emails": [],
            "calendar_events": [],
            "meeting_effectiveness": 7,
            "missing_attendees": [],
            "next_meeting_needed": len(my_items) > 2
        }
    
    # === EMAIL DRAFTING ===
    
    def draft_email_response(self, original_email: str, intent: str, tone: str = "professional") -> EmailDraft:
        """Draft email response based on original email and intent"""
        
        print(f"✉️ Drafting {tone} email response...")
        
        if self.llm_available:
            draft = self._llm_email_draft(original_email, intent, tone)
        else:
            draft = self._basic_email_draft(original_email, intent, tone)
        
        # Store the draft
        self.email_drafts.append(draft)
        
        return draft
    
    def _llm_email_draft(self, original_email: str, intent: str, tone: str) -> EmailDraft:
        """LLM-powered email drafting"""
        
        prompt = f"""Draft a {tone} email response based on this original email and my intent.

Original Email:
{original_email}

My Intent: {intent}
Tone: {tone}

Please draft an email response that:
1. Addresses all points from the original email
2. Clearly communicates my intent
3. Uses appropriate {tone} tone
4. Includes clear next steps
5. Is concise but complete

Provide JSON with:
- "subject": Email subject line
- "body": Email body text
- "key_points": Main points covered
- "next_steps": What happens after this email
- "urgency": How urgent is this (high/medium/low)"""
        
        try:
            response = self.llm.invoke(prompt)
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                email_data = json.loads(json_str)
                
                return EmailDraft(
                    to="[Recipient]",
                    subject=email_data.get("subject", "Re: Your Email"),
                    body=email_data.get("body", "Draft email body"),
                    tone=tone,
                    priority=email_data.get("urgency", "medium"),
                    context=intent
                )
        except Exception as e:
            print(f"⚠️ Email drafting failed: {e}")
        
        return self._basic_email_draft(original_email, intent, tone)
    
    def _basic_email_draft(self, original_email: str, intent: str, tone: str) -> EmailDraft:
        """Basic email drafting without LLM"""
        
        subject = "Re: " + (original_email.split('\n')[0] if original_email else "Your Email")
        
        if tone == "professional":
            body = f"""Thank you for your email.

{intent}

Please let me know if you need any additional information.

Best regards"""
        else:
            body = f"""Hi,

Thanks for reaching out. {intent}

Let me know if you have questions!

Thanks"""
        
        return EmailDraft(
            to="[Recipient]",
            subject=subject,
            body=body,
            tone=tone,
            priority="medium",
            context=intent
        )
    
    # === SMART QUESTIONS ===
    
    def generate_smart_questions(self, context: str, domain: str = "general") -> List[SmartQuestion]:
        """Generate intelligent questions based on context"""
        
        print(f"🧠 Generating smart questions for {domain}...")
        
        if self.llm_available:
            return self._llm_smart_questions(context, domain)
        else:
            return self._basic_smart_questions(context, domain)
    
    def _llm_smart_questions(self, context: str, domain: str) -> List[SmartQuestion]:
        """LLM-powered smart question generation"""
        
        prompt = f"""Based on this {domain} context, generate 5-7 smart questions that would help clarify, explore opportunities, identify risks, or move things forward.

Context: {context}

For each question, provide JSON with:
- "question": The actual question
- "category": Type (clarification/strategic/tactical/risk/opportunity)
- "reasoning": Why this question is important
- "urgency": How urgent (high/medium/low)
- "target_person": Who should answer (if specific, otherwise null)

Generate questions that are:
1. Specific and actionable
2. Likely to uncover important information
3. Help make better decisions
4. Address potential blind spots

Return as JSON array of question objects."""
        
        try:
            response = self.llm.invoke(prompt)
            json_start = response.content.find('[')
            json_end = response.content.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                questions_data = json.loads(json_str)
                
                questions = []
                for q_data in questions_data:
                    question = SmartQuestion(
                        question=q_data.get("question", ""),
                        category=q_data.get("category", "general"),
                        reasoning=q_data.get("reasoning", ""),
                        urgency=q_data.get("urgency", "medium"),
                        target_person=q_data.get("target_person"),
                        context=context[:100] + "..." if len(context) > 100 else context
                    )
                    questions.append(question)
                
                return questions
        except Exception as e:
            print(f"⚠️ Smart question generation failed: {e}")
        
        return self._basic_smart_questions(context, domain)
    
    def _basic_smart_questions(self, context: str, domain: str) -> List[SmartQuestion]:
        """Basic smart question generation without LLM"""
        
        generic_questions = [
            SmartQuestion(
                question="What are the key success criteria for this?",
                category="clarification",
                reasoning="Understanding success metrics is crucial",
                urgency="high",
                context=context[:100]
            ),
            SmartQuestion(
                question="What could go wrong and how can we prevent it?",
                category="risk",
                reasoning="Risk identification helps with planning",
                urgency="medium",
                context=context[:100]
            ),
            SmartQuestion(
                question="What resources do we need to succeed?",
                category="tactical",
                reasoning="Resource planning is essential",
                urgency="medium",
                context=context[:100]
            )
        ]
        
        return generic_questions
    
    # === ENHANCED INTERACTIVE SESSION ===
    
    def run_productivity_session(self):
        """Run enhanced interactive session with productivity features"""
        
        print("\n" + "="*70)
        print("🚀 Productivity Enhanced Digital Twin")
        print("="*70)
        print("Enhanced Features:")
        print("  📄 Document Analysis - analyze contracts, reports, emails")
        print("  🎤 Meeting Processing - extract action items from transcripts")
        print("  ✉️ Email Drafting - draft responses and follow-ups")
        print("  🧠 Smart Questions - generate insightful questions")
        print("  📅 Action Tracking - manage tasks and deadlines")
        print("  🔍 Research Help - structured research assistance")
        print("\nNew Commands:")
        print("  • 'analyze <text>' - Analyze document/content")
        print("  • 'meeting <transcript>' - Process meeting transcript")
        print("  • 'draft_email <original> | <intent>' - Draft email response")
        print("  • 'questions <context>' - Generate smart questions")
        print("  • 'my_actions' - View my action items")
        print("  • 'daily_brief' - Get productivity briefing")
        print("="*70)
        
        # Get user ID
        user_id = input("\n👤 Enter your user ID (or press Enter for default): ").strip()
        if not user_id:
            user_id = "default_user"
        
        self.current_user = user_id
        
        # Try to load previous session
        session_loaded = self.load_recent_session(user_id)
        
        print(f"✅ Productivity session started for: {user_id}")
        if session_loaded:
            print("💾 Previous session restored")
        
        print("\n" + "-"*70)
        
        while True:
            try:
                user_input = input(f"\n{user_id}: ").strip()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    self.save_session()
                    print(f"\n👋 Productivity session ended. {len(self.action_items)} action items tracked.")
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
                
                elif user_input.lower() == "my_actions":
                    self._display_action_items()
                
                elif user_input.lower() == "daily_brief":
                    self._display_daily_briefing()
                
                else:
                    # Process with regular enhanced twin functionality
                    response = self.process_user_input(user_input, user_id)
                    print(f"\nAssistant: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    # === DISPLAY METHODS ===
    
    def _display_document_analysis(self, analysis: Dict[str, Any]):
        """Display document analysis results"""
        print("\n📄 DOCUMENT ANALYSIS")
        print("-" * 40)
        print(f"Summary: {analysis.get('summary', 'No summary')}")
        
        if analysis.get('key_points'):
            print("\nKey Points:")
            for i, point in enumerate(analysis['key_points'][:5], 1):
                print(f"  {i}. {point}")
        
        if analysis.get('action_items'):
            print(f"\nAction Items ({len(analysis['action_items'])}):")
            for item in analysis['action_items'][:3]:
                if hasattr(item, 'task'):
                    print(f"  • {item.task} (Priority: {item.priority})")
                else:
                    print(f"  • {item}")
        
        if analysis.get('questions'):
            print(f"\nSmart Questions ({len(analysis['questions'])}):")
            for q in analysis['questions'][:3]:
                if hasattr(q, 'question'):
                    print(f"  ? {q.question}")
                else:
                    print(f"  ? {q}")
    
    def _display_meeting_analysis(self, analysis: Dict[str, Any]):
        """Display meeting analysis results"""
        print("\n🎤 MEETING ANALYSIS")
        print("-" * 40)
        
        my_items = analysis.get('my_action_items', [])
        if my_items:
            print(f"My Action Items ({len(my_items)}):")
            for item in my_items:
                if hasattr(item, 'task'):
                    print(f"  • {item.task}")
                else:
                    print(f"  • {item}")
        
        questions = analysis.get('questions_to_ask', [])
        if questions:
            print(f"\nQuestions to Ask ({len(questions)}):")
            for q in questions[:3]:
                if hasattr(q, 'question'):
                    print(f"  ? {q.question}")
                else:
                    print(f"  ? {q}")
        
        if analysis.get('next_steps'):
            print(f"\nNext Steps:")
            for step in analysis['next_steps'][:3]:
                print(f"  → {step}")
    
    def _display_email_draft(self, draft: EmailDraft):
        """Display email draft"""
        print("\n✉️ EMAIL DRAFT")
        print("-" * 40)
        print(f"To: {draft.to}")
        print(f"Subject: {draft.subject}")
        print(f"Tone: {draft.tone}")
        print("\nBody:")
        print(draft.body)
    
    def _display_smart_questions(self, questions: List[SmartQuestion]):
        """Display smart questions"""
        print(f"\n🧠 SMART QUESTIONS ({len(questions)})")
        print("-" * 40)
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q.question}")
            print(f"   Category: {q.category} | Urgency: {q.urgency}")
            if q.target_person:
                print(f"   Ask: {q.target_person}")
            print()
    
    def _display_action_items(self):
        """Display current action items"""
        print(f"\n📋 MY ACTION ITEMS ({len(self.action_items)})")
        print("-" * 40)
        if not self.action_items:
            print("No action items tracked yet.")
            return
        
        for item in self.action_items:
            status_icon = "✅" if item.status == "completed" else "🔄" if item.status == "in_progress" else "⏳"
            print(f"{status_icon} {item.task}")
            print(f"   Priority: {item.priority} | Status: {item.status}")
            if item.due_date:
                print(f"   Due: {item.due_date}")
            print()
    
    def _display_daily_briefing(self):
        """Display daily productivity briefing"""
        print("\n📊 DAILY PRODUCTIVITY BRIEFING")
        print("-" * 40)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        pending_items = [item for item in self.action_items if item.status == "pending"]
        in_progress_items = [item for item in self.action_items if item.status == "in_progress"]
        
        print(f"\nTask Status:")
        print(f"  • Pending: {len(pending_items)}")
        print(f"  • In Progress: {len(in_progress_items)}")
        print(f"  • Documents Analyzed: {len(self.document_insights)}")
        print(f"  • Meetings Processed: {len(self.meeting_summaries)}")
        
        if pending_items:
            print(f"\nTop Priority Tasks:")
            high_priority = [item for item in pending_items if item.priority == "high"]
            for item in high_priority[:3]:
                print(f"  🔥 {item.task}")

def main():
    """Main function to run productivity enhanced digital twin"""
    try:
        twin = ProductivityEnhancedTwin()
        twin.run_productivity_session()
    except KeyboardInterrupt:
        print("\n👋 Session interrupted.")
    except Exception as e:
        print(f"❌ Failed to start productivity twin: {e}")
        print("Make sure your .env file is configured with Azure credentials.")

if __name__ == "__main__":
    main()