import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

try:
    embedding_model = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    
    # Test embedding
    test_text = "Hello world"
    embedding = embedding_model.embed_query(test_text)
    
    print(f"✅ Embedding test successful!")
    print(f"✅ Embedding dimensions: {len(embedding)}")
    print(f"✅ First few values: {embedding[:5]}")
    
except Exception as e:
    print(f"⚠️ Embedding test failed: {e}")
    print("Check your AZURE_OPENAI_EMBEDDING_DEPLOYMENT value in .env")