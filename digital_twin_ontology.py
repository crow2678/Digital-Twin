import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OntologyDomain(Enum):
    """Core ontology domains for digital twin memories"""
    PERSONAL = "personal"
    WORK = "work"
    HEALTH = "health"
    FAMILY = "family"
    FINANCE = "finance"
    EDUCATION = "education"
    TRAVEL = "travel"
    HOBBIES = "hobbies"
    SOCIAL = "social"
    SYSTEM = "system"
    DIGITAL = "digital"  # Added for behavioral tracking

class OntologyCategory(Enum):
    """Ontology categories within domains"""
    # Personal
    IDENTITY = "identity"
    PREFERENCES = "preferences"
    GOALS = "goals"
    HABITS = "habits"
    
    # Work
    MEETINGS = "meetings"
    PROJECTS = "projects"
    TASKS = "tasks"
    COLLEAGUES = "colleagues"
    SKILLS = "skills"
    PRODUCTIVITY = "productivity"  # Added
    
    # Health
    MEDICAL = "medical"
    FITNESS = "fitness"
    NUTRITION = "nutrition"
    MENTAL_HEALTH = "mental_health"
    
    # Family
    RELATIONSHIPS = "relationships"
    EVENTS = "events"
    TRADITIONS = "traditions"
    
    # Finance
    BUDGETS = "budgets"
    INVESTMENTS = "investments"
    EXPENSES = "expenses"
    
    # System
    CONFIGURATION = "configuration"
    METADATA = "metadata"
    INTERACTIONS = "interactions"
    
    # Digital Behavioral
    BROWSING = "browsing"
    ENGAGEMENT = "engagement"
    TIME_TRACKING = "time_tracking"
    NAVIGATION = "navigation"

@dataclass
class OntologyProperty:
    """Represents a property in the ontology"""
    name: str
    value_type: str  # "string", "number", "boolean", "date", "list"
    required: bool = False
    description: str = ""
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OntologyRelationship:
    """Represents a relationship between ontology concepts"""
    source_concept: str
    target_concept: str
    relationship_type: str  # "is_a", "part_of", "relates_to", "causes", "enables"
    strength: float = 1.0  # 0.0 to 1.0
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OntologyConcept:
    """Represents a concept in the ontology"""
    id: str
    name: str
    domain: OntologyDomain
    category: OntologyCategory
    description: str = ""
    properties: List[OntologyProperty] = field(default_factory=list)
    relationships: List[OntologyRelationship] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DigitalTwinOntology:
    """Enhanced ontology framework for digital twin memory management with behavioral patterns"""
    
    def __init__(self):
        self.concepts: Dict[str, OntologyConcept] = {}
        self.domain_index: Dict[OntologyDomain, List[str]] = {}
        self.category_index: Dict[OntologyCategory, List[str]] = {}
        self.relationship_index: Dict[str, List[OntologyRelationship]] = {}
        self._initialize_core_ontology()
        self._initialize_behavioral_ontology()
    
    def _initialize_core_ontology(self):
        """Initialize core ontology concepts"""
        
        # Personal Identity Concepts
        identity_concept = OntologyConcept(
            id="personal_identity",
            name="Personal Identity",
            domain=OntologyDomain.PERSONAL,
            category=OntologyCategory.IDENTITY,
            description="Core identity information about the user",
            properties=[
                OntologyProperty("name", "string", required=True, description="User's preferred name"),
                OntologyProperty("title", "string", description="Professional title"),
                OntologyProperty("location", "string", description="Current location"),
                OntologyProperty("timezone", "string", description="User's timezone")
            ],
            synonyms=["identity", "self", "user_info", "profile", "who", "name"],
            examples=["My name is John", "I am a software engineer", "I live in San Francisco", "call me", "I prefer"]
        )
        
        # Work Meeting Concepts
        meeting_concept = OntologyConcept(
            id="work_meeting",
            name="Work Meeting",
            domain=OntologyDomain.WORK,
            category=OntologyCategory.MEETINGS,
            description="Work-related meetings and appointments",
            properties=[
                OntologyProperty("title", "string", required=True),
                OntologyProperty("participants", "list", description="Meeting attendees"),
                OntologyProperty("datetime", "date", description="Meeting date and time"),
                OntologyProperty("location", "string", description="Meeting location or platform"),
                OntologyProperty("agenda", "string", description="Meeting agenda or purpose"),
                OntologyProperty("duration", "number", description="Meeting duration in minutes"),
                OntologyProperty("urgency", "string", constraints={"values": ["low", "medium", "high", "critical"]})
            ],
            synonyms=["meeting", "appointment", "conference", "call", "standup", "sync", "discussion"],
            examples=["Team meeting at 2pm", "Client call tomorrow", "Weekly standup", "meeting with", "scheduled"]
        )
        
        # Health Information Concepts
        health_concept = OntologyConcept(
            id="health_information",
            name="Health Information",
            domain=OntologyDomain.HEALTH,
            category=OntologyCategory.MEDICAL,
            description="Health-related information and medical data",
            properties=[
                OntologyProperty("condition", "string", description="Medical condition or symptom"),
                OntologyProperty("medication", "string", description="Medications or treatments"),
                OntologyProperty("allergy", "string", description="Known allergies"),
                OntologyProperty("doctor", "string", description="Healthcare provider"),
                OntologyProperty("date", "date", description="Date of medical event"),
                OntologyProperty("severity", "string", constraints={"values": ["mild", "moderate", "severe"]})
            ],
            synonyms=["medical", "health", "doctor", "medication", "treatment", "allergy", "symptom"],
            examples=["I'm allergic to shellfish", "Taking medication for hypertension", "Doctor appointment next week"]
        )
        
        # Preference Concepts
        preference_concept = OntologyConcept(
            id="user_preference",
            name="User Preference",
            domain=OntologyDomain.PERSONAL,
            category=OntologyCategory.PREFERENCES,
            description="User preferences and likes/dislikes",
            properties=[
                OntologyProperty("item", "string", required=True, description="Preferred item or activity"),
                OntologyProperty("preference_type", "string", constraints={"values": ["like", "dislike", "neutral"]}),
                OntologyProperty("strength", "number", constraints={"min": 1, "max": 10}),
                OntologyProperty("context", "string", description="Context where preference applies"),
                OntologyProperty("reason", "string", description="Why user has this preference")
            ],
            synonyms=["preference", "like", "dislike", "favorite", "choice", "prefer", "love", "hate"],
            examples=["I love Italian food", "I prefer morning meetings", "I don't like loud music"]
        )
        
        # Add concepts to ontology
        self.add_concept(identity_concept)
        self.add_concept(meeting_concept)
        self.add_concept(health_concept)
        self.add_concept(preference_concept)
        
        # Define relationships
        self._define_core_relationships()
    
    def _initialize_behavioral_ontology(self):
        """Initialize behavioral tracking ontology concepts"""
        
        # Digital Behavior Concept
        digital_behavior_concept = OntologyConcept(
            id="digital_behavior",
            name="Digital Behavior",
            domain=OntologyDomain.DIGITAL,
            category=OntologyCategory.INTERACTIONS,
            description="Digital behavioral patterns and online interactions",
            properties=[
                OntologyProperty("action_type", "string", required=True, description="Type of digital action"),
                OntologyProperty("domain", "string", description="Website or platform domain"),
                OntologyProperty("duration", "number", description="Time spent in milliseconds"),
                OntologyProperty("engagement_level", "string", description="Level of user engagement"),
                OntologyProperty("platform", "string", description="Digital platform used")
            ],
            synonyms=[
                "digital", "online", "web", "browser", "tab", "page", "visit", "click", "scroll", 
                "engagement", "interaction", "browsing", "navigation", "switch", "activity"
            ],
            examples=[
                "tab switch", "page visit", "digital engagement", "web browsing", 
                "online activity", "browser interaction", "content engagement",
                "Digital content engagement", "explored and interacted", "Digital activity"
            ]
        )
        
        # Work Activity Concept  
        work_activity_concept = OntologyConcept(
            id="work_activity",
            name="Work Activity",
            domain=OntologyDomain.WORK,
            category=OntologyCategory.PRODUCTIVITY,
            description="Work-related activities and productivity patterns",
            properties=[
                OntologyProperty("activity_type", "string", required=True, description="Type of work activity"),
                OntologyProperty("productivity_score", "number", description="Productivity measurement"),
                OntologyProperty("time_spent", "number", description="Duration of activity"),
                OntologyProperty("platform", "string", description="Work platform or tool used"),
                OntologyProperty("company", "string", description="Company or organization")
            ],
            synonyms=[
                "work", "office", "business", "professional", "productivity", "active", "engagement", 
                "tavant", "company", "corporate", "employment", "job", "task", "project"
            ],
            examples=[
                "working with tavant", "office activity", "professional engagement",
                "business task", "work session", "productivity tracking", "tavant.com",
                "Active engagement", "spent", "working with"
            ]
        )
        
        # Time Tracking Concept
        time_tracking_concept = OntologyConcept(
            id="time_tracking", 
            name="Time Tracking",
            domain=OntologyDomain.PERSONAL,
            category=OntologyCategory.TIME_TRACKING,
            description="Time allocation and activity duration tracking",
            properties=[
                OntologyProperty("duration", "number", required=True, description="Duration in milliseconds"),
                OntologyProperty("activity", "string", description="Activity being tracked"),
                OntologyProperty("category", "string", description="Activity category"),
                OntologyProperty("efficiency", "number", description="Efficiency score")
            ],
            synonyms=[
                "time", "tracking", "duration", "spent", "minutes", "hours", "active", "session",
                "timing", "measurement", "allocation", "usage"
            ],
            examples=[
                "time tracking", "spent time", "active engagement", "session duration",
                "time allocation", "activity duration", "spent 0 minutes", "Active engagement: spent"
            ]
        )
        
        # Page Navigation Concept
        page_navigation_concept = OntologyConcept(
            id="page_navigation",
            name="Page Navigation", 
            domain=OntologyDomain.DIGITAL,
            category=OntologyCategory.NAVIGATION,
            description="Website and page navigation patterns",
            properties=[
                OntologyProperty("source_url", "string", description="Starting URL"),
                OntologyProperty("target_url", "string", description="Destination URL"),
                OntologyProperty("navigation_type", "string", description="Type of navigation"),
                OntologyProperty("referrer", "string", description="Referrer information")
            ],
            synonyms=[
                "page", "visit", "navigation", "browsing", "website", "url", "link", "redirect",
                "site", "domain", "web", "internet"
            ],
            examples=[
                "page visit", "website navigation", "browsing behavior", "site interaction",
                "web page access", "url navigation", "general_page_visit"
            ]
        )
        
        # Tab Management Concept
        tab_management_concept = OntologyConcept(
            id="tab_management",
            name="Tab Management",
            domain=OntologyDomain.DIGITAL, 
            category=OntologyCategory.BROWSING,
            description="Browser tab switching and management patterns",
            properties=[
                OntologyProperty("tab_count", "number", description="Number of open tabs"),
                OntologyProperty("switch_frequency", "number", description="Tab switching frequency"),
                OntologyProperty("multitasking_score", "number", description="Multitasking efficiency"),
                OntologyProperty("focus_duration", "number", description="Time spent focused on single tab")
            ],
            synonyms=[
                "tab", "switch", "switching", "browser", "multitask", "multitasking", 
                "focus", "attention", "window", "session"
            ],
            examples=[
                "tab switch", "browser switching", "multitasking behavior", "tab management",
                "focus switching", "attention patterns", "tab_switch"
            ]
        )
        
        # Add behavioral concepts to ontology
        self.add_concept(digital_behavior_concept)
        self.add_concept(work_activity_concept)
        self.add_concept(time_tracking_concept)
        self.add_concept(page_navigation_concept)
        self.add_concept(tab_management_concept)
        
        logger.info("✅ Initialized behavioral ontology concepts")
    
    def _define_core_relationships(self):
        """Define core relationships between concepts"""
        
        # Identity relates to preferences
        identity_preference_rel = OntologyRelationship(
            source_concept="personal_identity",
            target_concept="user_preference",
            relationship_type="has",
            strength=0.8,
            bidirectional=True,
            metadata={"description": "User identity influences preferences"}
        )
        
        # Work meetings relate to colleagues
        meeting_colleague_rel = OntologyRelationship(
            source_concept="work_meeting",
            target_concept="personal_identity",
            relationship_type="involves",
            strength=0.9,
            metadata={"description": "Meetings involve specific people"}
        )
        
        # Health information relates to preferences (dietary, activity)
        health_preference_rel = OntologyRelationship(
            source_concept="health_information",
            target_concept="user_preference",
            relationship_type="influences",
            strength=0.7,
            metadata={"description": "Health conditions influence preferences"}
        )
        
        # Digital behavior relates to work activity
        digital_work_rel = OntologyRelationship(
            source_concept="digital_behavior",
            target_concept="work_activity",
            relationship_type="enables",
            strength=0.8,
            metadata={"description": "Digital behavior enables work activities"}
        )
        
        # Time tracking relates to productivity
        time_productivity_rel = OntologyRelationship(
            source_concept="time_tracking",
            target_concept="work_activity",
            relationship_type="measures",
            strength=0.9,
            metadata={"description": "Time tracking measures work productivity"}
        )
        
        self.add_relationship(identity_preference_rel)
        self.add_relationship(meeting_colleague_rel)
        self.add_relationship(health_preference_rel)
        self.add_relationship(digital_work_rel)
        self.add_relationship(time_productivity_rel)
    
    def add_concept(self, concept: OntologyConcept):
        """Add a concept to the ontology"""
        self.concepts[concept.id] = concept
        
        # Update domain index
        if concept.domain not in self.domain_index:
            self.domain_index[concept.domain] = []
        self.domain_index[concept.domain].append(concept.id)
        
        # Update category index
        if concept.category not in self.category_index:
            self.category_index[concept.category] = []
        self.category_index[concept.category].append(concept.id)
        
        logger.debug(f"Added concept: {concept.name} ({concept.id})")
    
    def add_relationship(self, relationship: OntologyRelationship):
        """Add a relationship to the ontology"""
        if relationship.source_concept not in self.relationship_index:
            self.relationship_index[relationship.source_concept] = []
        self.relationship_index[relationship.source_concept].append(relationship)
        
        if relationship.bidirectional:
            if relationship.target_concept not in self.relationship_index:
                self.relationship_index[relationship.target_concept] = []
            reverse_rel = OntologyRelationship(
                source_concept=relationship.target_concept,
                target_concept=relationship.source_concept,
                relationship_type=relationship.relationship_type,
                strength=relationship.strength,
                bidirectional=False,
                metadata=relationship.metadata
            )
            self.relationship_index[relationship.target_concept].append(reverse_rel)
    
    def find_concepts_by_domain(self, domain: OntologyDomain) -> List[OntologyConcept]:
        """Find all concepts in a specific domain"""
        concept_ids = self.domain_index.get(domain, [])
        return [self.concepts[cid] for cid in concept_ids]
    
    def find_concepts_by_category(self, category: OntologyCategory) -> List[OntologyConcept]:
        """Find all concepts in a specific category"""
        concept_ids = self.category_index.get(category, [])
        return [self.concepts[cid] for cid in concept_ids]
    
    def find_related_concepts(self, concept_id: str) -> List[OntologyRelationship]:
        """Find all concepts related to a given concept"""
        return self.relationship_index.get(concept_id, [])
    
    def debug_classification(self, content: str) -> None:
        """Debug why ontology might not be finding classifications"""
        logger.info(f"\n🔍 DEBUGGING ONTOLOGY CLASSIFICATION")
        logger.info(f"Content: {content}")
        logger.info(f"Content (lowercase): {content.lower()}")
        
        # Check each concept manually
        for concept_id, concept in self.concepts.items():
            logger.debug(f"\n📋 Checking concept: {concept.name}")
            logger.debug(f"   Synonyms: {concept.synonyms}")
            
            score = 0.0
            matched_terms = []
            content_lower = content.lower()
            
            # Check concept name
            if concept.name.lower() in content_lower:
                score += 1.0
                matched_terms.append(concept.name)
                logger.debug(f"   ✅ Name match: {concept.name}")
            
            # Check synonyms
            for synonym in concept.synonyms:
                if synonym.lower() in content_lower:
                    score += 0.8
                    matched_terms.append(synonym)
                    logger.debug(f"   ✅ Synonym match: {synonym}")
            
            # Check examples (more flexible matching)
            for example in concept.examples:
                example_words = set(example.lower().split())
                content_words = set(content_lower.split())
                overlap = len(example_words.intersection(content_words))
                if overlap > 0:
                    example_score = (overlap / len(example_words)) * 0.6
                    score += example_score
                    matched_terms.append(f"example_match:{example}")
                    logger.debug(f"   ✅ Example match: {example} (score: {example_score:.2f})")
            
            if score > 0:
                logger.debug(f"   🎯 TOTAL SCORE: {score:.2f}")
            else:
                logger.debug(f"   ❌ No matches found")
        
        logger.info(f"\n" + "="*50)
    
    def classify_content(self, content: str) -> List[Dict[str, Any]]:
        """Classify content against ontology concepts with enhanced behavioral matching"""
        classifications = []
        content_lower = content.lower()
        
        # Enable debug mode for troubleshooting
        debug_mode = logger.getEffectiveLevel() <= logging.DEBUG
        if debug_mode:
            self.debug_classification(content)
        
        for concept_id, concept in self.concepts.items():
            score = 0.0
            matched_terms = []
            
            # Check concept name (exact match)
            if concept.name.lower() in content_lower:
                score += 1.0
                matched_terms.append(concept.name)
            
            # Check synonyms (exact match)
            for synonym in concept.synonyms:
                if synonym.lower() in content_lower:
                    score += 0.8
                    matched_terms.append(synonym)
            
            # Check examples (partial matching for behavioral patterns)
            for example in concept.examples:
                example_words = set(example.lower().split())
                content_words = set(content_lower.split())
                overlap = len(example_words.intersection(content_words))
                if overlap > 0:
                    # Calculate overlap score
                    overlap_ratio = overlap / len(example_words)
                    example_score = overlap_ratio * 0.6
                    
                    # Bonus for behavioral patterns
                    if overlap >= 2 and len(example_words) >= 2:  # Multi-word matches
                        example_score *= 1.5
                    
                    score += example_score
                    matched_terms.append(f"example_match:{example}")
            
            # Enhanced scoring for behavioral concepts
            if concept.domain in [OntologyDomain.DIGITAL, OntologyDomain.WORK]:
                # Boost scores for behavioral content
                if any(word in content_lower for word in ['digital', 'tab', 'page', 'visit', 'engagement', 'activity']):
                    score *= 1.2
                
                # Company-specific boosting
                if 'tavant' in content_lower and concept.id == 'work_activity':
                    score += 0.5
                
                # Time tracking boosting
                if any(word in content_lower for word in ['spent', 'minutes', 'time', 'duration']) and concept.id == 'time_tracking':
                    score += 0.4
            
            # Only include classifications with meaningful scores
            if score > 0.1:  # Lowered threshold for behavioral content
                classifications.append({
                    "concept_id": concept_id,
                    "concept_name": concept.name,
                    "domain": concept.domain.value,
                    "category": concept.category.value,
                    "score": score,
                    "matched_terms": matched_terms,
                    "properties": [p.name for p in concept.properties]
                })
        
        # Sort by score
        classifications.sort(key=lambda x: x["score"], reverse=True)
        
        if debug_mode and classifications:
            logger.info(f"🎯 Found {len(classifications)} classifications:")
            for c in classifications[:3]:  # Show top 3
                logger.info(f"   - {c['concept_name']}: {c['score']:.2f} (matches: {c['matched_terms']})")
        
        return classifications
    
    def classify_behavioral_content(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced classification specifically for behavioral data"""
        logger.debug(f"🧠 Classifying behavioral content: {content[:100]}...")
        
        # Run normal classification with enhanced behavioral patterns
        classifications = self.classify_content(content)
        
        logger.info(f"🎯 Ontology found {len(classifications)} classifications")
        if classifications:
            for c in classifications[:3]:  # Log top 3
                logger.debug(f"   - {c['concept_name']}: {c['score']:.2f}")
        
        return classifications
    
    def extract_properties(self, content: str, concept_id: str) -> Dict[str, Any]:
        """Extract property values from content based on concept definition"""
        if concept_id not in self.concepts:
            return {}
        
        concept = self.concepts[concept_id]
        extracted_properties = {}
        
        # Simple property extraction (can be enhanced with NLP)
        content_lower = content.lower()
        
        for prop in concept.properties:
            if prop.name == "name" and concept.category == OntologyCategory.IDENTITY:
                # Extract name patterns
                name_patterns = [
                    r"(?:my (?:preferred )?name is|call me|i am|i'm called|refer to me as)\s+([A-Za-z][A-Za-z\s]{1,30})",
                    r"(?:i'm|i am)\s+([A-Za-z][A-Za-z\s]{1,30})"
                ]
                import re
                for pattern in name_patterns:
                    match = re.search(pattern, content_lower)
                    if match:
                        extracted_properties["name"] = match.group(1).strip()
                        break
            
            elif prop.name == "urgency" and "urgent" in content_lower:
                extracted_properties["urgency"] = "high"
            elif prop.name == "urgency" and any(word in content_lower for word in ["asap", "immediately", "emergency"]):
                extracted_properties["urgency"] = "critical"
            
            elif prop.name == "preference_type":
                if any(word in content_lower for word in ["love", "like", "prefer", "enjoy", "favorite"]):
                    extracted_properties["preference_type"] = "like"
                elif any(word in content_lower for word in ["hate", "dislike", "don't like", "avoid"]):
                    extracted_properties["preference_type"] = "dislike"
            
            # Behavioral property extraction
            elif prop.name == "domain" and concept.domain == OntologyDomain.DIGITAL:
                # Extract domain from content
                import re
                domain_match = re.search(r'([a-zA-Z0-9-]+\.(?:com|org|net|edu|gov))', content)
                if domain_match:
                    extracted_properties["domain"] = domain_match.group(1)
            
            elif prop.name == "duration" and any(word in content_lower for word in ["minutes", "hours", "spent", "time"]):
                # Extract duration information
                import re
                duration_match = re.search(r'(\d+)\s*(?:minutes?|mins?|hours?|hrs?)', content_lower)
                if duration_match:
                    extracted_properties["duration"] = int(duration_match.group(1))
            
            elif prop.name == "activity_type" and concept.domain == OntologyDomain.WORK:
                # Extract work activity type
                if "meeting" in content_lower:
                    extracted_properties["activity_type"] = "meeting"
                elif "presentation" in content_lower:
                    extracted_properties["activity_type"] = "presentation"
                elif "email" in content_lower:
                    extracted_properties["activity_type"] = "email"
                elif "research" in content_lower:
                    extracted_properties["activity_type"] = "research"
        
        return extracted_properties
    
    def get_concept_schema(self, concept_id: str) -> Dict[str, Any]:
        """Get the schema definition for a concept"""
        if concept_id not in self.concepts:
            return {}
        
        concept = self.concepts[concept_id]
        
        return {
            "id": concept.id,
            "name": concept.name,
            "domain": concept.domain.value,
            "category": concept.category.value,
            "description": concept.description,
            "properties": [
                {
                    "name": prop.name,
                    "type": prop.value_type,
                    "required": prop.required,
                    "description": prop.description,
                    "constraints": prop.constraints
                }
                for prop in concept.properties
            ],
            "relationships": [
                {
                    "target": rel.target_concept,
                    "type": rel.relationship_type,
                    "strength": rel.strength
                }
                for rel in self.relationship_index.get(concept_id, [])
            ]
        }
    
    def expand_ontology(self, new_concept: OntologyConcept):
        """Dynamically expand the ontology with new concepts"""
        self.add_concept(new_concept)
        logger.info(f"Ontology expanded with new concept: {new_concept.name}")
    
    def get_ontology_stats(self) -> Dict[str, Any]:
        """Get statistics about the ontology"""
        return {
            "total_concepts": len(self.concepts),
            "domains": {domain.value: len(concepts) for domain, concepts in self.domain_index.items()},
            "categories": {category.value: len(concepts) for category, concepts in self.category_index.items()},
            "total_relationships": sum(len(rels) for rels in self.relationship_index.values()),
            "most_connected_concepts": self._get_most_connected_concepts(5)
        }
    
    def _get_most_connected_concepts(self, top_n: int) -> List[Dict[str, Any]]:
        """Get the most connected concepts in the ontology"""
        connection_counts = {}
        
        for concept_id in self.concepts:
            connection_counts[concept_id] = len(self.relationship_index.get(concept_id, []))
        
        sorted_concepts = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "concept_id": concept_id,
                "concept_name": self.concepts[concept_id].name,
                "connection_count": count
            }
            for concept_id, count in sorted_concepts[:top_n]
        ]