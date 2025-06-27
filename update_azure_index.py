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

def update_azure_index_for_hybrid():
    """Update Azure Search index to support hybrid memory records"""
    
    print("🔧 Starting Azure Search Index Update for Hybrid System")
    print("=" * 60)
    
    # Get configuration
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    current_index_name = os.getenv("AZURE_SEARCH_INDEX")
    
    if not all([endpoint, key, current_index_name]):
        print("❌ Missing Azure Search environment variables!")
        print("Required: AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX")
        return False
    
    print(f"📍 Endpoint: {endpoint}")
    print(f"📍 Current Index: {current_index_name}")
    
    # Initialize client
    credential = AzureKeyCredential(key)
    client = SearchIndexClient(endpoint=endpoint, credential=credential)
    
    # Step 1: Check current index
    print("\n1️⃣ Checking current index...")
    try:
        current_index = client.get_index(current_index_name)
        print(f"✅ Found current index with {len(current_index.fields)} fields")
        
        # Show current fields
        print("   Current fields:")
        for field in current_index.fields[:5]:  # Show first 5
            print(f"   - {field.name} ({field.type})")
        if len(current_index.fields) > 5:
            print(f"   ... and {len(current_index.fields) - 5} more")
            
    except Exception as e:
        print(f"❌ Error accessing current index: {e}")
        return False
    
    # Step 2: Create hybrid index name
    hybrid_index_name = f"{current_index_name}-hybrid"
    print(f"\n2️⃣ Creating new hybrid index: {hybrid_index_name}")
    
    # Step 3: Define hybrid fields (keep existing + add new)
    print("\n3️⃣ Defining hybrid field schema...")
    
    fields = [
        # ===== EXISTING CORE FIELDS (keep these) =====
        SearchField(name="id", type=SearchFieldDataType.String, key=True, searchable=False),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True, analyzer_name="standard.lucene"),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), 
                   searchable=True, vector_search_dimensions=3072, vector_search_profile_name="myHnswProfile"),
        SearchField(name="timestamp", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="is_active", type=SearchFieldDataType.Boolean, filterable=True),
        
        # ===== NEW ONTOLOGY FIELDS =====
        SearchField(name="ontology_domain", type=SearchFieldDataType.String, 
                   filterable=True, facetable=True, searchable=True),
        SearchField(name="ontology_category", type=SearchFieldDataType.String, 
                   filterable=True, facetable=True, searchable=True),
        SearchField(name="ontology_concept_id", type=SearchFieldDataType.String, 
                   filterable=True, searchable=True),
        SearchField(name="ontology_properties_json", type=SearchFieldDataType.String, 
                   searchable=False, retrievable=True),
        SearchField(name="ontology_confidence", type=SearchFieldDataType.Double, 
                   filterable=True, sortable=True),
        
        # ===== NEW AI FIELDS =====
        SearchField(name="ai_semantic_tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), 
                   searchable=True, filterable=True, facetable=True),
        SearchField(name="ai_confidence", type=SearchFieldDataType.Double, 
                   filterable=True, sortable=True),
        SearchField(name="ai_reasoning", type=SearchFieldDataType.String, 
                   searchable=True, retrievable=True),
        SearchField(name="ai_entities", type=SearchFieldDataType.Collection(SearchFieldDataType.String), 
                   searchable=True, filterable=True),
        SearchField(name="ai_concepts", type=SearchFieldDataType.Collection(SearchFieldDataType.String), 
                   searchable=True, filterable=True),
        
        # ===== NEW HYBRID SYNTHESIS FIELDS =====
        SearchField(name="semantic_summary", type=SearchFieldDataType.String, 
                   searchable=True, retrievable=True),
        SearchField(name="importance_score", type=SearchFieldDataType.Double, 
                   filterable=True, sortable=True),
        SearchField(name="hybrid_classification_json", type=SearchFieldDataType.String, 
                   searchable=False, retrievable=True),
        SearchField(name="searchable_content", type=SearchFieldDataType.String, 
                   searchable=True, analyzer_name="standard.lucene"),
        SearchField(name="all_tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), 
                   searchable=True, filterable=True, facetable=True),
        
        # ===== NEW USER CONTEXT FIELDS =====
        SearchField(name="user_id", type=SearchFieldDataType.String, 
                   filterable=True, facetable=True),
        SearchField(name="tenant_id", type=SearchFieldDataType.String, 
                   filterable=True, facetable=True),
        SearchField(name="session_id", type=SearchFieldDataType.String, 
                   filterable=True),
        SearchField(name="version", type=SearchFieldDataType.Int32, 
                   filterable=True, sortable=True),
        SearchField(name="expiry_date", type=SearchFieldDataType.String, 
                   filterable=True, sortable=True),
        
        # ===== ADDITIONAL METADATA FIELDS =====
        SearchField(name="extracted_value", type=SearchFieldDataType.String, 
                   searchable=True, retrievable=True),
        SearchField(name="confidence", type=SearchFieldDataType.Double, 
                   filterable=True, sortable=True),
        SearchField(name="memory_type", type=SearchFieldDataType.String, 
                   filterable=True, facetable=True),
        SearchField(name="context", type=SearchFieldDataType.String, 
                   searchable=True, retrievable=True),
        SearchField(name="metadata_json", type=SearchFieldDataType.String, 
                   searchable=False, retrievable=True),
    ]
    
    print(f"✅ Defined {len(fields)} fields for hybrid index")
    
    # Step 4: Configure vector search
    print("\n4️⃣ Configuring vector search...")
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
    
    # Step 5: Configure semantic search
    print("5️⃣ Configuring semantic search...")
    semantic_config = SemanticConfiguration(
        name="hybrid-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[
                SemanticField(field_name="content"),
                SemanticField(field_name="semantic_summary"),
                SemanticField(field_name="searchable_content")
            ],
            keywords_fields=[
                SemanticField(field_name="ai_semantic_tags"),
                SemanticField(field_name="all_tags")
            ]
        )
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    # Step 6: Create the hybrid index
    print("\n6️⃣ Creating hybrid index...")
    hybrid_index = SearchIndex(
        name=hybrid_index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    
    try:
        result = client.create_index(hybrid_index)
        print(f"✅ Successfully created hybrid index: {result.name}")
        print(f"✅ Index has {len(result.fields)} fields")
        print(f"✅ Vector search enabled with 3072 dimensions")
        print(f"✅ Semantic search configured")
        
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠️  Index {hybrid_index_name} already exists")
            print("   Checking if we should recreate it...")
            
            # Ask user what to do
            choice = input("   Do you want to delete and recreate the hybrid index? (y/N): ").lower()
            if choice == 'y':
                try:
                    client.delete_index(hybrid_index_name)
                    print(f"🗑️  Deleted existing hybrid index")
                    
                    # Recreate
                    result = client.create_index(hybrid_index)
                    print(f"✅ Recreated hybrid index: {result.name}")
                    
                except Exception as delete_error:
                    print(f"❌ Error recreating index: {delete_error}")
                    return False
            else:
                print("   Using existing hybrid index")
        else:
            print(f"❌ Error creating hybrid index: {e}")
            return False
    
    # Step 7: Update environment variable suggestion
    print(f"\n7️⃣ Update your environment configuration:")
    print(f"   Add this to your .env file:")
    print(f"   AZURE_SEARCH_INDEX_HYBRID={hybrid_index_name}")
    print(f"   ")
    print(f"   Or update existing:")
    print(f"   AZURE_SEARCH_INDEX={hybrid_index_name}")
    
    # Step 8: Verify the new index
    print(f"\n8️⃣ Verifying hybrid index...")
    try:
        verification_index = client.get_index(hybrid_index_name)
        
        # Count field types
        field_types = {}
        for field in verification_index.fields:
            field_type = str(field.type).split('.')[-1]
            field_types[field_type] = field_types.get(field_type, 0) + 1
        
        print(f"✅ Verification successful!")
        print(f"   Total fields: {len(verification_index.fields)}")
        print(f"   Field type breakdown:")
        for ftype, count in field_types.items():
            print(f"     {ftype}: {count}")
        
        # Show some key hybrid fields
        hybrid_fields = [f.name for f in verification_index.fields if any(prefix in f.name for prefix in ['ontology_', 'ai_', 'hybrid_', 'semantic_'])]
        print(f"   Hybrid-specific fields ({len(hybrid_fields)}):")
        for field in hybrid_fields[:8]:  # Show first 8
            print(f"     • {field}")
        if len(hybrid_fields) > 8:
            print(f"     ... and {len(hybrid_fields) - 8} more")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    # Step 9: Success summary
    print(f"\n🎉 HYBRID INDEX UPDATE COMPLETE!")
    print(f"=" * 60)
    print(f"✅ New hybrid index created: {hybrid_index_name}")
    print(f"✅ Ready for hybrid ontology + AI processing")
    print(f"✅ Backward compatible with existing data structure")
    print(f"✅ Enhanced search capabilities enabled")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Update your .env file with the new index name")
    print(f"2. Your existing data remains in: {current_index_name}")
    print(f"3. New hybrid data will go to: {hybrid_index_name}")
    print(f"4. You can migrate existing data later if needed")
    print(f"5. Run your hybrid system to start using new capabilities!")
    
    return hybrid_index_name

def check_index_compatibility():
    """Check if current index is compatible with hybrid system"""
    
    print("\n🔍 Checking Index Compatibility...")
    
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    
    credential = AzureKeyCredential(key)
    client = SearchIndexClient(endpoint=endpoint, credential=credential)
    
    try:
        current_index = client.get_index(index_name)
        current_fields = [f.name for f in current_index.fields]
        
        # Required fields for hybrid system
        required_fields = ['id', 'content', 'content_vector']
        
        # Hybrid fields to check
        hybrid_fields = [
            'ontology_domain', 'ontology_category', 'ai_semantic_tags', 
            'ai_confidence', 'semantic_summary', 'user_id'
        ]
        
        print(f"Current index: {index_name}")
        print(f"Current fields: {len(current_fields)}")
        
        # Check required fields
        missing_required = [f for f in required_fields if f not in current_fields]
        if missing_required:
            print(f"❌ Missing required fields: {missing_required}")
            return False
        else:
            print(f"✅ All required fields present")
        
        # Check hybrid fields
        missing_hybrid = [f for f in hybrid_fields if f not in current_fields]
        if missing_hybrid:
            print(f"⚠️  Missing hybrid fields: {len(missing_hybrid)} fields")
            print(f"   Need to create hybrid index for full functionality")
            return False
        else:
            print(f"✅ Index already has hybrid fields!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking compatibility: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Azure Search Index Updater for Hybrid Digital Twin")
    print("=" * 60)
    
    # Check current compatibility
    is_compatible = check_index_compatibility()
    
    if is_compatible:
        print("\n✅ Your current index already supports hybrid functionality!")
        print("You can proceed with the hybrid system implementation.")
    else:
        print("\n🔧 Index update required for hybrid functionality.")
        
        # Ask user if they want to proceed
        proceed = input("\nDo you want to create the hybrid index now? (Y/n): ").lower()
        if proceed != 'n':
            hybrid_index_name = update_azure_index_for_hybrid()
            
            if hybrid_index_name:
                print(f"\n🎯 READY TO PROCEED!")
                print(f"Update your .env file:")
                print(f"AZURE_SEARCH_INDEX={hybrid_index_name}")
                print(f"\nThen continue with hybrid system implementation!")
            else:
                print(f"\n❌ Index update failed. Please check the errors above.")
        else:
            print("Index update cancelled.")