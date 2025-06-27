import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.schema import Document

# Load environment variables
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

def add_memory(content, memory_type="general", priority="medium", **kwargs):
    """Add a single memory to the vector store"""
    
    metadata = {
        "type": memory_type,
        "priority": priority,
        **kwargs
    }
    
    doc = Document(page_content=content, metadata=metadata)
    
    try:
        vector_store.add_documents([doc])
        print(f"✅ Added memory: {content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Failed to add memory: {e}")
        return False

def add_multiple_memories(memories):
    """Add multiple memories at once"""
    
    docs = []
    for memory_data in memories:
        if isinstance(memory_data, str):
            # Simple string format
            doc = Document(page_content=memory_data, metadata={"type": "general"})
        else:
            # Dictionary format with metadata
            doc = Document(
                page_content=memory_data["content"],
                metadata=memory_data.get("metadata", {"type": "general"})
            )
        docs.append(doc)
    
    try:
        vector_store.add_documents(docs)
        print(f"✅ Added {len(docs)} memories successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to add memories: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Add some additional memories
    new_memories = [
        {
            "content": "Paresh works at Tavant and focuses on AI automation projects.",
            "metadata": {"type": "personal_info", "priority": "high", "person": "Paresh"}
        },
        {
            "content": "The company is exploring digital twin technology for customer engagement.",
            "metadata": {"type": "project_info", "priority": "high", "category": "digital_twin"}
        },
        {
            "content": "Weekly team meetings are every Monday at 10 AM EST.",
            "metadata": {"type": "schedule", "priority": "medium", "frequency": "weekly"}
        },
        {
            "content": "Always confirm meeting details 24 hours in advance with C-level executives.",
            "metadata": {"type": "business_rule", "priority": "high", "category": "meetings"}
        },
        {
            "content": "Paresh prefers Slack for quick updates and email for formal communications.",
            "metadata": {"type": "communication_preference", "priority": "medium", "person": "Paresh"}
        }
    ]
    
    print("Adding new memories to the vector store...")
    add_multiple_memories(new_memories)
    
    # Test individual memory addition
    add_memory(
        "Digital twin should remember user preferences and adapt responses accordingly.",
        memory_type="system_behavior",
        priority="critical",
        category="ai_behavior"
    )
    
    print("\n🧠 Memory system updated! Run test_memory_search.py to test the new memories.")