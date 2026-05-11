# 🩺 Medical Chatbot — RAG-Powered Q&A over Medical Encyclopedia

A production-ready medical question-answering chatbot built with **Retrieval-Augmented Generation (RAG)**. The system retrieves context from the *Gale Encyclopedia of Medicine* and generates concise, grounded answers using a large language model — without hallucinating facts outside the knowledge base.

---

## 📸 Demo

> Ask the chatbot anything like:
> - *"What is Acromegaly and what causes it?"*
> - *"What are the symptoms and treatment of Acne?"*
> - *"What is the difference between Type 1 and Type 2 Diabetes?"*

The bot retrieves the 3 most relevant chunks from the medical encyclopedia and answers in 3 sentences or fewer.

---

## 🏗️ Architecture

```
PDF (Gale Encyclopedia of Medicine)
         │
         ▼
  [PyPDF / DirectoryLoader]          ← Load all PDF pages
         │
         ▼
  [filter_to_minimal_docs]           ← Strip metadata, keep source + content
         │
         ▼
  [RecursiveCharacterTextSplitter]   ← chunk_size=500, chunk_overlap=20
         │
         ▼
  [HuggingFace Embeddings]           ← sentence-transformers/all-MiniLM-L6-v2 (384-dim)
         │
         ▼
  [Pinecone Vector Store]            ← Serverless index, cosine similarity, AWS us-east-1
         │
    ┌────┴────┐
    │  Query  │  ← User question via Flask UI
    └────┬────┘
         ▼
  [Similarity Retriever]             ← Top-3 chunks (k=3)
         │
         ▼
  [ChatGroq — gpt-oss-20b]          ← Generates answer from retrieved context
         │
         ▼
     [Flask UI]                      ← Real-time chat interface
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq API — `openai/gpt-oss-20b` |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) |
| **Vector Store** | Pinecone Serverless (AWS `us-east-1`, cosine, dim=384) |
| **RAG Framework** | LangChain 0.3 |
| **Backend** | Flask 3.1 |
| **Frontend** | HTML + CSS + jQuery (Bootstrap 4) |
| **Knowledge Base** | Gale Encyclopedia of Medicine Vol. 1 (A–B) |
| **Containerization** | Docker (PyTorch 2.5.1 + CUDA 12.1) |

---

## 📁 Project Structure

```
Medical-Chatbot/
│
├── app.py                   # Flask app — routes, RAG chain setup
├── store_index.py           # One-time script: load PDF → embed → upsert to Pinecone
├── setup.py                 # Package setup
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image (PyTorch + CUDA)
│
├── src/
│   ├── helper.py            # PDF loader, text splitter, embeddings
│   └── prompt.py            # System prompt for the medical assistant
│
├── data/
│   └── Gale Encyclopedia of Medicine Vol. 1 (A-B).pdf
│
├── templates/
│   └── chat.html            # Chat UI (Bootstrap + jQuery + AJAX)
│
├── static/
│   └── style.css            # Dark-themed chat styling
│
├── streamlit_app.py         # Streamlit launcher — auto-starts Flask and serves the chat UI
│
└── research/
    └── trials.ipynb         # Experimentation notebook (chunking, retrieval, LLM testing)
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- [Pinecone](https://www.pinecone.io/) account (free tier works)
- [Groq](https://console.groq.com/) API key (free tier works)

### 1. Clone the repository

```bash
git clone https://github.com/7BeshoyArnest/Medical-Chatbot-with-LLMs-LangChain-Pinecone-Flask-AWS.git
cd Medical-Chatbot-with-LLMs-LangChain-Pinecone-Flask-AWS
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Build the Pinecone index (run once)

This loads the PDF, splits it into chunks, embeds them, and uploads to Pinecone:

```bash
python store_index.py
```

> ⚠️ This step takes a few minutes depending on your machine and internet speed.

### 5. Run the application

**Option A — Flask directly:**
```bash
python app.py
```
Open your browser at `http://localhost:5000`

**Option B — Streamlit launcher (auto-starts Flask):**
```bash
streamlit run streamlit_app.py
```
Streamlit will automatically start the Flask backend in the background, wait until it's ready, then give you a clickable link to open the chat UI.

---

## 🐳 Docker

```bash
# Build the image
docker build -t medical-chatbot .

# Run with env variables
docker run -p 5000:5000 \
  -e PINECONE_API_KEY=your_key \
  -e GROQ_API_KEY=your_key \
  medical-chatbot
```

> The Dockerfile uses `pytorch/pytorch:2.5.1-cuda12.1-cudnn9-runtime` as the base image, supporting GPU acceleration for embeddings if available.

---

## 🔍 How It Works

1. **Indexing** (`store_index.py`): The PDF is loaded page by page, metadata is cleaned to keep only the source path, then split into 500-token chunks with 20-token overlap. Each chunk is embedded using `all-MiniLM-L6-v2` (384 dimensions) and stored in a Pinecone serverless index.

2. **Retrieval** (`app.py`): On each user query, the same embedding model encodes the question and searches Pinecone for the top 3 most similar chunks using cosine similarity.

3. **Generation** (`app.py`): The 3 retrieved chunks are injected into a system prompt and passed to `ChatGroq`. The model answers in at most 3 sentences. If the answer isn't in the context, it says so — no hallucination.

---

## 💡 Key Design Decisions

- **`filter_to_minimal_docs`**: Strips all Pinecone-incompatible metadata from LangChain document objects, keeping only the source path. This prevents upsert failures caused by nested or non-string metadata fields.
- **Chunk size 500 / overlap 20**: Chosen to fit complete medical definitions within a single chunk while maintaining context continuity across boundaries.
- **`k=3` retrieval**: Balances context richness with prompt length. Medical answers rarely need more than 3 passages.
- **Groq inference**: Used for low-latency responses — significantly faster than OpenAI at the same quality level for RAG tasks.

---

## 📦 Requirements

```
langchain==0.3.26
flask==3.1.1
sentence-transformers==4.1.0
pypdf==5.6.1
python-dotenv==1.1.0
langchain-pinecone==0.2.8
langchain-openai==0.3.24
langchain-community==0.3.26
langchain-groq==0.2.0
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Beshoy Arnest**
- GitHub: [@7BeshoyArnest](https://github.com/7BeshoyArnest)
- Email: beshoyarnest01@gmail.com
