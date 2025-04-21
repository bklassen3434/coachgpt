import chromadb
from chromadb.config import Settings
from typing import List
from llms import embedder



# ------------------ Query Vector DB ------------------ #
def query_vector_db(query: str, collection_name: str, top_n: int = 5) -> List[dict]:
    client = chromadb.Client(Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(name=collection_name)

    # Embed the user query
    query_embedding = embedder(query)

    # Query the vector database
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n,
        include=["documents", "metadatas", "distances"]
    )

    # Combine results into a list of dicts
    combined_results = []
    for i in range(len(results["documents"][0])):
        combined_results.append({
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return combined_results
