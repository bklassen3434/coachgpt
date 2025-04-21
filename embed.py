import json
import glob
from llms import embedder_chunks


# ------------------ Overview ------------------ #
# This script embeds text chunks from preprocessed JSON files using OpenAI's embedding model.
# The embeddings are then stored alongside their original content in a new JSON file.

def main():
    chunks = []
    for json_file in glob.glob("preprocessed/*.json"):
        with open(json_file) as f:
            chunks.extend(json.load(f))

    texts = [chunk["content"] for chunk in chunks]
    embeddings = embedder_chunks(texts, max_workers=10)
    print(f"✅ Embedded {len(chunks)} chunks")

    embedded_chunks = []
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding
        embedded_chunks.append(chunk)

    with open("embedded/embedded_chunks.json", "w") as f:
        json.dump(embedded_chunks, f)

if __name__ == "__main__":
    main()
