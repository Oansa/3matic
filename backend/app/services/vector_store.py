import chromadb
from chromadb.config import Settings
import os
from dotenv import load_dotenv

load_dotenv()

chroma_client = None
collection = None

async def init_vector_store():
    global chroma_client, collection
    try:
        chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        collection = chroma_client.get_or_create_collection(
            name="community_memory",
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ Chroma vector store initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Chroma: {e}")
        raise

def get_collection():
    return collection

async def add_document(community_id: str, document_id: str, text: str, metadata: dict = None):
    """Add document to vector store"""
    if not collection:
        raise Exception("Vector store not initialized")
    
    if not text or len(text.strip()) == 0:
        return
    
    collection.add(
        documents=[text],
        ids=[f"{community_id}_{document_id}"],
        metadatas=[{
            "community_id": community_id,
            "document_id": document_id,
            **(metadata or {})
        }]
    )

async def add_memory(community_id: str, memory_id: str, text: str, metadata: dict = None):
    """Add community memory to vector store"""
    if not collection:
        raise Exception("Vector store not initialized")
    
    if not text or len(text.strip()) == 0:
        return
    
    collection.add(
        documents=[text],
        ids=[f"memory_{community_id}_{memory_id}"],
        metadatas=[{
            "community_id": community_id,
            "type": "memory",
            **(metadata or {})
        }]
    )

async def search(community_id: str, query: str, n_results: int = 5):
    """Search in vector store for a specific community"""
    if not collection:
        raise Exception("Vector store not initialized")
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"community_id": community_id}
    )
    
    return results

