import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)

from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")

index_name = "twin-memory-langchain-3072"

credential = AzureKeyCredential(search_key)
client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

# Delete old index if it exists
try:
    client.delete_index(index_name)
    print(f"🗑️ Deleted existing index '{index_name}'")
except:
    print(f"ℹ️ Index '{index_name}' doesn't exist, creating new one")

# Define index schema compatible with LangChain
index = SearchIndex(
    name=index_name,
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="metadata", type=SearchFieldDataType.String, searchable=True, filterable=True),
        SearchField(
            name="content_vector", 
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single), 
            searchable=True, 
            vector_search_dimensions=3072,
            vector_search_profile_name="default-profile"
        ),
    ],
    vector_search=VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="default-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ],
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config"
            )
        ]
    ),
    semantic_search=SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="default-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    content_fields=[SemanticField(field_name="content")]
                )
            )
        ]
    )
)

# Create the index
try:
    result = client.create_index(index)
    print(f"✅ Index '{index_name}' created successfully!")
    print("✅ Vector search dimensions: 3072 (text-embedding-3-large)")
    print("✅ HNSW algorithm configured")
    print("✅ Semantic search configured")
    print("✅ Metadata field included for LangChain compatibility")
    print(f"\n📝 Update your .env file:")
    print(f"AZURE_SEARCH_INDEX={index_name}")
    
except Exception as e:
    print(f"⚠️ Error creating index: {e}")