import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from hybrid_memory_manager import HybridMemoryManager

# === CLEAN OUTPUT CONFIGURATION ===
import logging
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)  
logging.getLogger('azure.search').setLevel(logging.WARNING)
logging.getLogger('azure.core').setLevel(logging.WARNING)
logging.getLogger('hybrid_memory_manager').setLevel(logging.WARNING)
logging.getLogger('hybrid_memory_system').setLevel(logging.WARNING)
logging.getLogger('digital_twin_ontology').setLevel(logging.WARNING)
logging.getLogger().setLevel(logging.WARNING)
os.environ['AZURE_LOG_LEVEL'] = 'WARNING'

# Load environment variables
load_dotenv()

# Suppress verbose Azure and HTTP logs
verbose_loggers = [
    'azure.core.pipeline.policies.http_logging_policy',
    'azure.search.documents', 'azure.core', 'httpx', 'urllib3',
    'azure.identity', 'msal', 'requests',
    'hybrid_memory_manager', 'hybrid_memory_system', 
    'digital_twin_ontology', 'ai_semantic_processor'
]

for logger_name in verbose_loggers:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# Set Azure environment to reduce logs
os.environ['AZURE_LOG_LEVEL'] = 'ERROR'

# Configure root logger to be quieter
logging.basicConfig(level=logging.ERROR)

# Create clean memory logger for important events
memory_logger = logging.getLogger("memory_events")
memory_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('💾 %(message)s'))
memory_logger.addHandler(console_handler)

class EnhancedDigitalTwin:
    """Enhanced digital twin with LLM-powered answer generation"""
    
    def __init__(self):
        print("🚀 Initializing Enhanced Digital Twin with LLM Answer Generation...")
        self.setup_hybrid_system()
        self.setup_llm()
        self.conversation_history = []
        self.current_user = None
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now().isoformat()
        self.session_file = None
        print("✅ Enhanced Digital Twin with LLM ready!")
        
    def setup_hybrid_system(self):
        """Initialize hybrid memory system"""
        try:
            azure_config = {
                "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
                "search_key": os.getenv("AZURE_SEARCH_KEY"),
                "index_name": os.getenv("AZURE_SEARCH_INDEX")
            }
            
            self.hybrid_manager = HybridMemoryManager(azure_config)
            
            # Get system info
            analytics = self.hybrid_manager.get_system_analytics()
            ontology_stats = analytics['ontology_stats']
            
            print(f"   🧠 Ontology: {ontology_stats['total_concepts']} concepts loaded")
            print(f"   🤖 AI Processor: Ready for semantic analysis")
            print(f"   💾 Memory Store: Connected to Azure Search")
            
        except Exception as e:
            print(f"❌ Error initializing hybrid system: {e}")
            raise
    
    def setup_llm(self):
        """Initialize LLM for answer generation with fallback"""
        self.llm = None
        self.llm_available = False
        
        try:
            from langchain_openai import AzureChatOpenAI
            
            # Validate required environment variables
            required_vars = ["AZURE_OPENAI_DEPLOYMENT", "AZURE_OPENAI_KEY", 
                           "AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_ENDPOINT"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                print(f"⚠️ Missing Azure OpenAI config: {', '.join(missing_vars)}")
                print("   Continuing without LLM - basic memory retrieval available")
                return
            
            self.llm = AzureChatOpenAI(
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
                openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                temperature=0.3,  # Lower temperature for more consistent answers
                max_tokens=1000
            )
            self.llm_available = True
            print("   🤖 LLM initialized for answer generation")
            
        except Exception as e:
            print(f"⚠️ LLM initialization failed: {e}")
            print("   Continuing without LLM - basic memory retrieval available")
            self.llm = None
            self.llm_available = False
    
    def is_question(self, user_input: str) -> bool:
        """Enhanced question detection with better pattern recognition"""
        user_input_lower = user_input.lower().strip()
        
        # Direct question indicators
        question_starters = [
            'what', 'how', 'when', 'where', 'why', 'which', 'who',
            'do i', 'am i', 'can i', 'should i', 'will i', 'have i',
            'did i', 'was i', 'are you', 'do you know',
            'tell me about', 'what about', 'remind me', 'show me',
            'what do', 'what are', 'what is', 'how do', 'where do',
            'what can you tell me', 'what do you know about',
            'can you tell me', 'do you remember'
        ]
        
        # Check if it starts with question words
        for starter in question_starters:
            if user_input_lower.startswith(starter):
                return True
        
        # Check for question marks
        if '?' in user_input:
            return True
        
        # Check for implicit personal questions
        implicit_questions = [
            'about me', 'my name', 'my work', 'my job', 'my company',
            'my interests', 'my preferences', 'my background',
            'know about me', 'tell me', 'remind me'
        ]
        
        for pattern in implicit_questions:
            if pattern in user_input_lower:
                return True
        
        # Use LLM to detect less obvious questions if available
        if self.llm_available:
            return self.llm_question_detection(user_input)
        
        # Fallback: assume it's not a question if no clear indicators
        return False
    
    def llm_question_detection(self, user_input: str) -> bool:
        """Use LLM to detect if input is a question"""
        if not self.llm_available:
            return False
            
        try:
            prompt = f"""Determine if the following text is a question that expects an answer about the user's personal information, work, preferences, or background.

Text: "{user_input}"

Respond with only "YES" if it's a question seeking personal information, or "NO" if it's a statement or command.

Examples:
- "What's my name?" → YES
- "Tell me about my work" → YES  
- "I work at Microsoft" → NO
- "My name is John" → NO

Response:"""

            response = self.llm.invoke(prompt)
            return response.content.strip().upper() == "YES"
            
        except Exception as e:
            print(f"⚠️ LLM question detection failed, using fallback: {e}")
            return False
    
    def enhanced_memory_search(self, question: str, user_id: str, max_results: int = 15) -> List[tuple]:
        """Enhanced multi-strategy memory search with configurable limits"""
        all_memories = []
        
        # Calculate per-strategy limits based on max_results
        direct_limit = min(10, max_results // 2)
        variation_limit = min(5, max_results // 4)
        term_limit = min(3, max_results // 6)
        
        # Strategy 1: Direct question search
        try:
            memories1 = self.hybrid_manager.search_memories(
                question,
                search_options={"user_id": user_id, "limit": direct_limit}
            )
            all_memories.extend(memories1)
        except Exception as e:
            print(f"⚠️ Direct search failed: {e}")
        
        # Strategy 2: Search with user name
        try:
            memories2 = self.hybrid_manager.search_memories(
                f"{user_id} {question}",
                search_options={"user_id": user_id, "limit": direct_limit}
            )
            all_memories.extend(memories2)
        except Exception as e:
            print(f"⚠️ Name search failed: {e}")
        
        # Strategy 3: Semantic variations (limited to prevent overwhelming results)
        question_variations = self.generate_question_variations(question)[:3]  # Limit variations
        for variation in question_variations:
            try:
                memories3 = self.hybrid_manager.search_memories(
                    variation,
                    search_options={"user_id": user_id, "limit": variation_limit}
                )
                all_memories.extend(memories3)
            except Exception as e:
                continue
        
        # Strategy 4: Search for key terms (limited)
        key_terms = self.extract_key_terms(question)[:5]  # Limit key terms
        for term in key_terms:
            try:
                memories4 = self.hybrid_manager.search_memories(
                    term,
                    search_options={"user_id": user_id, "limit": term_limit}
                )
                all_memories.extend(memories4)
            except Exception as e:
                continue
        
        # Remove duplicates and rank by relevance
        return self.deduplicate_and_rank_memories(all_memories, question, max_results)
    
    def generate_question_variations(self, question: str) -> List[str]:
        """Generate semantic variations of the question"""
        variations = []
        question_lower = question.lower()
        
        # Common question mappings
        mappings = {
            "what's my name": ["name", "called", "identity"],
            "where do i work": ["work", "job", "company", "employment", "office"],
            "what do i do": ["job", "role", "work", "profession", "career"],
            "what are my interests": ["interests", "hobbies", "like", "enjoy", "preferences"],
            "tell me about myself": ["about me", "personal", "background", "profile"],
            "what's my background": ["background", "history", "experience", "education"]
        }
        
        # Add mapped terms
        for key, terms in mappings.items():
            if any(word in question_lower for word in key.split()):
                variations.extend(terms)
        
        return variations
    
    def extract_key_terms(self, question: str) -> List[str]:
        """Extract key search terms from question"""
        key_terms = []
        question_lower = question.lower()
        
        # Important terms that indicate personal information
        personal_terms = {
            "name": ["name", "called", "identity"],
            "work": ["work", "job", "company", "employment", "office", "career"],
            "interests": ["interests", "hobbies", "like", "enjoy", "preferences"],
            "background": ["background", "history", "experience", "education"],
            "skills": ["skills", "abilities", "expertise", "good at"],
            "projects": ["projects", "working on", "tasks", "assignments"],
            "meetings": ["meetings", "calls", "appointments", "schedule"],
            "goals": ["goals", "objectives", "targets", "aims"]
        }
        
        for category, terms in personal_terms.items():
            if any(term in question_lower for term in terms):
                key_terms.extend(terms)
        
        return list(set(key_terms))
    
    def deduplicate_and_rank_memories(self, memories: List[tuple], question: str, max_results: int = 15) -> List[tuple]:
        """Remove duplicates and rank memories by relevance with configurable limit"""
        seen_ids = set()
        unique_memories = []
        
        for memory, score in memories:
            if memory.id not in seen_ids:
                seen_ids.add(memory.id)
                # Boost score for memories with personal information
                if self.contains_personal_info(memory.content):
                    score *= 1.5
                unique_memories.append((memory, score))
        
        # Sort by score (highest first)
        unique_memories.sort(key=lambda x: x[1], reverse=True)
        return unique_memories[:max_results]
    
    def contains_personal_info(self, content: str) -> bool:
        """Check if memory contains personal information rather than generic activity"""
        content_lower = content.lower()
        
        # Indicators of personal information
        personal_indicators = [
            "my name", "i am", "i work", "my job", "my company",
            "my role", "i like", "i enjoy", "my interests", "my background",
            "i have", "my experience", "i can", "my skills"
        ]
        
        # Indicators of generic activity (lower priority)
        generic_indicators = [
            "performed", "activity related to", "browsing", "navigation",
            "tab_switch", "window focus", "clicked", "scrolled"
        ]
        
        personal_score = sum(1 for indicator in personal_indicators if indicator in content_lower)
        generic_score = sum(1 for indicator in generic_indicators if indicator in content_lower)
        
        return personal_score > generic_score
    
    def answer_from_memory_with_llm(self, question: str, user_id: str) -> Optional[str]:
        """Generate intelligent answers using LLM + relevant memories with fallback"""
        
        try:
            # Get relevant memories using enhanced search
            relevant_memories = self.enhanced_memory_search(question, user_id)
            
            if not relevant_memories:
                return None
            
            # If LLM is available, use it for intelligent answers
            if self.llm_available:
                # Prepare memory content for LLM
                memory_context = self.prepare_memory_context(relevant_memories, question)
                
                # Generate answer using LLM
                answer = self.generate_llm_answer(question, memory_context, user_id)
                return answer
            else:
                # Fallback: return basic memory content
                return self.generate_basic_answer(relevant_memories, question)
            
        except Exception as e:
            print(f"⚠️ Error generating answer, trying fallback: {e}")
            # Try basic answer generation as fallback
            try:
                relevant_memories = self.enhanced_memory_search(question, user_id)
                if relevant_memories:
                    return self.generate_basic_answer(relevant_memories, question)
            except Exception:
                pass
            return None
    
    def prepare_memory_context(self, memories: List[tuple], question: str) -> str:
        """Prepare memory content for LLM processing"""
        context_parts = []
        
        for i, (memory, score) in enumerate(memories[:10], 1):  # Top 10 memories
            # Create a clean context entry
            context_entry = f"Memory {i} (relevance: {score:.2f}):\n"
            context_entry += f"Content: {memory.content}\n"
            
            if memory.semantic_summary and memory.semantic_summary != memory.content:
                context_entry += f"Summary: {memory.semantic_summary}\n"
            
            if memory.ontology_domain:
                context_entry += f"Category: {memory.ontology_domain}\n"
            
            context_entry += f"Timestamp: {memory.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
            context_parts.append(context_entry)
        
        return "\n---\n".join(context_parts)
    
    def generate_basic_answer(self, memories: List[tuple], question: str) -> str:
        """Generate basic answer without LLM when it's unavailable"""
        if not memories:
            return "No relevant memories found."
        
        # Get the most relevant memory
        best_memory, best_score = memories[0]
        
        # Simple answer based on memory content
        if best_score > 0.7:
            return f"Based on my memories: {best_memory.semantic_summary or best_memory.content}"
        elif best_score > 0.4:
            return f"I found some related information: {best_memory.semantic_summary or best_memory.content}"
        else:
            # Show multiple memories if individual scores are low
            relevant_content = []
            for memory, score in memories[:3]:
                if score > 0.2:
                    relevant_content.append(memory.semantic_summary or memory.content)
            
            if relevant_content:
                return "Here's what I found in your memories: " + "; ".join(relevant_content)
            else:
                return "I found some memories but they don't seem directly relevant to your question."
    
    def generate_llm_answer(self, question: str, memory_context: str, user_id: str) -> str:
        """Use LLM to generate intelligent answer from memories"""
        if not self.llm_available:
            return "LLM not available for answer generation."
        
        # Basic input sanitization
        sanitized_question = self.sanitize_input(question)
        sanitized_user_id = self.sanitize_input(user_id)
        
        prompt = f"""You are an AI assistant helping a user named {sanitized_user_id} access their personal digital memory system. Based on the memories provided below, answer the user's question accurately and naturally.

IMPORTANT GUIDELINES:
1. Answer as if you're helping {sanitized_user_id} remember their own information
2. Be specific and factual - use exact details from the memories
3. If information is found in multiple memories, synthesize them coherently
4. If information is not found in the memories, say "I don't have that information in your memories yet"
5. Speak naturally and conversationally
6. Focus on personal facts, not generic behavioral data

USER'S QUESTION:
{sanitized_question}

RELEVANT MEMORIES:
{memory_context}

Please provide a helpful, accurate answer based on these memories. If you find relevant information, be specific about what you know. If the memories don't contain the requested information, be honest about that.

ANSWER:"""

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            print(f"⚠️ LLM answer generation failed: {e}")
            return "I encountered an error while processing your question. Please try again."
    
    def sanitize_input(self, user_input: str) -> str:
        """Basic input sanitization to prevent prompt injection"""
        if not user_input:
            return ""
        
        # Remove or escape potentially problematic characters/patterns
        sanitized = user_input.strip()
        
        # Remove excessive whitespace and newlines
        import re
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Limit length to prevent token overflow
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        # Remove potential prompt injection patterns
        dangerous_patterns = [
            r'ignore previous instructions',
            r'system:',
            r'assistant:',
            r'user:',
            r'<\|.*?\|>',  # Special tokens
        ]
        
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def save_session(self):
        """Save current session to file"""
        if not self.current_user or not self.conversation_history:
            return
        
        try:
            import json
            from pathlib import Path
            session_data = {
                "session_id": self.session_id,
                "user_id": self.current_user,
                "session_start": self.session_start,
                "last_updated": datetime.now().isoformat(),
                "conversation_history": self.conversation_history
            }
            
            # Create sessions directory if it doesn't exist
            sessions_dir = Path("sessions")
            sessions_dir.mkdir(exist_ok=True)
            
            session_filename = f"{self.current_user}_session_{self.session_id[:8]}.json"
            self.session_file = sessions_dir / session_filename
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Could not save session: {e}")
    
    def load_recent_session(self, user_id: str) -> bool:
        """Load the most recent session for a user"""
        try:
            import json
            from pathlib import Path
            
            sessions_dir = Path("sessions")
            if not sessions_dir.exists():
                return False
            
            # Find most recent session file for this user
            user_sessions = list(sessions_dir.glob(f"{user_id}_session_*.json"))
            if not user_sessions:
                return False
            
            # Sort by modification time and get the most recent
            latest_session = max(user_sessions, key=lambda x: x.stat().st_mtime)
            
            with open(latest_session, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.session_id = session_data.get("session_id", str(uuid.uuid4()))
            self.session_start = session_data.get("session_start", datetime.now().isoformat())
            self.conversation_history = session_data.get("conversation_history", [])
            self.session_file = latest_session
            
            print(f"📂 Loaded previous session with {len(self.conversation_history)} exchanges")
            return True
            
        except Exception as e:
            print(f"⚠️ Could not load previous session: {e}")
            return False
    
    def process_user_input(self, user_input: str, user_id: str = None) -> str:
        """Process user input with enhanced LLM-powered question answering"""
        
        if not user_id:
            user_id = self.current_user or "default_user"
        
        user_context = {
            "user_id": user_id,
            "tenant_id": "default_tenant",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Enhanced question detection
            if self.is_question(user_input):
                # Try to answer from memory using LLM
                memory_answer = self.answer_from_memory_with_llm(user_input, user_id)
                
                if memory_answer:
                    # Store successful Q&A interaction
                    self.conversation_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "user": user_input,
                        "assistant": memory_answer,
                        "type": "llm_memory_retrieval",
                        "success": True
                    })
                    return memory_answer
                else:
                    # No relevant memories found
                    fallback_response = self.generate_fallback_response(user_input, user_id)
                    self.conversation_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "user": user_input,
                        "assistant": fallback_response,
                        "type": "no_memory_found"
                    })
                    return fallback_response
            
            # Not a question - process and store as new memory
            memory, report = self.hybrid_manager.process_and_store_memory(
                user_input, user_context
            )
            
            # Generate intelligent response
            response = self.generate_intelligent_response(user_input, memory, report, user_context)
            
            # Store conversation
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": user_input,
                "assistant": response,
                "memory_id": memory.id,
                "type": "memory_storage",
                "processing_report": {
                    "success": report['success'],
                    "ontology_domain": report.get('ontology_domain'),
                    "ai_confidence": report.get('ai_confidence', 0),
                    "hybrid_confidence": report.get('hybrid_confidence', 0),
                    "importance_score": report.get('importance_score', 0),
                    "processing_time": report.get('processing_time_seconds', 0)
                }
            })
            
            # Auto-save session after each interaction
            self.save_session()
            
            return response
            
        except Exception as e:
            error_response = f"I encountered an error processing your message: {str(e)[:100]}. Please try again."
            
            # Store error in conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": user_input,
                "assistant": error_response,
                "type": "error",
                "error": str(e)
            })
            
            return error_response
    
    def generate_fallback_response(self, question: str, user_id: str) -> str:
        """Generate fallback response when no memories are found"""
        try:
            # Get user's memory profile to provide context
            profile = self.hybrid_manager.get_user_memory_profile(user_id)
            
            if profile['total_memories'] == 0:
                return "I don't have any memories stored yet. Start by telling me about yourself, and I'll remember it for future questions."
            else:
                return f"I couldn't find specific information to answer '{question}' in your {profile['total_memories']} stored memories. Could you share that information with me so I can remember it for next time?"
                
        except Exception as e:
            return "I don't have enough information to answer that question yet. Could you tell me more about yourself?"
    
    def generate_intelligent_response(self, user_input: str, memory, report: Dict, user_context: Dict) -> str:
        """Generate intelligent response using hybrid understanding"""
        
        try:
            # Get user's memory profile for context
            profile = self.hybrid_manager.get_user_memory_profile(user_context["user_id"])
            
            # Search for relevant memories
            relevant_memories = self.hybrid_manager.search_memories(
                user_input,
                search_options={"user_id": user_context["user_id"], "limit": 3}
            )
            
            # Build response components
            response_parts = []
            
            # Acknowledge processing
            if report.get("success"):
                response_parts.append("I've learned and stored this information.")
            else:
                response_parts.append("I've noted your message.")
            
            # Add ontology understanding
            ontology_domain = report.get('ontology_domain')
            if ontology_domain:
                domain_responses = {
                    "personal": "I understand this is personal information about you.",
                    "work": "I see this relates to your work and professional life.",
                    "health": "I've noted this health-related information securely.",
                    "family": "I understand this concerns your family.",
                    "finance": "I've recorded this financial information.",
                    "education": "I see this is about learning or education.",
                    "travel": "I've noted this travel-related information.",
                    "hobbies": "I understand this relates to your interests and hobbies."
                }
                
                domain_response = domain_responses.get(ontology_domain, f"I've classified this under {ontology_domain}.")
                response_parts.append(domain_response)
            
            # Add semantic summary if available
            semantic_summary = report.get('semantic_summary')
            if semantic_summary and semantic_summary != "General information":
                response_parts.append(f"In essence: {semantic_summary}")
            
            # Add context about memory building
            if profile['total_memories'] > 0:
                if profile['total_memories'] < 10:
                    response_parts.append(f"I now have {profile['total_memories']} memories about you and am learning more with each conversation.")
                else:
                    response_parts.append(f"This adds to the {profile['total_memories']} memories I have about you.")
            
            return " ".join(response_parts)
            
        except Exception as e:
            # Fallback response if generation fails
            return f"I've processed your message. {report.get('semantic_summary', 'Thank you for sharing.')}"
    
    def search_user_memories(self, query: str, user_id: str = None, limit: int = 5) -> List[str]:
        """Search user's memories and return formatted results with pagination"""
        
        if not user_id:
            user_id = self.current_user or "default_user"
        
        try:
            # Use enhanced search with appropriate limits
            search_limit = min(limit * 3, 50)  # Search more than needed for better filtering
            results = self.enhanced_memory_search(query, user_id, max_results=search_limit)
            
            if not results:
                return ["No memories found matching your search."]
            
            formatted_results = []
            # Show only the requested number of results
            for i, (memory, score) in enumerate(results[:limit], 1):
                # Format memory information
                time_ago = self._get_time_ago(memory.timestamp)
                domain_info = f" ({memory.ontology_domain})" if memory.ontology_domain else ""
                
                result = f"{i}. {memory.semantic_summary}{domain_info}"
                result += f"\n   Relevance: {score:.2f} | {time_ago}"
                
                if memory.ai_semantic_tags:
                    tags = ", ".join(memory.ai_semantic_tags[:3])
                    result += f" | Tags: {tags}"
                
                formatted_results.append(result)
            
            # Add pagination info if there are more results
            if len(results) > limit:
                formatted_results.append(f"\n... and {len(results) - limit} more results available")
            
            return formatted_results
            
        except Exception as e:
            return [f"Error searching memories: {str(e)}"]
    
    def get_user_profile_summary(self, user_id: str = None) -> str:
        """Get formatted user profile summary"""
        
        if not user_id:
            user_id = self.current_user or "default_user"
        
        try:
            profile = self.hybrid_manager.get_user_memory_profile(user_id)
            
            if profile['total_memories'] == 0:
                return "No memories stored yet. Start by telling me about yourself!"
            
            summary_parts = [
                f"📊 Memory Profile for {user_id}:",
                f"   Total memories: {profile['total_memories']}",
                f"   Average importance: {profile['average_importance']:.2f}/1.0"
            ]
            
            if profile['recent_activity'] > 0:
                summary_parts.append(f"   Recent activity: {profile['recent_activity']} memories in last 7 days")
            
            if profile['domain_distribution']:
                summary_parts.append("   📁 Memory domains:")
                for domain, count in sorted(profile['domain_distribution'].items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / profile['total_memories']) * 100
                    summary_parts.append(f"      {domain}: {count} ({percentage:.1f}%)")
            
            if profile['top_semantic_tags']:
                summary_parts.append("   🏷️ Top topics:")
                for tag, count in profile['top_semantic_tags'][:5]:
                    summary_parts.append(f"      {tag}: {count} mentions")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"Error getting profile: {str(e)}"
    
    def get_system_status(self) -> str:
        """Get system status and analytics"""
        
        try:
            analytics = self.hybrid_manager.get_system_analytics()
            
            perf = analytics['performance_metrics']
            onto_stats = analytics['ontology_stats']
            
            status_parts = [
                "🔧 System Status:",
                f"   Total processed: {perf['total_processed']} memories",
                f"   Hybrid success rate: {perf['hybrid_success_rate']:.1%}",
                f"   Average confidence: {perf['average_confidence']:.2f}",
                f"   Average processing time: {perf['average_processing_time']:.2f}s",
                "",
                "🧠 Ontology Status:",
                f"   Available concepts: {onto_stats['total_concepts']}",
                f"   Domains: {len(onto_stats['domains'])}",
                f"   Active relationships: {onto_stats['total_relationships']}",
                "",
                f"🤖 LLM Answer Generation: {'Enabled' if self.llm_available else 'Disabled (using fallback)'}",
                f"🛡️ Input Sanitization: Enabled",
                f"📄 Memory Pagination: Enabled"
            ]
            
            # Add recommendations
            recommendations = analytics['system_health']['recommended_actions']
            if recommendations and recommendations != ["System operating optimally"]:
                status_parts.extend(["", "💡 Recommendations:"])
                for rec in recommendations:
                    status_parts.append(f"   • {rec}")
            else:
                status_parts.append("   ✅ System operating optimally")
            
            return "\n".join(status_parts)
            
        except Exception as e:
            return f"Error getting system status: {str(e)}"
    
    def _get_time_ago(self, timestamp: datetime) -> str:
        """Get human-readable time ago string"""
        
        try:
            now = datetime.now()
            if timestamp.tzinfo is not None:
                # Remove timezone info for comparison
                timestamp = timestamp.replace(tzinfo=None)
            
            diff = now - timestamp
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "just now"
                
        except Exception:
            return "recently"
    
    def run_interactive_session(self):
        """Run enhanced interactive session with LLM-powered answers"""
        
        print("\n" + "="*60)
        print("🚀 Enhanced Digital Twin - LLM-Powered Answer Generation")
        print("="*60)
        print("Features:")
        print("  • Ontology-based structured understanding")
        print("  • AI-powered semantic analysis")
        print("  • LLM-powered question answering")
        print("  • Multi-strategy memory search")
        print("  • Intelligent answer synthesis")
        print("  • Real-time system analytics")
        print("\nCommands:")
        print("  • Ask questions naturally - I'll find answers in your memories")
        print("  • Tell me facts - I'll learn and remember them")
        print("  • 'search <query>' - Search your memories")
        print("  • 'profile' - View your memory profile")
        print("  • 'status' - System status and analytics") 
        print("  • 'history' - Recent conversation history")
        print("  • 'help' - Show all commands")
        print("  • 'exit' - End session")
        print("="*60)
        
        # Get user ID
        user_id = input("\n👤 Enter your user ID (or press Enter for default): ").strip()
        if not user_id:
            user_id = "default_user"
        
        self.current_user = user_id
        
        # Try to load previous session
        session_loaded = self.load_recent_session(user_id)
        
        print(f"✅ Session started for user: {user_id}")
        print(f"🔗 Session ID: {self.session_id[:8]}...")
        
        # Show user's existing profile if available
        try:
            profile = self.hybrid_manager.get_user_memory_profile(user_id)
            if profile['total_memories'] > 0:
                print(f"📚 Welcome back! I have {profile['total_memories']} memories about you.")
                if session_loaded:
                    print("💾 Previous conversation session restored.")
                print("💡 Try asking: 'What's my name?' or 'Where do I work?' or 'What do you know about me?'")
            else:
                print("👋 Nice to meet you! Start by telling me about yourself.")
        except Exception:
            print("👋 Ready to learn about you!")
        
        print("\n" + "-"*60)
        
        while True:
            try:
                user_input = input(f"\n{user_id}: ").strip()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    self.save_session()  # Final save before exit
                    print("\n👋 Session ended. All memories preserved with LLM intelligence.")
                    print(f"💾 Processed {len(self.conversation_history)} exchanges this session.")
                    if self.session_file:
                        print(f"📂 Session saved to: {self.session_file.name}")
                    break
                
                elif user_input.lower() == "help":
                    print("\n📖 Available Commands:")
                    print("  Questions & Learning:")
                    print("    • Ask any question about yourself - I'll search your memories")
                    print("    • Tell me facts about yourself - I'll learn and remember")
                    print("    • Examples: 'What's my name?', 'Where do I work?', 'What are my interests?'")
                    print("  Memory Management:")
                    print("    • 'search <query>' - Search your memories semantically")
                    print("    • 'profile' - View complete memory profile")
                    print("    • 'status' - System analytics and performance")
                    print("  Session:")
                    print("    • 'history' - Recent conversation history")
                    print("    • 'clear' - Clear conversation history")
                    print("  System:")
                    print("    • 'help' - Show this help")
                    print("    • 'exit' - End session")
                    continue
                
                elif user_input.lower() == "profile":
                    profile_summary = self.get_user_profile_summary(user_id)
                    print(f"\n{profile_summary}")
                    continue
                
                elif user_input.lower() == "status":
                    status = self.get_system_status()
                    print(f"\n{status}")
                    continue
                
                elif user_input.lower().startswith("search "):
                    query = user_input[7:].strip()
                    if query:
                        print(f"\n🔍 Searching for: '{query}'")
                        search_results = self.search_user_memories(query, user_id)
                        for result in search_results:
                            print(f"   {result}")
                    else:
                        print("Please provide a search query after 'search'")
                    continue
                
                elif user_input.lower() == "history":
                    print(f"\n📜 Conversation History ({len(self.conversation_history)} exchanges):")
                    for i, exchange in enumerate(self.conversation_history[-5:], 1):
                        timestamp = datetime.fromisoformat(exchange['timestamp']).strftime("%H:%M")
                        user_msg = exchange['user'][:50] + "..." if len(exchange['user']) > 50 else exchange['user']
                        print(f"   {i}. [{timestamp}] You: {user_msg}")
                        
                        exchange_type = exchange.get('type', 'unknown')
                        if exchange_type == 'llm_memory_retrieval':
                            print(f"      Assistant: {exchange['assistant'][:100]}...")
                            print(f"      Type: LLM Answer from Memory")
                        elif exchange_type == 'memory_storage':
                            report = exchange.get('processing_report', {})
                            print(f"      Assistant: Learned and stored information")
                            print(f"      Domain: {report.get('ontology_domain', 'general')}, "
                                  f"Confidence: {report.get('ai_confidence', 0):.2f}")
                        elif exchange_type == 'no_memory_found':
                            print(f"      Assistant: No relevant memories found")
                        else:
                            print(f"      Assistant: {exchange['assistant'][:80]}...")
                    continue
                
                elif user_input.lower() == "clear":
                    self.conversation_history = []
                    print("🗑️ Conversation history cleared.")
                    continue
                
                elif user_input.lower() == "test":
                    # Hidden test command for debugging
                    self.run_test_questions(user_id)
                    continue
                
                elif not user_input:
                    continue
                
                # Process the input with enhanced LLM-powered intelligence
                print(f"\n🧠 Processing with LLM-powered intelligence...")
                response = self.process_user_input(user_input, user_id)
                print(f"\nAssistant: {response}")
                
                # Show processing stats for this exchange
                if self.conversation_history:
                    last_exchange = self.conversation_history[-1]
                    exchange_type = last_exchange.get('type', 'unknown')
                    
                    if exchange_type == 'llm_memory_retrieval':
                        print(f"\n💡 Retrieved from memory using LLM synthesis")
                    elif exchange_type == 'memory_storage':
                        if 'processing_report' in last_exchange:
                            report = last_exchange['processing_report']
                            print(f"💡 Stored: {report['processing_time']:.2f}s | "
                                  f"Domain: {report.get('ontology_domain', 'general')} | "
                                  f"Confidence: {report.get('ai_confidence', 0):.2f}")
                    elif exchange_type == 'no_memory_found':
                        print(f"💡 No relevant memories found - ready to learn new information")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Memories preserved.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'help' for assistance.")
    
    def run_test_questions(self, user_id: str):
        """Hidden test function to verify LLM answer generation"""
        print(f"\n🧪 Testing LLM Answer Generation for {user_id}")
        print("=" * 50)
        
        test_questions = [
            "What's my name?",
            "Where do I work?", 
            "What's my job?",
            "What are my interests?",
            "What do you know about me?",
            "Tell me about my background",
            "What company do I work for?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Testing: '{question}'")
            try:
                answer = self.answer_from_memory_with_llm(question, user_id)
                if answer:
                    print(f"   ✅ Answer: {answer}")
                else:
                    print(f"   ❌ No answer generated")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n🧪 Test complete")
    
    def analyze_memory_coverage(self, user_id: str) -> Dict[str, Any]:
        """Analyze what types of questions the system can answer"""
        
        try:
            # Get user's memory profile
            profile = self.hybrid_manager.get_user_memory_profile(user_id)
            
            # Test key question categories
            question_categories = {
                "identity": ["What's my name?", "What am I called?"],
                "work": ["Where do I work?", "What's my job?", "What company do I work for?"],
                "interests": ["What are my interests?", "What do I like?"],
                "background": ["What's my background?", "What's my experience?"],
                "skills": ["What are my skills?", "What am I good at?"]
            }
            
            coverage_analysis = {
                "total_memories": profile.get('total_memories', 0),
                "personal_info_coverage": {},
                "answer_readiness": profile.get('answer_readiness_score', 0.0),
                "recommendations": []
            }
            
            for category, questions in question_categories.items():
                test_question = questions[0]
                try:
                    # Test if we can find relevant memories
                    relevant_memories = self.enhanced_memory_search(test_question, user_id)
                    
                    if relevant_memories and len(relevant_memories) > 0:
                        top_score = relevant_memories[0][1] if relevant_memories else 0
                        coverage_analysis["personal_info_coverage"][category] = {
                            "covered": top_score > 0.3,
                            "confidence": top_score,
                            "memory_count": len([m for m, s in relevant_memories if s > 0.2])
                        }
                    else:
                        coverage_analysis["personal_info_coverage"][category] = {
                            "covered": False,
                            "confidence": 0.0,
                            "memory_count": 0
                        }
                except Exception:
                    coverage_analysis["personal_info_coverage"][category] = {
                        "covered": False,
                        "confidence": 0.0,
                        "memory_count": 0
                    }
            
            # Generate recommendations
            uncovered_categories = [cat for cat, info in coverage_analysis["personal_info_coverage"].items() 
                                  if not info["covered"]]
            
            if uncovered_categories:
                coverage_analysis["recommendations"].append(
                    f"Consider sharing information about: {', '.join(uncovered_categories)}"
                )
            
            if coverage_analysis["total_memories"] < 50:
                coverage_analysis["recommendations"].append(
                    "Continue using the system to build more comprehensive memories"
                )
            
            return coverage_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing memory coverage: {e}")
            return {"error": str(e)}
    
    def export_conversation_data(self, user_id: str) -> Dict[str, Any]:
        """Export conversation and memory data for analysis"""
        
        try:
            # Get conversation history
            conversation_data = {
                "session_id": self.session_id,
                "user_id": user_id,
                "session_start": self.session_start,
                "total_exchanges": len(self.conversation_history),
                "conversation_history": self.conversation_history,
                "export_timestamp": datetime.now().isoformat()
            }
            
            # Get memory statistics
            try:
                profile = self.hybrid_manager.get_user_memory_profile(user_id)
                conversation_data["memory_profile"] = profile
            except Exception:
                conversation_data["memory_profile"] = "Error retrieving profile"
            
            # Get system analytics
            try:
                analytics = self.hybrid_manager.get_system_analytics()
                conversation_data["system_analytics"] = analytics
            except Exception:
                conversation_data["system_analytics"] = "Error retrieving analytics"
            
            # Analyze question answering performance
            qa_performance = {
                "questions_asked": len([ex for ex in self.conversation_history if ex.get('type') == 'llm_memory_retrieval']),
                "questions_answered": len([ex for ex in self.conversation_history 
                                         if ex.get('type') == 'llm_memory_retrieval' and ex.get('success', False)]),
                "memories_stored": len([ex for ex in self.conversation_history if ex.get('type') == 'memory_storage']),
                "no_memory_responses": len([ex for ex in self.conversation_history if ex.get('type') == 'no_memory_found'])
            }
            conversation_data["qa_performance"] = qa_performance
            
            return conversation_data
            
        except Exception as e:
            return {"error": f"Export failed: {str(e)}"}

def main():
    """Main function to run enhanced digital twin"""
    
    try:
        enhanced_twin = EnhancedDigitalTwin()
        enhanced_twin.run_interactive_session()
        
    except KeyboardInterrupt:
        print("\n👋 Startup interrupted.")
    except Exception as e:
        print(f"❌ Failed to initialize Enhanced Digital Twin: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has all required Azure credentials")
        print("2. Ensure Azure Search index exists and has data")
        print("3. Verify Azure OpenAI deployment is accessible")
        print("4. Check internet connection for Azure services")
        print("5. Run 'python memory_inspector.py' to verify memory data")

if __name__ == "__main__":
    main()