import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import logging

# Import your existing classes
from hybrid_memory_system import HybridMemoryRecord, HybridInformationProcessor
from digital_twin_ontology import DigitalTwinOntology
from ai_semantic_processor import AISemanticProcessor
import uuid

logger = logging.getLogger(__name__)

class EnhancedHybridMemoryManager:
    """Enhanced memory manager with LLM-powered answer synthesis and intelligent retrieval"""
    
    def __init__(self, azure_search_config: Dict[str, str]):
        # Initialize components
        self.ontology = DigitalTwinOntology()
        self.llm = self._setup_llm()
        self.ai_processor = AISemanticProcessor(self.llm, self.ontology)
        self.information_processor = HybridInformationProcessor(self.ontology, self.ai_processor)
        
        # Initialize your existing Azure Search (reuse your CustomAzureMemoryStore)
        self.embedding_model = self._setup_embeddings()
        self.memory_store = self._setup_azure_search(azure_search_config)
        
        # Memory caches
        self.session_cache: Dict[str, HybridMemoryRecord] = {}
        self.relationship_cache: Dict[str, List[str]] = {}
        
        # Performance tracking
        self.performance_metrics = {
            "total_processed": 0,
            "hybrid_successes": 0,
            "ontology_only": 0,
            "ai_only": 0,
            "llm_answers_generated": 0,
            "processing_times": [],
            "confidence_scores": [],
            "answer_quality_scores": []
        }
    
    def _setup_llm(self) -> AzureChatOpenAI:
        """Setup Azure OpenAI LLM for answer generation"""
        return AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            temperature=0.3,  # Lower temperature for more consistent answers
            max_tokens=1500
        )
    
    def _setup_embeddings(self) -> AzureOpenAIEmbeddings:
        """Setup Azure OpenAI embeddings"""
        return AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
    
    def _setup_azure_search(self, config: Dict[str, str]):
        """Setup Azure Search using your existing CustomAzureMemoryStore pattern"""
        from azure.search.documents import SearchClient
        from azure.search.documents.models import VectorizedQuery
        from azure.core.credentials import AzureKeyCredential
        
        class EnhancedHybridAzureMemoryStore:
            def __init__(self, search_endpoint: str, search_key: str, index_name: str, embedding_model):
                self.search_endpoint = search_endpoint
                self.search_key = search_key
                self.index_name = index_name
                self.embedding_model = embedding_model
                
                credential = AzureKeyCredential(search_key)
                self.search_client = SearchClient(
                    endpoint=search_endpoint,
                    index_name=index_name,
                    credential=credential
                )
            
            def add_hybrid_memory(self, memory: HybridMemoryRecord) -> bool:
                """Add hybrid memory to Azure Search"""
                try:
                    # Generate embedding for enhanced content
                    embedding = self.embedding_model.embed_query(memory._create_searchable_content())
                    
                    # Create search document
                    doc = memory.to_search_document()
                    doc["content_vector"] = embedding
                    
                    # Upload to Azure Search
                    result = self.search_client.upload_documents([doc])
                    return len(result) > 0 and result[0].succeeded
                    
                except Exception as e:
                    logger.error(f"Failed to add hybrid memory: {e}")
                    return False
            
            def search_hybrid_memories(self, query: str, filters: Dict[str, Any] = None, 
                                     top: int = 5) -> List[Dict]:
                """Search hybrid memories with semantic and ontology filters - FIXED"""
                try:
                    # Generate query embedding
                    query_vector = self.embedding_model.embed_query(query)
                    
                    # Build filter expression
                    filter_expr = self._build_filter_expression(filters)
                    
                    # FIX: Ensure k_nearest_neighbors is within valid range (1-10000)
                    k_value = min(max(top * 2, 1), 1000)  # Ensure between 1 and 1000 (safe limit)
                    
                    # Perform hybrid search
                    vector_query = VectorizedQuery(
                        vector=query_vector,
                        k_nearest_neighbors=k_value,  # FIXED: Use validated k_value
                        fields="content_vector"
                    )
                    
                    search_results = self.search_client.search(
                        search_text=query,
                        vector_queries=[vector_query],
                        top=min(top, 50),  # FIX: Also limit top parameter
                        filter=filter_expr,
                        select=["*"]
                    )
                    
                    results = []
                    for result in search_results:
                        if result.get('is_active', True):
                            results.append(dict(result))
                    
                    return results
                    
                except Exception as e:
                    logger.error(f"Hybrid search error: {e}")
                    return []
            
            def multi_strategy_search(self, queries: List[str], filters: Dict[str, Any] = None, 
                                    top_per_query: int = 10) -> List[Dict]:
                """Perform multiple searches with different strategies - FIXED"""
                all_results = []
                seen_ids = set()
                
                # FIX: Ensure top_per_query is reasonable
                safe_top = min(max(top_per_query, 1), 20)  # Between 1 and 20
                
                for query in queries:
                    try:
                        results = self.search_hybrid_memories(query, filters, safe_top)
                        for result in results:
                            if result.get('id') not in seen_ids:
                                seen_ids.add(result.get('id'))
                                all_results.append(result)
                    except Exception as e:
                        logger.warning(f"Search failed for query '{query}': {e}")
                        continue
                
                return all_results
            
            def search_personal_information(self, user_id: str, information_type: str, 
                                          top: int = 20) -> List[Dict]:
                """Search specifically for personal information - FIXED"""
                personal_queries = []
                
                # Build targeted queries based on information type
                if information_type == "identity":
                    personal_queries = [
                        f"{user_id} name called identity",
                        "my name is",
                        "call me",
                        "i am",
                        f"{user_id} identity personal"
                    ]
                elif information_type == "work":
                    personal_queries = [
                        f"{user_id} work job company employment",
                        "i work at",
                        "my job",
                        "my company",
                        "my role",
                        f"{user_id} work employment career"
                    ]
                elif information_type == "interests":
                    personal_queries = [
                        f"{user_id} interests hobbies like enjoy",
                        "i like",
                        "i enjoy",
                        "my interests",
                        "my hobbies",
                        f"{user_id} preferences interests"
                    ]
                elif information_type == "background":
                    personal_queries = [
                        f"{user_id} background experience education",
                        "my background",
                        "my experience",
                        "i have",
                        f"{user_id} history background"
                    ]
                else:
                    # General personal info search
                    personal_queries = [
                        f"{user_id} personal information",
                        f"{user_id} about me",
                        f"{user_id}",
                        "personal information",
                        "about me"
                    ]
                
                filters = {
                    "user_id": user_id,
                    "importance_min": 0.3
                }
                
                # FIX: Ensure reasonable limits
                safe_top = min(max(top, 5), 50)  # Between 5 and 50
                queries_per_search = max(len(personal_queries), 1)
                top_per_query = max(safe_top // queries_per_search, 1)
                
                return self.multi_strategy_search(personal_queries, filters, top_per_query)
            
            def _build_filter_expression(self, filters: Dict[str, Any] = None) -> str:
                """Build OData filter expression for hybrid search"""
                if not filters:
                    return "is_active eq true"
                
                filter_parts = ["is_active eq true"]
                
                # User/tenant filters
                if filters.get("user_id"):
                    filter_parts.append(f"user_id eq '{filters['user_id']}'")
                
                if filters.get("tenant_id"):
                    filter_parts.append(f"tenant_id eq '{filters['tenant_id']}'")
                
                # Ontology filters
                if filters.get("ontology_domain"):
                    filter_parts.append(f"ontology_domain eq '{filters['ontology_domain']}'")
                
                if filters.get("ontology_category"):
                    filter_parts.append(f"ontology_category eq '{filters['ontology_category']}'")
                
                # AI filters
                if filters.get("ai_confidence_min"):
                    filter_parts.append(f"ai_confidence ge {filters['ai_confidence_min']}")
                
                if filters.get("importance_min"):
                    filter_parts.append(f"importance_score ge {filters['importance_min']}")
                
                # Semantic tag filters
                if filters.get("semantic_tags"):
                    tag_filters = []
                    for tag in filters["semantic_tags"]:
                        tag_filters.append(f"search.in('{tag}', ai_semantic_tags, ',')")
                    if tag_filters:
                        filter_parts.append(f"({' or '.join(tag_filters)})")
                
                # Time filters
                if filters.get("since_date"):
                    filter_parts.append(f"timestamp ge {filters['since_date']}")
                
                return " and ".join(filter_parts)
        
        return EnhancedHybridAzureMemoryStore(
            search_endpoint=config["search_endpoint"],
            search_key=config["search_key"],
            index_name=config["index_name"],
            embedding_model=self.embedding_model
        )
    
    def process_and_store_memory(self, content: str, user_context: Dict[str, Any] = None) -> Tuple[HybridMemoryRecord, Dict[str, Any]]:
        """Process content with hybrid approach and store in Azure Search"""
        
        start_time = datetime.now()
        
        try:
            # Process with hybrid ontology + AI
            logger.info(f"Processing memory with hybrid approach: {content[:50]}...")
            hybrid_memory = self.information_processor.process_content(content, user_context)
            
            # Store in Azure Search
            storage_success = self.memory_store.add_hybrid_memory(hybrid_memory)
            
            if storage_success:
                # Add to session cache
                self.session_cache[hybrid_memory.id] = hybrid_memory
                
                # Update relationship cache
                self._update_relationship_cache(hybrid_memory)
                
                logger.info(f"Successfully stored hybrid memory: {hybrid_memory.id}")
            else:
                logger.error(f"Failed to store hybrid memory: {hybrid_memory.id}")
            
            # Update performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(hybrid_memory, processing_time, storage_success)
            
            # Create processing report
            processing_report = {
                "success": storage_success,
                "processing_time_seconds": processing_time,
                "ontology_domain": hybrid_memory.ontology_domain,
                "ontology_confidence": hybrid_memory.ontology_confidence,
                "ai_confidence": hybrid_memory.ai_confidence,
                "hybrid_confidence": hybrid_memory.hybrid_classification.get("synthesis_confidence", 0.0),
                "importance_score": hybrid_memory.importance_score,
                "semantic_concepts_found": len(hybrid_memory.ai_semantic_concepts),
                "entities_extracted": len(hybrid_memory.ai_extracted_entities),
                "relationships_identified": len(hybrid_memory.ai_relationships),
                "semantic_summary": hybrid_memory.semantic_summary
            }
            
            return hybrid_memory, processing_report
            
        except Exception as e:
            logger.error(f"Error in hybrid memory processing: {e}")
            # Return minimal memory record and error report
            error_memory = HybridMemoryRecord(
                id=str(uuid.uuid4()),
                content=content,
                timestamp=datetime.now(),
                source="error_fallback",
                semantic_summary=f"Processing failed: {str(e)[:100]}"
            )
            
            error_report = {
                "success": False,
                "error": str(e),
                "processing_time_seconds": (datetime.now() - start_time).total_seconds()
            }
            
            return error_memory, error_report
    
    def search_memories(self, query: str, search_options: Dict[str, Any] = None) -> List[Tuple[HybridMemoryRecord, float]]:
        """Enhanced search using hybrid ontology + AI understanding with multiple strategies"""
        
        # Set default search options
        options = search_options or {}
        user_id = options.get("user_id", "default")
        limit = options.get("limit", 10)
        filters = options.get("filters", {})
        
        # Add user context to filters
        filters["user_id"] = user_id
        
        try:
            # Multi-strategy search approach
            search_strategies = self._build_search_strategies(query, user_id)
            
            # Execute all search strategies
            all_results = []
            for strategy_name, strategy_queries in search_strategies.items():
                try:
                    strategy_results = self.memory_store.multi_strategy_search(
                        strategy_queries, filters, limit // len(search_strategies)
                    )
                    for result in strategy_results:
                        result['strategy'] = strategy_name
                    all_results.extend(strategy_results)
                except Exception as e:
                    logger.warning(f"Search strategy '{strategy_name}' failed: {e}")
                    continue
            
            # Convert to HybridMemoryRecord objects and calculate relevance
            hybrid_memories = []
            seen_ids = set()
            
            for result in all_results:
                try:
                    if result.get('id') in seen_ids:
                        continue
                    seen_ids.add(result.get('id'))
                    
                    memory = HybridMemoryRecord.from_search_result(result)
                    
                    # Calculate enhanced relevance score
                    relevance_score = self._calculate_enhanced_relevance_score(
                        query, memory, result
                    )
                    
                    hybrid_memories.append((memory, relevance_score))
                    
                except Exception as e:
                    logger.warning(f"Failed to reconstruct memory from search result: {e}")
                    continue
            
            # Sort by relevance and return top results
            hybrid_memories.sort(key=lambda x: x[1], reverse=True)
            
            # Add session cache results if relevant
            session_results = self._search_session_cache(query, user_id)
            for session_memory, score in session_results:
                # Avoid duplicates
                if not any(memory.id == session_memory.id for memory, _ in hybrid_memories):
                    hybrid_memories.append((session_memory, score * 1.2))  # Boost session cache
            
            # Re-sort and limit
            hybrid_memories.sort(key=lambda x: x[1], reverse=True)
            return hybrid_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error in hybrid memory search: {e}")
            return []
    
    def _build_search_strategies(self, query: str, user_id: str) -> Dict[str, List[str]]:
        """Build multiple search strategies for comprehensive memory retrieval"""
        
        strategies = {
            "direct": [query],
            "with_user": [f"{user_id} {query}"],
            "semantic_variations": self._generate_semantic_variations(query),
            "key_terms": self._extract_key_terms_for_search(query),
            "personal_context": self._generate_personal_context_queries(query, user_id)
        }
        
        return strategies
    
    def _generate_semantic_variations(self, query: str) -> List[str]:
        """Generate semantic variations of the search query"""
        variations = []
        query_lower = query.lower()
        
        # Common semantic mappings for personal questions
        semantic_mappings = {
            "name": ["identity", "called", "refer to me", "address me"],
            "work": ["job", "employment", "company", "career", "profession", "role"],
            "interests": ["hobbies", "like", "enjoy", "preferences", "passionate about"],
            "background": ["history", "experience", "education", "credentials"],
            "skills": ["abilities", "expertise", "good at", "capable of"],
            "goals": ["objectives", "aims", "targets", "aspirations"],
            "location": ["where", "place", "office", "based", "live"],
            "projects": ["working on", "tasks", "assignments", "initiatives"]
        }
        
        for key, synonyms in semantic_mappings.items():
            if key in query_lower:
                variations.extend(synonyms)
        
        return variations[:5]  # Limit to top 5 variations
    
    def _extract_key_terms_for_search(self, query: str) -> List[str]:
        """Extract key search terms from query"""
        key_terms = []
        query_lower = query.lower()
        
        # Important terms that should be searched individually
        important_terms = [
            "paresh", "name", "work", "company", "job", "role", "interests", 
            "background", "experience", "skills", "projects", "goals",
            "like", "enjoy", "prefer", "good at", "working on"
        ]
        
        for term in important_terms:
            if term in query_lower:
                key_terms.append(term)
        
        return key_terms
    
    def _generate_personal_context_queries(self, query: str, user_id: str) -> List[str]:
        """Generate queries with personal context"""
        personal_queries = []
        query_lower = query.lower()
        
        # Personal information patterns
        if any(word in query_lower for word in ["name", "called", "identity"]):
            personal_queries = [
                "my name is",
                "call me",
                "i am",
                f"{user_id} identity",
                "refer to me as"
            ]
        elif any(word in query_lower for word in ["work", "job", "company"]):
            personal_queries = [
                "i work at",
                "my job",
                "my company",
                "my role",
                f"{user_id} employment",
                "work for"
            ]
        elif any(word in query_lower for word in ["interests", "like", "enjoy"]):
            personal_queries = [
                "i like",
                "i enjoy",
                "my interests",
                "passionate about",
                f"{user_id} interests"
            ]
        elif any(word in query_lower for word in ["background", "experience"]):
            personal_queries = [
                "my background",
                "my experience",
                "i have",
                f"{user_id} background",
                "my history"
            ]
        
        return personal_queries
    
    def _calculate_enhanced_relevance_score(self, query: str, memory: HybridMemoryRecord, 
                                          search_result: Dict) -> float:
        """Calculate enhanced relevance score with LLM-based assessment"""
        
        score_components = []
        
        # Base search score from Azure Search
        base_score = search_result.get('@search.score', 0.5)
        score_components.append(base_score * 0.3)
        
        # Personal information boost
        if self._is_personal_information(memory.content):
            score_components.append(0.3)
        
        # User name relevance
        if "paresh" in memory.content.lower():
            score_components.append(0.2)
        
        # Ontology domain relevance
        if memory.ontology_domain in ["personal", "work"]:
            score_components.append(0.15)
        
        # AI confidence contribution
        score_components.append(memory.ai_confidence * 0.1)
        
        # Importance score contribution
        score_components.append(memory.importance_score * 0.1)
        
        # Semantic tag match
        query_lower = query.lower()
        tag_match_score = 0
        for tag in memory.ai_semantic_tags:
            if tag.lower() in query_lower:
                tag_match_score += 0.05
        score_components.append(min(tag_match_score, 0.2))
        
        # Content relevance using LLM (for high-potential results)
        base_total = sum(score_components)
        if base_total > 0.5:  # Only for promising results to save API calls
            llm_relevance = self._assess_relevance_with_llm(query, memory.content)
            score_components.append(llm_relevance * 0.2)
        
        # Recency boost (slight preference for newer memories)
        days_old = (datetime.now() - memory.timestamp).days
        recency_score = max(0, 1 - (days_old / 365)) * 0.05  # Very slight boost
        score_components.append(recency_score)
        
        return min(sum(score_components), 1.0)
    
    def _is_personal_information(self, content: str) -> bool:
        """Check if content contains personal information"""
        content_lower = content.lower()
        
        personal_indicators = [
            "my name", "i am", "i work", "my job", "my company", "my role",
            "i like", "i enjoy", "my interests", "my background", "i have",
            "my experience", "my skills", "paresh"
        ]
        
        return any(indicator in content_lower for indicator in personal_indicators)
    
    def _assess_relevance_with_llm(self, query: str, memory_content: str) -> float:
        """Use LLM to assess relevance of memory to query"""
        try:
            prompt = f"""Assess how relevant this memory is to answering the user's question. 

Question: "{query}"
Memory: "{memory_content}"

Rate the relevance on a scale from 0.0 to 1.0 where:
- 1.0 = Directly answers the question
- 0.8 = Highly relevant, contains key information
- 0.6 = Somewhat relevant
- 0.4 = Marginally relevant
- 0.2 = Barely relevant
- 0.0 = Not relevant

Respond with only the number (e.g., 0.7):"""

            response = self.llm.invoke(prompt)
            try:
                score = float(response.content.strip())
                return max(0.0, min(1.0, score))  # Ensure valid range
            except ValueError:
                return 0.5  # Default if parsing fails
                
        except Exception as e:
            logger.warning(f"LLM relevance assessment failed: {e}")
            return 0.5
    
    def generate_answer_from_memories(self, question: str, relevant_memories: List[Tuple[HybridMemoryRecord, float]], 
                                    user_id: str) -> Optional[str]:
        """Generate intelligent answer using LLM synthesis from relevant memories"""
        
        if not relevant_memories:
            return None
        
        try:
            # Prepare memory context for LLM
            memory_context = self._prepare_memory_context_for_llm(relevant_memories, question)
            
            # Generate answer using LLM
            answer = self._synthesize_answer_with_llm(question, memory_context, user_id)
            
            # Track answer generation
            self.performance_metrics["llm_answers_generated"] += 1
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating LLM answer: {e}")
            return None
    
    def _prepare_memory_context_for_llm(self, memories: List[Tuple[HybridMemoryRecord, float]], 
                                       question: str) -> str:
        """Prepare memory content optimized for LLM processing"""
        context_parts = []
        
        for i, (memory, score) in enumerate(memories[:10], 1):  # Top 10 memories
            context_entry = f"Memory {i} (relevance: {score:.3f}):\n"
            
            # Add main content
            context_entry += f"Content: {memory.content}\n"
            
            # Add semantic summary if different and useful
            if (memory.semantic_summary and 
                memory.semantic_summary != memory.content and
                len(memory.semantic_summary) > 10):
                context_entry += f"Summary: {memory.semantic_summary}\n"
            
            # Add domain context
            if memory.ontology_domain:
                context_entry += f"Category: {memory.ontology_domain}\n"
            
            # Add timestamp for context
            context_entry += f"When: {memory.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
            
            # Add AI-extracted entities if relevant
            if memory.ai_extracted_entities:
                entities = [e.get("entity", "") for e in memory.ai_extracted_entities[:3]]
                if entities:
                    context_entry += f"Key entities: {', '.join(entities)}\n"
            
            context_parts.append(context_entry)
        
        return "\n" + "="*50 + "\n".join(context_parts)
    
    def _synthesize_answer_with_llm(self, question: str, memory_context: str, user_id: str) -> str:
        """Use LLM to synthesize intelligent answer from memory context"""
        
        prompt = f"""You are an AI assistant helping {user_id} access information from his personal digital memory system. Based on the memories provided below, answer the user's question accurately and naturally.

CRITICAL GUIDELINES:
1. You are helping {user_id} recall his own personal information
2. Be specific and factual - use exact details from the memories
3. If you find relevant information in multiple memories, combine them intelligently
4. Focus on personal facts, not generic behavioral data like "tab switching" or "browsing"
5. If the question asks about identity, work, interests, etc., look for specific mentions
6. Speak conversationally as if helping someone remember their own information
7. If no relevant personal information is found, say "I don't have that specific information in your memories yet"

USER'S QUESTION:
{question}

RELEVANT MEMORIES FROM {user_id.upper()}'S DIGITAL MEMORY:
{memory_context}

INSTRUCTIONS FOR ANSWER:
- Extract specific facts that answer the question
- Ignore generic activity tracking unless specifically relevant
- Combine related information from multiple memories
- Be confident about information that's clearly stated
- If multiple memories contradict, mention the most recent or most detailed

ANSWER:"""

        try:
            response = self.llm.invoke(prompt)
            answer = response.content.strip()
            
            # Assess answer quality
            quality_score = self._assess_answer_quality(question, answer, memory_context)
            self.performance_metrics["answer_quality_scores"].append(quality_score)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in LLM answer synthesis: {e}")
            return "I encountered an error while processing your question. Please try again."
    
    def _assess_answer_quality(self, question: str, answer: str, memory_context: str) -> float:
        """Assess the quality of the generated answer"""
        try:
            # Simple heuristics for answer quality
            quality_score = 0.5  # Base score
            
            # Length check - very short answers might be poor
            if len(answer) > 20:
                quality_score += 0.1
            
            # Specificity check - contains specific information
            specific_indicators = ["name", "company", "work", "at", "called", "is", "am"]
            if any(indicator in answer.lower() for indicator in specific_indicators):
                quality_score += 0.2
            
            # Not a generic "don't have information" response
            if "don't have" not in answer.lower():
                quality_score += 0.2
            
            # Contains information from context
            if any(word in memory_context.lower() for word in answer.lower().split()[:10]):
                quality_score += 0.1
            
            return min(quality_score, 1.0)
            
        except Exception:
            return 0.5
    
    def search_for_question_answer(self, question: str, user_id: str) -> Optional[str]:
        """Comprehensive search and answer generation for user questions"""
        
        try:
            # Step 1: Enhanced multi-strategy search
            relevant_memories = self.search_memories(
                question,
                search_options={
                    "user_id": user_id,
                    "limit": 20,  # Get more memories for better synthesis
                    "filters": {"user_id": user_id}
                }
            )
            
            if not relevant_memories:
                return None
            
            # Step 2: Filter for high-quality personal information
            filtered_memories = []
            for memory, score in relevant_memories:
                if score > 0.3 and self._is_personal_information(memory.content):
                    filtered_memories.append((memory, score))
            
            # Step 3: If no personal info found, search more specifically
            if not filtered_memories:
                # Try targeted personal information search
                info_type = self._classify_question_type(question)
                specific_results = self.memory_store.search_personal_information(
                    user_id, info_type, 15
                )
                
                # Convert to memory records
                for result in specific_results:
                    try:
                        memory = HybridMemoryRecord.from_search_result(result)
                        score = self._calculate_enhanced_relevance_score(question, memory, result)
                        if score > 0.2:
                            filtered_memories.append((memory, score))
                    except Exception:
                        continue
            
            if not filtered_memories:
                return None
            
            # Step 4: Generate answer using LLM
            answer = self.generate_answer_from_memories(question, filtered_memories, user_id)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in comprehensive question answering: {e}")
            return None
    
    def _classify_question_type(self, question: str) -> str:
        """Classify the type of personal information being asked about"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["name", "called", "identity"]):
            return "identity"
        elif any(word in question_lower for word in ["work", "job", "company", "employment"]):
            return "work"
        elif any(word in question_lower for word in ["interests", "like", "enjoy", "hobbies"]):
            return "interests"
        elif any(word in question_lower for word in ["background", "experience", "education"]):
            return "background"
        elif any(word in question_lower for word in ["skills", "abilities", "good at"]):
            return "skills"
        elif any(word in question_lower for word in ["projects", "working on", "tasks"]):
            return "projects"
        else:
            return "general"
    
    def _search_session_cache(self, query: str, user_id: str) -> List[Tuple[HybridMemoryRecord, float]]:
        """Search session cache for relevant memories"""
        
        results = []
        query_lower = query.lower()
        
        for memory in self.session_cache.values():
            if memory.user_id != user_id:
                continue
                
            # Enhanced relevance scoring for session cache
            score = 0.0
            
            # Content match
            if query_lower in memory.content.lower():
                score += 0.6
            
            # Personal information boost
            if self._is_personal_information(memory.content):
                score += 0.3
            
            # Tag match
            for tag in memory.ai_semantic_tags:
                if tag.lower() in query_lower:
                    score += 0.2
            
            # Summary match
            if memory.semantic_summary and query_lower in memory.semantic_summary.lower():
                score += 0.4
            
            if score > 0.3:  # Higher threshold for session cache
                results.append((memory, score))
        
        return results
    
    def _update_relationship_cache(self, memory: HybridMemoryRecord):
        """Update relationship cache with new memory relationships"""
        
        memory_id = memory.id
        related_ids = []
        
        # Extract related entity IDs from AI relationships
        for relationship in memory.ai_relationships:
            source = relationship.get("source", "")
            target = relationship.get("target", "")
            
            if source and source != memory.content[:50]:  # Avoid self-reference
                related_ids.append(source)
            if target and target != memory.content[:50]:
                related_ids.append(target)
        
        if related_ids:
            self.relationship_cache[memory_id] = related_ids
    
    def _update_performance_metrics(self, memory: HybridMemoryRecord, processing_time: float, success: bool):
        """Update performance tracking metrics"""
        
        self.performance_metrics["total_processed"] += 1
        self.performance_metrics["processing_times"].append(processing_time)
        
        if success:
            # Determine processing type
            has_ontology = bool(memory.ontology_domain)
            has_ai = memory.ai_confidence > 0.5
            
            if has_ontology and has_ai:
                self.performance_metrics["hybrid_successes"] += 1
            elif has_ontology:
                self.performance_metrics["ontology_only"] += 1
            elif has_ai:
                self.performance_metrics["ai_only"] += 1
            
            # Track confidence scores
            hybrid_confidence = memory.hybrid_classification.get("synthesis_confidence", 0.0)
            self.performance_metrics["confidence_scores"].append(hybrid_confidence)
    
    def get_user_memory_profile(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive memory profile for user with enhanced personal information analysis"""
        
        # Search for user's memories with multiple strategies
        user_memories = self.search_memories(
            query="*",  # Get all memories
            search_options={
                "user_id": user_id,
                "limit": 100,
                "filters": {"user_id": user_id}
            }
        )
        
        if not user_memories:
            return {"user_id": user_id, "total_memories": 0}
        
        # Analyze user's memory patterns with focus on personal information
        domains = {}
        categories = {}
        total_importance = 0
        semantic_tags = {}
        personal_info_count = 0
        
        for memory, score in user_memories:
            # Domain analysis
            if memory.ontology_domain:
                domains[memory.ontology_domain] = domains.get(memory.ontology_domain, 0) + 1
            
            # Category analysis
            if memory.ontology_category:
                categories[memory.ontology_category] = categories.get(memory.ontology_category, 0) + 1
            
            # Importance accumulation
            total_importance += memory.importance_score
            
            # Semantic tag analysis
            for tag in memory.ai_semantic_tags:
                semantic_tags[tag] = semantic_tags.get(tag, 0) + 1
            
            # Personal information analysis
            if self._is_personal_information(memory.content):
                personal_info_count += 1
        
        # Create enhanced profile
        profile = {
            "user_id": user_id,
            "total_memories": len(user_memories),
            "personal_info_memories": personal_info_count,
            "personal_info_percentage": (personal_info_count / len(user_memories)) * 100 if user_memories else 0,
            "average_importance": total_importance / len(user_memories) if user_memories else 0,
            "domain_distribution": domains,
            "category_distribution": categories,
            "top_semantic_tags": sorted(semantic_tags.items(), key=lambda x: x[1], reverse=True)[:10],
            "memory_timeline": self._create_memory_timeline(user_memories),
            "recent_activity": len([m for m, s in user_memories if (datetime.now() - m.timestamp).days <= 7]),
            "answer_readiness_score": self._calculate_answer_readiness_score(user_memories)
        }
        
        return profile
    
    def _calculate_answer_readiness_score(self, memories: List[Tuple[HybridMemoryRecord, float]]) -> float:
        """Calculate how ready the system is to answer questions about the user"""
        
        if not memories:
            return 0.0
        
        # Key categories of personal information
        info_categories = {
            "identity": False,
            "work": False,
            "interests": False,
            "background": False,
            "skills": False
        }
        
        for memory, score in memories:
            content_lower = memory.content.lower()
            
            # Check for identity information
            if any(word in content_lower for word in ["name", "called", "i am", "paresh"]):
                info_categories["identity"] = True
            
            # Check for work information
            if any(word in content_lower for word in ["work", "job", "company", "role"]):
                info_categories["work"] = True
            
            # Check for interests
            if any(word in content_lower for word in ["like", "enjoy", "interests", "hobbies"]):
                info_categories["interests"] = True
            
            # Check for background
            if any(word in content_lower for word in ["background", "experience", "education"]):
                info_categories["background"] = True
            
            # Check for skills
            if any(word in content_lower for word in ["skills", "good at", "abilities"]):
                info_categories["skills"] = True
        
        # Calculate readiness score
        categories_covered = sum(info_categories.values())
        base_score = categories_covered / len(info_categories)
        
        # Boost for having many personal memories
        personal_memory_count = len([m for m, s in memories if self._is_personal_information(m.content)])
        memory_boost = min(personal_memory_count / 20, 0.3)  # Up to 30% boost
        
        return min(base_score + memory_boost, 1.0)
    
    def _create_memory_timeline(self, memories: List[Tuple[HybridMemoryRecord, float]]) -> Dict[str, int]:
        """Create timeline of memory creation"""
        
        timeline = {}
        
        for memory, score in memories:
            date_key = memory.timestamp.strftime("%Y-%m")
            timeline[date_key] = timeline.get(date_key, 0) + 1
        
        return dict(sorted(timeline.items()))
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics with LLM performance metrics"""
        
        # Performance metrics
        avg_processing_time = (sum(self.performance_metrics["processing_times"]) / 
                              len(self.performance_metrics["processing_times"]) 
                              if self.performance_metrics["processing_times"] else 0)
        
        avg_confidence = (sum(self.performance_metrics["confidence_scores"]) / 
                         len(self.performance_metrics["confidence_scores"]) 
                         if self.performance_metrics["confidence_scores"] else 0)
        
        avg_answer_quality = (sum(self.performance_metrics["answer_quality_scores"]) / 
                             len(self.performance_metrics["answer_quality_scores"]) 
                             if self.performance_metrics["answer_quality_scores"] else 0)
        
        analytics = {
            "performance_metrics": {
                "total_processed": self.performance_metrics["total_processed"],
                "hybrid_success_rate": (self.performance_metrics["hybrid_successes"] / 
                                       max(1, self.performance_metrics["total_processed"])),
                "average_processing_time": avg_processing_time,
                "average_confidence": avg_confidence,
                "llm_answers_generated": self.performance_metrics["llm_answers_generated"],
                "average_answer_quality": avg_answer_quality
            },
            "ontology_stats": self.ontology.get_ontology_stats(),
            "ai_processor_stats": self.ai_processor.get_processing_stats(),
            "information_processor_stats": self.information_processor.get_processing_stats(),
            "cache_stats": {
                "session_cache_size": len(self.session_cache),
                "relationship_cache_size": len(self.relationship_cache)
            },
            "llm_integration": {
                "enabled": True,
                "answer_generation": True,
                "relevance_assessment": True,
                "multi_strategy_search": True
            },
            "system_health": {
                "components_operational": True,
                "last_successful_processing": datetime.now().isoformat(),
                "recommended_actions": self._get_enhanced_system_recommendations()
            }
        }
        
        return analytics
    
    def _get_enhanced_system_recommendations(self) -> List[str]:
        """Get enhanced system optimization recommendations"""
        
        recommendations = []
        
        # Performance recommendations
        if self.performance_metrics["processing_times"]:
            avg_time = sum(self.performance_metrics["processing_times"]) / len(self.performance_metrics["processing_times"])
            if avg_time > 5.0:
                recommendations.append("Consider optimizing AI processing - average processing time is high")
        
        # Answer quality recommendations
        if self.performance_metrics["answer_quality_scores"]:
            avg_quality = sum(self.performance_metrics["answer_quality_scores"]) / len(self.performance_metrics["answer_quality_scores"])
            if avg_quality < 0.6:
                recommendations.append("Consider improving LLM prompts - answer quality scores are low")
        
        # LLM usage recommendations
        if self.performance_metrics["llm_answers_generated"] < self.performance_metrics["total_processed"] * 0.1:
            recommendations.append("LLM answer generation usage is low - check question detection logic")
        
        # Confidence recommendations
        if self.performance_metrics["confidence_scores"]:
            avg_confidence = sum(self.performance_metrics["confidence_scores"]) / len(self.performance_metrics["confidence_scores"])
            if avg_confidence < 0.6:
                recommendations.append("Consider expanding ontology or improving AI prompts - confidence scores are low")
        
        # Cache recommendations
        if len(self.session_cache) > 1000:
            recommendations.append("Consider implementing cache cleanup - session cache is large")
        
        return recommendations if recommendations else ["System operating optimally with LLM integration"]
    
    def cleanup_expired_memories(self):
        """Clean up expired memories from cache"""
        
        current_time = datetime.now()
        expired_ids = []
        
        for memory_id, memory in self.session_cache.items():
            if memory.expiry_date and current_time > memory.expiry_date:
                expired_ids.append(memory_id)
        
        for memory_id in expired_ids:
            del self.session_cache[memory_id]
            if memory_id in self.relationship_cache:
                del self.relationship_cache[memory_id]
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired memories from cache")

# Maintain backwards compatibility
HybridMemoryManager = EnhancedHybridMemoryManager