import json
import glob
from pathlib import Path
from llms import embedder_chunks
from typing import List, Dict


# ------------------ Overview ------------------ #
# This script embeds text chunks from preprocessed JSON files using OpenAI's embedding model.
# The embeddings are then stored alongside their original content in a new JSON file.

class ChunkEmbedder:
    def __init__(self, input_dir: str = "unstructured/preprocessed", 
                 output_dir: str = "unstructured/embedded"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_chunks(self) -> List[Dict]:
        """Load and combine chunks from all JSON files in input directory"""
        chunks = []
        for json_file in self.input_dir.glob("*.json"):
            with open(json_file) as f:
                chunks.extend(json.load(f))
        return chunks

    def embed_chunks(self, chunks: List[Dict], max_workers: int = 10) -> List[Dict]:
        """Generate embeddings for chunks and combine them"""
        texts = [chunk["content"] for chunk in chunks]
        embeddings = embedder_chunks(texts, max_workers=max_workers)
        print(f"Embedded {len(chunks)} chunks")

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
        return chunks

    def save_embedded_chunks(self, embedded_chunks: List[Dict]):
        """Save embedded chunks to output JSON file"""
        output_file = self.output_dir / "embedded_chunks.json"
        with open(output_file, "w") as f:
            json.dump(embedded_chunks, f)

    def process(self):
        """Main processing pipeline"""
        chunks = self.load_chunks()
        embedded_chunks = self.embed_chunks(chunks)
        self.save_embedded_chunks(embedded_chunks)


def main():
    embedder = ChunkEmbedder()
    embedder.process()


if __name__ == "__main__":
    main()
