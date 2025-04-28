import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from llms import embedder_chunk
import logging

class VectorDBQuerier:
    def __init__(self, db_path: str = "unstructured/vectordb"):
        self.db_path = db_path
        self.client = self._get_client()

    def _get_client(self) -> chromadb.PersistentClient:
        """Create and return a ChromaDB client"""
        return chromadb.PersistentClient(path=self.db_path)

    def _get_collection(self, collection_name: str) -> Any:
        """Get a collection from the vector database"""
        return self.client.get_collection(name=collection_name)

    def _execute_query(self, collection: Any, query_embedding: List[float], top_n: int) -> Dict:
        """Execute the query against the vector database"""
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=top_n,
            include=["documents", "metadatas", "distances"]
        )

    def _process_results(self, results: Dict) -> List[Dict]:
        """Process and combine query results into a list of dictionaries"""
        return [{
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        } for i in range(len(results["documents"][0]))]

    def query(self, query: str, collection_name: str, top_n: int = 5) -> List[Dict]:
        """Main function to query the vector database"""
        try:
            collection = self._get_collection(collection_name)
            query_embedding = embedder_chunk(query)
            results = self._execute_query(collection, query_embedding, top_n)
            return self._process_results(results)
        except Exception as e:
            logging.error(f"Error querying Vector DB: {str(e)}")
            raise

# def query_vector_db(query: str, collection_name: str, top_n: int = 5) -> List[Dict]:
#     """Convenience function to query the vector database"""
#     querier = VectorDBQuerier()
#     return querier.query(query, collection_name, top_n)
