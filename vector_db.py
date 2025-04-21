import chromadb
from chromadb.config import Settings
import json
import glob
from collections import defaultdict

# ------------------ Config ------------------ #
EMBEDDED_PATH = "embedded/*.json"
# Define which metadata fields to include for each collection
COLLECTION_SCHEMAS = {
    "rules": ["source", "document_name", "collection", "rule_title", "rule_number", "summary"],
    "coaching_videos": ["source", "channel_name", "channel_id", "collection", "video_title", "video_id", "url", "summary"],
}

# ------------------ Chroma Client ------------------ #
def start_chroma_client():
    return chromadb.Client(Settings(anonymized_telemetry=False))

# ------------------ Load Embedded Chunks ------------------ #
def load_embedded_chunks(path_pattern):
    chunks = []
    for json_file in glob.glob(path_pattern):
        with open(json_file) as f:
            chunks.extend(json.load(f))
    return chunks

# ------------------ Group by Collection ------------------ #
def group_chunks_by_collection(chunks):
    grouped = defaultdict(list)
    for chunk in chunks:
        collection_name = chunk.get("metadata").get("collection").lower().replace(" ", "_")
        grouped[collection_name].append(chunk)
    return grouped

# ------------------ Metadata Builder ------------------ #
def build_metadata(chunk, collection_name):
    schema = COLLECTION_SCHEMAS.get(collection_name)
    return {field: chunk.get("metadata").get(field) for field in schema}

# ------------------ Upload to Chroma ------------------ #
def upload_to_chroma(client, collection_name, chunks):
    collection = client.get_or_create_collection(name=collection_name)
    collection.add(
        ids=[chunk["metadata"].get("id") for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        metadatas=[build_metadata(chunk, collection_name) for chunk in chunks]
    )
    print(f"✅ Uploaded {len(chunks)} chunks to collection: '{collection_name}'")

# ------------------ Main Pipeline ------------------ #
def main():
    client = start_chroma_client()
    chunks = load_embedded_chunks(EMBEDDED_PATH)
    grouped = group_chunks_by_collection(chunks)

    for collection_name, chunk_group in grouped.items():
        upload_to_chroma(client, collection_name, chunk_group)

if __name__ == "__main__":
    main()
