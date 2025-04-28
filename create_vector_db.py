import chromadb
from chromadb.config import Settings
import json
import glob
from collections import defaultdict
import os
from typing import Dict, List, Any
import shutil

# ------------------ Overview ------------------ #
# This script creates a vector database from preprocessed chunks of text.
# It provides functionality to load chunks, group them by collection, and upload them to a vector database.

# ------------------ Config ------------------ #
EMBEDDED_PATH = "unstructured/embedded/*.json"
COLLECTION_SCHEMAS = {
    "rules": ["source", "document_name", "collection", "rule_title", "rule_number", "summary"],
    "coaching_videos": ["source", "channel_name", "channel_id", "collection", "video_title", "video_id", "url", "summary"],
    "data_dictionary": ["source", "document_name", "collection", "column_name", "column_letter"]
}

class VectorDBManager:
    def __init__(self, db_path: str = "unstructured/vectordb"):
        self.db_path = db_path
        # Clear existing database if it exists
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path)
        self.client = self._initialize_client()
        
    def _initialize_client(self) -> chromadb.PersistentClient:
        """Initialize ChromaDB client with persistent storage"""
        os.makedirs(self.db_path, exist_ok=True)
        return chromadb.PersistentClient(path=self.db_path)

    @staticmethod
    def _load_chunks(path_pattern: str) -> List[Dict[str, Any]]:
        """Load embedded chunks from JSON files"""
        chunks = []
        for json_file in glob.glob(path_pattern):
            with open(json_file) as f:
                chunks.extend(json.load(f))
        return chunks

    @staticmethod
    def _group_by_collection(chunks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group chunks by their collection"""
        grouped = defaultdict(list)
        for chunk in chunks:
            collection_name = chunk.get("metadata", {}).get("collection", "").lower().replace(" ", "_")
            grouped[collection_name].append(chunk)
        return grouped

    @staticmethod
    def _build_metadata(chunk: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
        """Build metadata dictionary based on collection schema"""
        schema = COLLECTION_SCHEMAS.get(collection_name, [])
        return {field: chunk.get("metadata", {}).get(field) for field in schema}

    def upload_collection(self, collection_name: str, chunks: List[Dict[str, Any]]) -> None:
        """Upload chunks to a specific collection"""
        collection = self.client.get_or_create_collection(name=collection_name)
        collection.add(
            ids=[chunk["metadata"].get("id") for chunk in chunks],
            embeddings=[chunk["embedding"] for chunk in chunks],
            documents=[chunk["content"] for chunk in chunks],
            metadatas=[self._build_metadata(chunk, collection_name) for chunk in chunks]
        )
        print(f"✅ Uploaded {len(chunks)} chunks to collection: '{collection_name}'")

    def process_all_chunks(self) -> None:
        """Process and upload all chunks to their respective collections"""
        chunks = self._load_chunks(EMBEDDED_PATH)
        grouped = self._group_by_collection(chunks)
        
        for collection_name, chunk_group in grouped.items():
            self.upload_collection(collection_name, chunk_group)

def main():
    vector_db = VectorDBManager()
    vector_db.process_all_chunks()

if __name__ == "__main__":
    main()
