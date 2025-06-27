import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_system_components():
    """Test all system components before running"""
    
    print("🧪 Testing Hybrid Digital Twin System Components")
    print("=" * 55)
    
    test_results = {}
    
    # Test 1: Environment Variables
    print("1️⃣ Testing Environment Variables...")
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
        test_results["environment"] = False
    else:
        print("✅ All environment variables present")
        test_results["environment"] = True
    
    # Test 2: File Imports
    print("\n2️⃣ Testing File Imports...")
    try:
        from digital_twin_ontology import DigitalTwinOntology
        print("✅ digital_twin_ontology.py imported successfully")
        
        from ai_semantic_processor import AISemanticProcessor
        print("✅ ai_semantic_processor.py imported successfully")
        
        from hybrid_memory_system import HybridMemoryRecord, HybridInformationProcessor
        print("✅ hybrid_memory_system.py imported successfully")
        
        from hybrid_memory_manager import HybridMemoryManager
        print("✅ hybrid_memory_manager.py imported successfully")
        
        from enhanced_twin_controller import EnhancedDigitalTwin
        print("✅ enhanced_twin_controller.py imported successfully")
        
        test_results["imports"] = True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        test_results["imports"] = False
    
    # Test 3: Component Initialization
    print("\n3️⃣ Testing Component Initialization...")
    try:
        # Test ontology
        ontology = DigitalTwinOntology()
        print(f"✅ Ontology initialized with {len(ontology.concepts)} concepts")
        
        # Test hybrid manager
        azure_config = {
            "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
            "search_key": os.getenv("AZURE_SEARCH_KEY"),
            "index_name": os.getenv("AZURE_SEARCH_INDEX")
        }
        
        hybrid_manager = HybridMemoryManager(azure_config)
        print("✅ Hybrid Memory Manager initialized successfully")
        
        test_results["initialization"] = True
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        test_results["initialization"] = False
    
    # Test 4: Basic Memory Processing
    print("\n4️⃣ Testing Basic Memory Processing...")
    if test_results.get("initialization"):
        try:
            test_content = "This is a test memory for system validation"
            test_context = {
                "user_id": "system_test",
                "tenant_id": "test_tenant",
                "session_id": "validation_session"
            }
            
            memory, report = hybrid_manager.process_and_store_memory(test_content, test_context)
            
            if report["success"]:
                print("✅ Memory processing successful")
                print(f"   Domain: {report.get('ontology_domain', 'Unknown')}")
                print(f"   AI Confidence: {report.get('ai_confidence', 0):.2f}")
                print(f"   Processing Time: {report.get('processing_time_seconds', 0):.2f}s")
                test_results["processing"] = True
            else:
                print("❌ Memory processing failed")
                test_results["processing"] = False
                
        except Exception as e:
            print(f"❌ Processing error: {e}")
            test_results["processing"] = False
    else:
        print("⏭️ Skipping processing test (initialization failed)")
        test_results["processing"] = False
    
    # Test 5: Search Functionality
    print("\n5️⃣ Testing Search Functionality...")
    if test_results.get("processing"):
        try:
            search_results = hybrid_manager.search_memories(
                "test validation",
                search_options={"user_id": "system_test", "limit": 1}
            )
            
            if search_results:
                print(f"✅ Search successful - found {len(search_results)} results")
                memory, score = search_results[0]
                print(f"   Best match score: {score:.2f}")
                test_results["search"] = True
            else:
                print("⚠️ Search returned no results (may be normal for new index)")
                test_results["search"] = True  # Not necessarily an error
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            test_results["search"] = False
    else:
        print("⏭️ Skipping search test (processing failed)")
        test_results["search"] = False
    
    # Test Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 55)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.title():15} {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL SYSTEMS GO! Your hybrid digital twin is ready!")
        return True
    elif passed_tests >= 3:
        print("\n⚠️ System partially ready - check failed components")
        return True
    else:
        print("\n❌ System not ready - please fix errors above")
        return False

def get_system_info():
    """Get system information and recommendations"""
    
    print("\n📋 SYSTEM INFORMATION")
    print("=" * 55)
    
    try:
        from hybrid_memory_manager import HybridMemoryManager
        
        azure_config = {
            "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
            "search_key": os.getenv("AZURE_SEARCH_KEY"),
            "index_name": os.getenv("AZURE_SEARCH_INDEX")
        }
        
        hybrid_manager = HybridMemoryManager(azure_config)
        
        # Get system analytics
        analytics = hybrid_manager.get_system_analytics()
        
        print("🧠 Ontology Stats:")
        onto_stats = analytics['ontology_stats']
        print(f"   Total Concepts: {onto_stats['total_concepts']}")
        print(f"   Domains: {len(onto_stats['domains'])}")
        print(f"   Available domains: {list(onto_stats['domains'].keys())}")
        
        print("\n🔧 System Configuration:")
        print(f"   Azure Search Index: {os.getenv('AZURE_SEARCH_INDEX')}")
        print(f"   OpenAI Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
        print(f"   Embedding Model: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT')}")
        
        print("\n💡 Available Commands:")
        print("   python enhanced_twin_controller.py  # Interactive digital twin")
        print("   python hybrid_usage_example.py      # Complete example demo")
        
    except Exception as e:
        print(f"Could not load system info: {e}")

if __name__ == "__main__":
    print("🚀 Hybrid Digital Twin System Validation")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    system_ready = test_system_components()
    
    if system_ready:
        get_system_info()
        
        print("\n🎯 NEXT STEPS:")
        print("1. Run the interactive system:")
        print("   python enhanced_twin_controller.py")
        print("\n2. Or try the complete demo:")
        print("   python hybrid_usage_example.py")
        print("\n3. Or integrate with your existing code")
        
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check your .env file has all required variables")
        print("2. Ensure all 5 Python files are created correctly")
        print("3. Verify Azure Search index was updated successfully")
        print("4. Check internet connection for Azure services")