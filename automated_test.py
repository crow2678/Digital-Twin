#!/usr/bin/env python3
"""
Test script to verify user preference learning
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.schema import Document

load_dotenv()

# Set up the embedding model and vector store
embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

vector_store = AzureSearch(
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    embedding_function=embedding_model.embed_query,
)

def test_learning_simulation():
    """Simulate the learning process"""
    print("🧪 Testing Enhanced Learning System")
    print("=" * 50)
    
    # Simulate user saying "call me Jarvis"
    user_preference = Document(
        page_content="User prefers to be called 'Jarvis' instead of their real name. Always address them as Jarvis.",
        metadata={
            'type': 'user_preference',
            'category': 'addressing',
            'priority': 'critical',
            'extracted_value': 'Jarvis',
            'timestamp': '2025-06-09 18:00',
            'auto_generated': True,
            'source': 'conversation_learning'
        }
    )
    
    # Add the preference
    try:
        vector_store.add_documents([user_preference])
        print("✅ Added user preference: Call user 'Jarvis'")
    except Exception as e:
        print(f"❌ Error adding preference: {e}")
        return False
    
    # Test retrieval
    print("\n🔍 Testing retrieval for 'what name do I prefer'...")
    try:
        results = vector_store.similarity_search("what name user prefer called address", k=5)
        print(f"Found {len(results)} results:")
        
        found_jarvis = False
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.page_content[:80]}...")
            if "Jarvis" in result.page_content:
                found_jarvis = True
                print("   ✅ Found Jarvis preference!")
                
        if not found_jarvis:
            print("❌ Jarvis preference not found in search results")
            return False
            
    except Exception as e:
        print(f"❌ Error in retrieval: {e}")
        return False
    
    print("\n✅ Learning system test passed!")
    return True

def test_current_memories():
    """Check what's currently in memory"""
    print("\n🔍 Current memories in the system:")
    try:
        # Search for various types of memories
        all_results = vector_store.similarity_search("user prefer Jarvis name call address", k=10)
        
        if not all_results:
            print("No memories found.")
            return
            
        for i, result in enumerate(all_results, 1):
            metadata = result.metadata or {}
            memory_type = metadata.get('type', 'unknown')
            category = metadata.get('category', 'unknown')
            priority = metadata.get('priority', 'unknown')
            
            print(f"{i}. [{memory_type}/{category}] {result.page_content[:100]}...")
            
    except Exception as e:
        print(f"❌ Error checking memories: {e}")

if __name__ == "__main__":
    print("Starting preference learning test...\n")
    
    # Test current state
    test_current_memories()
    
    # Simulate learning
    success = test_learning_simulation()
    
    if success:
        print("\n🎉 Now test with: python enhanced_twin_with_learning.py")
        print("Ask: 'what name do I prefer to be called?'")
        print("Expected: Should mention 'Jarvis' from memory")
    else:
        print("\n❌ Test failed. Check the errors above.")