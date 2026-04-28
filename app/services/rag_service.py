from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()


print("URL:", os.getenv("QDRANT_URL"))
print("KEY:", os.getenv("QDRANT_API_KEY"))

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


def get_answer(query: str) -> str:
    results = search(query)
    context = build_context(results)

    # 🔴 TEMP (until you connect LLM)
    return f"Context retrieved:\n\n{context}"