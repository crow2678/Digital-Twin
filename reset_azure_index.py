import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType, VectorSearch, 
    HnswAlgorithmConfiguration, VectorSearchProfile, SemanticConfiguration,
    SemanticPrioritizedFields, SemanticField, SemanticSearch
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

def recreate_azure_search_index():
    """Recreate Azure Search index with proper schema for memory storage including vector support"""
    
    # Azure Search connection
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    
    if not all([endpoint, key, index_name]):
        print("Error: Missing Azure Search environment variables")
        return False
    
    try:
        # Initialize the client
        credential = AzureKeyCredential(key)
        client = SearchIndexClient(endpoint=endpoint, credential=credential)
        
        print(f"Connecting to Azure Search: {endpoint}")
        print(f"Target index: {index_name}")
        
        # Check if index exists
        try:
            existing_index = client.get_index(index_name)
            print(f"Found existing index with {len(existing_index.fields)} fields")
            
            # Ask for confirmation
            response = input(f"Delete and recreate index '{index_name}'? This will remove ALL data. (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return False
            
            # Delete existing index
            client.delete_index(index_name)
            print(f"Deleted existing index: {index_name}")
            
        except Exception:
            print(f"Index '{index_name}' does not exist. Creating new one.")
        
        # Define the new index schema optimized for memory records with vector support
        fields = [
            # Core document fields
            SearchField(name="id", type=SearchFieldDataType.String, key=True, searchable=False),
            SearchField(name="content", type=SearchFieldDataType.String, searchable=True, analyzer_name="standard.lucene"),
            SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), 
                       searchable=True, vector_search_dimensions=3072, vector_search_profile_name="myHnswProfile"),
            
            # Memory metadata fields (flattened for Azure Search compatibility)
            SearchField(name="memory_type", type=SearchFieldDataType.String, searchable=True, filterable=True),
            SearchField(name="extracted_value", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="confidence", type=SearchFieldDataType.Double, filterable=True, sortable=True),
            SearchField(name="timestamp", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
            SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
            SearchField(name="version", type=SearchFieldDataType.Int32, filterable=True),
            SearchField(name="is_active", type=SearchFieldDataType.Boolean, filterable=True),
            SearchField(name="context", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="metadata_json", type=SearchFieldDataType.String, searchable=False),
            SearchField(name="expiry_date", type=SearchFieldDataType.String, filterable=True),
        ]
        
        # Configure vector search
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="myHnsw")
            ],
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="myHnsw",
                )
            ]
        )
        
        # Configure semantic search (optional but useful)
        semantic_config = SemanticConfiguration(
            name="memory-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )
        
        semantic_search = SemanticSearch(configurations=[semantic_config])
        
        # Create the index
        index = SearchIndex(
            name=index_name, 
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search
        )
        result = client.create_index(index)
        
        print(f"✅ Successfully created index: {result.name}")
        print(f"✅ Index has {len(result.fields)} fields properly configured")
        print(f"✅ Vector search enabled with 3072 dimensions")
        print(f"✅ Schema optimized for memory record storage")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recreating index: {e}")
        return False

def verify_index_schema():
    """Verify the index schema is correct"""
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    
    try:
        credential = AzureKeyCredential(key)
        client = SearchIndexClient(endpoint=endpoint, credential=credential)
        
        index = client.get_index(index_name)
        print(f"\n=== Index Schema Verification ===")
        print(f"Index name: {index.name}")
        print(f"Total fields: {len(index.fields)}")
        
        required_fields = [
            "id", "content", "content_vector", "memory_type", "extracted_value", 
            "confidence", "timestamp", "source", "is_active"
        ]
        
        existing_fields = [field.name for field in index.fields]
        
        for field in required_fields:
            status = "✅" if field in existing_fields else "❌"
            print(f"{status} {field}")
        
        # Check vector search configuration
        if hasattr(index, 'vector_search') and index.vector_search:
            print(f"✅ Vector search configured")
        else:
            print(f"❌ Vector search not configured")
        
        missing = set(required_fields) - set(existing_fields)
        if missing:
            print(f"\n❌ Missing required fields: {missing}")
            return False
        else:
            print(f"\n✅ All required fields present!")
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("Azure Search Index Recreation Tool v2.0")
    print("=======================================")
    print("Now with vector search support!")
    
    # First verify current state
    print("\n1. Checking current index...")
    verify_index_schema()
    
    print("\n2. Recreating index with proper schema...")
    if recreate_azure_search_index():
        print("\n3. Verifying new index...")
        verify_index_schema()
        print("\n🎯 Index recreation complete!")
        print("You can now run your twin_controller.py with a clean, properly configured index.")
    else:
        print("\n❌ Index recreation failed. Check your Azure Search configuration.")