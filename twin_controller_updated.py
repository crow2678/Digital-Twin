import os
import uuid
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

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

class CustomAzureMemoryStore:
    """Custom Azure Search wrapper optimized for memory storage"""
    
    def __init__(self, search_endpoint: str, search_key: str, index_name: str, embedding_function):
        self.search_endpoint = search_endpoint
        self.search_key = search_key
        self.index_name = index_name
        self.embedding_function = embedding_function
        
        # Initialize search client
        credential = AzureKeyCredential(search_key)
        self.search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=credential
        )
    
    def add_memory(self, memory: 'MemoryRecord') -> bool:
        """Add a memory record to the vector store"""
        try:
            # Generate embedding for the content
            embedding = self.embedding_function(memory.content)
            
            # Create document with flattened structure
            doc = {
                "id": memory.id,
                "content": memory.content,
                "content_vector": embedding,
                "memory_type": memory.memory_type.value,
                "extracted_value": memory.extracted_value,
                "confidence": memory.confidence,
                "timestamp": memory.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "source": memory.source,
                "version": memory.version,
                "is_active": memory.is_active,
                "context": memory.context or "",
                "metadata_json": json.dumps(memory.metadata or {}),
                "expiry_date": memory.expiry_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if memory.expiry_date else "",
            }
            
            # Upload to Azure Search
            result = self.search_client.upload_documents([doc])
            return len(result) > 0 and result[0].succeeded
            
        except Exception as e:
            print(f"Failed to add memory: {e}")
            return False
    
    def search_memories(self, query: str, top: int = 5, filter_expr: str = None) -> List[Dict]:
        """Search for memories using both text and vector search"""
        try:
            # Generate query embedding
            query_vector = self.embedding_function(query)
            
            # Perform hybrid search (text + vector) with proper vector query format
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top * 2,
                fields="content_vector"
            )
            
            search_results = self.search_client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=top,
                filter=filter_expr
            )
            
            results = []
            for result in search_results:
                if result.get('is_active', True):
                    results.append(dict(result))
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def update_memory_status(self, memory_id: str, is_active: bool) -> bool:
        """Update memory active status"""
        try:
            # Search for the document first
            search_results = self.search_client.search(
                search_text="",
                filter=f"id eq '{memory_id}'",
                top=1
            )
            
            doc = None
            for result in search_results:
                doc = dict(result)
                break
            
            if doc:
                doc['is_active'] = is_active
                if not is_active:
                    doc['content'] = f"INACTIVE: {doc['content']}"
                
                result = self.search_client.merge_or_upload_documents([doc])
                return len(result) > 0 and result[0].succeeded
            
            return False
            
        except Exception as e:
            print(f"Failed to update memory: {e}")
            return False

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
    
    def to_azure_search_doc(self):
        """Convert to Azure Search document format with flattened fields"""
        return {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'extracted_value': self.extracted_value,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'version': self.version,
            'is_active': self.is_active,
            'context': self.context or "",
            'metadata_json': json.dumps(self.metadata or {}),
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else "",
        }
    
    @classmethod
    def from_search_result(cls, result: dict):
        """Create MemoryRecord from Azure Search result"""
        
        # Parse metadata from JSON string
        metadata = {}
        if result.get('metadata_json'):
            try:
                metadata = json.loads(result['metadata_json'])
            except json.JSONDecodeError:
                metadata = {}
        
        # Parse timestamps with proper format handling
        timestamp_str = result['timestamp']
        if timestamp_str.endswith('Z'):
            timestamp = datetime.fromisoformat(timestamp_str[:-1])
        else:
            timestamp = datetime.fromisoformat(timestamp_str)
            
        expiry_date = None
        if result.get('expiry_date'):
            try:
                expiry_str = result['expiry_date']
                if expiry_str.endswith('Z'):
                    expiry_date = datetime.fromisoformat(expiry_str[:-1])
                else:
                    expiry_date = datetime.fromisoformat(expiry_str)
            except ValueError:
                pass
        
        return cls(
            id=result['id'],
            memory_type=MemoryType(result['memory_type']),
            content=result['content'],
            extracted_value=result['extracted_value'],
            confidence=float(result['confidence']),
            timestamp=timestamp,
            source=result['source'],
            version=int(result.get('version', 1)),
            is_active=bool(result.get('is_active', True)),
            context=result.get('context') if result.get('context') else None,
            metadata=metadata,
            expiry_date=expiry_date
        )

class MemoryManager:
    def __init__(self, memory_store: CustomAzureMemoryStore):
        self.memory_store = memory_store
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
        
        # Check memory store for conflicts
        try:
            search_query = f"user {new_memory.memory_type.value}"
            filter_expr = f"memory_type eq '{new_memory.memory_type.value}' and is_active eq true"
            
            results = self.memory_store.search_memories(search_query, top=10, filter_expr=filter_expr)
            
            for result in results:
                if (result.get('extracted_value', '').lower() != new_memory.extracted_value.lower()):
                    try:
                        memory_record = MemoryRecord.from_search_result(result)
                        conflicts.append(memory_record)
                    except Exception as e:
                        print(f"Warning: Skipping malformed memory record: {e}")
                        continue
                    
        except Exception as e:
            print(f"Error checking for conflicts: {e}")
        
        return conflicts
    
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
        return self.memory_store.add_memory(memory)
    
    def update_vector_store(self, memory: MemoryRecord):
        """Update memory in vector store (mark as inactive)"""
        try:
            self.memory_store.update_memory_status(memory.id, False)
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
        
        # Then search memory store
        try:
            search_query = f"user {query}" if not query.startswith("user") else query
            filter_expr = "is_active eq true"
            
            results = self.memory_store.search_memories(search_query, top=limit * 3, filter_expr=filter_expr)
            
            for result in results:
                if not result.get('content', '').startswith("INACTIVE:"):
                    try:
                        memory_record = MemoryRecord.from_search_result(result)
                        
                        # Avoid duplicates from session cache
                        if memory_record.id not in [m.id for m in memories]:
                            memories.append(memory_record)
                            
                    except Exception as e:
                        print(f"Warning: Skipping malformed memory record: {e}")
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
            MemoryType.USER_CONTEXT,
            MemoryType.WORK_PATTERN
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
        
        # Then add from memory store if not in session cache
        try:
            for mem_type in user_memory_types:
                if mem_type.value not in profile:
                    search_query = f"user {mem_type.value}"
                    filter_expr = f"memory_type eq '{mem_type.value}' and is_active eq true"
                    
                    results = self.memory_store.search_memories(search_query, top=3, filter_expr=filter_expr)
                    
                    for result in results:
                        try:
                            memory_record = MemoryRecord.from_search_result(result)
                            
                            profile[mem_type.value] = {
                                'value': memory_record.extracted_value,
                                'content': memory_record.content,
                                'confidence': memory_record.confidence,
                                'timestamp': memory_record.timestamp.isoformat(),
                                'source': 'stored'
                            }
                            break  # Take the first valid one
                            
                        except Exception as e:
                            print(f"Warning: Error reconstructing profile memory: {e}")
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
            
        if expired_ids:
            print(f"Cleaned up {len(expired_ids)} expired memories")

class InformationExtractor:
    """Handles extraction and validation of information from user input"""
    
    def __init__(self):
        self.extraction_patterns = {
            MemoryType.USER_IDENTITY: [
                (r"(?:my (?:preferred )?name is|call me|i am|i'm called|refer to me as|address me as)\s+([A-Za-z][A-Za-z\s]{1,30})(?:\s*\.|\s*$|,)", ConfidenceLevel.CRITICAL),
                (r"(?:change my name to|update my name to)\s+([A-Za-z][A-Za-z\s]{1,30})(?:\s*\.|\s*$|,)", ConfidenceLevel.CRITICAL)
            ],
            MemoryType.USER_PREFERENCE: [
                (r"(?:i like|i prefer|i enjoy|i love)\s+(.+?)(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH),
                (r"(?:i don't like|i hate|i dislike|not a fan of)\s+(.+?)(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH),
                (r"(?:my favorite|i usually|i typically|i always)\s+(.+?)(?:\s*\.|\s*$|,)", ConfidenceLevel.MEDIUM)
            ],
            MemoryType.USER_STATUS: [
                (r"(?:i am|i'm)\s+(on vacation|working|traveling|busy|available|free|in (?:a )?meeting)(?:\s+(?:till|until)\s+([^\.]+?))?(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH),
                (r"(?:currently|right now)\s+(on vacation|working|traveling|busy|available|free)(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH)
            ],
            MemoryType.USER_CONTEXT: [
                (r"(?:i am (?:currently )?in|i'm (?:currently )?in|currently in|located in)\s+([A-Za-z][A-Za-z\s]{1,30})(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH),
                (r"(?:my (?:current )?location is)\s+([A-Za-z][A-Za-z\s]{1,30})(?:\s*\.|\s*$|,)", ConfidenceLevel.HIGH)
            ],
            MemoryType.WORK_PATTERN: [
                (r"(?:i work|working|office hours?)\s+(?:from\s+)?(.+?)(?:\s*\.|\s*$|,)", ConfidenceLevel.MEDIUM),
                (r"(?:my schedule|meetings? (?:on|every))\s+(.+?)(?:\s*\.|\s*$|,)", ConfidenceLevel.MEDIUM),
                (r"(?:i'm (?:usually )?(?:in|at)|i work (?:at|from))\s+(.+?)(?:\s*\.|\s*$|,)", ConfidenceLevel.MEDIUM)
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
        
        if not value or len(value) < 1 or len(value) > 100:
            return False
        
        # Remove extra whitespace
        value = value.strip()
        
        # Memory type specific validation
        if memory_type == MemoryType.USER_IDENTITY:
            # Valid name pattern - letters, spaces, some special chars
            if not re.match(r'^[A-Za-z][A-Za-z0-9\s\-_\.]*$', value):
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
                
        elif memory_type == MemoryType.USER_PREFERENCE:
            # Allow broader range for preferences
            if len(value) < 2:
                return False
            # Skip overly generic preferences
            generic_prefs = ['things', 'stuff', 'it', 'that', 'this']
            if value.lower().strip() in generic_prefs:
                return False
                
        elif memory_type == MemoryType.USER_STATUS:
            valid_statuses = ['on vacation', 'working', 'traveling', 'busy', 'available', 'free', 'in meeting', 'in a meeting']
            if value.lower() not in valid_statuses:
                return False
                
        elif memory_type == MemoryType.USER_CONTEXT:
            # Basic location validation
            if not re.match(r'^[A-Za-z][A-Za-z0-9\s\-_\.]*$', value):
                return False
            # Avoid status-like words
            invalid_locations = ['vacation', 'working', 'busy', 'meeting', 'currently']
            if value.lower() in invalid_locations:
                return False
            # Length check for reasonable location names
            if len(value.split()) > 3:
                return False
                
        elif memory_type == MemoryType.WORK_PATTERN:
            # Work patterns can be more flexible
            if len(value) < 3:
                return False
            # Skip overly generic work info
            generic_work = ['work', 'office', 'job']
            if value.lower().strip() in generic_work:
                return False
        
        return True
    
    def generate_content(self, memory_type: MemoryType, value: str, additional_info: str = None) -> str:
        """Generate natural language content for memory"""
        
        if memory_type == MemoryType.USER_IDENTITY:
            return f"User prefers to be called {value}."
            
        elif memory_type == MemoryType.USER_PREFERENCE:
            if any(neg in value.lower() for neg in ["don't", "hate", "dislike"]):
                return f"User dislikes: {value}."
            else:
                return f"User likes: {value}."
            
        elif memory_type == MemoryType.USER_STATUS:
            content = f"User is currently {value}."
            if additional_info:
                content += f" Duration: {additional_info}."
            return content
            
        elif memory_type == MemoryType.USER_CONTEXT:
            return f"User is currently located in {value}."
            
        elif memory_type == MemoryType.WORK_PATTERN:
            return f"User's work pattern: {value}."
            
        return f"User information: {value}"

class EnterpriseDigitalTwin:
    """Enterprise-grade digital twin with advanced memory management"""
    
    def __init__(self):
        self.setup_llm()
        self.setup_memory_store()
        self.memory_manager = MemoryManager(self.memory_store)
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
        
    def setup_memory_store(self):
        """Initialize embedding model and custom memory store"""
        self.embedding_model = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        self.memory_store = CustomAzureMemoryStore(
            search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            search_key=os.getenv("AZURE_SEARCH_KEY"),
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
        
        # Use the modern RunnableSequence pattern
        self.chain = self.prompt | self.llm | StrOutputParser()
    
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
        
        # Track conversation context (topics mentioned)
        self.track_conversation_context(user_input)
    
    def track_conversation_context(self, user_input: str):
        """Track topics and context from conversation"""
        try:
            # Simple topic extraction - look for important nouns/topics
            topic_patterns = [
                r'\b(project|meeting|presentation|deadline|client|team|work|job|task)\b',
                r'\b(vacation|holiday|trip|travel|conference|event)\b',
                r'\b(family|friend|colleague|boss|manager|partner)\b',
                r'\b(python|java|javascript|ai|machine learning|coding|programming)\b'
            ]
            
            topics = []
            for pattern in topic_patterns:
                matches = re.findall(pattern, user_input.lower())
                topics.extend(matches)
            
            if topics:
                # Create conversation context memory
                context_content = f"Discussed topics: {', '.join(set(topics))}"
                context_memory = self.memory_manager.create_memory(
                    memory_type=MemoryType.CONVERSATION_CONTEXT,
                    content=context_content,
                    extracted_value=', '.join(set(topics)),
                    confidence=0.6,
                    source="conversation_tracker",
                    context=user_input,
                    expiry_hours=24  # Context expires after 24 hours
                )
                self.memory_manager.store_memory(context_memory)
        except Exception as e:
            print(f"Error in track_conversation_context: {e}")
    
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
            })
            
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
            print(f"Error processing request: {e}")
            return f"I encountered an error while processing your request. Please try again.", 0
    
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
    
    def show_memory_analytics(self):
        """Show advanced memory analytics"""
        profile = self.memory_manager.get_user_profile()
        
        print(f"\n=== Memory Analytics ===")
        print(f"Total profile elements: {len(profile)}")
        print(f"Session cache items: {len(self.memory_manager.session_cache)}")
        print(f"Active memories: {len(self.memory_manager.active_memories)}")
        
        # Confidence distribution
        if profile:
            confidences = [v['confidence'] for v in profile.values()]
            avg_confidence = sum(confidences) / len(confidences)
            print(f"Average confidence: {avg_confidence:.2f}")
            
            # Memory type breakdown
            memory_types = {}
            for key, value in profile.items():
                memory_types[key] = memory_types.get(key, 0) + 1
            
            print(f"\nMemory Distribution:")
            for mem_type, count in memory_types.items():
                print(f"  {mem_type}: {count} items")
        
        print("========================\n")
    
    def show_conversation_topics(self):
        """Show recent conversation topics"""
        context_memories = self.memory_manager.retrieve_memories(
            "conversation topics",
            memory_types=[MemoryType.CONVERSATION_CONTEXT],
            limit=10
        )
        
        if context_memories:
            print(f"\n=== Recent Topics ===")
            for memory in context_memories[-5:]:  # Last 5 topics
                time = memory.timestamp.strftime("%H:%M")
                print(f"[{time}] {memory.extracted_value}")
            print("=====================\n")
        else:
            print("No conversation topics tracked yet.\n")
    
    def run_interactive_session(self):
        """Run the interactive session"""
        print("Enterprise Digital Twin v3.1 - Enhanced Features")
        print("Features: Advanced patterns, conversation tracking, enhanced analytics")
        print("Commands: 'memory' | 'profile' | 'history' | 'analytics' | 'topics' | 'exit'\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ["exit", "quit"]:
                    print("Session ended. All memories preserved with versioning.")
                    break
                    
                elif user_input.lower() == "memory":
                    self.show_memory_status()
                    continue
                    
                elif user_input.lower() == "analytics":
                    self.show_memory_analytics()
                    continue
                    
                elif user_input.lower() == "topics":
                    self.show_conversation_topics()
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
                            print(f"    Source: {value['source']}")
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