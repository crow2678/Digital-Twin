import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.schema import Document

# Load environment variables
load_dotenv()

# Set up the embedding model using your Azure OpenAI deployment
embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Set up the vector store - simplified configuration for LangChain
vector_store = AzureSearch(
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    embedding_function=embedding_model.embed_query,
    # Remove the complex field mappings - let LangChain handle defaults
)

# Define memory chunks to insert with proper metadata format
docs = [
    Document(
        page_content="Paresh had a 1:1 meeting with the CEO and discussed AI-driven automation. Key insight: product-market fit is solid.",
        metadata={"type": "meeting_note", "priority": "high", "person": "Paresh"}
    ),
    Document(
        page_content="The twin should remember to never send financial data over email.",
        metadata={"type": "security_rule", "priority": "critical", "category": "data_protection"}
    ),
    Document(
        page_content="Paresh prefers to use short, direct communication when replying to C-level executives.",
        metadata={"type": "communication_style", "priority": "medium", "person": "Paresh"}
    )
]

try:
    # Insert documents into the vector memory index
    vector_store.add_documents(docs)
    print("✅ Documents inserted into Azure Cognitive Search.")
    print(f"✅ Added {len(docs)} documents to index: {os.getenv('AZURE_SEARCH_INDEX')}")
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    results = vector_store.similarity_search("CEO meeting", k=2)
    for i, result in enumerate(results):
        print(f"Result {i+1}: {result.page_content[:100]}...")
    
except Exception as e:
    print(f"⚠️ Error inserting documents: {e}")
    print("\nTry running fix_index_with_metadata.py first to create the correct index schema.")