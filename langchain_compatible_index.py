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
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")

# Use LangChain-friendly index name
index_name = "langchain-vector-store"

credential = AzureKeyCredential(search_key)
client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

# Delete old index if it exists
try:
    client.delete_index(index_name)
    print(f"🗑️ Deleted existing index '{index_name}'")
except:
    print(f"ℹ️ Index '{index_name}' doesn't exist, creating new one")

# Create index with LangChain's expected field names and structure
index = SearchIndex(
    name=index_name,
    fields=[
        # LangChain expects these specific field names
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True, retrievable=True),
        SearchField(name="metadata", type=SearchFieldDataType.String, searchable=True, retrievable=True),
        SearchField(
            name="content_vector",  # LangChain's default vector field name
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single), 
            searchable=True,
            retrievable=True,
            vector_search_dimensions=3072,  # text-embedding-3-large dimensions
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
    )
)

# Create the index
try:
    result = client.create_index(index)
    print(f"✅ LangChain-compatible index '{index_name}' created successfully!")
    print("✅ Fields: id, content, metadata, content_vector")
    print("✅ Vector dimensions: 3072 (text-embedding-3-large)")
    print("✅ Ready for LangChain integration")
    print(f"\n📝 Update your .env file:")
    print(f"AZURE_SEARCH_INDEX={index_name}")
    
except Exception as e:
    print(f"⚠️ Error creating index: {e}")