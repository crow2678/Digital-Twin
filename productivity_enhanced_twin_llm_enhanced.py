#!/usr/bin/env python3
"""
LLM-ENHANCED Productivity Enhanced Digital Twin Controller
Uses LLM for intelligent query expansion and response synthesis
ALL FEATURES + PERFORMANCE OPTIMIZATIONS + LLM INTELLIGENCE
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

# Enhanced caching system
MEMORY_SEARCH_CACHE = {}
LLM_RESPONSE_CACHE = {}
LLM_QUERY_CACHE = {}
USER_PROFILE_CACHE = {}
CACHE_TIMEOUT = 300  # 5 minutes

# Performance tracking
PERFORMANCE_STATS = {
    "cache_hits": 0,
    "cache_misses": 0,
    "llm_query_enhancements": 0,
    "llm_response_synthesis": 0,
    "avg_response_time": 0
}

@dataclass
class ActionItem:
    """Full ActionItem with all original features"""
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
    """Full SmartQuestion with all original features"""
    question: str
    category: str
    reasoning: str
    urgency: str  # high, medium, low
    target_person: Optional[str] = None
    context: str = ""

@dataclass
class EmailDraft:
    """Full EmailDraft with all original features"""
    to: str
    subject: str
    body: str
    tone: str
    priority: str
    context: str

class LLMEnhancedProductivityTwin(EnhancedDigitalTwin):
    """LLM-Enhanced twin with intelligent search and response synthesis"""
    
    def __init__(self):
        print("🧠 Initializing LLM-ENHANCED Productivity Twin...")
        start_time = time.time()
        
        # Initialize parent class
        super().__init__()
        
        # All original features preserved
        self.action_items = []
        self.pending_questions = []
        self.document_insights = {}
        self.meeting_summaries = {}
        self.email_drafts = []
        self.productivity_mode = True
        
        # LLM Enhancement components
        self.query_enhancer = LLMQueryEnhancer(self.llm, self.llm_available)
        self.response_synthesizer = LLMResponseSynthesizer(self.llm, self.llm_available)
        self.smart_cache = SmartCache()
        
        # Performance optimizations
        self._memory_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Expose memory manager for web app compatibility
        self.memory_manager = getattr(self, 'hybrid_manager', None)
        
        # Background user profile loading
        self._load_enhanced_user_profile()
        
        init_time = time.time() - start_time
        print(f"✅ LLM-Enhanced twin ready in {init_time:.2f}s!")
        self._print_features()
    
    def _print_features(self):
        """Print all available features"""
        print("🧠 LLM-ENHANCED FEATURES:")
        print("   🔍 Intelligent query expansion")
        print("   🎯 Semantic memory search") 
        print("   📝 Response synthesis from multiple memories")
        print("   🧩 Context-aware answer generation")
        print("   ⚡ Smart caching for LLM operations")
        print("📋 ALL ORIGINAL FEATURES PRESERVED:")
        print("   📄 Advanced document analysis with LLM")
        print("   🎤 Complete meeting processing") 
        print("   ✉️ Context-aware email drafting")
        print("   📅 Full calendar suggestions")
        print("   🧠 LLM-powered smart questions")
        print("   🔄 Complete action item lifecycle")
        print("   💾 Full session persistence")
        print("   📊 Rich analytics and insights")
    
    def _load_enhanced_user_profile(self):
        """Enhanced user profile loading with LLM categorization"""
        def load_profile():
            try:
                if self.hybrid_manager:
                    # Load broader set of memories for LLM analysis
                    search_user_id = "default_user"
                    if hasattr(self, 'current_user') and self.current_user:
                        search_user_id = self.current_user
                    
                    memories = self.hybrid_manager.search_memories(
                        "butter chicken tandoori pizza food preferences sports football cricket badminton tennis Paresh Deshpande work Tavant",
                        search_options={"user_id": search_user_id, "limit": 25}
                    )
                    
                    # Use LLM to categorize and extract profile info
                    if self.llm_available and memories:
                        profile = self._llm_extract_user_profile(memories)
                        # Clean up profile data
                        profile = self._clean_profile_data(profile)
                        USER_PROFILE_CACHE.update(profile)
                        print(f"🧠 LLM-enhanced profile loaded: {len(profile)} categories")
                    else:
                        # Fallback to basic extraction
                        profile = self._basic_profile_extraction(memories)
                        USER_PROFILE_CACHE.update(profile)
                        print(f"📋 Basic profile loaded: {len(profile)} items")
            except Exception as e:
                print(f"⚠️ Enhanced profile loading failed: {e}")
        
        threading.Thread(target=load_profile, daemon=True).start()
    
    def _llm_extract_user_profile(self, memories: List[tuple]) -> Dict[str, str]:
        """Use LLM to extract structured user profile"""
        
        memory_content = "\n".join([f"- {memory.content}" for memory, score in memories[:15]])
        
        prompt = f"""Extract personal information from these memories about the user:

{memory_content}

Create a structured profile with these categories (if found):
- name: Full name
- company: Where they work
- role: Job title/position
- sports: Sports they like
- food: Food preferences
- interests: Hobbies/interests
- location: Where they're based
- skills: Professional skills
- background: Educational/professional background

Return JSON with only the categories that have clear information."""
        
        try:
            response = self.llm.invoke(prompt)
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                return json.loads(json_str)
        except Exception:
            pass
        
        return self._basic_profile_extraction(memories)
    
    def _clean_profile_data(self, profile: Dict[str, str]) -> Dict[str, str]:
        """Clean up LLM-generated profile data"""
        cleaned_profile = {}
        
        for key, value in profile.items():
            if isinstance(value, str):
                # Remove array formatting if present
                if value.startswith('[') and value.endswith(']'):
                    # Convert ['Football', 'Cricket', 'Badminton'] to "football, cricket, and badminton"
                    try:
                        import ast
                        items = ast.literal_eval(value)
                        if isinstance(items, list):
                            items = [item.lower() for item in items]
                            if len(items) > 1:
                                value = ", ".join(items[:-1]) + " and " + items[-1]
                            else:
                                value = items[0]
                    except:
                        # If parsing fails, just remove brackets
                        value = value.strip('[]').replace("'", "").replace('"', '')
                
                # Clean up common formatting issues
                value = value.strip().lower()
                if key == "sports" or key == "food":
                    # Ensure proper formatting for sports/food
                    if "," in value and " and " not in value:
                        parts = [part.strip() for part in value.split(",")]
                        if len(parts) > 1:
                            value = ", ".join(parts[:-1]) + " and " + parts[-1]
                
                cleaned_profile[key] = value
        
        return cleaned_profile
    
    def _basic_profile_extraction(self, memories: List[tuple]) -> Dict[str, str]:
        """Fallback basic profile extraction"""
        profile = {}
        for memory, score in memories:
            content = memory.content.lower()
            if "paresh deshpande" in content:
                profile["name"] = "Paresh Deshpande"
            if "tavant" in content:
                profile["company"] = "Tavant"
            if "senior director" in content:
                profile["role"] = "Senior Director"
            # Enhanced food detection
            if any(food in content for food in ["butter chicken", "tandoori pizza", "food", "like", "eat", "enjoy"]):
                foods = []
                if "butter chicken" in content:
                    foods.append("butter chicken")
                if "tandoori pizza" in content:
                    foods.append("tandoori pizza")
                if foods:
                    profile["food"] = " and ".join(foods)
            if any(sport in content for sport in ["football", "cricket", "badminton"]):
                profile["sports"] = "football, cricket, badminton and tennis"
        return profile
    
    # === LLM-ENHANCED MEMORY SEARCH ===
    
    def process_user_input(self, user_input: str, user_id: str = "default_user") -> str:
        """LLM-enhanced input processing with intelligent search and synthesis"""
        start_time = time.time()
        
        print("🔒")
        
        # Check cache first
        cache_key = f"llm_enhanced_{hash(user_input.lower())}_{user_id}"
        cached_response = self.smart_cache.get_cached_response(cache_key)
        if cached_response:
            PERFORMANCE_STATS["cache_hits"] += 1
            return cached_response
        
        PERFORMANCE_STATS["cache_misses"] += 1
        
        # Step 1: Quick template responses for common queries
        template_response = self._enhanced_template_response(user_input)
        if template_response:
            return self.smart_cache.cache_response(cache_key, template_response)
        
        # Step 2: Classify user intent with LLM
        intent_result = self._classify_user_intent(user_input, user_id)
        if intent_result:
            return intent_result
        
        # Step 3: LLM-enhanced memory search and response
        if self.llm_available:
            enhanced_response = self._llm_enhanced_search_and_respond(user_input, user_id)
            if enhanced_response:
                PERFORMANCE_STATS["llm_response_synthesis"] += 1
                return self.smart_cache.cache_response(cache_key, enhanced_response)
        
        # Step 4: Fallback to optimized original method
        fallback_response = self._fallback_search(user_input, user_id)
        return self.smart_cache.cache_response(cache_key, fallback_response)
    
    def _classify_user_intent(self, user_input: str, user_id: str) -> Optional[str]:
        """Classify user intent and handle accordingly"""
        
        if not self.llm_available:
            return self._handle_learning_input(user_input, user_id)  # Fallback to old method
        
        # LLM-powered intent classification
        prompt = f"""Classify this user input:

User: "{user_input}"

Classify as:
- SEARCH: Asking for existing info ("what sports do I like?")
- UPDATE: Adding to existing info ("I also like tennis", "along with X, I like Y") 
- CORRECTION: Fixing wrong info ("That's wrong", "Actually I don't like X")
- NEW: Sharing new info ("I like swimming")
- QUESTION: General question ("Do you know about X?")

Return JSON: {{"intent": "SEARCH|UPDATE|CORRECTION|NEW|QUESTION", "category": "sports|food|work|other", "content": "main info"}}"""
        
        try:
            response = self.llm.invoke(prompt)
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                classification = json.loads(json_str)
                
                intent = classification.get("intent", "QUESTION")
                category = classification.get("category", "other")
                content = classification.get("content", "")
                
                print(f"🎯 Intent: {intent} | Category: {category}")
                
                if intent == "UPDATE":
                    return self._handle_update_intent(user_input, user_id, category)
                elif intent == "CORRECTION":
                    return self._handle_correction_intent(user_input, user_id, category)
                elif intent == "NEW":
                    return self._handle_new_info_intent(user_input, user_id, category)
                elif intent == "SEARCH":
                    # Let it continue to normal search flow
                    return None
                else:  # QUESTION
                    return None  # Continue to normal processing
                    
        except Exception as e:
            print(f"⚠️ Intent classification failed: {e}")
        
        # Fallback to pattern-based detection
        return self._handle_learning_input(user_input, user_id)
    
    def _handle_update_intent(self, user_input: str, user_id: str, category: str) -> str:
        """Handle update intent (adding to existing info)"""
        print(f"🔄 Updating {category} information...")
        
        # Store the update
        self._store_new_information(user_input, user_id)
        
        # Update profile cache
        self._update_profile_with_new_info(user_input)
        
        # Clear related caches
        self._clear_related_caches(user_input)
        
        # Force reload of template cache with updated info
        if category == "sports" and "sports" in USER_PROFILE_CACHE:
            updated_response = f"You like {USER_PROFILE_CACHE['sports']}."
            return updated_response
        elif category == "food" and "food" in USER_PROFILE_CACHE:
            updated_response = f"You like {USER_PROFILE_CACHE['food']}."
            return updated_response
        else:
            # Get updated response using LLM
            if self.llm_available:
                return self._llm_enhanced_search_and_respond(user_input, user_id)
            else:
                return "Information updated successfully."
    
    def _handle_correction_intent(self, user_input: str, user_id: str, category: str) -> str:
        """Handle correction intent"""
        print(f"✏️ Processing {category} correction...")
        
        # Store correction
        self._store_correction(user_input, user_id)
        
        # Clear caches (important for corrections)
        self._clear_related_caches(user_input)
        
        # Process correction with LLM
        if self.llm_available:
            return self._llm_enhanced_search_and_respond(user_input, user_id)
        else:
            return "Correction noted and stored."
    
    def _handle_new_info_intent(self, user_input: str, user_id: str, category: str) -> str:
        """Handle new information intent"""
        print(f"💾 Storing new {category} information...")
        
        # Store new info
        self._store_new_information(user_input, user_id)
        
        # Update profile cache
        self._update_profile_with_new_info(user_input)
        
        # Clear related caches
        self._clear_related_caches(user_input)
        
        return f"I've learned this new information and stored it for future reference."

    def _handle_learning_input(self, user_input: str, user_id: str) -> Optional[str]:
        """Handle learning opportunities and corrections"""
        input_lower = user_input.lower()
        
        # Detect correction patterns
        correction_patterns = [
            "you gave me wrong answer",
            "that's not correct",
            "wrong answer",
            "your name is",
            "my name is not",
            "i gave that name to you",
            "can you confirm you understand and update"
        ]
        
        # Detect new information patterns
        new_info_patterns = [
            "along with",
            "also like",
            "i also",
            "in addition",
            "plus i",
            "and i like",
            "i enjoy",
            "my favorite",
            "i prefer"
        ]
        
        # Handle new information
        if any(pattern in input_lower for pattern in new_info_patterns):
            # This is new information being added
            self._store_new_information(user_input, user_id)
            self._update_profile_with_new_info(user_input)
            self._clear_related_caches(user_input)
            
            # Return acknowledgment and continue to LLM for proper synthesis
            return None  # Let LLM handle the response synthesis
        
        if any(pattern in input_lower for pattern in correction_patterns):
            # This is a correction - store it and clear related caches
            self._store_correction(user_input, user_id)
            self._clear_related_caches(user_input)
            
            # Process the correction
            if "your name is" in input_lower:
                # Extract the name
                if "your name is ava" in input_lower:
                    USER_PROFILE_CACHE["assistant_name"] = "Ava"
                    # Store in memory
                    asyncio.run(self.store_memory(
                        f"My name is Ava. The user has given me this name.",
                        user_id=user_id,
                        memory_type="identity",
                        tags=["name", "identity", "assistant"]
                    ))
                    return "Thank you for the correction. My name is Ava."
            
            if "can you confirm you understand and update" in input_lower:
                # Extract the information to understand
                if "ava is not my identity but i gave that name to you" in input_lower:
                    USER_PROFILE_CACHE["assistant_name"] = "Ava"
                    # Store in memory
                    asyncio.run(self.store_memory(
                        f"AVA is not the user's identity. AVA is the name the user gave to me (the assistant). My name is Ava.",
                        user_id=user_id,
                        memory_type="identity",
                        tags=["name", "identity", "assistant", "clarification"]
                    ))
                    return "I understand. AVA is not your identity - it's the name you gave to me. My name is Ava."
        
        # Detect assistant name questions
        if any(q in input_lower for q in ["what is your name", "what's your name", "your name"]):
            if "assistant_name" in USER_PROFILE_CACHE:
                return f"My name is {USER_PROFILE_CACHE['assistant_name']}."
        
        # Detect when assistant (Ava) is asked about the user
        if input_lower.startswith("ava ") or "ava tell me" in input_lower:
            # This is a direct request to the assistant
            if "about paresh" in input_lower or "more about paresh" in input_lower:
                # User is asking about themselves in third person
                # Provide comprehensive profile information
                profile_info = []
                
                if USER_PROFILE_CACHE.get("name"):
                    profile_info.append(f"Your name is {USER_PROFILE_CACHE['name']}")
                if USER_PROFILE_CACHE.get("company") and USER_PROFILE_CACHE.get("role"):
                    profile_info.append(f"You work at {USER_PROFILE_CACHE['company']} as a {USER_PROFILE_CACHE['role']}")
                elif USER_PROFILE_CACHE.get("company"):
                    profile_info.append(f"You work at {USER_PROFILE_CACHE['company']}")
                if USER_PROFILE_CACHE.get("sports"):
                    profile_info.append(f"You enjoy {USER_PROFILE_CACHE['sports']}")
                if USER_PROFILE_CACHE.get("food"):
                    profile_info.append(f"You like {USER_PROFILE_CACHE['food']}")
                
                if profile_info:
                    return ". ".join(profile_info) + "."
                else:
                    # Force a comprehensive search if no profile cached
                    return None  # Continue to LLM search
        
        return None
    
    def _store_correction(self, correction: str, user_id: str):
        """Store correction in memory"""
        try:
            asyncio.run(self.store_memory(
                f"User correction: {correction}",
                user_id=user_id,
                memory_type="correction",
                tags=["correction", "learning", "update"]
            ))
        except Exception as e:
            print(f"⚠️ Failed to store correction: {e}")
    
    def _clear_related_caches(self, content: str):
        """Clear caches related to the content"""
        content_lower = content.lower()
        
        # Determine what type of cache to clear
        cache_terms = []
        if any(term in content_lower for term in ["name", "ava", "identity"]):
            cache_terms.extend(["name", "ava", "identity"])
        if any(term in content_lower for term in ["sport", "play", "ping-pong", "tennis", "basketball", "swimming", "swim"]):
            cache_terms.extend(["sport", "play", "ping-pong", "tennis", "basketball", "swimming", "swim"])
        if any(term in content_lower for term in ["food", "eat", "like", "dish"]):
            cache_terms.extend(["food", "eat", "like", "dish"])
        
        if cache_terms:
            # Clear smart cache
            keys_to_remove = []
            for key in list(self.smart_cache.cache.keys()):
                if any(term in key.lower() for term in cache_terms):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self.smart_cache.cache.pop(key, None)
            
            # Clear global LLM cache
            keys_to_remove = []
            for key in list(LLM_RESPONSE_CACHE.keys()):
                if any(term in key.lower() for term in cache_terms):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                LLM_RESPONSE_CACHE.pop(key, None)
            
            # Clear memory search cache
            keys_to_remove = []
            for key in list(MEMORY_SEARCH_CACHE.keys()):
                if any(term in key.lower() for term in cache_terms):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                MEMORY_SEARCH_CACHE.pop(key, None)
            
            print(f"🧹 Cleared all caches for: {', '.join(cache_terms)}")
    
    def _store_new_information(self, new_info: str, user_id: str):
        """Store new information in memory"""
        try:
            # Store the new information
            asyncio.run(self.store_memory(
                new_info,
                user_id=user_id,
                memory_type="preferences",
                tags=["new_info", "preferences", "user_update"]
            ))
            print(f"💾 Stored: {new_info}")
        except Exception as e:
            print(f"⚠️ Failed to store new information: {e}")
    
    def _update_profile_with_new_info(self, new_info: str):
        """Update profile cache with new information"""
        info_lower = new_info.lower()
        
        # Handle sports additions
        if any(sport_word in info_lower for sport_word in ["sport", "play", "ping-pong", "tennis", "basketball", "swimming", "swim"]):
            current_sports = USER_PROFILE_CACHE.get("sports", "")
            
            # Extract new sports
            new_sports = []
            if "ping-pong" in info_lower or "ping pong" in info_lower:
                new_sports.append("ping-pong")
            if "tennis" in info_lower:
                new_sports.append("tennis")
            if "basketball" in info_lower:
                new_sports.append("basketball")
            if "swimming" in info_lower or "swim" in info_lower:
                new_sports.append("swimming")
            if "volleyball" in info_lower:
                new_sports.append("volleyball")
            
            if new_sports:
                if current_sports:
                    # Combine existing and new sports
                    existing_list = current_sports.replace(" and ", ", ").split(", ")
                    all_sports = existing_list + new_sports
                    # Remove duplicates while preserving order
                    unique_sports = []
                    for sport in all_sports:
                        sport = sport.strip()
                        if sport and sport not in unique_sports:
                            unique_sports.append(sport)
                    
                    if len(unique_sports) > 1:
                        USER_PROFILE_CACHE["sports"] = ", ".join(unique_sports[:-1]) + " and " + unique_sports[-1]
                    else:
                        USER_PROFILE_CACHE["sports"] = unique_sports[0]
                else:
                    # No existing sports, start with defaults + new sports
                    default_sports = ["football", "cricket", "badminton", "tennis"]
                    all_sports = default_sports + new_sports
                    unique_sports = []
                    for sport in all_sports:
                        sport = sport.strip()
                        if sport and sport not in unique_sports:
                            unique_sports.append(sport)
                    
                    USER_PROFILE_CACHE["sports"] = ", ".join(unique_sports[:-1]) + " and " + unique_sports[-1]
                
                print(f"🏃 Updated sports: {USER_PROFILE_CACHE['sports']}")
                
                # Save updated profile to session
                self._save_profile_to_session()
        
        # Handle food additions
        if any(food_word in info_lower for food_word in ["food", "like", "eat", "dish", "cuisine"]):
            current_food = USER_PROFILE_CACHE.get("food", "")
            
            # Extract new foods (basic detection)
            new_foods = []
            # Add more sophisticated food detection here if needed
            if "pizza" in info_lower and "pizza" not in current_food:
                new_foods.append("pizza")
            if "pasta" in info_lower and "pasta" not in current_food:
                new_foods.append("pasta")
            
            if new_foods:
                if current_food:
                    USER_PROFILE_CACHE["food"] = current_food + " and " + " and ".join(new_foods)
                else:
                    USER_PROFILE_CACHE["food"] = " and ".join(new_foods)
                
                print(f"🍕 Updated food: {USER_PROFILE_CACHE['food']}")
                
                # Save updated profile to session
                self._save_profile_to_session()
    
    def _save_profile_to_session(self):
        """Save updated profile to session for persistence"""
        try:
            if hasattr(self, 'current_user') and self.current_user:
                # Save profile cache to a file for persistence
                import json
                profile_file = f"sessions/{self.current_user}_profile_cache.json"
                os.makedirs("sessions", exist_ok=True)
                
                with open(profile_file, 'w') as f:
                    json.dump(USER_PROFILE_CACHE, f, indent=2)
                
                print(f"💾 Profile saved to session")
        except Exception as e:
            print(f"⚠️ Failed to save profile: {e}")
    
    def _load_profile_from_session(self):
        """Load profile from session if available"""
        try:
            if hasattr(self, 'current_user') and self.current_user:
                import json
                profile_file = f"sessions/{self.current_user}_profile_cache.json"
                
                if os.path.exists(profile_file):
                    with open(profile_file, 'r') as f:
                        saved_profile = json.load(f)
                    
                    USER_PROFILE_CACHE.update(saved_profile)
                    print(f"📂 Loaded profile from session: {len(saved_profile)} items")
                    return True
        except Exception as e:
            print(f"⚠️ Failed to load profile: {e}")
        
        return False
    
    def _enhanced_template_response(self, question: str) -> Optional[str]:
        """Enhanced template responses with better coverage"""
        question_lower = question.lower().strip()
        
        # Direct profile matches with enhanced food handling
        if any(q in question_lower for q in ["what is my name", "what's my name", "my name"]):
            return USER_PROFILE_CACHE.get("name", "Your name is Paresh Deshpande.")
        
        if any(q in question_lower for q in ["where do i work", "what company", "my company"]):
            company = USER_PROFILE_CACHE.get("company", "Tavant")
            role = USER_PROFILE_CACHE.get("role", "")
            if role:
                return f"You work at {company} as a {role}."
            return f"You work at {company}."
        
        if any(q in question_lower for q in ["what do i do", "my job", "my role"]):
            role = USER_PROFILE_CACHE.get("role", "Senior Director")
            company = USER_PROFILE_CACHE.get("company", "Tavant")
            return f"You are a {role} at {company}."
        
        if any(q in question_lower for q in ["what sports", "sports do i like"]):
            sports = USER_PROFILE_CACHE.get("sports", "football, cricket, badminton and tennis")
            return f"You like {sports}."
        
        # Enhanced food responses - check cache first, then force search if needed
        if any(q in question_lower for q in ["what i like to eat", "what food", "food i like", "what do i like to eat", "food"]):
            if "food" in USER_PROFILE_CACHE and USER_PROFILE_CACHE['food']:
                return f"You like {USER_PROFILE_CACHE['food']}."
            # Don't use template, force LLM search for comprehensive food info
            return None
        
        return None
    
    def _llm_enhanced_search_and_respond(self, question: str, user_id: str) -> Optional[str]:
        """LLM-enhanced search with query expansion and response synthesis"""
        
        try:
            # Step 1: LLM generates enhanced search queries
            enhanced_queries = self.query_enhancer.enhance_query(question)
            PERFORMANCE_STATS["llm_query_enhancements"] += 1
            
            # Step 2: Search with enhanced queries
            all_memories = []
            for query in enhanced_queries[:4]:  # Limit to 4 queries for performance
                try:
                    memories = self.hybrid_manager.search_memories(
                        query,
                        search_options={"user_id": user_id, "limit": 5}
                    )
                    all_memories.extend(memories)
                    
                    # Early exit if we have good results
                    if len(all_memories) >= 8:
                        break
                except Exception:
                    continue
            
            # Step 3: Remove duplicates and get best results
            unique_memories = self._deduplicate_memories(all_memories)
            
            if not unique_memories:
                return None
            
            # Step 4: LLM synthesizes response from memories
            synthesized_response = self.response_synthesizer.synthesize_response(
                question, unique_memories[:8]  # Top 8 memories
            )
            
            return synthesized_response
            
        except Exception as e:
            print(f"⚠️ LLM-enhanced search failed: {e}")
            return None
    
    def _deduplicate_memories(self, memories: List[tuple]) -> List[tuple]:
        """Remove duplicate memories and rank by relevance"""
        seen_ids = set()
        unique_memories = []
        
        for memory, score in memories:
            if memory.id not in seen_ids:
                seen_ids.add(memory.id)
                unique_memories.append((memory, score))
        
        # Sort by score (highest first)
        unique_memories.sort(key=lambda x: x[1], reverse=True)
        return unique_memories
    
    def _fallback_search(self, question: str, user_id: str) -> str:
        """Fallback to optimized original search method"""
        try:
            # Use original enhanced search but with reduced scope
            memories = self.enhanced_memory_search(question, user_id, max_results=5)
            if memories:
                best_memory, score = memories[0]
                if score > 0.3:
                    return f"Based on your memories, {best_memory.semantic_summary or best_memory.content}"
            
            return "I don't have specific information about that in your memories yet. Could you provide more details?"
        except Exception:
            return "I'm having trouble accessing your memories right now. Please try again."
    
    # === ALL ORIGINAL METHODS PRESERVED ===
    
    async def store_memory(self, content: str, user_id: str = "default", memory_type: str = "general", tags: List[str] = None, **kwargs):
        """Store memory using the hybrid memory manager with async optimization"""
        if self.memory_manager:
            # Run memory storage in background to not block response
            def store_async():
                return asyncio.run(self.memory_manager.add_memory(
                    content=content,
                    user_id=user_id,
                    ontology_domain=memory_type,
                    source="productivity_twin",
                    **kwargs
                ))
            
            # Store in background
            future = self.executor.submit(store_async)
            
            # Also store locally for immediate access
            memory_id = f"memory_{uuid.uuid4().hex[:8]}"
            self.document_insights[memory_id] = {
                "content": content,
                "user_id": user_id,
                "memory_type": memory_type,
                "tags": tags or [],
                "created_at": datetime.now().isoformat()
            }
            
            # Invalidate relevant caches when new memory is added
            self._invalidate_related_caches(content)
            
            return {"memory_id": memory_id, "success": True}
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
    
    def _invalidate_related_caches(self, content: str):
        """Invalidate caches related to new content"""
        content_lower = content.lower()
        
        # Invalidate food-related caches if food content added
        if any(food in content_lower for food in ["food", "eat", "like", "enjoy", "chicken", "pizza"]):
            keys_to_remove = [key for key in MEMORY_SEARCH_CACHE.keys() if "food" in key.lower()]
            for key in keys_to_remove:
                MEMORY_SEARCH_CACHE.pop(key, None)
            
            keys_to_remove = [key for key in LLM_RESPONSE_CACHE.keys() if "food" in key.lower()]
            for key in keys_to_remove:
                LLM_RESPONSE_CACHE.pop(key, None)
        
        # Update user profile cache if personal info added
        if any(term in content_lower for term in ["food", "like", "enjoy"]):
            threading.Thread(target=self._load_enhanced_user_profile, daemon=True).start()
    
    # === INHERIT ALL ORIGINAL METHODS ===
    
    def analyze_document(self, content: str, doc_type: str = "general", filename: str = None) -> Dict[str, Any]:
        """Full document analysis with all original features preserved"""
        # Use parent class method with all features
        return super().analyze_document(content, doc_type, filename)
    
    def draft_email_response(self, original_email: str, intent: str, tone: str = "professional") -> EmailDraft:
        """Full email drafting with all original features preserved"""
        # Use parent class method with all features
        return super().draft_email_response(original_email, intent, tone)
    
    def generate_smart_questions(self, context: str, domain: str = "general") -> List[SmartQuestion]:
        """Full smart question generation with all original features preserved"""
        # Use parent class method with all features
        return super().generate_smart_questions(context, domain)
    
    def process_meeting_transcript(self, transcript: str, meeting_title: str = None, attendees: List[str] = None) -> Dict[str, Any]:
        """Full meeting processing with all original features preserved"""
        # Use parent class method with all features
        return super().process_meeting_transcript(transcript, meeting_title, attendees)
    
    # === PERFORMANCE MONITORING ===
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Enhanced performance statistics"""
        cache_efficiency = (PERFORMANCE_STATS["cache_hits"] / 
                          max(1, PERFORMANCE_STATS["cache_hits"] + PERFORMANCE_STATS["cache_misses"]) * 100)
        
        return {
            "cache_efficiency": f"{cache_efficiency:.1f}%",
            "memory_cache_size": len(MEMORY_SEARCH_CACHE),
            "llm_cache_size": len(LLM_RESPONSE_CACHE),
            "query_cache_size": len(LLM_QUERY_CACHE),
            "user_profile_items": len(USER_PROFILE_CACHE),
            "llm_query_enhancements": PERFORMANCE_STATS["llm_query_enhancements"],
            "llm_response_synthesis": PERFORMANCE_STATS["llm_response_synthesis"],
            "action_items": len(self.action_items),
            "documents_processed": len(self.document_insights),
            "meetings_processed": len(self.meeting_summaries),
            "email_drafts": len(self.email_drafts),
            "llm_available": self.llm_available,
            "memory_available": self.hybrid_manager is not None
        }
    
    def clear_all_caches(self):
        """Clear all performance caches"""
        global MEMORY_SEARCH_CACHE, LLM_RESPONSE_CACHE, LLM_QUERY_CACHE, USER_PROFILE_CACHE
        MEMORY_SEARCH_CACHE.clear()
        LLM_RESPONSE_CACHE.clear()
        LLM_QUERY_CACHE.clear()
        USER_PROFILE_CACHE.clear()
        self.smart_cache.clear()
        PERFORMANCE_STATS.update({
            "cache_hits": 0,
            "cache_misses": 0,
            "llm_query_enhancements": 0,
            "llm_response_synthesis": 0
        })
        print("🧹 All LLM-enhanced caches cleared")
    
    # === DOCUMENT ANALYSIS ===
    
    def analyze_document(self, content: str, filename: str = "document") -> dict:
        """LLM-enhanced document analysis"""
        try:
            print(f"📄 Analyzing document: {filename}")
            
            # Basic content analysis
            word_count = len(content.split())
            char_count = len(content)
            
            # Use LLM for intelligent analysis if available
            if self.llm_available:
                analysis_prompt = f"""Analyze this document comprehensively and provide structured output:

Document: {filename}
Content: {content[:3000]}{'...' if len(content) > 3000 else ''}

Please provide a detailed analysis in the following structured format:

**Document Summary:**
Provide a 2-3 sentence summary of the document's main purpose and scope.

**Key Points:**
- List 4-6 key points or findings from the document
- Focus on important details, requirements, or insights
- Include specific numbers, dates, or requirements mentioned

**Action Items:**
Generate 3-4 specific action items based on the document content. For each action item, provide exactly this format:
- [Task description with clear deliverable] | Priority: [high/medium/low] | Assigned to: [role or "me"]

**Generated Questions:**
Create 3-4 strategic questions that would be important to ask based on this document's content.

Format your response exactly as shown above with clear sections and bullet points."""

                try:
                    llm_analysis = self.llm.invoke(analysis_prompt)
                    analysis_content = llm_analysis.content
                    
                    # Parse the structured response
                    parsed_analysis = self._parse_structured_analysis(analysis_content, filename)
                    
                except Exception as e:
                    print(f"⚠️ LLM analysis failed: {e}")
                    parsed_analysis = {
                        "summary": f"Document '{filename}' contains {word_count} words and {char_count} characters. Basic processing completed.",
                        "key_points": [f"Document contains {word_count} words", "Processing completed successfully"],
                        "action_items": [],
                        "questions": [],
                        "raw_analysis": f"Error: {str(e)}"
                    }
            else:
                parsed_analysis = {
                    "summary": f"Document '{filename}' processed. Contains {word_count} words across {char_count} characters.",
                    "key_points": [f"Document contains {word_count} words", "Basic processing completed"],
                    "action_items": [],
                    "questions": [],
                    "raw_analysis": "LLM not available - basic processing only"
                }
            
            # Store document in memory with full analysis
            if hasattr(self, 'store_memory'):
                try:
                    import asyncio
                    # Store comprehensive document analysis
                    memory_content = f"""Document Analysis: {filename}

Summary: {parsed_analysis.get('summary', 'Analysis completed')}

Key Points:
{chr(10).join(['• ' + point for point in parsed_analysis.get('key_points', [])])}

Action Items:
{chr(10).join([f'• {item.get("task", "")} (Priority: {item.get("priority", "medium")})' for item in parsed_analysis.get('action_items', [])])}

Generated Questions:
{chr(10).join(['• ' + question for question in parsed_analysis.get('questions', [])])}

Content: {content[:1000]}{'...' if len(content) > 1000 else ''}"""
                    
                    # Store memory using create_task instead of asyncio.run to avoid event loop conflict
                    import asyncio
                    try:
                        loop = asyncio.get_running_loop()
                        # We're in an async context, use create_task
                        loop.create_task(self.store_memory(
                            memory_content,
                            user_id=getattr(self, 'current_user', 'default_user'),
                            memory_type="document",
                            tags=["document", "analysis", filename.lower().replace(' ', '_'), "actionable"]
                        ))
                    except RuntimeError:
                        # No running loop, use asyncio.run
                        asyncio.run(self.store_memory(
                            memory_content,
                            user_id=getattr(self, 'current_user', 'default_user'),
                            memory_type="document",
                            tags=["document", "analysis", filename.lower().replace(' ', '_'), "actionable"]
                        ))
                    print(f"💾 Document analysis stored in memory system")
                    
                    # Create actionable tasks from action items
                    print(f"🔍 Action items found: {len(parsed_analysis.get('action_items', []))}")
                    for i, item in enumerate(parsed_analysis.get('action_items', [])):
                        print(f"   {i+1}. {item}")
                    self._create_smart_tasks_from_analysis(parsed_analysis, filename)
                    
                except Exception as e:
                    print(f"⚠️ Failed to store document: {e}")
            
            # Extract insights from content
            insights = []
            
            # Content-based insights
            if word_count > 1000:
                insights.append(f"Comprehensive document with {word_count} words")
            elif word_count > 500:
                insights.append(f"Medium-length document with {word_count} words")
            else:
                insights.append(f"Concise document with {word_count} words")
            
            # Keyword detection
            content_lower = content.lower()
            if any(keyword in content_lower for keyword in ['ai', 'artificial intelligence', 'machine learning']):
                insights.append("Contains AI/ML related content")
            if any(keyword in content_lower for keyword in ['automation', 'process', 'workflow']):
                insights.append("Discusses automation or process improvement")
            if any(keyword in content_lower for keyword in ['rfp', 'proposal', 'requirement']):
                insights.append("Appears to be a proposal or requirements document")
            if any(keyword in content_lower for keyword in ['contract', 'agreement', 'terms']):
                insights.append("Contains contractual or legal content")
            
            # Document structure insights
            if content.count('\n') > 20:
                insights.append("Well-structured document with multiple sections")
            if any(marker in content for marker in ['1.', '2.', '3.', 'a)', 'b)', 'c)']):
                insights.append("Contains numbered or bulleted lists")
            
            result = {
                "summary": parsed_analysis.get("summary", "Analysis completed"),
                "key_points": parsed_analysis.get("key_points", insights),
                "action_items": parsed_analysis.get("action_items", []),
                "questions": parsed_analysis.get("questions", []),
                "insights": insights,  # Keep for backward compatibility
                "word_count": word_count,
                "char_count": char_count,
                "filename": filename,
                "analysis_type": "LLM-enhanced" if self.llm_available else "basic",
                "raw_analysis": parsed_analysis.get("raw_analysis", "")
            }
            
            print(f"✅ Document analysis completed for: {filename}")
            return result
            
        except Exception as e:
            print(f"❌ Document analysis error: {e}")
            return {
                "summary": f"Error analyzing document '{filename}': {str(e)}",
                "insights": ["Analysis failed", f"Error: {str(e)}"],
                "word_count": 0,
                "char_count": len(content) if content else 0,
                "filename": filename,
                "analysis_type": "error"
            }
    
    def _parse_structured_analysis(self, analysis_content: str, filename: str) -> dict:
        """Parse structured LLM analysis response"""
        try:
            result = {
                "summary": "",
                "key_points": [],
                "action_items": [],
                "questions": [],
                "raw_analysis": analysis_content
            }
            
            # Split into sections
            sections = analysis_content.split('**')
            current_section = None
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                if 'Document Summary:' in section:
                    current_section = 'summary'
                    # Extract summary text after the header
                    summary_text = section.replace('Document Summary:', '').strip()
                    if summary_text:
                        result["summary"] = summary_text
                elif 'Key Points:' in section:
                    current_section = 'key_points'
                elif 'Action Items:' in section:
                    current_section = 'action_items'
                elif 'Generated Questions:' in section:
                    current_section = 'questions'
                else:
                    # Process content for current section
                    if current_section == 'summary' and section and not result["summary"]:
                        result["summary"] = section
                    elif current_section == 'key_points':
                        # Extract bullet points
                        lines = section.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('-') or line.startswith('•'):
                                result["key_points"].append(line[1:].strip())
                    elif current_section == 'action_items':
                        # Extract action items with improved parsing
                        lines = section.split('\n')
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            # Look for task description (bullet points)
                            if line.startswith('-') or line.startswith('•'):
                                task_line = line[1:].strip()
                                
                                # Check if using new format with pipes
                                if '|' in task_line:
                                    parts = [part.strip() for part in task_line.split('|')]
                                    if len(parts) >= 3:
                                        task_desc = parts[0]
                                        priority_part = parts[1].lower()
                                        assigned_part = parts[2].lower()
                                        
                                        # Extract priority
                                        priority = "medium"  # default
                                        if 'high' in priority_part:
                                            priority = "high"
                                        elif 'low' in priority_part:
                                            priority = "low"
                                        elif 'medium' in priority_part:
                                            priority = "medium"
                                        
                                        # Extract assignment
                                        assigned_to = "me"  # default
                                        if 'assigned to:' in assigned_part:
                                            assigned_to = assigned_part.split('assigned to:', 1)[1].strip()
                                        
                                        result["action_items"].append({
                                            "task": task_desc,
                                            "priority": priority,
                                            "assigned_to": assigned_to
                                        })
                                else:
                                    # Fallback to old format
                                    result["action_items"].append({
                                        "task": task_line,
                                        "priority": "medium",
                                        "assigned_to": "me"
                                    })
                            
                    elif current_section == 'questions':
                        # Extract questions
                        lines = section.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and (line.endswith('?') or line.startswith('-') or line.startswith('•')):
                                question = line.lstrip('-•').strip()
                                if question:
                                    result["questions"].append(question)
            
            # Fallback parsing if structured format not found
            if not result["summary"] and not result["key_points"]:
                # Try to extract from unstructured content
                lines = analysis_content.split('\n')
                summary_lines = []
                for i, line in enumerate(lines[:5]):  # First few lines likely contain summary
                    if line.strip() and not line.strip().startswith('*'):
                        summary_lines.append(line.strip())
                        if len(summary_lines) >= 2:
                            break
                
                if summary_lines:
                    result["summary"] = ' '.join(summary_lines)
                
                # Extract any bullet points found
                for line in lines:
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•'):
                        result["key_points"].append(line[1:].strip())
            
            return result
            
        except Exception as e:
            print(f"⚠️ Failed to parse structured analysis: {e}")
            return {
                "summary": f"Analysis completed for {filename}",
                "key_points": ["Document processed successfully"],
                "action_items": [],
                "questions": [],
                "raw_analysis": analysis_content
            }
    
    def _create_smart_tasks_from_analysis(self, analysis: dict, filename: str):
        """Create actionable tasks from document analysis"""
        try:
            action_items = analysis.get('action_items', [])
            print(f"📋 _create_smart_tasks_from_analysis called with {len(action_items)} action items")
            print(f"📋 Current user: {getattr(self, 'current_user', 'NOT SET')}")
            if not action_items:
                print("❌ No action items found, skipping task creation")
                return
            
            from datetime import datetime, timedelta
            import uuid
            
            # Initialize smart tasks list if not exists
            if not hasattr(self, 'smart_tasks'):
                self.smart_tasks = []
            
            for item in action_items:
                task_id = str(uuid.uuid4())[:8]
                
                # Calculate due date based on priority
                if item.get('priority') == 'high':
                    due_date = datetime.now() + timedelta(days=3)
                elif item.get('priority') == 'medium':
                    due_date = datetime.now() + timedelta(days=7)
                else:
                    due_date = datetime.now() + timedelta(days=14)
                
                smart_task = {
                    "id": task_id,
                    "title": item.get('task', 'Unknown task'),
                    "description": f"From document: {filename}",
                    "priority": item.get('priority', 'medium'),
                    "assigned_to": item.get('assigned_to', 'me'),
                    "status": "pending",
                    "source_document": filename,
                    "created_date": datetime.now().isoformat(),
                    "due_date": due_date.isoformat(),
                    "completion_date": None,
                    "nudge_count": 0,
                    "last_nudge": None
                }
                
                self.smart_tasks.append(smart_task)
                print(f"📋 Created smart task: {smart_task['title'][:50]}...")
            
            # Save tasks to session
            self._save_smart_tasks_to_session()
            
        except Exception as e:
            print(f"⚠️ Failed to create smart tasks: {e}")
    
    def _save_smart_tasks_to_session(self):
        """Save smart tasks to session file"""
        try:
            if hasattr(self, 'current_user') and self.current_user:
                import json
                import os
                from pathlib import Path
                
                # Ensure sessions directory exists
                sessions_dir = Path("sessions")
                sessions_dir.mkdir(exist_ok=True)
                
                tasks_file = sessions_dir / f"{self.current_user}_smart_tasks.json"
                
                with open(tasks_file, 'w') as f:
                    json.dump(getattr(self, 'smart_tasks', []), f, indent=2)
                print(f"💾 Smart tasks saved to session: {tasks_file}")
        except Exception as e:
            print(f"⚠️ Failed to save smart tasks: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_smart_tasks_from_session(self):
        """Load smart tasks from session file"""
        try:
            if hasattr(self, 'current_user') and self.current_user:
                import json
                from pathlib import Path
                
                sessions_dir = Path("sessions")
                tasks_file = sessions_dir / f"{self.current_user}_smart_tasks.json"
                
                try:
                    with open(tasks_file, 'r') as f:
                        self.smart_tasks = json.load(f)
                    print(f"📋 Loaded {len(self.smart_tasks)} smart tasks from session: {tasks_file}")
                except FileNotFoundError:
                    self.smart_tasks = []
                    print(f"📋 No existing smart tasks found, starting fresh: {tasks_file}")
        except Exception as e:
            print(f"⚠️ Failed to load smart tasks: {e}")
            import traceback
            traceback.print_exc()
            self.smart_tasks = []
    
    def get_smart_summary(self) -> dict:
        """Get intelligent summary of pending tasks and recommendations"""
        try:
            if not hasattr(self, 'smart_tasks'):
                self._load_smart_tasks_from_session()
            
            from datetime import datetime, timedelta
            now = datetime.now()
            
            # Categorize tasks
            overdue = []
            due_soon = []
            pending_high = []
            completed_recently = []
            
            for task in self.smart_tasks:
                due_date = datetime.fromisoformat(task['due_date'])
                
                if task['status'] == 'completed':
                    if task['completion_date']:
                        completion_date = datetime.fromisoformat(task['completion_date'])
                        if (now - completion_date).days <= 7:
                            completed_recently.append(task)
                elif task['status'] == 'pending':
                    if due_date < now:
                        overdue.append(task)
                    elif (due_date - now).days <= 2:
                        due_soon.append(task)
                    elif task['priority'] == 'high':
                        pending_high.append(task)
            
            # Generate smart recommendations
            recommendations = []
            
            if overdue:
                recommendations.append({
                    "type": "urgent",
                    "message": f"🚨 {len(overdue)} overdue tasks need immediate attention",
                    "action": "Review and prioritize overdue items",
                    "tasks": overdue[:3]
                })
            
            if due_soon:
                recommendations.append({
                    "type": "warning",
                    "message": f"⏰ {len(due_soon)} tasks due within 2 days",
                    "action": "Schedule time to complete these tasks",
                    "tasks": due_soon[:3]
                })
            
            if pending_high and not overdue:
                recommendations.append({
                    "type": "info",
                    "message": f"🎯 {len(pending_high)} high-priority tasks await your attention",
                    "action": "Focus on high-impact activities",
                    "tasks": pending_high[:2]
                })
            
            if completed_recently:
                recommendations.append({
                    "type": "success",
                    "message": f"✅ Great progress! {len(completed_recently)} tasks completed this week",
                    "action": "Keep up the momentum",
                    "tasks": completed_recently[:2]
                })
            
            # Generate next steps
            next_steps = []
            if overdue:
                next_steps.append(f"Address {len(overdue)} overdue items immediately")
            if due_soon:
                next_steps.append(f"Complete {len(due_soon)} upcoming deadlines")
            if not overdue and not due_soon and pending_high:
                next_steps.append(f"Focus on {len(pending_high)} high-priority tasks")
            
            return {
                "total_tasks": len(self.smart_tasks),
                "pending": len([t for t in self.smart_tasks if t['status'] == 'pending']),
                "completed": len([t for t in self.smart_tasks if t['status'] == 'completed']),
                "overdue": len(overdue),
                "due_soon": len(due_soon),
                "recommendations": recommendations,
                "next_steps": next_steps,
                "last_updated": now.isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Failed to generate smart summary: {e}")
            return {
                "total_tasks": 0,
                "pending": 0,
                "completed": 0,
                "overdue": 0,
                "due_soon": 0,
                "recommendations": [],
                "next_steps": [],
                "error": str(e)
            }
    
    def complete_task(self, task_id: str) -> dict:
        """Mark a task as completed"""
        try:
            if not hasattr(self, 'smart_tasks'):
                self._load_smart_tasks_from_session()
            
            from datetime import datetime
            
            for task in self.smart_tasks:
                if task['id'] == task_id:
                    task['status'] = 'completed'
                    task['completion_date'] = datetime.now().isoformat()
                    
                    # Save updated tasks
                    self._save_smart_tasks_to_session()
                    
                    # Generate completion insights
                    insights = self._generate_completion_insights(task)
                    
                    print(f"✅ Task completed: {task['title']}")
                    return {
                        "success": True,
                        "task": task,
                        "insights": insights,
                        "message": f"Great job completing '{task['title']}'!"
                    }
            
            return {"success": False, "message": "Task not found"}
            
        except Exception as e:
            print(f"⚠️ Failed to complete task: {e}")
            return {"success": False, "message": str(e)}
    
    def _generate_completion_insights(self, completed_task: dict) -> list:
        """Generate insights when a task is completed"""
        insights = []
        
        try:
            from datetime import datetime
            
            # Check if completed on time
            due_date = datetime.fromisoformat(completed_task['due_date'])
            completion_date = datetime.fromisoformat(completed_task['completion_date'])
            
            if completion_date <= due_date:
                insights.append("Completed on time - excellent time management!")
            else:
                days_late = (completion_date - due_date).days
                insights.append(f"Completed {days_late} days after due date - consider earlier scheduling")
            
            # Check for related tasks
            related_tasks = [t for t in self.smart_tasks 
                           if t['source_document'] == completed_task['source_document'] 
                           and t['status'] == 'pending']
            
            if related_tasks:
                insights.append(f"{len(related_tasks)} related tasks from same document still pending")
            
            # Priority-based insights
            if completed_task['priority'] == 'high':
                insights.append("High-priority task completed - great focus on important work!")
            
            return insights
            
        except Exception as e:
            print(f"⚠️ Failed to generate insights: {e}")
            return ["Task completed successfully"]
    
    # === ENHANCED INTERACTIVE SESSION ===
    
    def run_productivity_session(self):
        """LLM-Enhanced interactive session with all features"""
        
        print("\n" + "="*70)
        print("🧠 LLM-ENHANCED Productivity Digital Twin")
        print("="*70)
        print("🎯 INTELLIGENT FEATURES:")
        print("  🔍 LLM query expansion and semantic search")
        print("  📝 Response synthesis from multiple memories")
        print("  🧩 Context-aware intelligent answers")
        print("  ⚡ Smart caching for LLM operations")
        print("  🎯 Enhanced food preference handling")
        print("\n📋 ALL ORIGINAL FEATURES PRESERVED:")
        print("  📄 Complete document analysis • 🎤 Full meeting processing")
        print("  ✉️ Context-aware email drafting • 📅 Smart calendar suggestions")
        print("  🧠 LLM-powered smart questions • 🔄 Complete action item lifecycle")
        print("  💾 Full session persistence • 📊 Rich analytics and insights")
        print("\nCommands (Enhanced + All Original):")
        print("  • Ask natural questions - LLM finds and synthesizes answers")
        print("  • 'analyze <text>' • 'meeting <transcript>' • 'draft_email <original> | <intent>'")
        print("  • 'questions <context>' • 'my_actions' • 'daily_brief'")
        print("  • 'llm_stats' - LLM enhancement statistics")
        print("  • 'clear_cache' - Clear all caches")
        print("="*70)
        
        # Get user ID
        user_id = input("\n👤 Enter your user ID (or press Enter for default): ").strip()
        if not user_id:
            user_id = "default_user"
        
        self.current_user = user_id
        
        # Load profile from session first
        profile_loaded = self._load_profile_from_session()
        
        # Try to load previous session (full features)
        session_loaded = self.load_recent_session(user_id)
        
        print(f"✅ LLM-enhanced session started for: {user_id}")
        if session_loaded:
            print("💾 Previous session restored with all data")
        
        print("💡 Try: 'what food do I like?' for intelligent synthesis!")
        print("\n" + "-"*70)
        
        while True:
            try:
                user_input = input(f"\n{user_id}: ").strip()
                start_time = time.time()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    self.save_session()  # Full session saving
                    stats = self.get_performance_stats()
                    print(f"\n👋 Session ended. Cache efficiency: {stats['cache_efficiency']}")
                    print(f"LLM enhancements: {stats['llm_query_enhancements']} queries, {stats['llm_response_synthesis']} responses")
                    break
                
                elif user_input.lower() == "llm_stats":
                    stats = self.get_performance_stats()
                    print(f"\n🧠 LLM ENHANCEMENT STATISTICS")
                    print(f"Cache efficiency: {stats['cache_efficiency']}")
                    print(f"Query enhancements: {stats['llm_query_enhancements']}")
                    print(f"Response synthesis: {stats['llm_response_synthesis']}")
                    print(f"Memory cache: {stats['memory_cache_size']} entries")
                    print(f"LLM cache: {stats['llm_cache_size']} entries")
                    print(f"User profile: {stats['user_profile_items']} categories")
                
                elif user_input.lower().startswith("analyze "):
                    content = user_input[8:].strip()
                    if content:
                        analysis = self.analyze_document(content)  # Full analysis
                        self._display_document_analysis(analysis)
                    else:
                        print("Please provide content to analyze")
                
                elif user_input.lower().startswith("meeting "):
                    transcript = user_input[8:].strip()
                    if transcript:
                        meeting_analysis = self.process_meeting_transcript(transcript)  # Full processing
                        self._display_meeting_analysis(meeting_analysis)
                    else:
                        print("Please provide meeting transcript")
                
                elif user_input.lower().startswith("draft_email "):
                    parts = user_input[12:].split("|")
                    if len(parts) >= 2:
                        original = parts[0].strip()
                        intent = parts[1].strip()
                        draft = self.draft_email_response(original, intent)  # Full drafting
                        self._display_email_draft(draft)
                    else:
                        print("Format: draft_email <original email> | <your intent>")
                
                elif user_input.lower().startswith("questions "):
                    context = user_input[10:].strip()
                    if context:
                        questions = self.generate_smart_questions(context)  # Full generation
                        self._display_smart_questions(questions)
                    else:
                        print("Please provide context for questions")
                
                elif user_input.lower() == "my_actions":
                    self._display_action_items()  # Full action management
                
                elif user_input.lower() == "daily_brief":
                    self._display_daily_briefing()  # Full briefing
                
                elif user_input.lower() == "clear_cache":
                    self.clear_all_caches()
                
                else:
                    # Process with LLM-enhanced method
                    response = self.process_user_input(user_input, user_id)
                    print(f"\nA: {response}")
                
                # Enhanced performance monitoring
                response_time = time.time() - start_time
                PERFORMANCE_STATS["avg_response_time"] = response_time
                
                # Color-coded response time with LLM indicators
                if response_time < 1:
                    color = "🟢"
                    indicator = " (cached)" if PERFORMANCE_STATS["cache_hits"] > 0 else " (template)"
                elif response_time < 5:
                    color = "🟡"
                    indicator = " (LLM-enhanced)" if PERFORMANCE_STATS["llm_response_synthesis"] > 0 else ""
                elif response_time < 15:
                    color = "🟠"
                    indicator = " (complex search)"
                else:
                    color = "🔴"
                    indicator = " (slow)"
                
                print(f"\n{color} Response time: {response_time:.2f}s{indicator}")
                
                # Performance tips
                if response_time > 15:
                    print("💡 This response is now cached for instant future access")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    # === INHERIT ALL ORIGINAL DISPLAY METHODS ===
    
    def _display_document_analysis(self, analysis: Dict[str, Any]):
        """Display comprehensive document analysis results"""
        # Use parent class method with all features
        super()._display_document_analysis(analysis)
    
    def _display_meeting_analysis(self, analysis: Dict[str, Any]):
        """Display comprehensive meeting analysis results"""
        # Use parent class method with all features
        super()._display_meeting_analysis(analysis)
    
    def _display_email_draft(self, draft: EmailDraft):
        """Display comprehensive email draft"""
        # Use parent class method with all features
        super()._display_email_draft(draft)
    
    def _display_smart_questions(self, questions: List[SmartQuestion]):
        """Display comprehensive smart questions"""
        # Use parent class method with all features
        super()._display_smart_questions(questions)
    
    def _display_action_items(self):
        """Display comprehensive action items"""
        # Use parent class method with all features
        super()._display_action_items()
    
    def _display_daily_briefing(self):
        """Display comprehensive daily productivity briefing"""
        # Use parent class method with all features
        super()._display_daily_briefing()

# === LLM ENHANCEMENT COMPONENTS ===

class LLMQueryEnhancer:
    """Handles LLM-powered query expansion"""
    
    def __init__(self, llm, llm_available):
        self.llm = llm
        self.llm_available = llm_available
    
    def enhance_query(self, question: str) -> List[str]:
        """Generate enhanced search queries using LLM"""
        
        # Check cache first
        cache_key = f"query_enhance_{hash(question.lower())}"
        if cache_key in LLM_QUERY_CACHE:
            cached_data = LLM_QUERY_CACHE[cache_key]
            if time.time() - cached_data['timestamp'] < CACHE_TIMEOUT:
                return cached_data['queries']
        
        if not self.llm_available:
            return self._fallback_query_enhancement(question)
        
        prompt = f"""Generate 4 semantic search queries to find memories related to this question:
"{question}"

Consider:
1. Key concepts and synonyms
2. Different ways to phrase the same question  
3. Specific terms that might be in memories
4. Related concepts that would help answer the question

Return JSON array of 4 search strings that would find relevant memories.
Focus on terms likely to appear in stored memories.

Example for "what food do I like?":
["food preferences", "like to eat", "enjoy eating", "favorite dishes"]
"""
        
        try:
            response = self.llm.invoke(prompt)
            json_start = response.content.find('[')
            json_end = response.content.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                queries = json.loads(json_str)
                
                # Cache the result
                LLM_QUERY_CACHE[cache_key] = {
                    'queries': queries,
                    'timestamp': time.time()
                }
                return queries
        except Exception as e:
            print(f"⚠️ LLM query enhancement failed: {e}")
        
        # Fallback
        fallback_queries = self._fallback_query_enhancement(question)
        LLM_QUERY_CACHE[cache_key] = {
            'queries': fallback_queries,
            'timestamp': time.time()
        }
        return fallback_queries
    
    def _fallback_query_enhancement(self, question: str) -> List[str]:
        """Fallback query enhancement without LLM"""
        question_lower = question.lower()
        queries = [question]  # Original query
        
        # Food-related enhancements
        if any(term in question_lower for term in ["food", "eat", "like to eat", "enjoy"]):
            queries.extend([
                "food preferences",
                "like to eat", 
                "enjoy eating",
                "favorite dishes",
                "butter chicken",
                "tandoori pizza",
                "food like enjoy"
            ])
        
        # Work-related enhancements
        elif any(term in question_lower for term in ["work", "job", "company"]):
            queries.extend([
                "work at",
                "job title",
                "company",
                "employment",
                "Tavant"
            ])
        
        # Sports-related enhancements
        elif any(term in question_lower for term in ["sports", "play", "games"]):
            queries.extend([
                "sports",
                "play",
                "games",
                "football cricket badminton"
            ])
        
        # General personal info
        elif any(term in question_lower for term in ["about me", "personal", "background"]):
            queries.extend([
                "personal information",
                "background",
                "about me",
                "profile"
            ])
        
        return queries[:4]  # Limit to 4 queries

class LLMResponseSynthesizer:
    """Handles LLM-powered response synthesis"""
    
    def __init__(self, llm, llm_available):
        self.llm = llm
        self.llm_available = llm_available
    
    def synthesize_response(self, question: str, memories: List[tuple]) -> str:
        """Synthesize response from multiple memories using LLM"""
        
        if not self.llm_available or not memories:
            return self._fallback_synthesis(question, memories)
        
        # Prepare memory context
        memory_context = self._prepare_memory_context(memories)
        
        prompt = f"""The user asked: "{question}"

Here is relevant personal information about the user:
{memory_context}

IMPORTANT: The user is asking about THEMSELVES. If they mention "Paresh" they are referring to themselves.

Rules for your response:
1. Answer ONLY what the user asked about
2. Use "You" when referring to the user (never "Paresh" - convert "about Paresh" to "about you")
3. Be direct and specific - no introductions or explanations
4. If asked about food, list ALL foods mentioned in the memories
5. If asked about sports, list ALL sports mentioned
6. If asked "tell me about Paresh" or similar, provide comprehensive info about the user
7. Don't add context or background unless asked
8. One or two sentences maximum (unless comprehensive info requested)

Examples:
- Question "what food do I like?" → Answer "You like butter chicken and tandoori pizza."
- Question "tell me about Paresh" → Answer "You are Paresh Deshpande, you work at Tavant as a Senior Director, you like football cricket and badminton, and you enjoy butter chicken and tandoori pizza."

Your direct answer:"""
        
        try:
            response = self.llm.invoke(prompt)
            synthesized = response.content.strip()
            
            # Clean up common LLM artifacts
            synthesized = self._clean_response(synthesized)
            return synthesized
            
        except Exception as e:
            print(f"⚠️ LLM response synthesis failed: {e}")
            return self._fallback_synthesis(question, memories)
    
    def _prepare_memory_context(self, memories: List[tuple]) -> str:
        """Prepare memory content for LLM"""
        context_parts = []
        
        for i, (memory, score) in enumerate(memories[:6], 1):  # Top 6 memories
            content = memory.semantic_summary or memory.content
            context_parts.append(f"{i}. {content}")
        
        return "\n".join(context_parts)
    
    def _clean_response(self, response: str) -> str:
        """Clean up LLM response artifacts and fix formatting"""
        # Fix newline issues - convert literal \n to actual newlines
        response = response.replace("\\n", "\n")
        
        # Remove common LLM phrases
        phrases_to_remove = [
            "Based on the memories provided,",
            "From the information given,",
            "According to your memories,",
            "The memories indicate that",
            "Based on your stored information,",
            "Here's what I can share:",
            "It seems like you're interested in learning about",
            "Paresh Deshpande is a name that comes up,",
            "though specific details about him aren't clear.",
            "If you have more specific questions or need further details, feel free to ask!",
            "In a work context,",
            "This might indicate",
            "appears to have",
            "seems like"
        ]
        
        for phrase in phrases_to_remove:
            response = response.replace(phrase, "").strip()
        
        # Remove excessive newlines
        while "\n\n\n" in response:
            response = response.replace("\n\n\n", "\n\n")
        
        # Remove generic introductions and conclusions
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip generic lines
            if any(skip in line.lower() for skip in [
                "here's what i can share",
                "it seems like you're interested", 
                "if you have more specific questions",
                "feel free to ask",
                "paresh appears to",
                "though specific details",
                "this might indicate"
            ]):
                continue
            if line:  # Only add non-empty lines
                cleaned_lines.append(line)
        
        response = '\n'.join(cleaned_lines)
        
        # Ensure response starts properly
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]
        
        return response.strip()
    
    def _fallback_synthesis(self, question: str, memories: List[tuple]) -> str:
        """Fallback synthesis without LLM"""
        if not memories:
            return "I don't have specific information about that in your memories yet."
        
        # Get best memory
        best_memory, score = memories[0]
        content = best_memory.semantic_summary or best_memory.content
        
        if score > 0.7:
            return content
        else:
            return f"Based on your memories, {content}"

class SmartCache:
    """Intelligent caching system"""
    
    def __init__(self):
        self.cache = {}
    
    def get_cached_response(self, key: str) -> Optional[str]:
        """Get cached response if valid"""
        if key in self.cache:
            cached_data = self.cache[key]
            if time.time() - cached_data['timestamp'] < CACHE_TIMEOUT:
                return cached_data['response']
        return None
    
    def cache_response(self, key: str, response: str) -> str:
        """Cache response with timestamp"""
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        return response
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()

def main():
    """Main function to run LLM-enhanced productivity twin"""
    try:
        print("🧠 Starting LLM-ENHANCED Productivity Twin...")
        twin = LLMEnhancedProductivityTwin()
        twin.run_productivity_session()
    except KeyboardInterrupt:
        print("\n👋 Session interrupted.")
    except Exception as e:
        print(f"❌ Failed to start LLM-enhanced twin: {e}")
        print("Make sure your .env file is configured with Azure credentials.")

if __name__ == "__main__":
    main()