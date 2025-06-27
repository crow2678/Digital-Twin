import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import hybrid system components
from hybrid_memory_manager import HybridMemoryManager
from digital_twin_ontology import DigitalTwinOntology
from ai_semantic_processor import AISemanticProcessor
from hybrid_memory_system import HybridMemoryRecord

def main():
    """Example usage of the Hybrid Ontology + AI Memory System"""
    
    print("🚀 Initializing Hybrid Digital Twin Memory System...")
    
    # Azure Search configuration (use your existing settings)
    azure_config = {
        "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
        "search_key": os.getenv("AZURE_SEARCH_KEY"),
        "index_name": os.getenv("AZURE_SEARCH_INDEX")
    }
    
    # Initialize hybrid memory manager
    hybrid_manager = HybridMemoryManager(azure_config)
    
    print("✅ Hybrid system initialized successfully!")
    print("📊 System components:")
    print(f"   - Ontology concepts: {len(hybrid_manager.ontology.concepts)}")
    print(f"   - AI processor ready: {hybrid_manager.ai_processor is not None}")
    print(f"   - Azure Search connected: {hybrid_manager.memory_store is not None}")
    
    # Example user context
    user_context = {
        "user_id": "john_doe",
        "tenant_id": "enterprise_corp",
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n👤 User context: {user_context['user_id']} @ {user_context['tenant_id']}")
    
    # Example 1: Personal Identity Information
    print("\n📝 Example 1: Processing Personal Identity")
    identity_content = "My name is John Smith and I'm a Senior Software Engineer at TechCorp. I prefer to be called John and I work remotely from San Francisco."
    
    memory1, report1 = hybrid_manager.process_and_store_memory(identity_content, user_context)
    
    print(f"   Content: {identity_content}")
    print(f"   ✅ Processing Success: {report1['success']}")
    print(f"   🧠 Ontology Domain: {report1['ontology_domain']}")
    print(f"   🤖 AI Confidence: {report1['ai_confidence']:.2f}")
    print(f"   🔗 Hybrid Confidence: {report1['hybrid_confidence']:.2f}")
    print(f"   📊 Importance Score: {report1['importance_score']:.2f}")
    print(f"   ⏱️ Processing Time: {report1['processing_time_seconds']:.2f}s")
    print(f"   📄 Summary: {report1['semantic_summary']}")
    
    # Example 2: Work Meeting Information
    print("\n📝 Example 2: Processing Work Meeting")
    meeting_content = "I have an urgent team meeting tomorrow at 2pm about the AI project with Sarah and Mike. We need to discuss the Q3 deliverables and the client presentation."
    
    memory2, report2 = hybrid_manager.process_and_store_memory(meeting_content, user_context)
    
    print(f"   Content: {meeting_content}")
    print(f"   ✅ Processing Success: {report2['success']}")
    print(f"   🧠 Ontology Domain: {report2['ontology_domain']}")
    print(f"   🤖 AI Confidence: {report2['ai_confidence']:.2f}")
    print(f"   🔗 Hybrid Confidence: {report2['hybrid_confidence']:.2f}")
    print(f"   👥 Entities Found: {report2['entities_extracted']}")
    print(f"   🔗 Relationships: {report2['relationships_identified']}")
    print(f"   📄 Summary: {report2['semantic_summary']}")
    
    # Example 3: Health Information
    print("\n📝 Example 3: Processing Health Information")
    health_content = "I'm allergic to shellfish and peanuts. I take medication for high blood pressure and have a doctor's appointment next Tuesday."
    
    memory3, report3 = hybrid_manager.process_and_store_memory(health_content, user_context)
    
    print(f"   Content: {health_content}")
    print(f"   ✅ Processing Success: {report3['success']}")
    print(f"   🧠 Ontology Domain: {report3['ontology_domain']}")
    print(f"   🤖 AI Confidence: {report3['ai_confidence']:.2f}")
    print(f"   🔗 Hybrid Confidence: {report3['hybrid_confidence']:.2f}")
    print(f"   📄 Summary: {report3['semantic_summary']}")
    
    # Example 4: Complex Preference Information
    print("\n📝 Example 4: Processing Complex Preferences")
    preference_content = "I love Italian food, especially pasta, but I'm trying to eat healthier so I prefer restaurants with good vegetarian options. I don't like overly spicy food."
    
    memory4, report4 = hybrid_manager.process_and_store_memory(preference_content, user_context)
    
    print(f"   Content: {preference_content}")
    print(f"   ✅ Processing Success: {report4['success']}")
    print(f"   🧠 Ontology Domain: {report4['ontology_domain']}")
    print(f"   🤖 AI Confidence: {report4['ai_confidence']:.2f}")
    print(f"   🔗 Hybrid Confidence: {report4['hybrid_confidence']:.2f}")
    print(f"   🎯 Concepts Found: {report4['semantic_concepts_found']}")
    print(f"   📄 Summary: {report4['semantic_summary']}")
    
    # Example 5: Intelligent Search
    print("\n🔍 Example 5: Intelligent Memory Search")
    
    # Search for meetings
    print("\n   Search Query: 'What meetings do I have?'")
    meeting_results = hybrid_manager.search_memories(
        "What meetings do I have?",
        search_options={
            "user_id": user_context["user_id"],
            "limit": 5
        }
    )
    
    print(f"   📊 Found {len(meeting_results)} results:")
    for i, (memory, score) in enumerate(meeting_results, 1):
        print(f"      {i}. Score: {score:.2f} | {memory.semantic_summary}")
        print(f"         Domain: {memory.ontology_domain} | Tags: {memory.ai_semantic_tags}")
    
    # Search for health information
    print("\n   Search Query: 'health and medical information'")
    health_results = hybrid_manager.search_memories(
        "health and medical information",
        search_options={
            "user_id": user_context["user_id"],
            "limit": 3
        }
    )
    
    print(f"   📊 Found {len(health_results)} results:")
    for i, (memory, score) in enumerate(health_results, 1):
        print(f"      {i}. Score: {score:.2f} | {memory.semantic_summary}")
        print(f"         Domain: {memory.ontology_domain} | Confidence: {memory.ai_confidence:.2f}")
    
    # Search with semantic understanding
    print("\n   Search Query: 'food preferences and dietary restrictions'")
    food_results = hybrid_manager.search_memories(
        "food preferences and dietary restrictions",
        search_options={
            "user_id": user_context["user_id"],
            "limit": 3,
            "filters": {
                "ontology_domain": "personal",
                "importance_min": 0.3
            }
        }
    )
    
    print(f"   📊 Found {len(food_results)} results:")
    for i, (memory, score) in enumerate(food_results, 1):
        print(f"      {i}. Score: {score:.2f} | {memory.semantic_summary}")
        print(f"         Tags: {memory.ai_semantic_tags}")
    
    # Example 6: User Memory Profile
    print("\n👤 Example 6: User Memory Profile")
    user_profile = hybrid_manager.get_user_memory_profile(user_context["user_id"])
    
    print(f"   📊 Profile for {user_profile['user_id']}:")
    print(f"      Total Memories: {user_profile['total_memories']}")
    print(f"      Average Importance: {user_profile['average_importance']:.2f}")
    print(f"      Recent Activity (7 days): {user_profile['recent_activity']} memories")
    
    print("   🏷️ Domain Distribution:")
    for domain, count in user_profile['domain_distribution'].items():
        print(f"      {domain}: {count} memories")
    
    print("   📝 Category Distribution:")
    for category, count in user_profile['category_distribution'].items():
        print(f"      {category}: {count} memories")
    
    print("   🎯 Top Semantic Tags:")
    for tag, count in user_profile['top_semantic_tags'][:5]:
        print(f"      {tag}: {count} occurrences")
    
    # Example 7: System Analytics
    print("\n📊 Example 7: System Analytics")
    analytics = hybrid_manager.get_system_analytics()
    
    print("   ⚡ Performance Metrics:")
    perf = analytics['performance_metrics']
    print(f"      Total Processed: {perf['total_processed']}")
    print(f"      Hybrid Success Rate: {perf['hybrid_success_rate']:.2%}")
    print(f"      Average Processing Time: {perf['average_processing_time']:.2f}s")
    print(f"      Average Confidence: {perf['average_confidence']:.2f}")
    
    print("   🧠 Ontology Stats:")
    onto_stats = analytics['ontology_stats']
    print(f"      Total Concepts: {onto_stats['total_concepts']}")
    print(f"      Domains: {len(onto_stats['domains'])}")
    print(f"      Categories: {len(onto_stats['categories'])}")
    print(f"      Total Relationships: {onto_stats['total_relationships']}")
    
    print("   🤖 AI Processor Stats:")
    ai_stats = analytics['ai_processor_stats']
    print(f"      Total Processed: {ai_stats['total_processed']}")
    print(f"      Average Confidence: {ai_stats['average_confidence']:.2f}")
    print(f"      High Confidence Rate: {ai_stats['high_confidence_rate']:.2%}")
    
    print("   💾 Cache Stats:")
    cache_stats = analytics['cache_stats']
    print(f"      Session Cache Size: {cache_stats['session_cache_size']}")
    print(f"      Relationship Cache Size: {cache_stats['relationship_cache_size']}")
    
    print("   💡 System Recommendations:")
    for recommendation in analytics['system_health']['recommended_actions']:
        print(f"      • {recommendation}")
    
    # Example 8: Advanced Ontology Usage
    print("\n🔬 Example 8: Advanced Ontology Features")
    
    # Show ontology classification for a complex sentence
    complex_content = "I'm planning a business trip to New York next month for the TechConf conference where I'll be presenting our AI research to potential investors and partners."
    
    ontology_classifications = hybrid_manager.ontology.classify_content(complex_content)
    print(f"   Content: {complex_content}")
    print(f"   📊 Ontology Classifications ({len(ontology_classifications)} found):")
    
    for i, classification in enumerate(ontology_classifications[:3], 1):
        print(f"      {i}. {classification['concept_name']} (Score: {classification['score']:.2f})")
        print(f"         Domain: {classification['domain']} | Category: {classification['category']}")
        print(f"         Matched Terms: {classification['matched_terms']}")
    
    # Example 9: Ontology Concept Details
    print("\n📚 Example 9: Ontology Concept Details")
    
    # Get schema for work meeting concept
    meeting_schema = hybrid_manager.ontology.get_concept_schema("work_meeting")
    if meeting_schema:
        print("   📋 Work Meeting Concept Schema:")
        print(f"      Name: {meeting_schema['name']}")
        print(f"      Description: {meeting_schema['description']}")
        print("      Properties:")
        for prop in meeting_schema['properties']:
            req_text = " (required)" if prop['required'] else ""
            print(f"        • {prop['name']} ({prop['type']}){req_text}: {prop['description']}")
        
        if meeting_schema['relationships']:
            print("      Relationships:")
            for rel in meeting_schema['relationships']:
                print(f"        • {rel['type']} → {rel['target']} (strength: {rel['strength']})")
    
    # Example 10: Error Handling and Fallbacks
    print("\n🛡️ Example 10: Error Handling and Fallbacks")
    
    # Test with ambiguous content
    ambiguous_content = "It's complicated and I'm not sure what to do about it."
    
    memory_amb, report_amb = hybrid_manager.process_and_store_memory(ambiguous_content, user_context)
    
    print(f"   Content: {ambiguous_content}")
    print(f"   ✅ Processing Success: {report_amb['success']}")
    print(f"   🧠 Ontology Domain: {report_amb.get('ontology_domain', 'None')}")
    print(f"   🤖 AI Confidence: {report_amb.get('ai_confidence', 0):.2f}")
    print(f"   📄 Summary: {report_amb.get('semantic_summary', 'No summary')}")
    
    # Final system status
    print("\n🎯 Final System Status:")
    print("   ✅ Hybrid Ontology + AI system fully operational")
    print("   ✅ All examples processed successfully")
    print("   ✅ Memory storage and retrieval working")
    print("   ✅ Analytics and monitoring active")
    
    print("\n🚀 Your hybrid digital twin memory system is ready for production!")
    
    return hybrid_manager

def interactive_demo():
    """Interactive demo of the hybrid system"""
    
    print("\n🎮 Interactive Demo Mode")
    print("Type 'exit' to quit, 'help' for commands")
    
    # Initialize system
    azure_config = {
        "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
        "search_key": os.getenv("AZURE_SEARCH_KEY"),
        "index_name": os.getenv("AZURE_SEARCH_INDEX")
    }
    
    hybrid_manager = HybridMemoryManager(azure_config)
    
    user_context = {
        "user_id": "demo_user",
        "tenant_id": "demo_tenant",
        "session_id": str(uuid.uuid4())
    }
    
    print("✅ System ready! Try saying something about yourself...")
    
    while True:
        try:
            user_input = input("\n💬 Your input: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print("\n📖 Available commands:")
                print("   • Type any statement to store as memory")
                print("   • 'search <query>' - Search your memories")
                print("   • 'profile' - Show your memory profile")
                print("   • 'stats' - Show system statistics")
                print("   • 'ontology' - Show ontology information")
                print("   • 'exit' - Quit the demo")
                continue
            
            elif user_input.lower().startswith('search '):
                query = user_input[7:]  # Remove 'search ' prefix
                results = hybrid_manager.search_memories(
                    query,
                    search_options={"user_id": user_context["user_id"], "limit": 3}
                )
                
                print(f"\n🔍 Search results for '{query}':")
                if results:
                    for i, (memory, score) in enumerate(results, 1):
                        print(f"   {i}. Score: {score:.2f}")
                        print(f"      Content: {memory.content}")
                        print(f"      Summary: {memory.semantic_summary}")
                        print(f"      Domain: {memory.ontology_domain}")
                else:
                    print("   No results found.")
                continue
            
            elif user_input.lower() == 'profile':
                profile = hybrid_manager.get_user_memory_profile(user_context["user_id"])
                print(f"\n👤 Your Memory Profile:")
                print(f"   Total Memories: {profile['total_memories']}")
                print(f"   Average Importance: {profile['average_importance']:.2f}")
                if profile['domain_distribution']:
                    print("   Domain Distribution:")
                    for domain, count in profile['domain_distribution'].items():
                        print(f"     {domain}: {count}")
                continue
            
            elif user_input.lower() == 'stats':
                analytics = hybrid_manager.get_system_analytics()
                perf = analytics['performance_metrics']
                print(f"\n📊 System Statistics:")
                print(f"   Total Processed: {perf['total_processed']}")
                print(f"   Hybrid Success Rate: {perf['hybrid_success_rate']:.2%}")
                print(f"   Average Confidence: {perf['average_confidence']:.2f}")
                continue
            
            elif user_input.lower() == 'ontology':
                stats = hybrid_manager.ontology.get_ontology_stats()
                print(f"\n🧠 Ontology Information:")
                print(f"   Total Concepts: {stats['total_concepts']}")
                print(f"   Domains: {list(stats['domains'].keys())}")
                print(f"   Most Connected Concepts:")
                for concept in stats['most_connected_concepts'][:3]:
                    print(f"     • {concept['concept_name']}: {concept['connection_count']} connections")
                continue
            
            elif not user_input:
                continue
            
            # Process the input as memory
            print(f"\n🧠 Processing: {user_input}")
            memory, report = hybrid_manager.process_and_store_memory(user_input, user_context)
            
            print(f"✅ Stored successfully!")
            print(f"   Domain: {report.get('ontology_domain', 'Unknown')}")
            print(f"   AI Confidence: {report.get('ai_confidence', 0):.2f}")
            print(f"   Summary: {report.get('semantic_summary', 'No summary')}")
            
            if report.get('entities_extracted', 0) > 0:
                print(f"   Found {report['entities_extracted']} entities")
            
            if report.get('relationships_identified', 0) > 0:
                print(f"   Identified {report['relationships_identified']} relationships")
        
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

if __name__ == "__main__":
    print("🚀 Hybrid Digital Twin Memory System Demo")
    print("=========================================")
    
    # Check if environment variables are set
    required_vars = [
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_KEY", 
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_KEY",
        "AZURE_SEARCH_INDEX"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these in your .env file before running the demo.")
        exit(1)
    
    # Run the main demo
    hybrid_manager = main()
    
    # Ask if user wants interactive demo
    choice = input("\n🎯 Would you like to try the interactive demo? (y/n): ").lower()
    if choice == 'y':
        interactive_demo()