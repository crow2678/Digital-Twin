#!/usr/bin/env python3
"""
Memory Database Inspector - View All Stored Memories for Paresh
Comprehensive analysis of what's actually stored in the Digital Twin system
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def inspect_azure_search_memories():
    """Inspect memories stored in Azure Search"""
    print("🔍 AZURE SEARCH MEMORY INSPECTION")
    print("=" * 60)
    
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Azure Search connection
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_KEY")
        index_name = os.getenv("AZURE_SEARCH_INDEX")
        
        if not all([search_endpoint, search_key, index_name]):
            print("❌ Missing Azure Search configuration")
            return []
        
        credential = AzureKeyCredential(search_key)
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=credential
        )
        
        # Search for all Paresh's memories
        print(f"📡 Searching index: {index_name}")
        print(f"🔎 Looking for user: Paresh")
        
        # Try different search approaches
        search_queries = [
            "*",  # All documents
            "Paresh",  # Documents containing Paresh
            "user_id:Paresh",  # User ID filter (if supported)
        ]
        
        all_memories = []
        
        for query in search_queries:
            try:
                print(f"\n🔍 Search query: '{query}'")
                
                if query == "*":
                    # Get all documents
                    results = search_client.search(
                        search_text="",
                        top=1000,
                        include_total_count=True
                    )
                else:
                    # Targeted search
                    results = search_client.search(
                        search_text=query,
                        top=1000,
                        include_total_count=True
                    )
                
                memory_count = 0
                paresh_memories = []
                
                for result in results:
                    memory_count += 1
                    result_dict = dict(result)
                    
                    # Check if this is Paresh's memory
                    is_paresh_memory = (
                        result_dict.get('user_id') == 'Paresh' or
                        'paresh' in str(result_dict.get('content', '')).lower() or
                        'paresh' in str(result_dict.get('metadata', '')).lower()
                    )
                    
                    if is_paresh_memory:
                        paresh_memories.append(result_dict)
                    
                    # Show first few results for debugging
                    if memory_count <= 5:
                        print(f"   Result {memory_count}: {list(result_dict.keys())}")
                        if 'content' in result_dict:
                            content_preview = str(result_dict['content'])[:100]
                            print(f"      Content: {content_preview}...")
                        if 'user_id' in result_dict:
                            print(f"      User ID: {result_dict.get('user_id')}")
                        if 'metadata' in result_dict:
                            print(f"      Metadata keys: {list(result_dict.get('metadata', {}).keys()) if isinstance(result_dict.get('metadata'), dict) else 'Not dict'}")
                
                print(f"   📊 Total results: {memory_count}")
                print(f"   👤 Paresh's memories: {len(paresh_memories)}")
                
                all_memories.extend(paresh_memories)
                
                if len(paresh_memories) > 0:
                    break  # Found memories, no need to try other queries
                    
            except Exception as e:
                print(f"   ❌ Error with query '{query}': {e}")
                continue
        
        return all_memories
        
    except ImportError as e:
        print(f"❌ Azure Search SDK not available: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inspecting Azure Search: {e}")
        return []

def inspect_langchain_vector_store():
    """Inspect LangChain vector store"""
    print("\n🔍 LANGCHAIN VECTOR STORE INSPECTION")
    print("=" * 60)
    
    try:
        from langchain_openai import AzureOpenAIEmbeddings
        from langchain_community.vectorstores.azuresearch import AzureSearch
        
        # Set up embeddings
        embedding_model = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        # Set up vector store
        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX"),
            embedding_function=embedding_model.embed_query,
        )
        
        print("✅ LangChain vector store connected")
        
        # Search for Paresh's memories
        search_queries = [
            "Paresh",
            "user",
            "work",
            "meeting",
            "sales",
            "productivity"
        ]
        
        all_documents = []
        
        for query in search_queries:
            try:
                print(f"\n🔍 Vector search: '{query}'")
                results = vector_store.similarity_search(query, k=20)
                
                print(f"   📊 Found {len(results)} documents")
                
                for i, doc in enumerate(results[:5]):  # Show first 5
                    print(f"   Doc {i+1}:")
                    print(f"      Content: {doc.page_content[:100]}...")
                    print(f"      Metadata: {doc.metadata}")
                
                all_documents.extend(results)
                
            except Exception as e:
                print(f"   ❌ Error with query '{query}': {e}")
        
        return all_documents
        
    except ImportError as e:
        print(f"❌ LangChain not available: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inspecting LangChain: {e}")
        return []

def inspect_hybrid_memory_system():
    """Inspect the hybrid memory system directly"""
    print("\n🔍 HYBRID MEMORY SYSTEM INSPECTION")
    print("=" * 60)
    
    try:
        # Try to import and initialize the hybrid system
        from hybrid_memory_manager import HybridMemoryManager
        
        azure_config = {
            "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
            "search_key": os.getenv("AZURE_SEARCH_KEY"),
            "index_name": os.getenv("AZURE_SEARCH_INDEX")
        }
        
        hybrid_manager = HybridMemoryManager(azure_config)
        print("✅ Hybrid Memory Manager initialized")
        
        # Get Paresh's profile
        user_profile = hybrid_manager.get_user_memory_profile("Paresh")
        print(f"\n👤 Paresh's Profile:")
        print(json.dumps(user_profile, indent=2, default=str))
        
        # Search for Paresh's memories
        print(f"\n🔍 Searching Paresh's memories...")
        memories = hybrid_manager.search_memories(
            "Paresh user work sales",
            search_options={"user_id": "Paresh", "limit": 50}
        )
        
        print(f"📊 Found {len(memories)} memories for Paresh")
        
        paresh_memories = []
        for memory, score in memories:
            memory_info = {
                "id": memory.id,
                "content": memory.content,
                "timestamp": memory.timestamp.isoformat(),
                "ontology_domain": memory.ontology_domain,
                "ontology_category": memory.ontology_category,
                "ai_confidence": memory.ai_confidence,
                "importance_score": memory.importance_score,
                "semantic_summary": memory.semantic_summary,
                "user_id": memory.user_id,
                "score": score
            }
            paresh_memories.append(memory_info)
        
        return paresh_memories
        
    except ImportError as e:
        print(f"❌ Hybrid system not available: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inspecting hybrid system: {e}")
        return []

def analyze_memory_patterns(memories: List[Dict]):
    """Analyze patterns in the collected memories"""
    print("\n📊 MEMORY PATTERN ANALYSIS")
    print("=" * 60)
    
    if not memories:
        print("❌ No memories to analyze")
        return
    
    print(f"📈 Total memories analyzed: {len(memories)}")
    
    # Content analysis
    content_words = {}
    domains = {}
    timestamps = []
    
    for memory in memories:
        # Analyze content
        content = str(memory.get('content', ''))
        words = content.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                content_words[word] = content_words.get(word, 0) + 1
        
        # Analyze domains
        domain = memory.get('ontology_domain') or memory.get('domain') or 'unknown'
        domains[domain] = domains.get(domain, 0) + 1
        
        # Collect timestamps
        timestamp_str = memory.get('timestamp')
        if timestamp_str:
            try:
                if isinstance(timestamp_str, str):
                    timestamps.append(datetime.fromisoformat(timestamp_str.replace('Z', '')))
                elif isinstance(timestamp_str, datetime):
                    timestamps.append(timestamp_str)
            except:
                pass
    
    # Show top content words
    print(f"\n🏷️ Top content themes:")
    sorted_words = sorted(content_words.items(), key=lambda x: x[1], reverse=True)
    for word, count in sorted_words[:10]:
        print(f"   {word}: {count} mentions")
    
    # Show domain distribution
    print(f"\n📁 Domain distribution:")
    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
        print(f"   {domain}: {count} memories")
    
    # Show time range
    if timestamps:
        timestamps.sort()
        print(f"\n⏰ Time range:")
        print(f"   Earliest: {timestamps[0].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Latest: {timestamps[-1].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Span: {(timestamps[-1] - timestamps[0]).days} days")

def main():
    """Main inspection function"""
    print("🔍 DIGITAL TWIN MEMORY DATABASE INSPECTOR")
    print("=" * 70)
    print(f"🕒 Inspection time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Target user: Paresh")
    
    all_memories = []
    
    # Method 1: Azure Search direct inspection
    azure_memories = inspect_azure_search_memories()
    if azure_memories:
        all_memories.extend(azure_memories)
        print(f"✅ Azure Search: {len(azure_memories)} memories found")
    
    # Method 2: LangChain vector store inspection
    langchain_docs = inspect_langchain_vector_store()
    if langchain_docs:
        # Convert LangChain docs to memory format
        for doc in langchain_docs:
            memory_info = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": "langchain"
            }
            all_memories.append(memory_info)
        print(f"✅ LangChain: {len(langchain_docs)} documents found")
    
    # Method 3: Hybrid system inspection
    hybrid_memories = inspect_hybrid_memory_system()
    if hybrid_memories:
        all_memories.extend(hybrid_memories)
        print(f"✅ Hybrid System: {len(hybrid_memories)} memories found")
    
    # Remove duplicates based on content
    unique_memories = []
    seen_content = set()
    
    for memory in all_memories:
        content = str(memory.get('content', ''))[:100]  # First 100 chars
        if content not in seen_content:
            seen_content.add(content)
            unique_memories.append(memory)
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   Total raw results: {len(all_memories)}")
    print(f"   Unique memories: {len(unique_memories)}")
    
    # Analyze patterns
    analyze_memory_patterns(unique_memories)
    
    # Show detailed memory samples
    print(f"\n📝 SAMPLE MEMORIES (First 10):")
    print("=" * 60)
    
    for i, memory in enumerate(unique_memories[:10], 1):
        print(f"\n{i}. Memory ID: {memory.get('id', 'Unknown')}")
        print(f"   Content: {str(memory.get('content', ''))[:200]}...")
        print(f"   Domain: {memory.get('ontology_domain') or memory.get('domain', 'Unknown')}")
        print(f"   User ID: {memory.get('user_id', 'Unknown')}")
        print(f"   Timestamp: {memory.get('timestamp', 'Unknown')}")
        if 'score' in memory:
            print(f"   Relevance Score: {memory['score']:.3f}")
    
    # Save detailed results to file
    output_file = f"paresh_memory_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_memories, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to: {output_file}")
    except Exception as e:
        print(f"\n❌ Could not save results: {e}")
    
    print(f"\n🎯 INSPECTION COMPLETE")
    
    return unique_memories

if __name__ == "__main__":
    try:
        memories = main()
        print(f"\n✅ Found {len(memories)} total unique memories for Paresh")
        
        # Final recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if len(memories) == 0:
            print("   🔄 No memories found - system may need data initialization")
            print("   📝 Try adding some test memories manually")
            print("   🔧 Check if Azure Search index exists and has data")
        elif len(memories) < 10:
            print("   📈 Low memory count - normal for new system")
            print("   🔄 Continue using the system to build more memories")
        else:
            print("   ✅ Good memory collection - system is working")
            print("   🔍 Check if search/retrieval logic needs optimization")
        
    except KeyboardInterrupt:
        print("\n🛑 Inspection interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error during inspection: {e}")
        import traceback
        traceback.print_exc()