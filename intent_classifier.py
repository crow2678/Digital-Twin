#!/usr/bin/env python3
"""
Intelligent Intent Classification System
Uses LLM to understand user intent: NEW, UPDATE, SEARCH, or CORRECTION
"""

import json
from typing import Dict, Optional, List
from enum import Enum

class UserIntent(Enum):
    SEARCH = "search"           # "what sports do I like?"
    NEW = "new"                # "I like swimming" (completely new info)
    UPDATE = "update"          # "I also like tennis" (adding to existing)
    CORRECTION = "correction"  # "Actually, I don't like football"
    QUESTION = "question"      # "Do you know about...?"

class IntentClassifier:
    """LLM-powered intent classification"""
    
    def __init__(self, llm, llm_available):
        self.llm = llm
        self.llm_available = llm_available
    
    def classify_intent(self, user_input: str, conversation_context: str = "") -> Dict:
        """Classify user intent and extract relevant information"""
        
        if not self.llm_available:
            return self._fallback_classification(user_input)
        
        prompt = f"""Analyze this user input and classify their intent:

User input: "{user_input}"
Previous context: {conversation_context}

Classify the intent as one of:
1. SEARCH - User is asking for existing information ("what sports do I like?")
2. NEW - User is providing completely new information ("I like swimming")
3. UPDATE - User is adding to existing information ("I also like tennis", "along with X, I like Y")
4. CORRECTION - User is correcting previous information ("Actually, I don't like X", "That's wrong")
5. QUESTION - User is asking a general question ("Do you know about X?")

Return JSON with:
{{
    "intent": "SEARCH|NEW|UPDATE|CORRECTION|QUESTION",
    "category": "sports|food|work|personal|other",
    "content": "the main information being shared/requested",
    "confidence": 0.8,
    "reasoning": "why you classified it this way"
}}

Examples:
- "what sports do I like?" → {{"intent": "SEARCH", "category": "sports", "content": "sports preferences"}}
- "I also like tennis" → {{"intent": "UPDATE", "category": "sports", "content": "tennis"}}
- "Actually, I don't like football" → {{"intent": "CORRECTION", "category": "sports", "content": "football"}}

Classify this input:"""
        
        try:
            response = self.llm.invoke(prompt)
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                classification = json.loads(json_str)
                return classification
        except Exception as e:
            print(f"⚠️ Intent classification failed: {e}")
        
        return self._fallback_classification(user_input)
    
    def _fallback_classification(self, user_input: str) -> Dict:
        """Fallback classification without LLM"""
        input_lower = user_input.lower()
        
        # Question patterns
        if any(q in input_lower for q in ["what", "how", "where", "when", "who", "?"]):
            return {
                "intent": "SEARCH",
                "category": self._detect_category(input_lower),
                "content": user_input,
                "confidence": 0.7,
                "reasoning": "Contains question words"
            }
        
        # Update patterns
        if any(pattern in input_lower for pattern in ["also", "along with", "in addition", "plus"]):
            return {
                "intent": "UPDATE", 
                "category": self._detect_category(input_lower),
                "content": user_input,
                "confidence": 0.8,
                "reasoning": "Contains addition words"
            }
        
        # Correction patterns
        if any(pattern in input_lower for pattern in ["actually", "wrong", "not", "don't", "correction"]):
            return {
                "intent": "CORRECTION",
                "category": self._detect_category(input_lower), 
                "content": user_input,
                "confidence": 0.8,
                "reasoning": "Contains correction words"
            }
        
        # Default to new information
        return {
            "intent": "NEW",
            "category": self._detect_category(input_lower),
            "content": user_input,
            "confidence": 0.6,
            "reasoning": "Default classification"
        }
    
    def _detect_category(self, text: str) -> str:
        """Detect content category"""
        if any(word in text for word in ["sport", "play", "game", "football", "cricket", "tennis"]):
            return "sports"
        if any(word in text for word in ["food", "eat", "like", "dish", "chicken", "pizza"]):
            return "food"
        if any(word in text for word in ["work", "job", "company", "office"]):
            return "work"
        return "other"

class SmartMemoryManager:
    """Intelligent memory management based on intent"""
    
    def __init__(self, twin_instance):
        self.twin = twin_instance
        self.classifier = IntentClassifier(twin_instance.llm, twin_instance.llm_available)
    
    def process_user_input(self, user_input: str, user_id: str) -> str:
        """Process input based on classified intent"""
        
        # Classify the intent
        classification = self.classifier.classify_intent(user_input)
        intent = classification["intent"]
        category = classification["category"]
        content = classification["content"]
        
        print(f"🎯 Intent: {intent} | Category: {category} | Confidence: {classification['confidence']}")
        
        if intent == "SEARCH":
            return self._handle_search(user_input, user_id, category)
        
        elif intent == "NEW":
            return self._handle_new_info(user_input, user_id, category, content)
        
        elif intent == "UPDATE":
            return self._handle_update(user_input, user_id, category, content)
        
        elif intent == "CORRECTION":
            return self._handle_correction(user_input, user_id, category, content)
        
        else:  # QUESTION or fallback
            return self._handle_general_question(user_input, user_id)
    
    def _handle_search(self, query: str, user_id: str, category: str) -> str:
        """Handle search requests"""
        print(f"🔍 Searching for {category} information...")
        
        # Use existing search logic
        return self.twin._llm_enhanced_search_and_respond(query, user_id)
    
    def _handle_new_info(self, info: str, user_id: str, category: str, content: str) -> str:
        """Handle completely new information"""
        print(f"💾 Storing new {category} information...")
        
        # Store in memory
        self.twin._store_new_information(info, user_id)
        
        # Update profile cache
        self.twin._update_profile_with_new_info(info)
        
        # Clear related caches
        self.twin._clear_related_caches(info)
        
        return f"I've learned that {content}. This information has been stored."
    
    def _handle_update(self, update: str, user_id: str, category: str, content: str) -> str:
        """Handle updates to existing information"""
        print(f"🔄 Updating {category} information...")
        
        # Store the update
        self.twin._store_new_information(update, user_id)
        
        # Update profile cache (this will merge with existing)
        self.twin._update_profile_with_new_info(update)
        
        # Clear caches to force fresh responses
        self.twin._clear_related_caches(update)
        
        # Get updated information to confirm
        if category == "sports" and "sports" in self.twin.USER_PROFILE_CACHE:
            return f"Updated! You now like {self.twin.USER_PROFILE_CACHE['sports']}."
        elif category == "food" and "food" in self.twin.USER_PROFILE_CACHE:
            return f"Updated! You now like {self.twin.USER_PROFILE_CACHE['food']}."
        else:
            # Use LLM to synthesize updated response
            return self.twin._llm_enhanced_search_and_respond(f"what {category} do I like?", user_id)
    
    def _handle_correction(self, correction: str, user_id: str, category: str, content: str) -> str:
        """Handle corrections to existing information"""
        print(f"✏️ Correcting {category} information...")
        
        # Store the correction
        self.twin._store_correction(correction, user_id)
        
        # Clear all related caches (important for corrections)
        self.twin._clear_related_caches(correction)
        
        # For corrections, we might need more sophisticated logic
        # For now, acknowledge and let LLM handle the response
        return self.twin._llm_enhanced_search_and_respond(correction, user_id)
    
    def _handle_general_question(self, question: str, user_id: str) -> str:
        """Handle general questions"""
        print(f"❓ Processing general question...")
        
        # Use existing LLM search
        return self.twin._llm_enhanced_search_and_respond(question, user_id)

# Integration example
def integrate_smart_memory(twin_instance):
    """Integrate smart memory management into existing twin"""
    
    # Replace the process_user_input method
    original_process = twin_instance.process_user_input
    smart_manager = SmartMemoryManager(twin_instance)
    
    def smart_process_user_input(user_input: str, user_id: str = "default_user") -> str:
        """Smart processing with intent classification"""
        start_time = time.time()
        print("🔒")
        
        # Check cache first (only for search intents)
        cache_key = f"llm_enhanced_{hash(user_input.lower())}_{user_id}"
        
        # Quick classification to decide on caching
        quick_classification = smart_manager.classifier._fallback_classification(user_input)
        
        if quick_classification["intent"] == "SEARCH":
            cached_response = twin_instance.smart_cache.get_cached_response(cache_key)
            if cached_response:
                return cached_response
        
        # Process with smart memory management
        response = smart_manager.process_user_input(user_input, user_id)
        
        # Cache only search responses
        if quick_classification["intent"] == "SEARCH":
            twin_instance.smart_cache.cache_response(cache_key, response)
        
        return response
    
    # Replace the method
    twin_instance.process_user_input = smart_process_user_input
    
    return twin_instance

print("🧠 Smart Intent Classification System loaded!")
print("Features:")
print("  🎯 LLM-powered intent detection")
print("  🔍 Smart search vs. update vs. correction")
print("  💾 Intelligent memory management")
print("  🔄 Context-aware cache handling")
print("  ✏️ Automatic correction processing")