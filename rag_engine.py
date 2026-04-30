import os
import chromadb
from chromadb.config import Settings
from ollama import Client as OllamaClient
from typing import List, Dict, Any

class RAGEngine:
    def __init__(self, chroma_host="localhost", chroma_port=8000, ollama_host="http://localhost:11434"):
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        self.ollama = OllamaClient(host=ollama_host)
        self.collection_name = "security_knowledge"
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
        
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Ollama's nomic-embed-text model"""
        response = self.ollama.embeddings(model="nomic-embed-text", prompt=text)
        return response["embedding"]

    def add_document(self, text: str, metadata: Dict[str, Any], doc_id: str):
        """Index a document into ChromaDB"""
        embedding = self._get_embedding(text)
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
        print(f"[*] Document {doc_id} indexed successfully.")

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant context from the knowledge base"""
        query_embedding = self._get_embedding(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
        return formatted_results

    def ingest_directory(self, directory_path: str):
        """Batch ingest text files from a directory"""
        if not os.path.exists(directory_path):
            print(f"[!] Directory {directory_path} not found.")
            return

        for filename in os.listdir(directory_path):
            if filename.endswith(".txt") or filename.endswith(".md"):
                file_path = os.path.join(directory_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.add_document(content, {"source": filename}, filename)

if __name__ == "__main__":
    # Test/Initialization
    engine = RAGEngine()
    
    # Check if we should test or ingest
    import sys
    if "--test" in sys.argv:
        res = engine.query("How to scan for vulnerabilities?")
        print(f"[*] Query result: {res}")
    elif "--ingest" in sys.argv:
        engine.ingest_directory("knowledge_base")
