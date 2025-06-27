import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from langchain_openai import AzureChatOpenAI
import logging

logger = logging.getLogger(__name__)

@dataclass
class AIAnalysisResult:
    """Result of AI semantic analysis"""
    content: str
    semantic_concepts: List[Dict[str, Any]] = field(default_factory=list)
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    context_understanding: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    reasoning: str = ""
    suggested_properties: Dict[str, Any] = field(default_factory=dict)
    semantic_tags: List[str] = field(default_factory=list)

@dataclass
class SemanticEnrichment:
    """Semantic enrichment of memory content"""
    abstract_concepts: List[str] = field(default_factory=list)
    emotional_context: Dict[str, float] = field(default_factory=dict)
    temporal_references: List[Dict[str, Any]] = field(default_factory=list)
    implicit_relationships: List[Dict[str, Any]] = field(default_factory=list)
    domain_expertise: Dict[str, float] = field(default_factory=dict)
    contextual_importance: float = 0.0

@dataclass
class QuestionAnalysis:
    """Analysis of user questions for better understanding"""
    question_type: str = ""  # "identity", "work", "interests", "factual", etc.
    information_sought: List[str] = field(default_factory=list)
    key_terms: List[str] = field(default_factory=list)
    search_strategies: List[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""

class EnhancedAISemanticProcessor:
    """Enhanced AI-powered semantic processing with question interpretation and answer generation"""
    
    def __init__(self, llm: AzureChatOpenAI, ontology):
        self.llm = llm
        self.ontology = ontology
        self.processing_history = []
        self.question_analysis_cache = {}
        
    def analyze_content(self, content: str, user_context: Dict[str, Any] = None) -> AIAnalysisResult:
        """Perform comprehensive AI analysis of memory content"""
        
        # Get ontology context for guidance
        ontology_classifications = self.ontology.classify_content(content)
        
        # Build analysis prompt
        analysis_prompt = self._build_analysis_prompt(content, ontology_classifications, user_context)
        
        try:
            # Get AI analysis
            ai_response = self.llm.invoke(analysis_prompt)
            
            # Parse AI response
            analysis_result = self._parse_ai_analysis(content, ai_response)
            
            # Enhance with semantic enrichment
            enrichment = self._perform_semantic_enrichment(content, analysis_result)
            analysis_result.semantic_concepts.append({"enrichment": enrichment})
            
            # Store processing history
            self.processing_history.append({
                "timestamp": datetime.now().isoformat(),
                "content": content[:100] + "..." if len(content) > 100 else content,
                "confidence": analysis_result.confidence_score,
                "concepts_found": len(analysis_result.semantic_concepts)
            })
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._create_fallback_analysis(content, ontology_classifications)
    
    def analyze_question(self, question: str, user_context: Dict[str, Any] = None) -> QuestionAnalysis:
        """Analyze user questions to understand what information they're seeking"""
        
        # Check cache first
        cache_key = f"{question.lower().strip()}_{user_context.get('user_id', 'default') if user_context else 'default'}"
        if cache_key in self.question_analysis_cache:
            return self.question_analysis_cache[cache_key]
        
        try:
            analysis_prompt = self._build_question_analysis_prompt(question, user_context)
            ai_response = self.llm.invoke(analysis_prompt)
            analysis = self._parse_question_analysis(question, ai_response)
            
            # Cache the result
            self.question_analysis_cache[cache_key] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Question analysis failed: {e}")
            return self._create_fallback_question_analysis(question)
    
    def generate_answer_from_context(self, question: str, memory_contexts: List[Dict[str, Any]], 
                                   user_id: str) -> str:
        """Generate intelligent answers from memory contexts using LLM"""
        
        try:
            # Prepare context for LLM
            formatted_context = self._format_memory_contexts_for_answer(memory_contexts)
            
            # Build answer generation prompt
            answer_prompt = self._build_answer_generation_prompt(question, formatted_context, user_id)
            
            # Generate answer
            ai_response = self.llm.invoke(answer_prompt)
            answer = ai_response.content.strip()
            
            # Post-process answer
            processed_answer = self._post_process_answer(answer, question, user_id)
            
            return processed_answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return f"I encountered an error while generating an answer to your question. Please try again."
    
    def extract_personal_information(self, content: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced extraction of personal information from content"""
        
        try:
            extraction_prompt = self._build_personal_extraction_prompt(content, user_context)
            ai_response = self.llm.invoke(extraction_prompt)
            extracted_info = self._parse_personal_extraction(content, ai_response)
            
            return extracted_info
            
        except Exception as e:
            logger.error(f"Personal information extraction failed: {e}")
            return {}
    
    def _build_question_analysis_prompt(self, question: str, user_context: Dict[str, Any] = None) -> str:
        """Build prompt for analyzing user questions"""
        
        user_id = user_context.get('user_id', 'the user') if user_context else 'the user'
        
        prompt = f"""Analyze the following question to understand what personal information the user is seeking about themselves.

QUESTION: "{question}"
USER: {user_id}

Analyze and respond in this JSON format:
{{
    "question_type": "identity|work|interests|background|skills|projects|relationships|preferences|factual|general",
    "information_sought": ["specific information items the user wants to know"],
    "key_terms": ["important terms to search for"],
    "search_strategies": ["direct search terms", "semantic variations", "related concepts"],
    "confidence": 0.9,
    "reasoning": "explanation of the analysis"
}}

QUESTION TYPES:
- identity: Name, what they're called, personal identity
- work: Job, company, role, career, employment
- interests: Hobbies, likes, dislikes, preferences, passions
- background: History, experience, education, credentials
- skills: Abilities, expertise, what they're good at
- projects: Current work, tasks, assignments they're working on
- relationships: Family, friends, colleagues, connections
- preferences: Likes, dislikes, preferred ways of doing things
- factual: Specific facts about their life, situation, circumstances
- general: Broad questions about themselves

EXAMPLES:
- "What's my name?" → identity type, seeking name/identity information
- "Where do I work?" → work type, seeking employment information
- "What are my interests?" → interests type, seeking hobby/preference information

Respond with only the JSON:"""

        return prompt
    
    def _build_personal_extraction_prompt(self, content: str, user_context: Dict[str, Any] = None) -> str:
        """Build prompt for extracting personal information"""
        
        user_id = user_context.get('user_id', 'user') if user_context else 'user'
        
        prompt = f"""Extract personal information from this text about {user_id}. Focus on facts that would help answer personal questions about them.

TEXT: "{content}"

Extract information in this JSON format:
{{
    "identity": {{
        "name": "extracted name if mentioned",
        "title": "professional title if mentioned",
        "identity_facts": ["any identity-related facts"]
    }},
    "work": {{
        "company": "company name if mentioned",
        "role": "job role if mentioned", 
        "responsibilities": ["work responsibilities if mentioned"],
        "work_facts": ["any work-related facts"]
    }},
    "interests": {{
        "likes": ["things they like or enjoy"],
        "dislikes": ["things they dislike"],
        "hobbies": ["hobbies or interests mentioned"],
        "preferences": ["stated preferences"]
    }},
    "background": {{
        "experience": ["experience or background mentioned"],
        "education": ["education if mentioned"],
        "history": ["relevant background facts"]
    }},
    "skills": {{
        "abilities": ["skills or abilities mentioned"],
        "expertise": ["areas of expertise"],
        "good_at": ["things they're good at"]
    }},
    "personal_facts": ["any other personal facts that would help answer questions about them"],
    "confidence": 0.8,
    "reasoning": "why this information is relevant for answering personal questions"
}}

IMPORTANT:
- Only extract information that's explicitly stated or clearly implied
- Focus on facts that would help answer "What's my name?", "Where do I work?", "What are my interests?" etc.
- Ignore generic activity tracking like "browsed website" or "clicked button"
- Be specific and factual

Respond with only the JSON:"""

        return prompt
    
    def _build_answer_generation_prompt(self, question: str, memory_context: str, user_id: str) -> str:
        """Build prompt for generating answers from memory context"""
        
        prompt = f"""You are helping {user_id} access information from their personal digital memory system. Based on the memory contexts below, provide a specific, accurate answer to their question.

QUESTION: {question}

MEMORY CONTEXTS:
{memory_context}

GUIDELINES:
1. Answer as if helping {user_id} remember their own information
2. Be specific and factual - use exact details from the memories
3. Combine information from multiple memories if relevant
4. Focus on personal facts, ignore generic behavioral data
5. If you find the answer, be confident and specific
6. If the information isn't in the memories, say "I don't have that information in your memories yet"
7. Speak naturally and conversationally

EXAMPLE GOOD ANSWERS:
- "Your name is Paresh"
- "You work at Tavant Technologies as a software engineer"
- "You enjoy working on AI automation projects"

EXAMPLE BAD ANSWERS:
- "Based on the memories..." (too formal)
- "The data suggests..." (too analytical)
- Generic responses without specific facts

Provide a direct, helpful answer:"""

        return prompt
    
    def _format_memory_contexts_for_answer(self, memory_contexts: List[Dict[str, Any]]) -> str:
        """Format memory contexts for answer generation"""
        
        if not memory_contexts:
            return "No relevant memories found."
        
        formatted_contexts = []
        
        for i, context in enumerate(memory_contexts[:8], 1):  # Limit to top 8
            context_text = f"Memory {i}:\n"
            
            if 'content' in context:
                context_text += f"Content: {context['content']}\n"
            
            if 'summary' in context and context['summary']:
                context_text += f"Summary: {context['summary']}\n"
            
            if 'relevance_score' in context:
                context_text += f"Relevance: {context['relevance_score']:.2f}\n"
            
            if 'timestamp' in context:
                context_text += f"When: {context['timestamp']}\n"
            
            formatted_contexts.append(context_text)
        
        return "\n" + "="*30 + "\n".join(formatted_contexts)
    
    def _build_analysis_prompt(self, content: str, ontology_classifications: List[Dict], 
                              user_context: Dict[str, Any] = None) -> str:
        """Build comprehensive analysis prompt for AI"""
        
        # Prepare ontology context
        ontology_context = ""
        if ontology_classifications:
            ontology_context = "ONTOLOGY SUGGESTS:\n"
            for i, classification in enumerate(ontology_classifications[:3]):  # Top 3
                ontology_context += f"{i+1}. Domain: {classification['domain']}, Category: {classification['category']}, Score: {classification['score']:.2f}\n"
        
        # Prepare user context
        context_str = ""
        if user_context:
            context_str = f"USER CONTEXT: {json.dumps(user_context, indent=2)}\n"
        
        prompt = f"""You are an advanced semantic analyzer for a digital twin memory system. Analyze the following content and provide comprehensive understanding with enhanced focus on personal information extraction.

CONTENT TO ANALYZE:
"{content}"

{ontology_context}

{context_str}

ANALYSIS REQUIRED:
1. SEMANTIC CONCEPTS: Identify key concepts, themes, and abstract ideas
2. ENTITIES: Extract people, places, objects, dates, numbers, organizations
3. RELATIONSHIPS: Identify connections between entities and concepts
4. CONTEXT UNDERSTANDING: Interpret implicit meaning, intent, and significance
5. PERSONAL INFORMATION: Detect and extract personal facts that could answer questions
6. TEMPORAL ASPECTS: Identify time references, deadlines, schedules
7. DOMAIN CLASSIFICATION: Best domain(s) and categories for this content
8. ANSWER POTENTIAL: How useful this content would be for answering personal questions

RESPOND IN THIS JSON FORMAT:
{{
    "semantic_concepts": [
        {{
            "concept": "concept_name",
            "relevance": 0.95,
            "type": "abstract|concrete|relational|personal",
            "description": "what this concept represents in the content"
        }}
    ],
    "extracted_entities": [
        {{
            "entity": "entity_name",
            "type": "person|place|organization|date|time|number|object|personal_fact",
            "value": "extracted_value",
            "context": "how this entity appears in content",
            "importance": 0.8,
            "personal_relevance": 0.9
        }}
    ],
    "relationships": [
        {{
            "source": "entity_or_concept",
            "target": "entity_or_concept", 
            "relationship_type": "works_with|located_at|called|is|has|likes|dislikes|good_at",
            "strength": 0.7,
            "description": "nature of the relationship"
        }}
    ],
    "context_understanding": {{
        "primary_intent": "what the user is trying to communicate",
        "implicit_meaning": "what's implied but not stated",
        "urgency_level": "low|medium|high|critical",
        "importance_level": "low|medium|high|critical",
        "emotional_tone": "neutral|positive|negative|excited|concerned|frustrated",
        "temporal_scope": "immediate|short_term|long_term|permanent",
        "personal_information_type": "identity|work|interests|background|skills|preferences|none"
    }},
    "domain_classification": {{
        "primary_domain": "personal|work|health|family|finance|education|travel|hobbies|social",
        "secondary_domains": ["domain1", "domain2"],
        "confidence": 0.9,
        "reasoning": "why this domain classification"
    }},
    "suggested_properties": {{
        "key_property_1": "value",
        "key_property_2": "value"
    }},
    "semantic_tags": ["tag1", "tag2", "tag3"],
    "personal_facts": ["extractable personal facts that could answer questions"],
    "answer_potential": {{
        "can_answer_about_identity": 0.8,
        "can_answer_about_work": 0.6,
        "can_answer_about_interests": 0.4,
        "overall_usefulness": 0.7
    }},
    "confidence_score": 0.85,
    "reasoning": "detailed explanation of analysis decisions"
}}

IMPORTANT:
- Focus heavily on extracting personal information
- Identify facts that could answer questions like "What's my name?", "Where do I work?", etc.
- Distinguish between personal facts and generic activity tracking
- Be thorough but concise
- Consider context and implications
- Provide confidence scores for assessments
"""
        
        return prompt
    
    def _parse_ai_analysis(self, content: str, ai_response) -> AIAnalysisResult:
        """Parse AI response into structured analysis result"""
        
        try:
            # Handle LangChain AIMessage object
            if hasattr(ai_response, 'content'):
                response_text = ai_response.content.strip()
            else:
                response_text = str(ai_response).strip()
            
            # Remove any non-JSON content before/after JSON
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].strip()
            
            # Find JSON content if wrapped in other text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse JSON response
            if response_text:
                analysis_data = json.loads(response_text)
            else:
                raise json.JSONDecodeError("Empty response", "", 0)
            
            return AIAnalysisResult(
                content=content,
                semantic_concepts=analysis_data.get("semantic_concepts", []),
                extracted_entities=analysis_data.get("extracted_entities", []),
                relationships=analysis_data.get("relationships", []),
                context_understanding=analysis_data.get("context_understanding", {}),
                confidence_score=analysis_data.get("confidence_score", 0.0),
                reasoning=analysis_data.get("reasoning", ""),
                suggested_properties=analysis_data.get("suggested_properties", {}),
                semantic_tags=analysis_data.get("semantic_tags", [])
            )
            
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            # Try to extract structured information from text response
            return self._parse_text_response(content, response_text if 'response_text' in locals() else str(ai_response))
    
    def _parse_question_analysis(self, question: str, ai_response) -> QuestionAnalysis:
        """Parse AI response for question analysis"""
        
        try:
            if hasattr(ai_response, 'content'):
                response_text = ai_response.content.strip()
            else:
                response_text = str(ai_response).strip()
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            if response_text:
                analysis_data = json.loads(response_text)
            else:
                raise json.JSONDecodeError("Empty response", "", 0)
            
            return QuestionAnalysis(
                question_type=analysis_data.get("question_type", "general"),
                information_sought=analysis_data.get("information_sought", []),
                key_terms=analysis_data.get("key_terms", []),
                search_strategies=analysis_data.get("search_strategies", []),
                confidence=analysis_data.get("confidence", 0.5),
                reasoning=analysis_data.get("reasoning", "")
            )
            
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse question analysis: {e}")
            return self._create_fallback_question_analysis(question)
    
    def _parse_personal_extraction(self, content: str, ai_response) -> Dict[str, Any]:
        """Parse AI response for personal information extraction"""
        
        try:
            if hasattr(ai_response, 'content'):
                response_text = ai_response.content.strip()
            else:
                response_text = str(ai_response).strip()
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            if response_text:
                return json.loads(response_text)
            else:
                return {}
                
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse personal extraction: {e}")
            return {}
    
    def _post_process_answer(self, answer: str, question: str, user_id: str) -> str:
        """Post-process generated answers for better quality"""
        
        # Remove common LLM artifacts
        answer = answer.replace("Based on the memories,", "").strip()
        answer = answer.replace("According to your memories,", "").strip()
        answer = answer.replace("From the memory contexts,", "").strip()
        
        # Ensure answer starts with capital letter
        if answer and not answer[0].isupper():
            answer = answer[0].upper() + answer[1:]
        
        # Add period if missing
        if answer and not answer.endswith(('.', '!', '?')):
            answer += "."
        
        # Handle empty or generic answers
        if not answer or len(answer.strip()) < 10:
            return f"I don't have specific information to answer '{question}' in your memories yet."
        
        # Check for generic non-answers
        generic_phrases = [
            "i don't have", "no information", "not found", "cannot find",
            "unable to determine", "no specific", "no relevant"
        ]
        
        if any(phrase in answer.lower() for phrase in generic_phrases):
            # Return as-is since it's appropriately indicating no information
            return answer
        
        return answer
    
    def _create_fallback_question_analysis(self, question: str) -> QuestionAnalysis:
        """Create fallback question analysis"""
        
        question_lower = question.lower()
        
        # Simple heuristic classification
        if any(word in question_lower for word in ["name", "called", "identity"]):
            question_type = "identity"
            key_terms = ["name", "called", "identity"]
        elif any(word in question_lower for word in ["work", "job", "company"]):
            question_type = "work"
            key_terms = ["work", "job", "company", "employment"]
        elif any(word in question_lower for word in ["interests", "like", "enjoy"]):
            question_type = "interests"
            key_terms = ["interests", "like", "enjoy", "hobbies"]
        else:
            question_type = "general"
            key_terms = question.lower().split()[:5]
        
        return QuestionAnalysis(
            question_type=question_type,
            information_sought=[question_type],
            key_terms=key_terms,
            search_strategies=key_terms,
            confidence=0.6,
            reasoning="Fallback heuristic analysis"
        )
    
    def _parse_text_response(self, content: str, ai_response: str) -> AIAnalysisResult:
        """Fallback: Parse text response when JSON parsing fails"""
        
        # Extract key information using regex patterns
        semantic_tags = []
        confidence = 0.5
        reasoning = ai_response[:200] + "..." if len(ai_response) > 200 else ai_response
        
        # Look for common patterns
        if "work" in ai_response.lower():
            semantic_tags.append("work")
        if "personal" in ai_response.lower():
            semantic_tags.append("personal")
        if "name" in ai_response.lower():
            semantic_tags.append("identity")
        if "company" in ai_response.lower():
            semantic_tags.append("employment")
            
        return AIAnalysisResult(
            content=content,
            confidence_score=confidence,
            reasoning=reasoning,
            semantic_tags=semantic_tags
        )
    
    def _perform_semantic_enrichment(self, content: str, analysis: AIAnalysisResult) -> SemanticEnrichment:
        """Perform additional semantic enrichment with focus on personal information"""
        
        enrichment = SemanticEnrichment()
        
        # Extract abstract concepts
        for concept in analysis.semantic_concepts:
            if concept.get("type") == "abstract":
                enrichment.abstract_concepts.append(concept.get("concept", ""))
        
        # Enhanced emotional context analysis
        emotional_context = analysis.context_understanding.get("emotional_tone", "neutral")
        enrichment.emotional_context = {
            "primary_emotion": emotional_context,
            "intensity": self._calculate_emotional_intensity(content),
            "valence": self._calculate_emotional_valence(content),
            "personal_significance": self._assess_personal_significance(content)
        }
        
        # Extract temporal references
        temporal_scope = analysis.context_understanding.get("temporal_scope", "immediate")
        enrichment.temporal_references = [{
            "scope": temporal_scope,
            "urgency": analysis.context_understanding.get("urgency_level", "medium"),
            "extracted_times": self._extract_time_references(content)
        }]
        
        # Calculate contextual importance with personal info boost
        importance_level = analysis.context_understanding.get("importance_level", "medium")
        importance_map = {"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 1.0}
        base_importance = importance_map.get(importance_level, 0.6)
        
        # Boost for personal information
        personal_boost = 0.0
        if self._contains_personal_information(content):
            personal_boost = 0.3
        
        enrichment.contextual_importance = min(base_importance + personal_boost, 1.0)
        
        # Enhanced relationship extraction
        for relationship in analysis.relationships:
            if relationship.get("strength", 0) > 0.6:  # High-confidence relationships
                relationship_info = {
                    "type": "strong_connection",
                    "elements": [relationship.get("source"), relationship.get("target")],
                    "nature": relationship.get("relationship_type"),
                    "personal_relevance": self._assess_relationship_personal_relevance(relationship)
                }
                enrichment.implicit_relationships.append(relationship_info)
        
        return enrichment
    
    def _contains_personal_information(self, content: str) -> bool:
        """Check if content contains personal information"""
        content_lower = content.lower()
        
        personal_indicators = [
            "my name", "i am", "i work", "my job", "my company", "my role",
            "i like", "i enjoy", "my interests", "my background", "i have",
            "my experience", "my skills", "paresh", "call me", "i'm called"
        ]
        
        return any(indicator in content_lower for indicator in personal_indicators)
    
    def _assess_personal_significance(self, content: str) -> float:
        """Assess how personally significant the content is"""
        
        significance_score = 0.0
        content_lower = content.lower()
        
        # High significance indicators
        high_significance = ["my name", "i am", "my identity", "call me", "my background"]
        medium_significance = ["my work", "my job", "my company", "my interests", "i like"]
        low_significance = ["i went", "i saw", "i clicked", "browsed", "visited"]
        
        for indicator in high_significance:
            if indicator in content_lower:
                significance_score += 0.3
        
        for indicator in medium_significance:
            if indicator in content_lower:
                significance_score += 0.2
        
        for indicator in low_significance:
            if indicator in content_lower:
                significance_score -= 0.1  # Reduce for generic activity
        
        return max(0.0, min(1.0, significance_score))
    
    def _assess_relationship_personal_relevance(self, relationship: Dict[str, Any]) -> float:
        """Assess how personally relevant a relationship is"""
        
        relationship_type = relationship.get("relationship_type", "")
        source = str(relationship.get("source", "")).lower()
        target = str(relationship.get("target", "")).lower()
        
        # Personal relationship types
        personal_types = ["is", "called", "works_with", "likes", "dislikes", "good_at", "has"]
        
        relevance = 0.5  # Base relevance
        
        if relationship_type in personal_types:
            relevance += 0.3
        
        if "paresh" in source or "paresh" in target:
            relevance += 0.2
        
        if any(term in source or term in target for term in ["i", "my", "me"]):
            relevance += 0.2
        
        return min(1.0, relevance)
    
    def _calculate_emotional_intensity(self, content: str) -> float:
        """Calculate emotional intensity from content"""
        intensity_indicators = {
            "very": 0.8, "extremely": 1.0, "really": 0.7, "super": 0.8,
            "urgent": 0.9, "critical": 1.0, "emergency": 1.0,
            "love": 0.8, "hate": 0.8, "amazing": 0.8, "terrible": 0.8,
            "passionate": 0.9, "excited": 0.8, "frustrated": 0.7
        }
        
        content_lower = content.lower()
        max_intensity = 0.0
        
        for indicator, intensity in intensity_indicators.items():
            if indicator in content_lower:
                max_intensity = max(max_intensity, intensity)
        
        return max_intensity if max_intensity > 0 else 0.3  # Default mild intensity
    
    def _calculate_emotional_valence(self, content: str) -> float:
        """Calculate emotional valence (positive/negative) from content"""
        positive_words = ["love", "like", "enjoy", "happy", "great", "amazing", "excellent", "good", "excited", "passionate"]
        negative_words = ["hate", "dislike", "terrible", "bad", "awful", "frustrated", "angry", "sad", "disappointed"]
        
        content_lower = content.lower()
        positive_score = sum(1 for word in positive_words if word in content_lower)
        negative_score = sum(1 for word in negative_words if word in content_lower)
        
        if positive_score > negative_score:
            return 0.7  # Positive
        elif negative_score > positive_score:
            return -0.7  # Negative
        else:
            return 0.0  # Neutral
    
    def _extract_time_references(self, content: str) -> List[str]:
        """Extract time references from content"""
        time_patterns = [
            r'\b(?:today|tomorrow|yesterday)\b',
            r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b\d{1,2}:\d{2}\s*(?:am|pm)?\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\b(?:next|last)\s+(?:week|month|year)\b',
            r'\b(?:in|after)\s+\d+\s+(?:minutes|hours|days|weeks|months)\b'
        ]
        
        found_times = []
        content_lower = content.lower()
        
        for pattern in time_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            found_times.extend(matches)
        
        return found_times
    
    def _create_fallback_analysis(self, content: str, ontology_classifications: List[Dict]) -> AIAnalysisResult:
        """Create fallback analysis when AI processing fails"""
        
        # Use ontology classifications as backup
        semantic_concepts = []
        semantic_tags = []
        
        if ontology_classifications:
            best_classification = ontology_classifications[0]
            semantic_concepts.append({
                "concept": best_classification["concept_name"],
                "relevance": best_classification["score"],
                "type": "ontology_derived",
                "description": f"Classified as {best_classification['domain']} - {best_classification['category']}"
            })
            semantic_tags.extend([best_classification["domain"], best_classification["category"]])
        
        # Basic entity extraction
        extracted_entities = self._basic_entity_extraction(content)
        
        # Enhanced context understanding with personal info detection
        context_understanding = {
            "primary_intent": "information_sharing",
            "urgency_level": "medium",
            "importance_level": "high" if self._contains_personal_information(content) else "medium",
            "emotional_tone": "neutral",
            "temporal_scope": "immediate",
            "personal_information_type": self._detect_personal_info_type(content)
        }
        
        return AIAnalysisResult(
            content=content,
            semantic_concepts=semantic_concepts,
            extracted_entities=extracted_entities,
            context_understanding=context_understanding,
            confidence_score=0.6,  # Higher confidence for fallback
            reasoning="Fallback analysis using ontology classification and enhanced extraction",
            semantic_tags=semantic_tags
        )
    
    def _detect_personal_info_type(self, content: str) -> str:
        """Detect type of personal information in content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["name", "called", "i am"]):
            return "identity"
        elif any(word in content_lower for word in ["work", "job", "company"]):
            return "work"
        elif any(word in content_lower for word in ["like", "enjoy", "interests"]):
            return "interests"
        elif any(word in content_lower for word in ["background", "experience"]):
            return "background"
        elif any(word in content_lower for word in ["skills", "good at", "abilities"]):
            return "skills"
        else:
            return "none"
    
    def _basic_entity_extraction(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced basic entity extraction without AI"""
        entities = []
        
        # Extract potential names (capitalized words)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        names = re.findall(name_pattern, content)
        for name in names:
            if len(name.split()) <= 3:  # Reasonable name length
                personal_relevance = 0.8 if "paresh" in name.lower() else 0.6
                entities.append({
                    "entity": name,
                    "type": "person",
                    "value": name,
                    "context": "capitalized_word_pattern",
                    "importance": 0.6,
                    "personal_relevance": personal_relevance
                })
        
        # Extract times
        time_pattern = r'\b\d{1,2}:\d{2}\s*(?:am|pm)?\b'
        times = re.findall(time_pattern, content, re.IGNORECASE)
        for time in times:
            entities.append({
                "entity": time,
                "type": "time",
                "value": time,
                "context": "time_pattern",
                "importance": 0.7,
                "personal_relevance": 0.4
            })
        
        # Extract dates
        date_pattern = r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'
        dates = re.findall(date_pattern, content)
        for date in dates:
            entities.append({
                "entity": date,
                "type": "date",
                "value": date,
                "context": "date_pattern",
                "importance": 0.8,
                "personal_relevance": 0.5
            })
        
        # Extract potential personal facts
        personal_patterns = [
            (r'(?:my name is|i am called|call me)\s+([A-Za-z]+)', "identity"),
            (r'(?:i work at|my company is)\s+([A-Za-z\s]+)', "work"),
            (r'(?:i like|i enjoy)\s+([^\.]+)', "interests")
        ]
        
        for pattern, fact_type in personal_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "entity": match.strip(),
                    "type": "personal_fact",
                    "value": match.strip(),
                    "context": f"{fact_type}_extraction",
                    "importance": 0.9,
                    "personal_relevance": 1.0
                })
        
        return entities
    
    def enhance_ontology_classification(self, content: str, 
                                       ontology_classifications: List[Dict],
                                       ai_analysis: AIAnalysisResult) -> List[Dict[str, Any]]:
        """Enhance ontology classifications with AI insights"""
        
        enhanced_classifications = []
        
        # Combine ontology and AI classifications
        for ontology_class in ontology_classifications:
            enhanced_class = ontology_class.copy()
            
            # Add AI-derived confidence boost
            ai_domain = ai_analysis.context_understanding.get("domain_classification", {}).get("primary_domain")
            if ai_domain and ai_domain == ontology_class["domain"]:
                enhanced_class["score"] *= 1.2  # Boost score when AI agrees
                enhanced_class["ai_confirmation"] = True
            
            # Add personal information boost
            if self._contains_personal_information(content):
                enhanced_class["score"] *= 1.3
                enhanced_class["personal_info_boost"] = True
            
            # Add AI-discovered properties
            enhanced_class["ai_properties"] = ai_analysis.suggested_properties
            enhanced_class["ai_tags"] = ai_analysis.semantic_tags
            enhanced_class["ai_entities"] = [e["entity"] for e in ai_analysis.extracted_entities]
            
            enhanced_classifications.append(enhanced_class)
        
        # Add purely AI-discovered classifications
        ai_domain = ai_analysis.context_understanding.get("domain_classification", {})
        if ai_domain.get("primary_domain"):
            # Check if AI found a domain not in ontology classifications
            ontology_domains = [c["domain"] for c in ontology_classifications]
            if ai_domain["primary_domain"] not in ontology_domains:
                enhanced_classifications.append({
                    "concept_id": f"ai_discovered_{ai_domain['primary_domain']}",
                    "concept_name": f"AI Discovered: {ai_domain['primary_domain'].title()}",
                    "domain": ai_domain["primary_domain"],
                    "category": "ai_derived",
                    "score": ai_domain.get("confidence", 0.7),
                    "matched_terms": ai_analysis.semantic_tags,
                    "properties": list(ai_analysis.suggested_properties.keys()),
                    "ai_generated": True,
                    "ai_reasoning": ai_domain.get("reasoning", ""),
                    "personal_info_detected": self._contains_personal_information(content)
                })
        
        return enhanced_classifications
    
    def generate_semantic_summary(self, ai_analysis: AIAnalysisResult) -> str:
        """Generate a human-readable semantic summary with personal info focus"""
        
        summary_parts = []
        
        # Primary understanding
        primary_intent = ai_analysis.context_understanding.get("primary_intent", "")
        if primary_intent:
            summary_parts.append(f"Intent: {primary_intent}")
        
        # Personal information type
        personal_info_type = ai_analysis.context_understanding.get("personal_information_type", "none")
        if personal_info_type != "none":
            summary_parts.append(f"Personal info: {personal_info_type}")
        
        # Key concepts with personal focus
        if ai_analysis.semantic_concepts:
            personal_concepts = [c.get("concept", "") for c in ai_analysis.semantic_concepts 
                               if c.get("type") == "personal"]
            if personal_concepts:
                summary_parts.append(f"Personal concepts: {', '.join(personal_concepts[:2])}")
            else:
                top_concepts = [c.get("concept", "") for c in ai_analysis.semantic_concepts[:2]]
                summary_parts.append(f"Key concepts: {', '.join(top_concepts)}")
        
        # Important entities with personal relevance
        if ai_analysis.extracted_entities:
            personal_entities = [e["entity"] for e in ai_analysis.extracted_entities 
                               if e.get("personal_relevance", 0) > 0.7]
            if personal_entities:
                summary_parts.append(f"Personal entities: {', '.join(personal_entities[:2])}")
        
        # Context
        urgency = ai_analysis.context_understanding.get("urgency_level", "")
        importance = ai_analysis.context_understanding.get("importance_level", "")
        if urgency != "medium" or importance != "medium":
            context_info = []
            if urgency and urgency != "medium":
                context_info.append(f"urgency: {urgency}")
            if importance and importance != "medium":
                context_info.append(f"importance: {importance}")
            if context_info:
                summary_parts.append(f"Context: {', '.join(context_info)}")
        
        return " | ".join(summary_parts) if summary_parts else "General information"
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about AI processing performance"""
        
        if not self.processing_history:
            return {"total_processed": 0}
        
        confidences = [entry["confidence"] for entry in self.processing_history]
        concept_counts = [entry["concepts_found"] for entry in self.processing_history]
        
        return {
            "total_processed": len(self.processing_history),
            "average_confidence": sum(confidences) / len(confidences),
            "average_concepts_per_analysis": sum(concept_counts) / len(concept_counts),
            "high_confidence_rate": len([c for c in confidences if c > 0.8]) / len(confidences),
            "question_analysis_cache_size": len(self.question_analysis_cache),
            "personal_info_processing_enabled": True,
            "answer_generation_enabled": True,
            "recent_performance": self.processing_history[-10:] if len(self.processing_history) > 10 else self.processing_history
        }

# Maintain backwards compatibility
AISemanticProcessor = EnhancedAISemanticProcessor