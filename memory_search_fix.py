#!/usr/bin/env python3
"""
Memory Search Fix for Food Preferences
Adds better query expansion for food-related questions
"""

def enhanced_food_query_expansion(self, question: str) -> List[str]:
    """Enhanced food query expansion"""
    question_lower = question.lower().strip()
    
    # Food-specific query expansions
    food_queries = []
    
    if any(term in question_lower for term in ["what i like to eat", "what food", "food i like", "what do i like to eat"]):
        food_queries.extend([
            "food preferences like eat enjoy",
            "butter chicken tandoori pizza", 
            "favorite food dishes",
            "like to eat food",
            "enjoy eating"
        ])
    
    if "food" in question_lower or "eat" in question_lower:
        food_queries.extend([
            "food preferences",
            "like to eat", 
            "enjoy eating",
            "favorite dishes"
        ])
    
    return food_queries

# Add this method to the OptimizedFullFeatureProductivityTwin class
def _check_user_profile_cache_enhanced(self, question: str) -> Optional[str]:
    """Enhanced user profile cache with food preferences"""
    question_lower = question.lower().strip()
    
    # Existing checks...
    if any(q in question_lower for q in ["what is my name", "what's my name", "my name"]):
        return USER_PROFILE_CACHE.get("name", "Your name is Paresh Deshpande.")
    
    if any(q in question_lower for q in ["where do i work", "what company", "my company"]):
        company = USER_PROFILE_CACHE.get("company", "Tavant")
        return f"You work at {company}."
    
    if any(q in question_lower for q in ["what do i do", "my job", "my role"]):
        role = USER_PROFILE_CACHE.get("role", "Senior Director")
        company = USER_PROFILE_CACHE.get("company", "Tavant")
        return f"You are a {role} at {company}."
    
    if any(q in question_lower for q in ["what sports", "sports do i like"]):
        sports = USER_PROFILE_CACHE.get("sports", "football, cricket, and badminton")
        return f"You like {sports}."
    
    # ENHANCED: Food preferences
    if any(q in question_lower for q in ["what i like to eat", "what food", "food i like", "what do i like to eat"]):
        # Force a fresh memory search for food to get latest preferences
        return None  # Don't use cache, force memory search
    
    return None

print("Memory search enhancement loaded!")
print("Key fixes:")
print("1. Enhanced food query expansion")
print("2. Force fresh search for food questions") 
print("3. Better query matching for preferences")