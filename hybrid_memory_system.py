import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging


# Import your existing classes
from digital_twin_ontology import DigitalTwinOntology, OntologyDomain, OntologyCategory, OntologyConcept
from ai_semantic_processor import AISemanticProcessor, AIAnalysisResult, SemanticEnrichment

logger = logging.getLogger(__name__)

@dataclass
class HybridMemoryRecord:
    """Enhanced memory record combining ontology structure with AI intelligence"""
    
    # Core identification
    id: str
    content: str
    timestamp: datetime
    source: str
    
    # Ontology-based classification
    ontology_domain: str = None
    ontology_category: str = None
    ontology_concept_id: str = None
    ontology_properties: Dict[str, Any] = field(default_factory=dict)
    ontology_confidence: float = 0.0
    
    # AI-powered enhancements
    ai_semantic_concepts: List[Dict[str, Any]] = field(default_factory=list)
    ai_extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    ai_relationships: List[Dict[str, Any]] = field(default_factory=list)
    ai_context_understanding: Dict[str, Any] = field(default_factory=dict)
    ai_semantic_tags: List[str] = field(default_factory=list)
    ai_confidence: float = 0.0
    ai_reasoning: str = ""
    
    # Hybrid synthesis
    hybrid_classification: Dict[str, Any] = field(default_factory=dict)
    semantic_summary: str = ""
    importance_score: float = 0.0
    relationship_graph_id: str = None
    
    # Memory management
    version: int = 1
    is_active: bool = True
    expiry_date: Optional[datetime] = None
    update_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # User context
    user_id: str = "default"
    tenant_id: str = "default"
    session_id: str = None
    
    def to_search_document(self) -> Dict[str, Any]:
        """Convert to Azure Search document format"""
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),  # Fixed format
            "source": self.source,
            
            # Ontology fields
            "ontology_domain": self.ontology_domain,
            "ontology_category": self.ontology_category,
            "ontology_concept_id": self.ontology_concept_id,
            "ontology_properties_json": json.dumps(self.ontology_properties),
            "ontology_confidence": self.ontology_confidence,
            
            # AI fields
            "ai_semantic_tags": self.ai_semantic_tags,
            "ai_confidence": self.ai_confidence,
            "ai_reasoning": self.ai_reasoning,
            "ai_entities": [e.get("entity", "") for e in self.ai_extracted_entities],
            "ai_concepts": [c.get("concept", "") for c in self.ai_semantic_concepts],
            
            # Hybrid fields
            "semantic_summary": self.semantic_summary,
            "importance_score": self.importance_score,
            "hybrid_classification_json": json.dumps(self.hybrid_classification),
            
            # Search optimization
            "searchable_content": self._create_searchable_content(),
            "all_tags": self._get_all_tags(),
            
            # Management fields
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "version": self.version,
            "is_active": self.is_active,
            "expiry_date": self.expiry_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if self.expiry_date else None
        }
    
    def _create_searchable_content(self) -> str:
        """Create enhanced searchable content"""
        searchable_parts = [self.content]
        
        # Add semantic concepts
        for concept in self.ai_semantic_concepts:
            searchable_parts.append(concept.get("concept", ""))
            searchable_parts.append(concept.get("description", ""))
        
        # Add extracted entities
        for entity in self.ai_extracted_entities:
            searchable_parts.append(entity.get("entity", ""))
            searchable_parts.append(entity.get("context", ""))
        
        # Add ontology information
        if self.ontology_domain:
            searchable_parts.append(self.ontology_domain)
        if self.ontology_category:
            searchable_parts.append(self.ontology_category)
        
        # Add semantic summary
        if self.semantic_summary:
            searchable_parts.append(self.semantic_summary)
        
        return " ".join(filter(None, searchable_parts))
    
    def _get_all_tags(self) -> List[str]:
        """Get all tags for filtering"""
        all_tags = []
        
        # Add AI semantic tags
        all_tags.extend(self.ai_semantic_tags)
        
        # Add ontology tags
        if self.ontology_domain:
            all_tags.append(self.ontology_domain)
        if self.ontology_category:
            all_tags.append(self.ontology_category)
        
        # Add derived tags
        urgency = self.ai_context_understanding.get("urgency_level")
        if urgency:
            all_tags.append(f"urgency:{urgency}")
        
        importance = self.ai_context_understanding.get("importance_level")
        if importance:
            all_tags.append(f"importance:{importance}")
        
        return list(set(all_tags))  # Remove duplicates
    
    @classmethod
    def from_search_result(cls, result: Dict[str, Any]) -> 'HybridMemoryRecord':
        """Create HybridMemoryRecord from search result"""
        
        # Parse JSON fields
        ontology_properties = {}
        hybrid_classification = {}
        
        try:
            if result.get('ontology_properties_json'):
                ontology_properties = json.loads(result['ontology_properties_json'])
        except json.JSONDecodeError:
            pass
        
        try:
            if result.get('hybrid_classification_json'):
                hybrid_classification = json.loads(result['hybrid_classification_json'])
        except json.JSONDecodeError:
            pass
        
        # Parse timestamp
        timestamp = datetime.fromisoformat(result['timestamp'].replace('Z', ''))
        
        # Parse expiry date
        expiry_date = None
        if result.get('expiry_date'):
            try:
                expiry_date = datetime.fromisoformat(result['expiry_date'].replace('Z', ''))
            except ValueError:
                pass
        
        return cls(
            id=result['id'],
            content=result['content'],
            timestamp=timestamp,
            source=result.get('source', 'unknown'),
            
            # Ontology fields
            ontology_domain=result.get('ontology_domain'),
            ontology_category=result.get('ontology_category'),
            ontology_concept_id=result.get('ontology_concept_id'),
            ontology_properties=ontology_properties,
            ontology_confidence=result.get('ontology_confidence', 0.0),
            
            # AI fields
            ai_semantic_tags=result.get('ai_semantic_tags', []),
            ai_confidence=result.get('ai_confidence', 0.0),
            ai_reasoning=result.get('ai_reasoning', ''),
            
            # Hybrid fields
            semantic_summary=result.get('semantic_summary', ''),
            importance_score=result.get('importance_score', 0.0),
            hybrid_classification=hybrid_classification,
            
            # Management fields
            user_id=result.get('user_id', 'default'),
            tenant_id=result.get('tenant_id', 'default'),
            session_id=result.get('session_id'),
            version=result.get('version', 1),
            is_active=result.get('is_active', True),
            expiry_date=expiry_date
        )

class HybridInformationProcessor:
    """Processes information using both ontology and AI analysis"""
    
    def __init__(self, ontology: DigitalTwinOntology, ai_processor: AISemanticProcessor):
        self.ontology = ontology
        self.ai_processor = ai_processor
        self.processing_stats = {
            "total_processed": 0,
            "ontology_matches": 0,
            "ai_enhancements": 0,
            "hybrid_syntheses": 0
        }
    
    def process_content(self, content: str, user_context: Dict[str, Any] = None) -> HybridMemoryRecord:
        """Process content using hybrid ontology + AI approach"""
        
        logger.info(f"Processing content with hybrid approach: {content[:50]}...")
        
        # Step 1: Ontology Analysis
        #ontology_classifications = self.ontology.classify_content(content)
        # In your hybrid_memory_system.py, add this debug line:
        ontology_classifications = self.ontology.classify_behavioral_content(content)  # Instead of classify_content
        logger.info(f"Ontology found {len(ontology_classifications)} classifications")
        
        # Step 2: AI Semantic Analysis
        ai_analysis = self.ai_processor.analyze_content(content, user_context)
        logger.info(f"AI analysis completed with confidence: {ai_analysis.confidence_score}")
        
        # Step 3: Hybrid Synthesis
        hybrid_classification = self._synthesize_classifications(ontology_classifications, ai_analysis)
        logger.info(f"Hybrid synthesis created: {hybrid_classification.get('primary_domain', 'unknown')}")
        
        # Step 4: Create Enhanced Memory Record
        memory_record = self._create_hybrid_memory_record(
            content, ontology_classifications, ai_analysis, hybrid_classification, user_context
        )
        
        # Update stats
        self._update_processing_stats(ontology_classifications, ai_analysis)
        
        return memory_record
    
    def _synthesize_classifications(self, ontology_classifications: List[Dict], 
                                  ai_analysis: AIAnalysisResult) -> Dict[str, Any]:
        """Synthesize ontology and AI classifications into hybrid understanding"""
        
        synthesis = {
            "synthesis_method": "hybrid_ontology_ai",
            "synthesis_confidence": 0.0,
            "primary_domain": None,
            "primary_category": None,
            "ontology_agreement": False,
            "ai_enhancements": [],
            "confidence_breakdown": {},
            "decision_reasoning": ""
        }
        
        # Get AI domain classification
        ai_domain_info = ai_analysis.context_understanding.get("domain_classification", {})
        ai_primary_domain = ai_domain_info.get("primary_domain")
        ai_confidence = ai_domain_info.get("confidence", 0.0)
        
        # Get best ontology classification
        ontology_primary = None
        ontology_confidence = 0.0
        if ontology_classifications:
            best_ontology = ontology_classifications[0]
            ontology_primary = best_ontology["domain"]
            ontology_confidence = best_ontology["score"]
        
        # Synthesis logic
        if ontology_primary and ai_primary_domain:
            if ontology_primary == ai_primary_domain:
                # Perfect agreement
                synthesis["primary_domain"] = ontology_primary
                synthesis["primary_category"] = ontology_classifications[0]["category"]
                synthesis["ontology_agreement"] = True
                synthesis["synthesis_confidence"] = (ontology_confidence + ai_confidence) / 2 * 1.2  # Boost for agreement
                synthesis["decision_reasoning"] = f"Both ontology and AI agree on {ontology_primary} domain"
                
            elif ontology_confidence > ai_confidence * 1.5:
                # Ontology is much more confident
                synthesis["primary_domain"] = ontology_primary
                synthesis["primary_category"] = ontology_classifications[0]["category"]
                synthesis["synthesis_confidence"] = ontology_confidence
                synthesis["decision_reasoning"] = f"Ontology more confident: {ontology_primary} vs AI: {ai_primary_domain}"
                
            elif ai_confidence > ontology_confidence * 1.5:
                # AI is much more confident
                synthesis["primary_domain"] = ai_primary_domain
                synthesis["primary_category"] = "ai_derived"
                synthesis["synthesis_confidence"] = ai_confidence
                synthesis["decision_reasoning"] = f"AI more confident: {ai_primary_domain} vs Ontology: {ontology_primary}"
                
            else:
                # Similar confidence - use weighted average
                if ontology_confidence >= ai_confidence:
                    synthesis["primary_domain"] = ontology_primary
                    synthesis["primary_category"] = ontology_classifications[0]["category"]
                else:
                    synthesis["primary_domain"] = ai_primary_domain
                    synthesis["primary_category"] = "ai_derived"
                
                synthesis["synthesis_confidence"] = (ontology_confidence + ai_confidence) / 2
                synthesis["decision_reasoning"] = f"Weighted decision between {ontology_primary} and {ai_primary_domain}"
        
        elif ontology_primary:
            # Only ontology classification available
            synthesis["primary_domain"] = ontology_primary
            synthesis["primary_category"] = ontology_classifications[0]["category"]
            synthesis["synthesis_confidence"] = ontology_confidence
            synthesis["decision_reasoning"] = "Only ontology classification available"
            
        elif ai_primary_domain:
            # Only AI classification available
            synthesis["primary_domain"] = ai_primary_domain
            synthesis["primary_category"] = "ai_derived"
            synthesis["synthesis_confidence"] = ai_confidence
            synthesis["decision_reasoning"] = "Only AI classification available"
            
        else:
            # No strong classification from either
            synthesis["primary_domain"] = "general"
            synthesis["primary_category"] = "unclassified"
            synthesis["synthesis_confidence"] = 0.3
            synthesis["decision_reasoning"] = "No strong classification from ontology or AI"
        
        # Add AI enhancements
        synthesis["ai_enhancements"] = [
            {"type": "semantic_concepts", "count": len(ai_analysis.semantic_concepts)},
            {"type": "extracted_entities", "count": len(ai_analysis.extracted_entities)},
            {"type": "relationships", "count": len(ai_analysis.relationships)},
            {"type": "context_understanding", "available": bool(ai_analysis.context_understanding)}
        ]
        
        # Confidence breakdown
        synthesis["confidence_breakdown"] = {
            "ontology_confidence": ontology_confidence,
            "ai_confidence": ai_confidence,
            "synthesis_confidence": synthesis["synthesis_confidence"],
            "agreement_bonus": synthesis["ontology_agreement"]
        }
        
        return synthesis
    
    def _create_hybrid_memory_record(self, content: str, ontology_classifications: List[Dict],
                                   ai_analysis: AIAnalysisResult, hybrid_classification: Dict[str, Any],
                                   user_context: Dict[str, Any] = None) -> HybridMemoryRecord:
        """Create comprehensive hybrid memory record"""
        
        # Extract primary ontology classification
        primary_ontology = ontology_classifications[0] if ontology_classifications else {}
        
        # Calculate importance score
        importance_score = self._calculate_importance_score(ai_analysis, hybrid_classification)
        
        # Generate semantic summary
        semantic_summary = self.ai_processor.generate_semantic_summary(ai_analysis)
        
        # Create memory record
        memory_record = HybridMemoryRecord(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.now(),
            source="hybrid_processor",
            
            # Ontology classification
            ontology_domain=primary_ontology.get("domain"),
            ontology_category=primary_ontology.get("category"),
            ontology_concept_id=primary_ontology.get("concept_id"),
            ontology_properties=self.ontology.extract_properties(content, primary_ontology.get("concept_id", "")),
            ontology_confidence=primary_ontology.get("score", 0.0),
            
            # AI analysis
            ai_semantic_concepts=ai_analysis.semantic_concepts,
            ai_extracted_entities=ai_analysis.extracted_entities,
            ai_relationships=ai_analysis.relationships,
            ai_context_understanding=ai_analysis.context_understanding,
            ai_semantic_tags=ai_analysis.semantic_tags,
            ai_confidence=ai_analysis.confidence_score,
            ai_reasoning=ai_analysis.reasoning,
            
            # Hybrid synthesis
            hybrid_classification=hybrid_classification,
            semantic_summary=semantic_summary,
            importance_score=importance_score,
            
            # User context
            user_id=user_context.get("user_id", "default") if user_context else "default",
            tenant_id=user_context.get("tenant_id", "default") if user_context else "default",
            session_id=user_context.get("session_id") if user_context else None
        )
        
        return memory_record
    
    def _calculate_importance_score(self, ai_analysis: AIAnalysisResult, 
                                  hybrid_classification: Dict[str, Any]) -> float:
        """Calculate overall importance score for the memory"""
        
        score_components = []
        
        # AI confidence contributes to importance
        score_components.append(ai_analysis.confidence_score * 0.3)
        
        # Synthesis confidence contributes
        synthesis_confidence = hybrid_classification.get("synthesis_confidence", 0.0)
        score_components.append(synthesis_confidence * 0.2)
        
        # Urgency and importance from AI context
        urgency_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        importance_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        
        urgency = ai_analysis.context_understanding.get("urgency_level", "medium")
        importance = ai_analysis.context_understanding.get("importance_level", "medium")
        
        score_components.append(urgency_map.get(urgency, 0.5) * 0.25)
        score_components.append(importance_map.get(importance, 0.5) * 0.25)
        
        # Number of relationships and entities
        entity_score = min(len(ai_analysis.extracted_entities) * 0.1, 0.5)
        relationship_score = min(len(ai_analysis.relationships) * 0.1, 0.3)
        
        score_components.extend([entity_score, relationship_score])
        
        # Calculate final score
        final_score = sum(score_components)
        return min(final_score, 1.0)  # Cap at 1.0
    
    def _update_processing_stats(self, ontology_classifications: List[Dict], ai_analysis: AIAnalysisResult):
        """Update processing statistics"""
        self.processing_stats["total_processed"] += 1
        
        if ontology_classifications:
            self.processing_stats["ontology_matches"] += 1
        
        if ai_analysis.confidence_score > 0.5:
            self.processing_stats["ai_enhancements"] += 1
        
        if ontology_classifications and ai_analysis.confidence_score > 0.5:
            self.processing_stats["hybrid_syntheses"] += 1
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.processing_stats.copy()
        
        if stats["total_processed"] > 0:
            stats["ontology_match_rate"] = stats["ontology_matches"] / stats["total_processed"]
            stats["ai_enhancement_rate"] = stats["ai_enhancements"] / stats["total_processed"]
            stats["hybrid_synthesis_rate"] = stats["hybrid_syntheses"] / stats["total_processed"]
        
        return stats