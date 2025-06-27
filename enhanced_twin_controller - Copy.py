import os
import uuid
import json
import requests
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

class SmartDigitalTwin:
    """Enhanced Digital Twin with Behavioral API Integration and Semantic Memory"""
    
    def __init__(self):
        print("🚀 Initializing Enhanced Smart Digital Twin with Behavioral Intelligence...")
        self.setup_hybrid_system()
        self.setup_behavioral_api()
        self.conversation_history = []
        self.current_user = None
        self.session_id = str(uuid.uuid4())
        print("✅ Enhanced Smart Digital Twin ready with behavioral insights!")
        
    def setup_hybrid_system(self):
        """Initialize hybrid memory system with increased limits"""
        try:
            azure_config = {
                "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
                "search_key": os.getenv("AZURE_SEARCH_KEY"),
                "index_name": os.getenv("AZURE_SEARCH_INDEX")
            }
            
            self.hybrid_manager = HybridMemoryManager(azure_config)
            
            # Get system info with increased limits
            analytics = self.hybrid_manager.get_system_analytics()
            ontology_stats = analytics['ontology_stats']
            
            print(f"   🧠 Ontology: {ontology_stats['total_concepts']} concepts loaded")
            print(f"   🤖 AI Processor: Ready for semantic analysis")
            print(f"   💾 Memory Store: Connected to Azure Search")
            
        except Exception as e:
            print(f"❌ Error initializing hybrid system: {e}")
            raise
    
    def setup_behavioral_api(self):
        """Initialize behavioral API connection"""
        self.behavioral_api_url = "http://localhost:8000"
        self.behavioral_api_available = self._check_behavioral_api()
        
        if self.behavioral_api_available:
            print("   📊 Behavioral API: Connected and ready")
        else:
            print("   📊 Behavioral API: Not available (will use memory-only mode)")
    
    def _check_behavioral_api(self) -> bool:
        """Check if behavioral API is available"""
        try:
            response = requests.get(f"{self.behavioral_api_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"📊 Behavioral API check failed: {e}")
            return False
    
    def get_behavioral_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed behavioral statistics from API with retry logic"""
        if not self.behavioral_api_available:
            return None
            
        for attempt in range(2):  # Try twice
            try:
                response = requests.get(
                    f"{self.behavioral_api_url}/user/{user_id}/stats", 
                    timeout=15  # Increased timeout
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"📊 API returned status {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"⏱️ API timeout on attempt {attempt + 1}")
                if attempt == 0:  # Only print on first attempt
                    continue
            except Exception as e:
                print(f"⚠️ API error: {e}")
                break
        
        return None
    
    def get_dashboard_analytics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive dashboard analytics with retry logic"""
        if not self.behavioral_api_available:
            return None
            
        for attempt in range(2):  # Try twice
            try:
                response = requests.get(
                    f"{self.behavioral_api_url}/analytics/dashboard?user_id={user_id}", 
                    timeout=15  # Increased timeout
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"📊 Dashboard API returned status {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"⏱️ Dashboard API timeout on attempt {attempt + 1}")
                if attempt == 0:  # Only print on first attempt
                    continue
            except Exception as e:
                print(f"⚠️ Dashboard API error: {e}")
                break
        
        return None
    
    def is_question(self, user_input: str) -> bool:
        """Detect if user input is a question that should be answered from memory/API"""
        user_input_lower = user_input.lower().strip()
        
        # Question indicators - expanded list
        question_starters = [
            'what', 'how', 'when', 'where', 'why', 'which', 'who',
            'do i', 'am i', 'can i', 'should i', 'will i', 'have i',
            'tell me about', 'what about', 'remind me', 'show me',
            'what do', 'what are', 'what is', 'how do', 'where do',
            'analyze', 'insights', 'patterns', 'behavior', 'statistics'
        ]
        
        # Check if it starts with question words
        for starter in question_starters:
            if user_input_lower.startswith(starter):
                return True
        
        # Check for question marks
        if '?' in user_input:
            return True
        
        # Check for behavioral analysis requests
        behavioral_keywords = [
            'behavioral', 'behavior', 'patterns', 'insights', 'analytics',
            'productivity', 'focus', 'work', 'research', 'email', 'salesforce'
        ]
        
        for keyword in behavioral_keywords:
            if keyword in user_input_lower:
                return True
        
        return False
    
    def answer_from_memory_and_api(self, question: str, user_id: str) -> Optional[str]:
        """Answer question using both memory search and behavioral API data"""
        
        try:
            # Get behavioral stats from API
            behavioral_stats = self.get_behavioral_stats(user_id)
            dashboard_data = self.get_dashboard_analytics(user_id)
            
            # Search existing memories with increased limit
            relevant_memories = self.hybrid_manager.search_memories(
                question,
                search_options={"user_id": user_id, "limit": 500}  # Increased from 5 to 500
            )
            
            # Build comprehensive answer
            return self._build_comprehensive_answer(question, relevant_memories, behavioral_stats, dashboard_data)
            
        except Exception as e:
            print(f"Error answering from memory and API: {e}")
            return None
    
    def _build_comprehensive_answer(self, question: str, memories: List, behavioral_stats: Dict, dashboard_data: Dict) -> str:
        """Build comprehensive answer combining memory and API data"""
        
        question_lower = question.lower()
        answer_parts = []
        
        # Behavioral pattern analysis
        if any(word in question_lower for word in ['behavior', 'pattern', 'insight', 'analytic']):
            if behavioral_stats and behavioral_stats.get('total_events', 0) > 0:
                answer_parts.append(self._format_behavioral_insights(behavioral_stats, dashboard_data))
            else:
                answer_parts.append("I'm still collecting behavioral data. Continue using your work tools to see detailed patterns emerge.")
        
        # Productivity and focus analysis
        elif any(word in question_lower for word in ['productivity', 'focus', 'work', 'efficient']):
            if dashboard_data:
                answer_parts.append(self._format_productivity_insights(dashboard_data))
            else:
                answer_parts.append("I'm tracking your productivity patterns. Use your tools more to see insights.")
        
        # Tool-specific analysis (Salesforce, Email, Research)
        elif any(word in question_lower for word in ['salesforce', 'crm', 'deals']):
            if dashboard_data and dashboard_data.get('salesforce_usage'):
                sf_data = dashboard_data['salesforce_usage']
                if not sf_data.get('loading'):
                    answer_parts.append(f"Salesforce Analysis: {sf_data.get('total_sessions', 0)} sessions, average {sf_data.get('avg_session_time', 'unknown')} per session. Top activities: {', '.join(sf_data.get('top_activities', []))}")
                else:
                    answer_parts.append("Salesforce tracking active - visit Salesforce to see detailed usage patterns.")
        
        elif any(word in question_lower for word in ['email', 'outlook', 'communication']):
            if dashboard_data and dashboard_data.get('email_efficiency'):
                email_data = dashboard_data['email_efficiency']
                if not email_data.get('loading'):
                    answer_parts.append(f"Email Efficiency: {email_data.get('emails_sent', 0)} emails sent, {email_data.get('avg_response_time', 'unknown')} average response time, productivity score: {email_data.get('productivity_score', 0)}")
                else:
                    answer_parts.append("Email tracking active - use Outlook web to see communication patterns.")
        
        elif any(word in question_lower for word in ['research', 'linkedin', 'prospect']):
            if dashboard_data and dashboard_data.get('research_patterns'):
                research_data = dashboard_data['research_patterns']
                if not research_data.get('loading'):
                    answer_parts.append(f"Research Patterns: {research_data.get('research_sessions', 0)} sessions, {research_data.get('avg_depth', 'unknown')} average depth. Top sources: {', '.join(research_data.get('top_sources', []))}")
                else:
                    answer_parts.append("Research tracking active - browse LinkedIn/research sites to see patterns.")
        
        # Memory-based answers for personal information
        else:
            memory_answer = self._extract_memory_answer(question_lower, memories)
            if memory_answer:
                answer_parts.append(memory_answer)
        
        # Add memory count if available
        if memories:
            answer_parts.append(f"\n📊 Analysis based on {len(memories)} relevant memories from your digital interactions.")
        
        if answer_parts:
            return "\n\n".join(answer_parts)
        else:
            return "I'm continuously learning about your patterns. Continue using your digital tools and I'll provide deeper insights as more data becomes available."
    
    def _format_behavioral_insights(self, stats: Dict, dashboard: Dict) -> str:
        """Format comprehensive behavioral insights"""
        insights = ["🧠 Behavioral Intelligence Analysis:"]
        
        if stats.get('total_events', 0) > 0:
            insights.append(f"📈 Total behavioral events tracked: {stats['total_events']}")
        
        # Event type breakdown
        if stats.get('event_types'):
            insights.append("\n🎯 Activity Distribution:")
            for event_type, count in stats['event_types'].items():
                formatted_type = event_type.replace('_', ' ').title()
                insights.append(f"  • {formatted_type}: {count} instances")
        
        # Domain analysis
        if stats.get('domains'):
            insights.append(f"\n🌐 Digital domains engaged: {len(stats['domains'])} unique platforms")
            top_domains = sorted(stats['domains'].items(), key=lambda x: x[1], reverse=True)[:3]
            for domain, count in top_domains:
                insights.append(f"  • {domain}: {count} interactions")
        
        # Dashboard data integration
        if dashboard and not dashboard.get('message'):
            if dashboard.get('energy_trends', {}).get('focus_sessions', 0) > 0:
                energy = dashboard['energy_trends']
                insights.append(f"\n⚡ Energy Patterns: {energy['focus_sessions']} focus sessions, peak efficiency at {energy.get('peak_hours', 'unknown')}")
        
        return "\n".join(insights)
    
    def _format_productivity_insights(self, dashboard: Dict) -> str:
        """Format productivity-specific insights"""
        insights = ["🎯 Productivity Intelligence:"]
        
        if dashboard.get('energy_trends'):
            energy = dashboard['energy_trends']
            insights.append(f"⚡ Focus Sessions: {energy.get('focus_sessions', 0)} deep work periods")
            insights.append(f"📊 Peak Performance: {energy.get('peak_hours', 'Unknown time')}")
            insights.append(f"🔗 Productivity Correlation: {energy.get('productivity_correlation', 0)}")
        
        # Combine insights from multiple tools
        tool_insights = []
        
        if dashboard.get('salesforce_usage', {}).get('total_sessions', 0) > 0:
            sf = dashboard['salesforce_usage']
            tool_insights.append(f"Salesforce: {sf['total_sessions']} sessions")
        
        if dashboard.get('email_efficiency', {}).get('emails_sent', 0) > 0:
            email = dashboard['email_efficiency']
            tool_insights.append(f"Email: {email['emails_sent']} messages, {email.get('productivity_score', 0)} efficiency score")
        
        if dashboard.get('research_patterns', {}).get('research_sessions', 0) > 0:
            research = dashboard['research_patterns']
            tool_insights.append(f"Research: {research['research_sessions']} sessions")
        
        if tool_insights:
            insights.append(f"\n🛠️ Tool Usage Synthesis: {' | '.join(tool_insights)}")
        
        return "\n".join(insights)
    
    def _extract_memory_answer(self, question_lower: str, memories: List) -> Optional[str]:
        """Extract answers from memory for personal information"""
        
        answers = []
        
        for memory, score in memories:
            # Check for specific question types
            if any(word in question_lower for word in ['like', 'prefer', 'enjoy']):
                if 'classic cars' in memory.content.lower() or 'mustang' in memory.content.lower():
                    answers.append("You like classic cars, especially your 1969 Mustang")
                if 'dogs' in memory.content.lower() or 'animals' in memory.content.lower():
                    answers.append("You love dogs and care about animal welfare")
                if 'precision' in memory.content.lower():
                    answers.append("You value precision in everything you do")
            
            elif any(word in question_lower for word in ['car', 'drive', 'vehicle']):
                if '1969 mustang' in memory.content.lower():
                    answers.append("You drive a 1969 Mustang")
                elif 'classic car' in memory.content.lower():
                    answers.append("You prefer classic cars")
            
            elif any(word in question_lower for word in ['work', 'job', 'employment']):
                if 'continental hotel' in memory.content.lower():
                    answers.append("You work in the Continental Hotel network")
                if 'marksmanship' in memory.content.lower():
                    answers.append("You have excellent marksmanship skills")
            
            elif any(word in question_lower for word in ['fitness', 'training', 'physical']):
                if 'training regimen' in memory.content.lower():
                    answers.append("You maintain peak physical condition with a strict training regimen")
        
        if answers:
            return "Based on what I know about you: " + ". ".join(set(answers)) + "."
        elif memories:
            # Generic answer from top memory
            top_memory = memories[0][0]
            return f"From what I remember: {top_memory.semantic_summary}"
        
        return None
    
    def process_user_input(self, user_input: str, user_id: str = None) -> str:
        """Process user input with enhanced memory and API integration"""
        
        if not user_id:
            user_id = self.current_user or "default_user"
        
        user_context = {
            "user_id": user_id,
            "tenant_id": "default_tenant",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check if this is a question that should be answered from existing memory/API
            if self.is_question(user_input):
                comprehensive_answer = self.answer_from_memory_and_api(user_input, user_id)
                if comprehensive_answer:
                    # Don't store questions as memories, just answer them
                    self.conversation_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "user": user_input,
                        "assistant": comprehensive_answer,
                        "type": "comprehensive_analysis",
                        "api_integrated": self.behavioral_api_available
                    })
                    return comprehensive_answer
            
            # Process and store memory with hybrid approach (for statements, not questions)
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
                "processing_report": {
                    "success": report['success'],
                    "ontology_domain": report.get('ontology_domain'),
                    "ai_confidence": report.get('ai_confidence', 0),
                    "hybrid_confidence": report.get('hybrid_confidence', 0),
                    "importance_score": report.get('importance_score', 0),
                    "processing_time": report.get('processing_time_seconds', 0)
                }
            })
            
            return response
            
        except Exception as e:
            error_response = f"I encountered an error processing your message: {str(e)[:100]}. Please try again."
            
            # Store error in conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": user_input,
                "assistant": error_response,
                "error": str(e)
            })
            
            return error_response
    
    def generate_intelligent_response(self, user_input: str, memory, report: Dict, user_context: Dict) -> str:
        """Generate intelligent response using hybrid understanding"""
        
        try:
            # Get user's memory profile for context with increased limit
            profile = self.hybrid_manager.get_user_memory_profile(user_context["user_id"])
            
            # Search for relevant memories with increased limit
            relevant_memories = self.hybrid_manager.search_memories(
                user_input,
                search_options={"user_id": user_context["user_id"], "limit": 500}  # Increased from 3 to 500
            )
            
            # Build response components
            response_parts = []
            
            # Acknowledge processing
            if report.get("success"):
                response_parts.append("I've processed and integrated your message into my understanding.")
            else:
                response_parts.append("I've noted your message.")
            
            # Add ontology understanding
            ontology_domain = report.get('ontology_domain')
            if ontology_domain:
                domain_responses = {
                    "personal": "I understand this is personal information about you.",
                    "work": "I see this relates to your work and professional activities.",
                    "health": "I've noted this health-related information securely.",
                    "family": "I understand this concerns your family relationships.",
                    "finance": "I've recorded this financial information.",
                    "education": "I see this is about learning or educational activities.",
                    "travel": "I've noted this travel-related information.",
                    "hobbies": "I understand this relates to your interests and hobbies."
                }
                
                domain_response = domain_responses.get(ontology_domain, f"I've classified this under {ontology_domain}.")
                response_parts.append(domain_response)
            
            # Add AI insights
            entities_count = report.get('entities_extracted', 0)
            if entities_count > 0:
                if entities_count == 1:
                    response_parts.append("I identified 1 key detail.")
                else:
                    response_parts.append(f"I identified {entities_count} key details.")
            
            relationships_count = report.get('relationships_identified', 0)
            if relationships_count > 0:
                response_parts.append(f"I found {relationships_count} connections to other information.")
            
            # Add semantic summary if available
            semantic_summary = report.get('semantic_summary')
            if semantic_summary and semantic_summary != "General information":
                response_parts.append(f"In essence: {semantic_summary}")
            
            # Add behavioral intelligence context if API is available
            if self.behavioral_api_available:
                behavioral_stats = self.get_behavioral_stats(user_context["user_id"])
                if behavioral_stats and behavioral_stats.get('total_events', 0) > 0:
                    response_parts.append(f"Your behavioral intelligence shows {behavioral_stats['total_events']} tracked digital interactions across {len(behavioral_stats.get('domains', {}))} platforms.")
            
            # Add relevant context from memory
            if relevant_memories and len(relevant_memories) > 1:
                # More than just the current memory
                response_parts.append(f"This connects to {len(relevant_memories) - 1} other elements in my knowledge about you.")
            
            # Add confidence and importance context
            hybrid_confidence = report.get('hybrid_confidence', 0)
            importance_score = report.get('importance_score', 0)
            
            if hybrid_confidence > 0.8:
                response_parts.append("I'm quite confident in my understanding.")
            elif hybrid_confidence < 0.5:
                response_parts.append("I'm still learning about this aspect.")
            
            if importance_score > 0.7:
                response_parts.append("This seems particularly significant to remember.")
            
            # Combine response parts
            response = " ".join(response_parts)
            
            # Add helpful context for the user
            if profile['total_memories'] > 0:
                if profile['total_memories'] == 1:
                    response += f"\n\nThis is the first element in my understanding of you."
                elif profile['total_memories'] < 10:
                    response += f"\n\nI now understand {profile['total_memories']} aspects about you."
                else:
                    response += f"\n\nMy knowledge about you has grown to {profile['total_memories']} interconnected memories."
            
            return response
            
        except Exception as e:
            # Fallback response if generation fails
            return f"I've processed your message. {report.get('semantic_summary', 'Thank you for sharing.')}"
    
    def search_user_memories(self, query: str, user_id: str = None) -> List[str]:
        """Search user's memories and return formatted results with increased limit"""
        
        if not user_id:
            user_id = self.current_user or "default_user"
        
        try:
            results = self.hybrid_manager.search_memories(
                query,
                search_options={"user_id": user_id, "limit": 500}  # Increased from 5 to 500
            )
            
            if not results:
                return ["No memories found matching your search."]
            
            formatted_results = []
            for i, (memory, score) in enumerate(results[:20], 1):  # Show top 20 results
                # Format memory information
                time_ago = self._get_time_ago(memory.timestamp)
                domain_info = f" ({memory.ontology_domain})" if memory.ontology_domain else ""
                
                result = f"{i}. {memory.semantic_summary}{domain_info}"
                result += f"\n   Relevance: {score:.2f} | {time_ago}"
                
                if memory.ai_semantic_tags:
                    tags = ", ".join(memory.ai_semantic_tags[:3])
                    result += f" | Tags: {tags}"
                
                formatted_results.append(result)
            
            # Add summary if more results available
            if len(results) > 20:
                formatted_results.append(f"\n... and {len(results) - 20} more results available")
            
            return formatted_results
            
        except Exception as e:
            return [f"Error searching memories: {str(e)}"]
    
    def get_user_profile_summary(self, user_id: str = None) -> str:
        """Get comprehensive user profile summary with behavioral integration"""
        
        if not user_id:
            user_id = self.current_user or "default_user"
        
        try:
            profile = self.hybrid_manager.get_user_memory_profile(user_id)
            
            if profile['total_memories'] == 0:
                return "No memories stored yet. Start by telling me about yourself or continue using your digital tools!"
            
            summary_parts = [
                f"📊 Comprehensive Profile for {user_id}:",
                f"   Memory Intelligence: {profile['total_memories']} total memories",
                f"   Average importance: {profile['average_importance']:.2f}/1.0"
            ]
            
            if profile['recent_activity'] > 0:
                summary_parts.append(f"   Recent activity: {profile['recent_activity']} memories in last 7 days")
            
            # Add behavioral intelligence if available
            if self.behavioral_api_available:
                behavioral_stats = self.get_behavioral_stats(user_id)
                if behavioral_stats and behavioral_stats.get('total_events', 0) > 0:
                    summary_parts.append(f"   Behavioral Intelligence: {behavioral_stats['total_events']} digital interactions tracked")
                    
                    if behavioral_stats.get('event_types'):
                        top_activity = max(behavioral_stats['event_types'].items(), key=lambda x: x[1])
                        summary_parts.append(f"   Primary digital pattern: {top_activity[0].replace('_', ' ').title()} ({top_activity[1]} instances)")
            
            if profile['domain_distribution']:
                summary_parts.append("   📁 Memory domains:")
                for domain, count in sorted(profile['domain_distribution'].items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / profile['total_memories']) * 100
                    summary_parts.append(f"      {domain}: {count} ({percentage:.1f}%)")
            
            if profile['top_semantic_tags']:
                summary_parts.append("   🏷️ Top knowledge areas:")
                for tag, count in profile['top_semantic_tags'][:5]:
                    summary_parts.append(f"      {tag}: {count} mentions")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"Error getting profile: {str(e)}"
    
    def get_system_status(self) -> str:
        """Get comprehensive system status including API integration"""
        
        try:
            analytics = self.hybrid_manager.get_system_analytics()
            
            perf = analytics['performance_metrics']
            onto_stats = analytics['ontology_stats']
            
            status_parts = [
                "🔧 Enhanced System Status:",
                f"   Total processed: {perf['total_processed']} memories",
                f"   Hybrid success rate: {perf['hybrid_success_rate']:.1%}",
                f"   Average confidence: {perf['average_confidence']:.2f}",
                f"   Average processing time: {perf['average_processing_time']:.2f}s",
                "",
                "🧠 Intelligence Components:",
                f"   Memory concepts: {onto_stats['total_concepts']}",
                f"   Domains: {len(onto_stats['domains'])}",
                f"   Active relationships: {onto_stats['total_relationships']}",
                f"   Behavioral API: {'✅ Connected' if self.behavioral_api_available else '⚠️ Offline'}",
            ]
            
            # Add behavioral API status
            if self.behavioral_api_available:
                try:
                    api_status = requests.get(f"{self.behavioral_api_url}/health", timeout=10).json()
                    status_parts.extend([
                        "",
                        "📊 Behavioral Intelligence:",
                        f"   API Status: {api_status.get('status', 'unknown')}",
                        f"   Digital Twin Integration: {'Active' if api_status.get('digital_twin_connected') else 'Pending'}",
                        f"   Active Users: {api_status.get('active_users', 0)}",
                        f"   Tracked Events: {api_status.get('stored_events', 0)}"
                    ])
                except Exception as e:
                    status_parts.append(f"   📊 Behavioral API: Connected but status check failed ({e})")
            else:
                status_parts.append("   📊 Behavioral API: Offline (start with: python behavioral_api_server.py)")
            
            # Add recommendations
            recommendations = analytics['system_health']['recommended_actions']
            if recommendations and recommendations != ["System operating optimally"]:
                status_parts.extend(["", "💡 Recommendations:"])
                for rec in recommendations:
                    status_parts.append(f"   • {rec}")
            else:
                status_parts.append("   ✅ All systems operating optimally")
            
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
        """Run enhanced interactive session with behavioral intelligence"""
        
        print("\n" + "="*70)
        print("🚀 Enhanced Smart Digital Twin - Behavioral Intelligence System")
        print("="*70)
        print("Features:")
        print("  • Ontology-based structured understanding")
        print("  • AI-powered semantic analysis")
        print("  • Real-time behavioral intelligence integration")
        print("  • Advanced memory search (500+ memories)")
        print("  • Comprehensive analytics and insights")
        print("  • Universal life pattern discovery")
        print("\nCommands:")
        print("  • Talk naturally - I'll understand and remember")
        print("  • 'search <query>' - Search your memories (500+ limit)")
        print("  • 'profile' - View comprehensive memory profile")
        print("  • 'behavioral' - Get behavioral intelligence analysis")
        print("  • 'status' - System status and analytics") 
        print("  • 'insights' - Deep behavioral pattern analysis")
        print("  • 'history' - Recent conversation history")
        print("  • 'help' - Show all commands")
        print("  • 'exit' - End session")
        print("="*70)
        
        # Get user ID
        user_id = input("\n👤 Enter your user ID (or press Enter for 'demo_user'): ").strip()
        if not user_id:
            user_id = "demo_user"
        
        self.current_user = user_id
        print(f"✅ Enhanced session started for user: {user_id}")
        print(f"🔗 Session ID: {self.session_id[:8]}...")
        
        # Show user's existing profile if available
        try:
            profile = self.hybrid_manager.get_user_memory_profile(user_id)
            if profile['total_memories'] > 0:
                print(f"📚 Welcome back! I have {profile['total_memories']} memories about you.")
                
                # Show behavioral intelligence if available
                if self.behavioral_api_available:
                    behavioral_stats = self.get_behavioral_stats(user_id)
                    if behavioral_stats and behavioral_stats.get('total_events', 0) > 0:
                        print(f"📊 Behavioral Intelligence: {behavioral_stats['total_events']} digital interactions tracked.")
            else:
                print("👋 Nice to meet you! Start by telling me about yourself or ask about your patterns.")
        except Exception:
            print("👋 Ready to learn about you and analyze your patterns!")
        
        print("\n" + "-"*70)
        
        while True:
            try:
                user_input = input(f"\n{user_id}: ").strip()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("\n👋 Session ended. All memories and behavioral insights preserved.")
                    print(f"💾 Processed {len(self.conversation_history)} exchanges this session.")
                    if self.behavioral_api_available:
                        print("📊 Behavioral data continues to be collected for deeper insights.")
                    break
                
                elif user_input.lower() == "help":
                    print("\n📖 Enhanced Commands:")
                    print("  General:")
                    print("    • Talk naturally - I'll process with hybrid intelligence")
                    print("    • 'search <query>' - Search your memories (up to 500 results)")
                    print("    • 'profile' - View comprehensive memory profile")
                    print("    • 'behavioral' - Get detailed behavioral analysis")
                    print("    • 'insights' - Deep pattern discovery and analytics")
                    print("  System:")
                    print("    • 'status' - System analytics and performance")
                    print("    • 'history' - Recent conversation history")
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
                
                elif user_input.lower() in ["behavioral", "behavior", "patterns"]:
                    behavioral_analysis = self.get_comprehensive_behavioral_analysis(user_id)
                    print(f"\n{behavioral_analysis}")
                    continue
                
                elif user_input.lower() in ["insights", "analysis", "analytics"]:
                    insights = self.get_deep_insights_analysis(user_id)
                    print(f"\n{insights}")
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
                        exchange_type = exchange.get('type', 'processing')
                        print(f"   {i}. [{timestamp}] You: {user_msg}")
                        print(f"      Type: {exchange_type}")
                        
                        if exchange.get('processing_report'):
                            report = exchange['processing_report']
                            print(f"      Domain: {report.get('ontology_domain', 'general')}, "
                                  f"AI confidence: {report.get('ai_confidence', 0):.2f}")
                    continue
                
                elif not user_input:
                    continue
                
                # Process the input with enhanced hybrid intelligence
                print(f"\n🧠 Processing with enhanced behavioral intelligence...")
                response = self.process_user_input(user_input, user_id)
                print(f"\nSmart Twin: {response}")
                
                # Show processing insights for this exchange
                if self.conversation_history:
                    last_exchange = self.conversation_history[-1]
                    if last_exchange.get('processing_report'):
                        report = last_exchange['processing_report']
                        if report.get('processing_time', 0) > 0:
                            print(f"\n💡 Processing: {report['processing_time']:.2f}s | "
                                  f"Domain: {report.get('ontology_domain', 'general')} | "
                                  f"Confidence: {report.get('ai_confidence', 0):.2f}")
                    
                    if last_exchange.get('api_integrated'):
                        print(f"📊 Enhanced with real-time behavioral intelligence")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. All memories preserved.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'help' for assistance.")
    
    def get_comprehensive_behavioral_analysis(self, user_id: str) -> str:
        """Get comprehensive behavioral analysis combining memory and API data"""
        
        try:
            # Get behavioral stats from API
            behavioral_stats = self.get_behavioral_stats(user_id)
            dashboard_data = self.get_dashboard_analytics(user_id)
            
            if not behavioral_stats or behavioral_stats.get('total_events', 0) == 0:
                return ("🧠 Behavioral Intelligence Analysis:\n\n"
                       "📊 I'm actively collecting your digital behavior patterns.\n"
                       "Continue using your work tools (Salesforce, Outlook, LinkedIn, etc.) "
                       "and I'll provide comprehensive behavioral insights as patterns emerge.\n\n"
                       "Current tracking includes:\n"
                       "  • Work productivity patterns\n"
                       "  • Focus and attention metrics\n"
                       "  • Tool usage optimization\n"
                       "  • Energy and efficiency trends")
            
            analysis_parts = [
                "🧠 Comprehensive Behavioral Intelligence Analysis:",
                "=" * 50
            ]
            
            # Overall statistics
            analysis_parts.extend([
                f"📈 Digital Interaction Profile:",
                f"   Total behavioral events: {behavioral_stats['total_events']}",
                f"   Digital platforms engaged: {len(behavioral_stats.get('domains', {}))}",
                f"   Data collection active: {'Yes' if self.behavioral_api_available else 'Limited'}"
            ])
            
            # Event type analysis
            if behavioral_stats.get('event_types'):
                analysis_parts.extend([
                    "",
                    "🎯 Activity Pattern Breakdown:"
                ])
                
                sorted_events = sorted(behavioral_stats['event_types'].items(), 
                                     key=lambda x: x[1], reverse=True)
                
                total_events = sum(behavioral_stats['event_types'].values())
                
                for event_type, count in sorted_events:
                    percentage = (count / total_events) * 100
                    formatted_type = event_type.replace('_', ' ').title()
                    analysis_parts.append(f"   • {formatted_type}: {count} instances ({percentage:.1f}%)")
            
            # Platform analysis
            if behavioral_stats.get('domains'):
                analysis_parts.extend([
                    "",
                    "🌐 Platform Engagement Analysis:"
                ])
                
                sorted_domains = sorted(behavioral_stats['domains'].items(), 
                                      key=lambda x: x[1], reverse=True)
                
                for domain, count in sorted_domains[:10]:  # Top 10 domains
                    analysis_parts.append(f"   • {domain}: {count} interactions")
            
            # Dashboard integration
            if dashboard_data and not dashboard_data.get('message'):
                analysis_parts.extend([
                    "",
                    "⚡ Productivity Intelligence:"
                ])
                
                # Salesforce analysis
                if dashboard_data.get('salesforce_usage', {}).get('total_sessions', 0) > 0:
                    sf_data = dashboard_data['salesforce_usage']
                    analysis_parts.extend([
                        f"   💼 Salesforce Productivity:",
                        f"      Sessions: {sf_data['total_sessions']}",
                        f"      Average time: {sf_data.get('avg_session_time', 'Unknown')}",
                        f"      Focus areas: {', '.join(sf_data.get('top_activities', []))}"
                    ])
                
                # Email efficiency
                if dashboard_data.get('email_efficiency', {}).get('emails_sent', 0) > 0:
                    email_data = dashboard_data['email_efficiency']
                    analysis_parts.extend([
                        f"   📧 Communication Efficiency:",
                        f"      Messages sent: {email_data['emails_sent']}",
                        f"      Response time: {email_data.get('avg_response_time', 'Unknown')}",
                        f"      Productivity score: {email_data.get('productivity_score', 0)}/100"
                    ])
                
                # Research patterns
                if dashboard_data.get('research_patterns', {}).get('research_sessions', 0) > 0:
                    research_data = dashboard_data['research_patterns']
                    analysis_parts.extend([
                        f"   🔍 Research Intelligence:",
                        f"      Research sessions: {research_data['research_sessions']}",
                        f"      Average depth: {research_data.get('avg_depth', 'Unknown')}",
                        f"      Primary sources: {', '.join(research_data.get('top_sources', []))}"
                    ])
                
                # Energy trends
                if dashboard_data.get('energy_trends', {}).get('focus_sessions', 0) > 0:
                    energy_data = dashboard_data['energy_trends']
                    analysis_parts.extend([
                        f"   ⚡ Energy & Focus Patterns:",
                        f"      Focus sessions: {energy_data['focus_sessions']}",
                        f"      Peak performance: {energy_data.get('peak_hours', 'Unknown')}",
                        f"      Productivity correlation: {energy_data.get('productivity_correlation', 0)}"
                    ])
            
            # Memory integration
            profile = self.hybrid_manager.get_user_memory_profile(user_id)
            if profile['total_memories'] > 0:
                analysis_parts.extend([
                    "",
                    "🧠 Memory Intelligence Integration:",
                    f"   Stored memories: {profile['total_memories']}",
                    f"   Knowledge domains: {len(profile.get('domain_distribution', {}))}",
                    f"   Recent activity: {profile.get('recent_activity', 0)} new memories (7 days)"
                ])
            
            return "\n".join(analysis_parts)
            
        except Exception as e:
            return f"Error generating behavioral analysis: {str(e)}"
    
    def get_deep_insights_analysis(self, user_id: str) -> str:
        """Get deep insights and pattern discovery analysis"""
        
        try:
            insights_parts = [
                "🔍 Deep Pattern Discovery & Insights Analysis:",
                "=" * 55
            ]
            
            # Get comprehensive data
            behavioral_stats = self.get_behavioral_stats(user_id)
            dashboard_data = self.get_dashboard_analytics(user_id)
            profile = self.hybrid_manager.get_user_memory_profile(user_id)
            
            # Memory patterns
            if profile['total_memories'] > 0:
                insights_parts.extend([
                    "🧠 Memory Pattern Analysis:",
                    f"   Knowledge complexity: {profile['total_memories']} interconnected memories",
                    f"   Information quality: {profile['average_importance']:.2f}/1.0 average importance"
                ])
                
                if profile.get('domain_distribution'):
                    primary_domain = max(profile['domain_distribution'].items(), key=lambda x: x[1])
                    insights_parts.append(f"   Primary focus area: {primary_domain[0]} ({primary_domain[1]} memories)")
                
                if profile.get('top_semantic_tags'):
                    top_tags = [tag for tag, count in profile['top_semantic_tags'][:3]]
                    insights_parts.append(f"   Key knowledge themes: {', '.join(top_tags)}")
            
            # Behavioral insights
            if behavioral_stats and behavioral_stats.get('total_events', 0) > 0:
                insights_parts.extend([
                    "",
                    "📊 Behavioral Pattern Insights:"
                ])
                
                # Calculate productivity metrics
                total_events = behavioral_stats['total_events']
                work_events = sum(count for event_type, count in behavioral_stats.get('event_types', {}).items() 
                                if any(work_word in event_type.lower() for work_word in ['salesforce', 'outlook', 'work', 'research']))
                
                if work_events > 0:
                    work_percentage = (work_events / total_events) * 100
                    insights_parts.append(f"   Work-focused behavior: {work_percentage:.1f}% of digital activity")
                
                # Platform diversity
                platform_count = len(behavioral_stats.get('domains', {}))
                if platform_count > 1:
                    insights_parts.append(f"   Digital diversity: Active across {platform_count} platforms")
                
                # Engagement intensity
                if behavioral_stats.get('event_types'):
                    most_frequent = max(behavioral_stats['event_types'].items(), key=lambda x: x[1])
                    insights_parts.append(f"   Primary digital pattern: {most_frequent[0].replace('_', ' ').title()}")
            
            # Cross-platform intelligence
            if dashboard_data and not dashboard_data.get('message'):
                insights_parts.extend([
                    "",
                    "🔗 Cross-Platform Intelligence Synthesis:"
                ])
                
                active_systems = []
                efficiency_scores = []
                
                # Analyze each system
                for system_name, system_key in [
                    ('Salesforce', 'salesforce_usage'),
                    ('Email', 'email_efficiency'),
                    ('Research', 'research_patterns'),
                    ('Focus', 'energy_trends')
                ]:
                    system_data = dashboard_data.get(system_key, {})
                    if system_data and not system_data.get('loading'):
                        active_systems.append(system_name)
                        
                        # Extract efficiency metrics where available
                        if 'productivity_score' in system_data:
                            efficiency_scores.append(system_data['productivity_score'])
                
                if active_systems:
                    insights_parts.append(f"   Integrated systems: {', '.join(active_systems)}")
                
                if efficiency_scores:
                    avg_efficiency = sum(efficiency_scores) / len(efficiency_scores)
                    insights_parts.append(f"   Overall efficiency index: {avg_efficiency:.1f}/100")
            
            # Temporal patterns
            if behavioral_stats and behavioral_stats.get('total_events', 0) > 10:
                insights_parts.extend([
                    "",
                    "⏰ Temporal Intelligence Patterns:",
                    "   Pattern recognition: Analyzing usage timing and frequency",
                    "   Trend analysis: Identifying peak performance periods",
                    "   Optimization opportunities: Based on behavioral rhythms"
                ])
            
            # Predictive insights
            insights_parts.extend([
                "",
                "🔮 Predictive Insights & Recommendations:"
            ])
            
            # Generate recommendations based on available data
            recommendations = []
            
            if profile['total_memories'] > 50:
                recommendations.append("Rich knowledge base established - excellent for complex pattern analysis")
            
            if behavioral_stats and behavioral_stats.get('total_events', 0) > 100:
                recommendations.append("Strong behavioral data foundation - ready for advanced optimization insights")
            
            if self.behavioral_api_available:
                recommendations.append("Real-time behavioral intelligence active - continuous learning enabled")
            
            if not recommendations:
                recommendations.append("Continue using your digital tools to build intelligence foundation")
                recommendations.append("Ask specific questions about patterns you're curious about")
                recommendations.append("Share more personal context to enhance understanding depth")
            
            for rec in recommendations:
                insights_parts.append(f"   • {rec}")
            
            # Future capabilities
            insights_parts.extend([
                "",
                "🚀 Evolving Intelligence Capabilities:",
                "   • Advanced pattern prediction as data grows",
                "   • Cross-temporal behavior analysis",
                "   • Personalized optimization recommendations",
                "   • Intelligent automation suggestions",
                "   • Universal life pattern discovery"
            ])
            
            return "\n".join(insights_parts)
            
        except Exception as e:
            return f"Error generating deep insights: {str(e)}"

def main():
    """Main function to run enhanced smart digital twin"""
    
    try:
        enhanced_twin = SmartDigitalTwin()
        enhanced_twin.run_interactive_session()
        
    except KeyboardInterrupt:
        print("\n👋 Startup interrupted.")
    except Exception as e:
        print(f"❌ Failed to initialize Enhanced Smart Digital Twin: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has all required Azure credentials")
        print("2. Ensure Azure Search index was created successfully")
        print("3. Verify hybrid memory system components are available")
        print("4. Start behavioral API server: python behavioral_api_server.py")
        print("5. Run system test: python quick_system_test.py")

if __name__ == "__main__":
    main()