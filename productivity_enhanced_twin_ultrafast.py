#!/usr/bin/env python3
"""
ULTRA-FAST Productivity Enhanced Digital Twin Controller
Target: Sub-3 second response times with aggressive optimizations
"""

import os
import re
import json
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import uuid
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the existing enhanced twin
from enhanced_twin_controller import EnhancedDigitalTwin

# Aggressive caching
FAST_CACHE = {}
CACHE_TIMEOUT = 300  # 5 minutes
USER_PROFILE_CACHE = {}

# Pre-computed common responses
COMMON_RESPONSES = {
    "name": "Your name is Paresh Deshpande.",
    "work": "You work at Tavant as a Senior Director.",
    "sports": "You like football, cricket, and badminton.",
    "company": "You work at Tavant.",
    "job": "You are a Senior Director at Tavant.",
    "role": "You are a Senior Director working with Financial Services and Media clients."
}

@dataclass
class FastActionItem:
    """Lightweight action item"""
    task: str
    priority: str = "medium"
    status: str = "pending"

@dataclass 
class FastQuestion:
    """Lightweight question"""
    question: str
    category: str = "general"

class UltraFastProductivityTwin(EnhancedDigitalTwin):
    """Ultra-fast twin with aggressive optimizations"""
    
    def __init__(self):
        print("⚡ Initializing ULTRA-FAST Productivity Twin...")
        start_time = time.time()
        
        # Skip heavy initialization
        self.action_items = []
        self.pending_questions = []
        self.document_insights = {}
        self.email_drafts = []
        self.productivity_mode = True
        
        # Initialize parent with minimal setup
        try:
            super().__init__()
        except Exception as e:
            print(f"⚠️ Full initialization failed, using fast mode: {e}")
            self.llm_available = False
            self.hybrid_manager = None
        
        # Fast caches
        self._response_cache = {}
        self._user_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Pre-load user profile
        self._load_user_profile_async()
        
        init_time = time.time() - start_time
        print(f"🚀 Ultra-fast twin ready in {init_time:.2f}s!")
        print("   ⚡ Response caching enabled")
        print("   🎯 Single-query memory search")
        print("   📋 Template responses")
        print("   🔥 Async processing")
    
    def _load_user_profile_async(self):
        """Pre-load common user info asynchronously"""
        def load_profile():
            try:
                if self.hybrid_manager:
                    # Single optimized search for user profile
                    memories = self.hybrid_manager.search_memories(
                        "Paresh Deshpande name work job company sports interests",
                        search_options={"user_id": "default_user", "limit": 10}
                    )
                    # Cache key user info
                    for memory, score in memories:
                        content = memory.content.lower()
                        if "paresh deshpande" in content:
                            USER_PROFILE_CACHE["name"] = "Paresh Deshpande"
                        if "tavant" in content:
                            USER_PROFILE_CACHE["company"] = "Tavant"
                        if "senior director" in content:
                            USER_PROFILE_CACHE["role"] = "Senior Director"
                        if any(sport in content for sport in ["football", "cricket", "badminton"]):
                            USER_PROFILE_CACHE["sports"] = "football, cricket, and badminton"
            except Exception:
                pass
        
        # Load in background
        threading.Thread(target=load_profile, daemon=True).start()
    
    def _get_cache_key(self, question: str, user_id: str) -> str:
        """Generate cache key"""
        import hashlib
        key_text = f"{question.lower().strip()}_{user_id}"
        return hashlib.md5(key_text.encode()).hexdigest()[:12]
    
    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check if response is cached"""
        if cache_key in FAST_CACHE:
            cached_data = FAST_CACHE[cache_key]
            if time.time() - cached_data['timestamp'] < CACHE_TIMEOUT:
                return cached_data['response']
        return None
    
    def _cache_response(self, cache_key: str, response: str) -> str:
        """Cache response"""
        FAST_CACHE[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        return response
    
    def _quick_template_response(self, question: str) -> Optional[str]:
        """Ultra-fast template-based responses"""
        question_lower = question.lower().strip()
        
        # Direct matches
        if question_lower in ["what is my name?", "what's my name?", "my name?"]:
            return USER_PROFILE_CACHE.get("name", COMMON_RESPONSES["name"])
        
        if question_lower in ["what is your name?", "what's your name?", "your name?"]:
            return USER_PROFILE_CACHE.get("name", COMMON_RESPONSES["name"])
        
        if "where do i work" in question_lower or "what company" in question_lower:
            return USER_PROFILE_CACHE.get("company", COMMON_RESPONSES["work"])
        
        if "what do i do" in question_lower or "my job" in question_lower or "my role" in question_lower:
            return USER_PROFILE_CACHE.get("role", COMMON_RESPONSES["role"])
        
        if "what sports" in question_lower or "sports do i like" in question_lower:
            return f"You like {USER_PROFILE_CACHE.get('sports', 'football, cricket, and badminton')}."
        
        # Keyword-based matching
        keywords = {
            "name": USER_PROFILE_CACHE.get("name", COMMON_RESPONSES["name"]),
            "work": USER_PROFILE_CACHE.get("company", COMMON_RESPONSES["work"]),
            "job": USER_PROFILE_CACHE.get("role", COMMON_RESPONSES["job"]),
            "company": USER_PROFILE_CACHE.get("company", COMMON_RESPONSES["company"]),
            "sports": f"You like {USER_PROFILE_CACHE.get('sports', 'football, cricket, and badminton')}.",
        }
        
        for keyword, response in keywords.items():
            if keyword in question_lower:
                return response
        
        return None
    
    def _single_memory_search(self, question: str, user_id: str) -> Optional[str]:
        """Single optimized memory search"""
        try:
            if not self.hybrid_manager:
                return None
            
            # Single search with optimized query
            memories = self.hybrid_manager.search_memories(
                question,
                search_options={"user_id": user_id, "limit": 3}  # Limit to 3 results
            )
            
            if memories:
                best_memory, score = memories[0]
                if score > 0.3:
                    return f"Based on your memories, {best_memory.semantic_summary or best_memory.content}"
            
            return None
        except Exception:
            return None
    
    def _fast_llm_response(self, question: str, context: str) -> Optional[str]:
        """Fast LLM response with minimal prompt"""
        if not self.llm_available:
            return None
        
        try:
            # Ultra-short prompt
            prompt = f"Question: {question}\nContext: {context[:200]}\nAnswer briefly:"
            
            response = self.llm.invoke(prompt)
            return response.content.strip()[:500]  # Limit response length
        except Exception:
            return None
    
    def process_user_input(self, user_input: str, user_id: str = "default_user") -> str:
        """Ultra-fast input processing"""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(user_input, user_id)
        cached_response = self._check_cache(cache_key)
        if cached_response:
            return cached_response
        
        # Try template response (fastest)
        template_response = self._quick_template_response(user_input)
        if template_response:
            return self._cache_response(cache_key, template_response)
        
        # Single memory search (fast)
        memory_response = self._single_memory_search(user_input, user_id)
        if memory_response:
            return self._cache_response(cache_key, memory_response)
        
        # LLM fallback (slower but still optimized)
        if self.llm_available:
            llm_response = self._fast_llm_response(user_input, "")
            if llm_response:
                return self._cache_response(cache_key, llm_response)
        
        # Final fallback
        fallback = "I don't have specific information about that in your memories yet. Could you provide more details?"
        return self._cache_response(cache_key, fallback)
    
    # === ULTRA-FAST DOCUMENT ANALYSIS ===
    
    def analyze_document(self, content: str, doc_type: str = "general", filename: str = None) -> Dict[str, Any]:
        """Ultra-fast document analysis"""
        print(f"⚡ Fast analyzing: {filename or 'document'}")
        start_time = time.time()
        
        # Aggressive content limiting
        if len(content) > 1000:
            content = content[:1000] + "..."
        
        # Fast template-based analysis
        analysis = {
            "summary": f"Document analyzed: {len(content)} characters",
            "key_points": self._extract_key_sentences(content),
            "action_items": self._extract_fast_actions(content),
            "questions": [],
            "deadlines": self._extract_dates(content),
            "processing_time": time.time() - start_time
        }
        
        print(f"✅ Analysis complete ({analysis['processing_time']:.2f}s)")
        return analysis
    
    def _extract_key_sentences(self, content: str) -> List[str]:
        """Extract key sentences quickly"""
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        # Return first 3 non-empty sentences
        return [s for s in sentences[:5] if len(s) > 20][:3]
    
    def _extract_fast_actions(self, content: str) -> List[FastActionItem]:
        """Fast action item extraction"""
        actions = []
        lines = content.split('\n')[:10]  # Only check first 10 lines
        
        action_keywords = ['todo', 'action', 'task', 'must', 'need to', 'should']
        
        for line in lines:
            if any(kw in line.lower() for kw in action_keywords) and len(actions) < 3:
                actions.append(FastActionItem(
                    task=line.strip()[:100],
                    priority="medium"
                ))
        
        return actions
    
    def _extract_dates(self, content: str) -> List[str]:
        """Fast date extraction"""
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b'
        dates = re.findall(date_pattern, content)
        return dates[:3]  # Limit to 3 dates
    
    # === ULTRA-FAST EMAIL DRAFTING ===
    
    def draft_email_response(self, original_email: str, intent: str, tone: str = "professional") -> Dict[str, str]:
        """Ultra-fast email drafting"""
        print(f"⚡ Fast drafting {tone} email...")
        
        # Ultra-simple templates
        if tone == "professional":
            body = f"Thank you for your email.\n\n{intent}\n\nBest regards"
            subject = "Re: Your Email"
        else:
            body = f"Hi!\n\n{intent}\n\nThanks!"
            subject = "Re: Your Message"
        
        return {
            "subject": subject,
            "body": body,
            "tone": tone,
            "draft_time": "< 0.1s"
        }
    
    # === PERFORMANCE MONITORING ===
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "cache_size": len(FAST_CACHE),
            "user_profile_loaded": len(USER_PROFILE_CACHE),
            "action_items": len(self.action_items),
            "documents_processed": len(self.document_insights),
            "template_responses": len(COMMON_RESPONSES),
            "memory_available": self.hybrid_manager is not None,
            "llm_available": self.llm_available
        }
    
    def clear_cache(self):
        """Clear all caches"""
        global FAST_CACHE, USER_PROFILE_CACHE
        FAST_CACHE.clear()
        USER_PROFILE_CACHE.clear()
        print("🗑️ All caches cleared")
    
    # === ULTRA-FAST INTERACTIVE SESSION ===
    
    def run_productivity_session(self):
        """Run ultra-fast interactive session"""
        
        print("\n" + "="*70)
        print("⚡ ULTRA-FAST Productivity Enhanced Digital Twin")
        print("="*70)
        print("Performance Features:")
        print("  🎯 Template responses (instant)")
        print("  ⚡ Single-query memory search")
        print("  📋 Aggressive caching")
        print("  🔥 Response time tracking")
        print("  🚀 Background profile loading")
        print("\nTarget: Sub-3 second responses")
        print("="*70)
        
        # Get user ID
        user_id = input("\n👤 Enter your user ID (or press Enter for default): ").strip()
        if not user_id:
            user_id = "default_user"
        
        self.current_user = user_id
        
        print(f"🚀 Ultra-fast session started for: {user_id}")
        print("💡 Tip: Ask about your name, work, sports for instant responses!")
        print("\n" + "-"*70)
        
        while True:
            try:
                user_input = input(f"\n{user_id}: ").strip()
                start_time = time.time()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    stats = self.get_performance_stats()
                    print(f"\n👋 Ultra-fast session ended. Cache: {stats['cache_size']} entries.")
                    break
                
                elif user_input.lower() == "stats":
                    stats = self.get_performance_stats()
                    print(f"\n⚡ ULTRA-FAST STATS")
                    print(f"Cache entries: {stats['cache_size']}")
                    print(f"User profile loaded: {stats['user_profile_loaded']} items")
                    print(f"Template responses: {stats['template_responses']}")
                    print(f"Memory available: {stats['memory_available']}")
                    print(f"LLM available: {stats['llm_available']}")
                
                elif user_input.lower() == "clear_cache":
                    self.clear_cache()
                
                elif user_input.lower().startswith("analyze "):
                    content = user_input[8:].strip()
                    if content:
                        analysis = self.analyze_document(content)
                        print(f"\n📄 FAST ANALYSIS")
                        print(f"Summary: {analysis['summary']}")
                        if analysis['key_points']:
                            print(f"Key points: {len(analysis['key_points'])}")
                        if analysis['action_items']:
                            print(f"Actions: {len(analysis['action_items'])}")
                    else:
                        print("Please provide content to analyze")
                
                elif user_input.lower().startswith("draft_email "):
                    parts = user_input[12:].split("|")
                    if len(parts) >= 2:
                        original = parts[0].strip()
                        intent = parts[1].strip()
                        draft = self.draft_email_response(original, intent)
                        print(f"\n✉️ FAST EMAIL DRAFT")
                        print(f"Subject: {draft['subject']}")
                        print(f"Body: {draft['body'][:100]}...")
                    else:
                        print("Format: draft_email <original> | <intent>")
                
                else:
                    # Process with ultra-fast method
                    response = self.process_user_input(user_input, user_id)
                    print(f"\nA: {response}")
                
                # Show response time
                response_time = time.time() - start_time
                color = "🟢" if response_time < 3 else "🟡" if response_time < 10 else "🔴"
                print(f"\n{color} Response time: {response_time:.2f}s")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def main():
    """Main function to run ultra-fast productivity twin"""
    try:
        print("⚡ Starting ULTRA-FAST Productivity Twin...")
        twin = UltraFastProductivityTwin()
        twin.run_productivity_session()
    except KeyboardInterrupt:
        print("\n👋 Session interrupted.")
    except Exception as e:
        print(f"❌ Failed to start ultra-fast twin: {e}")

if __name__ == "__main__":
    main()