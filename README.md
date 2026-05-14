# NLP-RAG — Egyptian Civil Code Legal Assistant

A bilingual (Arabic/English) RAG chatbot that answers legal questions about the Egyptian Civil Code. It retrieves the most relevant law articles using semantic search, then generates a grounded answer with citations — in whatever language the user asks.

> The model never fabricates. If the answer isn't in the retrieved articles, it says so.

---

## Demo

Ask a question like:

- *"I was threatened into signing a contract. Is that contract valid?"*
- *"كلبي عض جار ليا. أنا مسؤول؟"*
- *"Can interest accumulate on top of unpaid interest?"*

The assistant retrieves the relevant articles and gives a clear, cited answer in the same language you used.

---

## Architecture

```
[ User Browser ]
       |
       | question (HTTP)
       ▼
[ Streamlit Frontend :8501 ]
       |
       | POST /query
       ▼
[ FastAPI Backend :8000 ]
      |          |
 vector search  LLM call
      |          |
      ▼          ▼
[ Qdrant :6333 ] [ Gemini / Groq ]
```

Three Docker services:

| Service    | Port | Role |
|------------|------|------|
| `qdrant`   | 6333 | Vector database — stores embedded Civil Code articles |
| `rag-app`  | 8000 | FastAPI backend — search, generation, auth |
| `frontend` | 8501 | Streamlit chat UI |

---

### Steps

**1. Clone the repo**
```bash
git clone https://github.com/farahelmashad/nlp-rag.git
cd nlp-rag
```

**2. Add your API keys**

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
LLM_PROVIDER=gemini   # or "groq"
```

**3. Start everything**
```bash
docker-compose up --build
```
The first run takes a few minutes while Docker builds images and loads the Civil Code snapshot into Qdrant. Once you see the Streamlit and uvicorn startup messages, you're ready.

**4. Open the app**

| URL | What |
|-----|------|
| http://localhost:8501 | Chat interface |
| http://localhost:8000/docs | Interactive API docs |
| http://localhost:6333/dashboard | Qdrant vector DB dashboard |

**5. Stop**
```bash
docker-compose down
```
Your data persists in a Docker volume. Next time just run `docker-compose up`.

---

## API

### `POST /query`

Main endpoint. Send a question, get back an answer and source articles.

**Request:**
```json
{
  "question": "Can a creditor cancel a contract?",
  "chat_history": [
    { "role": "user", "content": "What is Article 102?" },
    { "role": "assistant", "content": "Article 102 says..." }
  ]
}
```
`chat_history` is optional — pass `[]` for a fresh conversation.

**Response:**
```json
{
  "answer": "Based on Article 157, a creditor may cancel...",
  "sources": [
    { "article": 157, "text_en": "...", "text_ar": "..." },
    { "article": 160, "text_en": "...", "text_ar": "..." }
  ]
}
```

### `GET /health`
Returns `{ "status": "ok" }`. Used as a Docker health check.

### `POST /register` and `POST /login`
Standard auth. `/register` creates an account; `/login` returns a JWT bearer token.

---

## How It Works

### 1. PDF Extraction
The Egyptian Civil Code PDF is parsed with `pdfplumber`. Because the PDF is bilingual (Arabic right column, English left column), a custom extractor splits words by their x-position relative to the page midpoint, reverses RTL Arabic tokens where needed, and normalizes Arabic-Indic numerals.

### 2. Parsing & JSON
The extracted text is parsed into structured articles using regex — detecting `Article N`, `BOOK`, `CHAPTER`, and `SECTION` headers for English, and `مادة (N)` for Arabic. Both languages are merged into a single JSON record per article.

### 3. Chunking Strategy
One article = one chunk. Each article is already a complete, self-contained legal rule — the natural citation unit. Token-length analysis across all 1,093 articles showed:

| Metric | Value |
|--------|-------|
| Mean tokens | 189.8 |
| Max tokens | 1,017 |
| Articles under 512 tokens | 99.4% (1,086 / 1,093) |
| Articles over 512 tokens | 0.6% (7 / 1,093) |

The 7 oversized articles are split at sentence boundaries (`.` or `;`), keeping the article number in every sub-chunk so partial matches still identify the source.

### 4. Embedding & Vector DB
Articles are embedded using [`intfloat/multilingual-e5-small`](https://huggingface.co/intfloat/multilingual-e5-small) — a multilingual sentence-transformer that maps semantically similar text close together in vector space regardless of language. Both Arabic and English text are stored in the same Qdrant point. Embeddings are L2-normalized and stored with cosine distance.

### 5. Query Pipeline
When a question arrives:
1. **Query expansion** — the LLM rewrites the question using formal legal terminology (same language as input).
2. **Semantic search** — the expanded query is embedded and the top-k most similar articles are retrieved from Qdrant (score threshold: 0.55).
3. **Generation** — retrieved articles + conversation history are injected into a structured prompt. The LLM responds in the user's language, cites only articles it actually used, and falls back to a safe message if the articles don't support an answer.

### 6. LLM Switching
The `LLM_PROVIDER` env variable selects between Gemini and Groq at startup. Both implement the same `LLMProvider` abstract interface, so swapping providers requires no code changes.

---

## Evaluation

A ground-truth test suite of 21 cases covers English legal queries, Arabic MSA queries, and Egyptian colloquial Arabic. Results at retrieval cutoffs of k=3 and k=7:

| k | Overall | English | Arabic |
|---|---------|---------|--------|
| 3 | 75% | 87.5% | 25% |
| 7 | 75% | 81.2% | 50% |

---

## Project Structure

```
nlp-rag/
├── app/
│   ├── main.py
│   ├── models/
│   │   └── schemas.py
│   ├── routers/
│   │   └── query.py
│   └── services/
│       ├── rag_service.py
│       ├── llm_factory.py
│       └── prompts.py
├── frontend/
│   ├── streamlit_app.py
│   └── Dockerfile
├── snapshots/
│   └── egyptian_civil_code.snapshot
├── preprocessing/
│   └── extract_and_chunk.ipynb
├── evaluate.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

---

## Tech Stack

`Python` · `FastAPI` · `Streamlit` · `Qdrant` · `sentence-transformers` · `pdfplumber` · `Gemini / Groq` · `Docker Compose`
