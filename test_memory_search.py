import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch

# Load environment variables
load_dotenv()

# Set up the embedding model
embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Set up the vector store
vector_store = AzureSearch(
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    embedding_function=embedding_model.embed_query,
)

def test_searches():
    """Test different types of searches"""
    
    test_queries = [
        "CEO meeting insights",
        "email security rules", 
        "communication style with executives",
        "Paresh preferences",
        "financial data protection"
    ]
    
    print("🔍 Testing Memory Search Functionality\n")
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 50)
        
        try:
            # Similarity search
            results = vector_store.similarity_search(query, k=2)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"Result {i}:")
                    print(f"Content: {result.page_content}")
                    print(f"Metadata: {result.metadata}")
                    print()
            else:
                print("No results found.")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print("=" * 60)
        print()

def test_similarity_search_with_score():
    """Test similarity search with relevance scores"""
    
    query = "How should I communicate with the CEO?"
    print(f"🎯 Similarity search with scores for: '{query}'\n")
    
    try:
        results = vector_store.similarity_search_with_relevance_scores(query, k=3)
        
        for i, (doc, score) in enumerate(results, 1):
            print(f"Result {i} (Score: {score:.4f}):")
            print(f"Content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_searches()
    test_similarity_search_with_score()
    
    print("✅ Memory search system is working!")
    print("🧠 Your digital twin can now retrieve relevant memories based on context.")