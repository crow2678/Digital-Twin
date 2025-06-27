import os
import uuid
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

class MemoryType(Enum):
    USER_IDENTITY = "user_identity"
    USER_PREFERENCE = "user_preference"
    USER_STATUS = "user_status"
    USER_CONTEXT = "user_context"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    COMMUNICATION_STYLE = "communication_style"
    WORK_PATTERN = "work_pattern"
    CONVERSATION_CONTEXT = "conversation_context"

class ConfidenceLevel(Enum):
    CRITICAL = 0.9  # User explicitly stated
    HIGH = 0.8      # Strong inference
    MEDIUM = 0.6    # Moderate inference
    LOW = 0.4       # Weak inference

@dataclass
class MemoryRecord:
    id: str
    memory_type: MemoryType
    content: str
    extracted_value: str
    confidence: float
    timestamp: datetime
    source: str
    version: int = 1
    is_active: bool = True
    context: Optional[str] = None
    metadata: Optional[Dict] = None
    expiry_date: Optional[datetime] = None
    
    def to_dict(self):
        data = {
            'id': self.id,
            'memory_type': self.memory_type.value,
            'content': self.content,
            'extracted_value': self.extracted_value,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'version': self.version,
            'is_active': self.is_active,
            'context': self.context,
            'metadata': self.metadata or {},
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None
        }
        return data
    
    @classmethod
    def from_dict(cls, data):
        # Handle missing or None values safely
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid data for MemoryRecord")
            
        # Required fields check
        required_fields = ['id', 'memory_type', 'extracted_value', 'confidence', 'timestamp', 'source']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        # Safe field extraction with defaults
        memory_data = {
            'id': data['id'],
            'memory_type': MemoryType(data['memory_type']),
            'content': data.get('content', ''),
            'extracted_value': data['extracted_value'],
            'confidence': float(data['confidence']),
            'timestamp': datetime.fromisoformat(data['timestamp']),
            'source': data['source'],
            'version': data.get('version', 1),
            'is_active': data.get('is_active', True),
            'context': data.get('context'),
            'metadata': data.get('metadata') or {},
            'expiry_date': datetime.fromisoformat(data['expiry_date']) if data.get('expiry_date') else None
        }
        
        return cls(**memory_data)

class MemoryManager:
    def __init__(self, vector_store: AzureSearch):
        self.vector_store = vector_store
        self.active_memories: Dict[str, MemoryRecord] = {}
        self.session_cache: Dict[MemoryType, MemoryRecord] = {}
        
    def create_memory(self, memory_type: MemoryType, content: str, extracted_value: str, 
                     confidence: float, source: str, context: str = None, 
                     expiry_hours: int = None) -> MemoryRecord:
        """Create a new memory record"""
        
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now()
        expiry_date = timestamp + timedelta(hours=expiry_hours) if expiry_hours else None
        
        memory = MemoryRecord(
            id=memory_id,
            memory_type=memory_type,
            content=content,
            extracted_value=extracted_value,
            confidence=confidence,
            timestamp=timestamp,
            source=source,
            context=context,
            expiry_date=expiry_date
        )
        
        return memory
    
    def store_memory(self, memory: MemoryRecord) -> bool:
        """Store memory with conflict resolution"""
        
        # Check for conflicts with existing memories
        conflicting_memories = self.find_conflicting_memories(memory)
        
        if conflicting_memories:
            # Resolve conflicts based on confidence and recency
            resolution = self.resolve_conflicts(memory, conflicting_memories)
            if resolution == "reject":
                print(f"Memory rejected due to lower confidence: {memory.content}")
                return False
            elif resolution == "update":
                # Deactivate old memories
                for old_memory in conflicting_memories:
                    old_memory.is_active = False
                    self.update_vector_store(old_memory)
        
        # Store in session cache for immediate access
        self.session_cache[memory.memory_type] = memory
        self.active_memories[memory.id] = memory
        
        # Store in vector database
        return self.save_to_vector_store(memory)
    
    def find_conflicting_memories(self, new_memory: MemoryRecord) -> List[MemoryRecord]:
        """Find memories that conflict with the new memory"""
        
        conflicts = []
        
        # Check session cache first
        if new_memory.memory_type in self.session_cache:
            existing = self.session_cache[new_memory.memory_type]
            if existing.extracted_value.lower() != new_memory.extracted_value.lower():
                conflicts.append(existing)
        
        # Check vector store for conflicts
        try:
            search_query = f"user {new_memory.memory_type.value}"
            docs = self.vector_store.similarity_search(search_query, k=10)
            
            for doc in docs:
                if (doc.metadata and 
                    doc.metadata.get('memory_type') == new_memory.memory_type.value and
                    doc.metadata.get('is_active', True) and
                    doc.metadata.get('extracted_value', '').lower() != new_memory.extracted_value.lower()):
                    
                    try:
                        # Safely reconstruct memory record
                        memory_data = doc.metadata.copy()
                        memory_data['content'] = doc.page_content
                        
                        # Validate before reconstruction
                        if self.validate_memory_data(memory_data):
                            memory_record = MemoryRecord.from_dict(memory_data)
                            conflicts.append(memory_record)
                    except Exception as e:
                        print(f"Skipping malformed conflict record: {e}")
                        continue
                    
        except Exception as e:
            print(f"Error checking for conflicts: {e}")
        
        return conflicts
    
    def validate_memory_data(self, data: dict) -> bool:
        """Validate memory data before reconstruction"""
        required_fields = ['id', 'memory_type', 'extracted_value', 'confidence', 'timestamp', 'source']
        return all(field in data and data[field] is not None for field in required_fields)
    
    def resolve_conflicts(self, new_memory: MemoryRecord, conflicts: List[MemoryRecord]) -> str:
        """Resolve conflicts between memories"""
        
        for conflict in conflicts:
            # Confidence-based resolution
            if new_memory.confidence > conflict.confidence + 0.1:
                continue  # New memory wins
            elif conflict.confidence > new_memory.confidence + 0.1:
                return "reject"  # Existing memory wins
            
            # Recency-based resolution for similar confidence
            if new_memory.timestamp > conflict.timestamp:
                continue  # New memory wins
            else:
                return "reject"  # Existing memory wins
        
        return "update"  # Update existing memories
    
    def save_to_vector_store(self, memory: MemoryRecord) -> bool:
        """Save memory to vector store"""
        
        try:
            doc = Document(
                page_content=memory.content,
                metadata=memory.to_dict()
            )
            
            self.vector_store.add_documents([doc])
            return True
            
        except Exception as e:
            print(f"Failed to save memory to vector store: {e}")
            return False
    
    def update_vector_store(self, memory: MemoryRecord):
        """Update memory in vector store (mark as inactive)"""
        
        try:
            # Note: This is a simplified approach. In production, you'd want
            # a more sophisticated update mechanism
            memory.is_active = False
            doc = Document(
                page_content=f"INACTIVE: {memory.content}",
                metadata=memory.to_dict()
            )
            self.vector_store.add_documents([doc])
            
        except Exception as e:
            print(f"Failed to update memory: {e}")
    
    def retrieve_memories(self, query: str, memory_types: List[MemoryType] = None, 
                         limit: int = 5) -> List[MemoryRecord]:
        """Retrieve relevant memories with priority ranking"""
        
        memories = []
        
        # First check session cache for immediate context
        if memory_types:
            for mem_type in memory_types:
                if mem_type in self.session_cache:
                    memories.append(self.session_cache[mem_type])
        else:
            # Add all session cache if no specific types requested
            memories.extend(self.session_cache.values())
        
        # Then search vector store
        try:
            search_query = f"user {query}" if not query.startswith("user") else query
            docs = self.vector_store.similarity_search(search_query, k=limit * 3)
            
            for doc in docs:
                if (doc.metadata and 
                    doc.metadata.get('is_active', True) and
                    not doc.page_content.startswith("INACTIVE:") and
                    self.validate_memory_data(doc.metadata)):
                    
                    try:
                        # Safely reconstruct memory record
                        memory_data = doc.metadata.copy()
                        memory_data['content'] = doc.page_content
                        
                        memory_record = MemoryRecord.from_dict(memory_data)
                        
                        # Avoid duplicates from session cache
                        if memory_record.id not in [m.id for m in memories]:
                            memories.append(memory_record)
                            
                    except Exception as inner_e:
                        print(f"Skipping malformed memory record: {inner_e}")
                        continue
                        
        except Exception as e:
            print(f"Error retrieving memories: {e}")
        
        # Sort by confidence and recency, prioritize session cache
        def sort_key(memory):
            is_session = memory.id in [m.id for m in self.session_cache.values()]
            return (is_session, memory.confidence, memory.timestamp)
        
        memories.sort(key=sort_key, reverse=True)
        
        return memories[:limit]
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get current user profile from active memories with session priority"""
        
        profile = {}
        
        user_memory_types = [
            MemoryType.USER_IDENTITY,
            MemoryType.USER_PREFERENCE,
            MemoryType.USER_STATUS,
            MemoryType.USER_CONTEXT
        ]
        
        # First add session cache (highest priority)
        for mem_type in user_memory_types:
            if mem_type in self.session_cache:
                memory = self.session_cache[mem_type]
                profile[mem_type.value] = {
                    'value': memory.extracted_value,
                    'content': memory.content,
                    'confidence': memory.confidence,
                    'timestamp': memory.timestamp.isoformat(),
                    'source': 'session'
                }
        
        # Then add from vector store if not in session cache
        try:
            for mem_type in user_memory_types:
                if mem_type.value not in profile:
                    search_query = f"user {mem_type.value}"
                    docs = self.vector_store.similarity_search(search_query, k=3)
                    
                    for doc in docs:
                        if (doc.metadata and 
                            doc.metadata.get('memory_type') == mem_type.value and
                            doc.metadata.get('is_active', True) and
                            self.validate_memory_data(doc.metadata)):
                            
                            try:
                                memory_data = doc.metadata.copy()
                                memory_record = MemoryRecord.from_dict(memory_data)
                                
                                profile[mem_type.value] = {
                                    'value': memory_record.extracted_value,
                                    'content': memory_record.content,
                                    'confidence': memory_record.confidence,
                                    'timestamp': memory_record.timestamp.isoformat(),
                                    'source': 'stored'
                                }
                                break  # Take the first valid one
                                
                            except Exception as e:
                                print(f"Error reconstructing profile memory: {e}")
                                continue
                                
        except Exception as e:
            print(f"Error building profile from stored memories: {e}")
        
        return profile
    
    def cleanup_expired_memories(self):
        """Remove expired memories"""
        
        current_time = datetime.now()
        expired_ids = []
        
        for memory_id, memory in self.active_memories.items():
            if memory.expiry_date and current_time > memory.expiry_date:
                memory.is_active = False
                expired_ids.append(memory_id)
        
        for memory_id in expired_ids:
            del self.active_memories[memory_id]
            
        print(f"Cleaned up {len(expired_ids)} expired memories")

class InformationExtractor:
    """Handles extraction and validation of information from user input"""
    
    def __init__(self):
        self.extraction_patterns = {
            MemoryType.USER_IDENTITY: [
                (r"(?:my (?:preferred )?name is|call me|i am|i'm called|refer to me as|address me as)\s+([A-Za-z][A-Za-z\s]{1,30})(?:\s*\.|\s*$|,)", ConfidenceLevel.CRITICAL),
                (r"(?:change my name to|update my name to)\s+([A-Za-z][A-Za-z\s]{1,30})(?:\s*\.|\s*$|,)", ConfidenceLevel.CRITICAL)
            ],
            MemoryType.USER_STATUS: [
                (r"(?:i am|i'm)\s+(on vacation|working|traveling|busy|available|free|in (?:a )?meeting)(?:\s+(?:till|until)\s+([^\.]+?))?(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH),
                (r"(?:currently|right now)\s+(on vacation|working|traveling|busy|available|free)(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH)
            ],
            MemoryType.USER_CONTEXT: [
                (r"(?:i am (?:currently )?in|i'm (?:currently )?in|currently in|located in)\s+([A-Za-z][A-Za-z\s]{1,30})(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH),
                (r"(?:my (?:current )?location is)\s+([A-Za-z][A-Za-z\s]{1,30})(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH)
            ]
        }
    
    def extract_information(self, text: str) -> List[Dict]:
        """Extract structured information from text"""
        
        text = text.strip().lower()
        extracted_info = []
        
        # Skip questions
        if any(word in text[:15] for word in ["what", "where", "when", "how", "why", "which", "do i", "am i"]):
            return extracted_info
        
        for memory_type, patterns in self.extraction_patterns.items():
            for pattern, confidence in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    value = match.group(1).strip()
                    
                    if self.validate_extraction(memory_type, value):
                        additional_info = None
                        if len(match.groups()) > 1 and match.group(2):
                            additional_info = match.group(2).strip()
                        
                        extracted_info.append({
                            'memory_type': memory_type,
                            'value': value,
                            'additional_info': additional_info,
                            'confidence': confidence.value,
                            'full_match': match.group(0),
                            'content': self.generate_content(memory_type, value, additional_info)
                        })
        
        return extracted_info
    
    def validate_extraction(self, memory_type: MemoryType, value: str) -> bool:
        """Validate extracted information with stricter rules"""
        
        if not value or len(value) < 1 or len(value) > 50:
            return False
        
        # Remove extra whitespace
        value = value.strip()
        
        # Memory type specific validation
        if memory_type == MemoryType.USER_IDENTITY:
            # Valid name pattern - letters, spaces, some special chars
            if not re.match(r'^[A-Za-z][A-Za-z0-9\s\-_\.]*$'
    
    def generate_content(self, memory_type: MemoryType, value: str, additional_info: str = None) -> str:
        """Generate natural language content for memory"""
        
        if memory_type == MemoryType.USER_IDENTITY:
            return f"User prefers to be called {value}."
            
        elif memory_type == MemoryType.USER_STATUS:
            content = f"User is currently {value}."
            if additional_info:
                content += f" Duration: {additional_info}."
            return content
            
        elif memory_type == MemoryType.USER_CONTEXT:
            return f"User is currently located in {value}."
            
        return f"User information: {value}"

class EnterpriseDigitalTwin:
    """Enterprise-grade digital twin with advanced memory management"""
    
    def __init__(self):
        self.setup_llm()
        self.setup_vector_store()
        self.memory_manager = MemoryManager(self.vector_store)
        self.information_extractor = InformationExtractor()
        self.conversation_history = []
        self.session_start = datetime.now()
        
    def setup_llm(self):
        """Initialize the chat model"""
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            temperature=0.7
        )
        
    def setup_vector_store(self):
        """Initialize embedding model and vector store"""
        self.embedding_model = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        self.vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX"),
            embedding_function=self.embedding_model.embed_query
        )
        
    def setup_chain(self):
        """Setup the response generation chain"""
        prompt_template = """You are Paresh's digital twin with enterprise-grade memory management.

Current User Profile:
{user_profile}

Relevant Context Memories:
{context_memories}

Conversation History:
{chat_history}

User Query: {query}

Instructions:
1. Use the user profile for personal information about the user
2. Respond as Paresh would, but use accurate user information when asked about the user
3. Be direct and professional
4. If information is missing from the profile, acknowledge honestly

Response:"""

        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["user_profile", "context_memories", "chat_history", "query"]
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def process_input(self, user_input: str):
        """Process user input for information extraction and storage"""
        
        # Extract information
        extracted_info = self.information_extractor.extract_information(user_input)
        
        # Store extracted information
        for info in extracted_info:
            memory = self.memory_manager.create_memory(
                memory_type=info['memory_type'],
                content=info['content'],
                extracted_value=info['value'],
                confidence=info['confidence'],
                source="user_direct_input",
                context=user_input
            )
            
            success = self.memory_manager.store_memory(memory)
            if success:
                print(f"Updated: {info['content']}")
    
    def get_response(self, user_input: str):
        """Generate response using enterprise memory management"""
        
        try:
            print("Processing with enterprise memory management...")
            
            # Setup response chain if not already done
            if not hasattr(self, 'chain'):
                self.setup_chain()
            
            # Process input for information extraction
            self.process_input(user_input)
            
            # Get user profile
            user_profile = self.memory_manager.get_user_profile()
            profile_text = "\n".join([f"{k}: {v['content']}" for k, v in user_profile.items()])
            if not profile_text:
                profile_text = "No user profile information available."
            
            # Get relevant context memories
            context_memories = self.memory_manager.retrieve_memories(
                user_input, 
                memory_types=[MemoryType.CONVERSATION_CONTEXT, MemoryType.BEHAVIORAL_PATTERN],
                limit=3
            )
            context_text = "\n".join([m.content for m in context_memories])
            if not context_text:
                context_text = "No additional context available."
            
            # Format conversation history
            chat_history = self.format_conversation_history()
            
            # Generate response
            response = self.chain.invoke({
                "user_profile": profile_text,
                "context_memories": context_text,
                "chat_history": chat_history,
                "query": user_input
            })["text"]
            
            # Store conversation
            self.conversation_history.append({
                "user": user_input,
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Cleanup expired memories
            self.memory_manager.cleanup_expired_memories()
            
            return response, len(user_profile)
            
        except Exception as e:
            return f"Error processing request: {e}", 0
    
    def format_conversation_history(self, max_exchanges: int = 3) -> str:
        """Format recent conversation history"""
        if not self.conversation_history:
            return "No previous conversation."
        
        recent = self.conversation_history[-max_exchanges:]
        formatted = []
        
        for exchange in recent:
            formatted.append(f"User: {exchange['user']}")
            formatted.append(f"Paresh: {exchange['assistant']}")
        
        return "\n".join(formatted)
    
    def show_memory_status(self):
        """Show current memory management status"""
        profile = self.memory_manager.get_user_profile()
        active_memories = len(self.memory_manager.active_memories)
        session_cache = len(self.memory_manager.session_cache)
        
        print(f"\nMemory Management Status:")
        print(f"  Active memories: {active_memories}")
        print(f"  Session cache: {session_cache}")
        print(f"  User profile items: {len(profile)}")
        
        if profile:
            print(f"\nCurrent User Profile:")
            for key, value in profile.items():
                print(f"  {key}: {value['content']} (confidence: {value['confidence']:.2f})")
    
    def run_interactive_session(self):
        """Run the interactive session"""
        print("Enterprise Digital Twin v2.0 - Advanced Memory Management")
        print("Features: Conflict resolution, confidence scoring, memory versioning")
        print("Commands: 'memory' | 'profile' | 'history' | 'exit'\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ["exit", "quit"]:
                    print("Session ended. All memories preserved with versioning.")
                    break
                    
                elif user_input.lower() == "memory":
                    self.show_memory_status()
                    continue
                    
                elif user_input.lower() == "profile":
                    profile = self.memory_manager.get_user_profile()
                    if profile:
                        print("\nDetailed User Profile:")
                        for key, value in profile.items():
                            timestamp = datetime.fromisoformat(value['timestamp']).strftime("%Y-%m-%d %H:%M")
                            print(f"  {key}:")
                            print(f"    Value: {value['content']}")
                            print(f"    Confidence: {value['confidence']:.2f}")
                            print(f"    Updated: {timestamp}")
                    else:
                        print("No user profile available yet.")
                    continue
                    
                elif user_input.lower() == "history":
                    if self.conversation_history:
                        print("\nRecent Conversation:")
                        for i, exchange in enumerate(self.conversation_history[-5:], 1):
                            time = datetime.fromisoformat(exchange['timestamp']).strftime("%H:%M")
                            print(f"  {i}. [{time}] {exchange['user'][:40]}...")
                    else:
                        print("No conversation history.")
                    continue
                    
                elif not user_input:
                    continue
                
                response, profile_count = self.get_response(user_input)
                print(f"Paresh: {response}")
                
                if profile_count > 0:
                    print(f"   (Using {profile_count} profile elements)")
                print()
                
            except KeyboardInterrupt:
                print("\nSession interrupted. Memories preserved.")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function"""
    try:
        twin = EnterpriseDigitalTwin()
        twin.run_interactive_session()
    except Exception as e:
        print(f"Failed to initialize: {e}")

if __name__ == "__main__":
    main()
, value):
                return False
            # Avoid common false positives
            invalid_names = [
                'currently', 'working', 'vacation', 'busy', 'available', 
                'located', 'in', 'at', 'on', 'till', 'until', 'from'
            ]
            if value.lower() in invalid_names:
                return False
            # Avoid location-like patterns
            if any(word in value.lower() for word in ['jfk', 'airport', 'nyc', 'phl']):
                return False
                
        elif memory_type == MemoryType.USER_STATUS:
            valid_statuses = ['on vacation', 'working', 'traveling', 'busy', 'available', 'free', 'in meeting', 'in a meeting']
            if value.lower() not in valid_statuses:
                return False
                
        elif memory_type == MemoryType.USER_CONTEXT:
            # Basic location validation
            if not re.match(r'^[A-Za-z][A-Za-z0-9\s\-_\.]*$'
    
    def generate_content(self, memory_type: MemoryType, value: str, additional_info: str = None) -> str:
        """Generate natural language content for memory"""
        
        if memory_type == MemoryType.USER_IDENTITY:
            return f"User prefers to be called {value}."
            
        elif memory_type == MemoryType.USER_STATUS:
            content = f"User is currently {value}."
            if additional_info:
                content += f" Duration: {additional_info}."
            return content
            
        elif memory_type == MemoryType.USER_CONTEXT:
            return f"User is currently located in {value}."
            
        return f"User information: {value}"

class EnterpriseDigitalTwin:
    """Enterprise-grade digital twin with advanced memory management"""
    
    def __init__(self):
        self.setup_llm()
        self.setup_vector_store()
        self.memory_manager = MemoryManager(self.vector_store)
        self.information_extractor = InformationExtractor()
        self.conversation_history = []
        self.session_start = datetime.now()
        
    def setup_llm(self):
        """Initialize the chat model"""
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            temperature=0.7
        )
        
    def setup_vector_store(self):
        """Initialize embedding model and vector store"""
        self.embedding_model = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        self.vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX"),
            embedding_function=self.embedding_model.embed_query
        )
        
    def setup_chain(self):
        """Setup the response generation chain"""
        prompt_template = """You are Paresh's digital twin with enterprise-grade memory management.

Current User Profile:
{user_profile}

Relevant Context Memories:
{context_memories}

Conversation History:
{chat_history}

User Query: {query}

Instructions:
1. Use the user profile for personal information about the user
2. Respond as Paresh would, but use accurate user information when asked about the user
3. Be direct and professional
4. If information is missing from the profile, acknowledge honestly

Response:"""

        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["user_profile", "context_memories", "chat_history", "query"]
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def process_input(self, user_input: str):
        """Process user input for information extraction and storage"""
        
        # Extract information
        extracted_info = self.information_extractor.extract_information(user_input)
        
        # Store extracted information
        for info in extracted_info:
            memory = self.memory_manager.create_memory(
                memory_type=info['memory_type'],
                content=info['content'],
                extracted_value=info['value'],
                confidence=info['confidence'],
                source="user_direct_input",
                context=user_input
            )
            
            success = self.memory_manager.store_memory(memory)
            if success:
                print(f"Updated: {info['content']}")
    
    def get_response(self, user_input: str):
        """Generate response using enterprise memory management"""
        
        try:
            print("Processing with enterprise memory management...")
            
            # Setup response chain if not already done
            if not hasattr(self, 'chain'):
                self.setup_chain()
            
            # Process input for information extraction
            self.process_input(user_input)
            
            # Get user profile
            user_profile = self.memory_manager.get_user_profile()
            profile_text = "\n".join([f"{k}: {v['content']}" for k, v in user_profile.items()])
            if not profile_text:
                profile_text = "No user profile information available."
            
            # Get relevant context memories
            context_memories = self.memory_manager.retrieve_memories(
                user_input, 
                memory_types=[MemoryType.CONVERSATION_CONTEXT, MemoryType.BEHAVIORAL_PATTERN],
                limit=3
            )
            context_text = "\n".join([m.content for m in context_memories])
            if not context_text:
                context_text = "No additional context available."
            
            # Format conversation history
            chat_history = self.format_conversation_history()
            
            # Generate response
            response = self.chain.invoke({
                "user_profile": profile_text,
                "context_memories": context_text,
                "chat_history": chat_history,
                "query": user_input
            })["text"]
            
            # Store conversation
            self.conversation_history.append({
                "user": user_input,
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Cleanup expired memories
            self.memory_manager.cleanup_expired_memories()
            
            return response, len(user_profile)
            
        except Exception as e:
            return f"Error processing request: {e}", 0
    
    def format_conversation_history(self, max_exchanges: int = 3) -> str:
        """Format recent conversation history"""
        if not self.conversation_history:
            return "No previous conversation."
        
        recent = self.conversation_history[-max_exchanges:]
        formatted = []
        
        for exchange in recent:
            formatted.append(f"User: {exchange['user']}")
            formatted.append(f"Paresh: {exchange['assistant']}")
        
        return "\n".join(formatted)
    
    def show_memory_status(self):
        """Show current memory management status"""
        profile = self.memory_manager.get_user_profile()
        active_memories = len(self.memory_manager.active_memories)
        session_cache = len(self.memory_manager.session_cache)
        
        print(f"\nMemory Management Status:")
        print(f"  Active memories: {active_memories}")
        print(f"  Session cache: {session_cache}")
        print(f"  User profile items: {len(profile)}")
        
        if profile:
            print(f"\nCurrent User Profile:")
            for key, value in profile.items():
                print(f"  {key}: {value['content']} (confidence: {value['confidence']:.2f})")
    
    def run_interactive_session(self):
        """Run the interactive session"""
        print("Enterprise Digital Twin v2.0 - Advanced Memory Management")
        print("Features: Conflict resolution, confidence scoring, memory versioning")
        print("Commands: 'memory' | 'profile' | 'history' | 'exit'\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ["exit", "quit"]:
                    print("Session ended. All memories preserved with versioning.")
                    break
                    
                elif user_input.lower() == "memory":
                    self.show_memory_status()
                    continue
                    
                elif user_input.lower() == "profile":
                    profile = self.memory_manager.get_user_profile()
                    if profile:
                        print("\nDetailed User Profile:")
                        for key, value in profile.items():
                            timestamp = datetime.fromisoformat(value['timestamp']).strftime("%Y-%m-%d %H:%M")
                            print(f"  {key}:")
                            print(f"    Value: {value['content']}")
                            print(f"    Confidence: {value['confidence']:.2f}")
                            print(f"    Updated: {timestamp}")
                    else:
                        print("No user profile available yet.")
                    continue
                    
                elif user_input.lower() == "history":
                    if self.conversation_history:
                        print("\nRecent Conversation:")
                        for i, exchange in enumerate(self.conversation_history[-5:], 1):
                            time = datetime.fromisoformat(exchange['timestamp']).strftime("%H:%M")
                            print(f"  {i}. [{time}] {exchange['user'][:40]}...")
                    else:
                        print("No conversation history.")
                    continue
                    
                elif not user_input:
                    continue
                
                response, profile_count = self.get_response(user_input)
                print(f"Paresh: {response}")
                
                if profile_count > 0:
                    print(f"   (Using {profile_count} profile elements)")
                print()
                
            except KeyboardInterrupt:
                print("\nSession interrupted. Memories preserved.")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function"""
    try:
        twin = EnterpriseDigitalTwin()
        twin.run_interactive_session()
    except Exception as e:
        print(f"Failed to initialize: {e}")

if __name__ == "__main__":
    main()
, value):
                return False
            # Avoid status-like words
            invalid_locations = ['vacation', 'working', 'busy', 'meeting', 'currently']
            if value.lower() in invalid_locations:
                return False
            # Length check for reasonable location names
            if len(value.split()) > 3:  # Avoid capturing full sentences
                return False
        
        return True
    
    def generate_content(self, memory_type: MemoryType, value: str, additional_info: str = None) -> str:
        """Generate natural language content for memory"""
        
        if memory_type == MemoryType.USER_IDENTITY:
            return f"User prefers to be called {value}."
            
        elif memory_type == MemoryType.USER_STATUS:
            content = f"User is currently {value}."
            if additional_info:
                content += f" Duration: {additional_info}."
            return content
            
        elif memory_type == MemoryType.USER_CONTEXT:
            return f"User is currently located in {value}."
            
        return f"User information: {value}"

class EnterpriseDigitalTwin:
    """Enterprise-grade digital twin with advanced memory management"""
    
    def __init__(self):
        self.setup_llm()
        self.setup_vector_store()
        self.memory_manager = MemoryManager(self.vector_store)
        self.information_extractor = InformationExtractor()
        self.conversation_history = []
        self.session_start = datetime.now()
        
    def setup_llm(self):
        """Initialize the chat model"""
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            temperature=0.7
        )
        
    def setup_vector_store(self):
        """Initialize embedding model and vector store"""
        self.embedding_model = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        self.vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX"),
            embedding_function=self.embedding_model.embed_query
        )
        
    def setup_chain(self):
        """Setup the response generation chain"""
        prompt_template = """You are Paresh's digital twin with enterprise-grade memory management.

Current User Profile:
{user_profile}

Relevant Context Memories:
{context_memories}

Conversation History:
{chat_history}

User Query: {query}

Instructions:
1. Use the user profile for personal information about the user
2. Respond as Paresh would, but use accurate user information when asked about the user
3. Be direct and professional
4. If information is missing from the profile, acknowledge honestly

Response:"""

        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["user_profile", "context_memories", "chat_history", "query"]
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def process_input(self, user_input: str):
        """Process user input for information extraction and storage"""
        
        # Extract information
        extracted_info = self.information_extractor.extract_information(user_input)
        
        # Store extracted information
        for info in extracted_info:
            memory = self.memory_manager.create_memory(
                memory_type=info['memory_type'],
                content=info['content'],
                extracted_value=info['value'],
                confidence=info['confidence'],
                source="user_direct_input",
                context=user_input
            )
            
            success = self.memory_manager.store_memory(memory)
            if success:
                print(f"Updated: {info['content']}")
    
    def get_response(self, user_input: str):
        """Generate response using enterprise memory management"""
        
        try:
            print("Processing with enterprise memory management...")
            
            # Setup response chain if not already done
            if not hasattr(self, 'chain'):
                self.setup_chain()
            
            # Process input for information extraction
            self.process_input(user_input)
            
            # Get user profile
            user_profile = self.memory_manager.get_user_profile()
            profile_text = "\n".join([f"{k}: {v['content']}" for k, v in user_profile.items()])
            if not profile_text:
                profile_text = "No user profile information available."
            
            # Get relevant context memories
            context_memories = self.memory_manager.retrieve_memories(
                user_input, 
                memory_types=[MemoryType.CONVERSATION_CONTEXT, MemoryType.BEHAVIORAL_PATTERN],
                limit=3
            )
            context_text = "\n".join([m.content for m in context_memories])
            if not context_text:
                context_text = "No additional context available."
            
            # Format conversation history
            chat_history = self.format_conversation_history()
            
            # Generate response
            response = self.chain.invoke({
                "user_profile": profile_text,
                "context_memories": context_text,
                "chat_history": chat_history,
                "query": user_input
            })["text"]
            
            # Store conversation
            self.conversation_history.append({
                "user": user_input,
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Cleanup expired memories
            self.memory_manager.cleanup_expired_memories()
            
            return response, len(user_profile)
            
        except Exception as e:
            return f"Error processing request: {e}", 0
    
    def format_conversation_history(self, max_exchanges: int = 3) -> str:
        """Format recent conversation history"""
        if not self.conversation_history:
            return "No previous conversation."
        
        recent = self.conversation_history[-max_exchanges:]
        formatted = []
        
        for exchange in recent:
            formatted.append(f"User: {exchange['user']}")
            formatted.append(f"Paresh: {exchange['assistant']}")
        
        return "\n".join(formatted)
    
    def show_memory_status(self):
        """Show current memory management status"""
        profile = self.memory_manager.get_user_profile()
        active_memories = len(self.memory_manager.active_memories)
        session_cache = len(self.memory_manager.session_cache)
        
        print(f"\nMemory Management Status:")
        print(f"  Active memories: {active_memories}")
        print(f"  Session cache: {session_cache}")
        print(f"  User profile items: {len(profile)}")
        
        if profile:
            print(f"\nCurrent User Profile:")
            for key, value in profile.items():
                print(f"  {key}: {value['content']} (confidence: {value['confidence']:.2f})")
    
    def run_interactive_session(self):
        """Run the interactive session"""
        print("Enterprise Digital Twin v2.0 - Advanced Memory Management")
        print("Features: Conflict resolution, confidence scoring, memory versioning")
        print("Commands: 'memory' | 'profile' | 'history' | 'exit'\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ["exit", "quit"]:
                    print("Session ended. All memories preserved with versioning.")
                    break
                    
                elif user_input.lower() == "memory":
                    self.show_memory_status()
                    continue
                    
                elif user_input.lower() == "profile":
                    profile = self.memory_manager.get_user_profile()
                    if profile:
                        print("\nDetailed User Profile:")
                        for key, value in profile.items():
                            timestamp = datetime.fromisoformat(value['timestamp']).strftime("%Y-%m-%d %H:%M")
                            print(f"  {key}:")
                            print(f"    Value: {value['content']}")
                            print(f"    Confidence: {value['confidence']:.2f}")
                            print(f"    Updated: {timestamp}")
                    else:
                        print("No user profile available yet.")
                    continue
                    
                elif user_input.lower() == "history":
                    if self.conversation_history:
                        print("\nRecent Conversation:")
                        for i, exchange in enumerate(self.conversation_history[-5:], 1):
                            time = datetime.fromisoformat(exchange['timestamp']).strftime("%H:%M")
                            print(f"  {i}. [{time}] {exchange['user'][:40]}...")
                    else:
                        print("No conversation history.")
                    continue
                    
                elif not user_input:
                    continue
                
                response, profile_count = self.get_response(user_input)
                print(f"Paresh: {response}")
                
                if profile_count > 0:
                    print(f"   (Using {profile_count} profile elements)")
                print()
                
            except KeyboardInterrupt:
                print("\nSession interrupted. Memories preserved.")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function"""
    try:
        twin = EnterpriseDigitalTwin()
        twin.run_interactive_session()
    except Exception as e:
        print(f"Failed to initialize: {e}")

if __name__ == "__main__":
    main()