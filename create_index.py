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

index_name = "twin-memory-index-with-vectors"

credential = AzureKeyCredential(search_key)
client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

# Define your complete index schema with vector search
index = SearchIndex(
    name=index_name,
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(
            name="embedding", 
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single), 
            searchable=True, 
            vector_search_dimensions=1536, 
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
    print(f"✅ Index '{index_name}' created successfully with vector and semantic search!")
    print("✅ Vector search dimensions: 1536 (OpenAI embeddings)")
    print("✅ HNSW algorithm configured")
    print("✅ Semantic search configured")
except Exception as e:
    print(f"⚠️ Error creating index: {e}")
    # If there's an error, let's try a simpler version
    print("Trying without semantic search...")
    
    try:
        simple_index = SearchIndex(
            name=index_name,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
                SearchField(
                    name="embedding", 
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single), 
                    searchable=True, 
                    vector_search_dimensions=1536, 
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
        
        result = client.create_index(simple_index)
        print(f"✅ Index '{index_name}' created successfully with vector search!")
        
    except Exception as e2:
        print(f"⚠️ Error creating simplified index: {e2}")