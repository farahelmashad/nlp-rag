from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import google.generativeai as genai
import os

from prompts import build_prompt

load_dotenv()


print("URL:", os.getenv("QDRANT_URL"))
print("KEY:", os.getenv("QDRANT_API_KEY"))




genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model  = genai.GenerativeModel("gemini-2.5-flash")

def call_llm(prompt: str) -> str:
    response = gemini_model.generate_content(prompt)

    if response.text:
        return response.text
    else:
        return response.candidates[0].content.parts[0].text

# Load once (VERY IMPORTANT)
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

model = SentenceTransformer('intfloat/multilingual-e5-small')


def search(query, top_k=3):
    embedding = model.encode(f"query: {query}", normalize_embeddings=True)

    results = client.query_points(
        collection_name="egyptian_civil_code",
        query=embedding.tolist(),
        limit=top_k
    )

    return results.points


def build_context(results):
    context = ""
    for r in results:
        context += f"Article {r.payload['article_number']}:\n"
        context += f"English: {r.payload['english_text']}\n"
        context += f"Arabic: {r.payload['arabic_text']}\n\n"
    return context


def get_answer(query: str):
    results = search(query)
    context = build_context(results)

    prompt = build_prompt(context, query)
    answer = call_llm(prompt)

    return {
        "answer": answer,
        "sources": [
            {
                "article": r.payload["article_number"],
                "english": r.payload["english_text"]
            }
            for r in results
        ]
    }