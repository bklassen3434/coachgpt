import openai
import os
from dotenv import load_dotenv
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed



# ------------------ Overview ------------------ #
# This module provides LLM-related functionality including:
# - Text embedding using OpenAI's embedding model
# - Text summarization using GPT models
# - Semantic reranking of search results



# ------------------ Initialize OpenAI Client ------------------ #
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)



# ------------------ Summarizer ------------------ #
def summarize_chunk(text: str, model="gpt-4o-mini") -> str:
    prompt = f"Summarize this softball-related text in 1-2 sentences:\n\n{text}"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print("Failed to summarize:", e)
        return ""
    
def summarize_chunks(chunks, max_workers=10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        summaries = list(executor.map(summarize_chunk, chunks))
    return summaries
    


# ------------------ Reranker ------------------ #
def reranker(query: str, summaries: list, top_n: int = 3, model="gpt-4o-mini") -> List[int]:
    prompt = f"""
            You're a helpful softball assistant. The user asked:

            "{query}"

            Here are short summaries of content retrieved from a database. Rank the summaries from most to least helpful in answering the question. Respond ONLY with the ordered list of numbers (e.g., "2, 1, 3").

            Summaries:
            {chr(10).join([f"[{i+1}] {summary}" for i, summary in enumerate(summaries)])}
            """

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    ranking_str = response.choices[0].message["content"].strip()
    ranking = [int(i.strip()) - 1 for i in ranking_str.split(",") if i.strip().isdigit()]
    return ranking[:top_n]



# ------------------ Embedder ------------------ #
def embedder_chunk(text: str, model="text-embedding-3-large") -> list:
    response = openai.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding

def embedder_chunks(texts: list[str], model="text-embedding-3-large", max_workers=10) -> list[list[float]]:
    embeddings = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(embedder_chunk, text, model) for text in texts]
        for future in as_completed(futures):
            try:
                embeddings.append(future.result())
            except Exception as e:
                print("Embedding failed:", e)
                embeddings.append([])  # or handle differently
    return embeddings