# SecureShield Insurance Support – Agentic RAG System

## Overview

SecureShield Insurance Support is an end-to-end Agentic RAG system designed to provide accurate, evidence-based answers to insurance-related queries. The system leverages LLMs (OpenAI GPT-4), semantic search over vectorized insurance documents, and a modern web frontend to deliver a friendly, reliable insurance assistant.

---

## AI Frameworks Used

While many modern RAG systems rely heavily on end-to-end orchestration frameworks like LangChain or LlamaIndex, SecureShield takes a more deliberate and minimalist approach.

### What We Use:

- **LlamaIndex Parser**  
  Used exclusively for parsing and converting insurance PDFs into markdown format (`Data/parse.py`). Its reliability in structured document extraction made it ideal for this preprocessing step.

- **LangChain (Text Splitter Only)**  
  We use LangChain’s `RecursiveCharacterTextSplitter` in `Data/embeddings.py` to intelligently chunk the cleaned text into overlapping windows. This preserves semantic coherence across chunks without introducing complexity.

### What We Don’t Use:

We **do not** use LlamaIndex or LangChain for RAG orchestration, agent logic, memory, or retrieval workflows.

### Why We Avoided Full Framework Abstractions:

- ✅ **Full Transparency & Debuggability**  
  Custom Python gives us end-to-end visibility over prompt construction, response streaming, memory updates, and function-calling flows — critical when working in regulated domains like insurance.

- ✅ **Agentic Flexibility**  
  With core logic fully in Python (`backend/core/`), we can fine-tune the control flow of LLM reasoning, retrieval invocation, and response formatting — something frameworks often abstract away or constrain.

- ✅ **Less Overhead**  
  Reduced dependencies, lower cold-start time, and easier deployment, especially on minimal hosting environments like Render or simple containers.

- ✅ **Better Prompt Discipline**  
  Frameworks often bundle defaults or implicit behavior; our approach guarantees strict prompt enforcement through `prompt.py`.

- ✅ **RAG-as-Code Philosophy**  
  We treat RAG not as a black box, but as a programmable pipeline — this philosophy keeps the stack lightweight, auditable, and extensible.

In short, we treat frameworks as utilities, not as architecture. This gives us the best of both worlds: ergonomic tools for preprocessing, and total control for reasoning and retrieval.

## Architecture

### 1. Data Pipeline

**a. PDF Parsing & Markdown Conversion**

- Insurance PDFs are parsed using [`Data/parse.py`](Data/parse.py) with LlamaParse, extracting both plain text and markdown per page.
- Output markdown files are saved in `Data/markdowns/`.

**b. Markdown Refinement**

- [`Data/refine.py`](Data/refine.py) sends raw markdown to GPT-4 to clean and structure it into chunk-friendly plain text.
- Cleaned files are saved in `Data/cleaned/`.

**c. Embedding & Vector Storage**

- [`Data/embeddings.py`](Data/embeddings.py) splits cleaned text into overlapping chunks.
- Each chunk is embedded using OpenAI's `text-embedding-3-small` model.
- Chunks and embeddings are uploaded to a Supabase vector table (`markdown_docs`).

---

### 2. Backend (API & RAG Logic)

**a. FastAPI Server**

- Entrypoint: [`backend/main.py`](backend/main.py)
- CORS enabled for frontend integration.
- Includes chat and reset endpoints via [`backend/router/chat.py`](backend/router/chat.py).
- Serves the frontend static files from [`backend/frontend/`](backend/frontend/).

**b. Chat Routing**

- `/chat` endpoint streams LLM responses.
- `/reset_chat` resets session memory.

**c. Core Modules**

- **Prompt Engineering:** [`backend/core/prompt.py`](backend/core/prompt.py) defines a strict system prompt to ensure evidence-based, insurance-only responses.
- **Session Memory:** [`backend/core/memory.py`](backend/core/memory.py) manages per-session chat history, always starting with the system prompt.
- **Agent Loop:** [`backend/core/agent.py`](backend/core/agent.py) handles LLM streaming, OpenAI function-calling, and memory updates.
- **Function Calling:** [`backend/core/specs.py`](backend/core/specs.py) defines the `insurance_doc_search` function for retrieval.
- **Function Handler:** [`backend/core/handler.py`](backend/core/handler.py) executes semantic search when the LLM requests it.
- **Semantic Search:** [`backend/utils/query.py`](backend/utils/query.py) computes query embeddings and calls a Supabase RPC to retrieve top-matching chunks.

---

### 3. Frontend

**a. UI**

- Located in [`backend/frontend/`](backend/frontend/)
- Modern chat interface with suggestion chips, markdown rendering, and streaming responses.
- [`backend/frontend/index.html`](backend/frontend/index.html): Main HTML structure.
- [`backend/frontend/style.css`](backend/frontend/style.css): Responsive, modern CSS.
- [`backend/frontend/script.js`](backend/frontend/script.js): Handles chat logic, session management, and streaming updates.

---

## Setup & Run Instructions

### Prerequisites

- Python 3.11+
- Node.js (for frontend, optional)
- Supabase project with `markdown_docs` table and `match_markdown_chunks` RPC
- OpenAI API key
- LlamaParse API key

### 1. Environment Setup

1. Clone the repo.
2. Fill in `.env` with your OpenAI, Supabase, and LlamaParse credentials.

### 2. Data Preparation

1. Place insurance PDFs in `Data/Insurance PDFs/`.
2. Run PDF parsing:
   ```sh
   python Data/parse.py
   ```
3. Refine markdown:
   ```sh
   python Data/refine.py
   ```
4. Generate embeddings and upload to Supabase:
   ```sh
   python Data/embeddings.py
   ```

### 3. Backend

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```sh
   uvicorn backend.main:app --reload
   ```

### 4. Frontend

1. Open [`backend/frontend/index.html`](backend/frontend/index.html) in your browser.
   - Or serve with a simple HTTP server:
     ```sh
     cd backend/frontend
     python -m http.server 8080
     ```

---

## Architectural Decisions

### Retrieval-Augmented Generation (RAG)

- **Why RAG?**  
  Ensures all answers are grounded in actual insurance documents, preventing hallucinations and ensuring compliance.

- **Chunking & Embedding:**  
  Cleaned, chunked text enables fine-grained retrieval and evidence citation.

- **Supabase Vector Store:**  
  Chosen for easy integration, scalable storage, and fast similarity search via custom RPC.

- **OpenAI Function Calling:**  
  Lets the LLM decide when to retrieve evidence, keeping the system flexible and future-proof.

- **Strict Prompting:**  
  The system prompt in [`backend/core/prompt.py`](backend/core/prompt.py) enforces scope, style, and evidence requirements, minimizing off-topic or speculative responses.

- **Session Memory:**  
  Each chat session is isolated, always starting with the system prompt, ensuring context consistency.

- **Streaming Responses:**  
  Both backend and frontend are designed for streaming, providing a responsive user experience.

- **Frontend Simplicity:**  
  The frontend is static, dependency-light, and uses `marked.js` for markdown rendering, ensuring compatibility and ease of deployment.

---

## File Reference

- **Data Pipeline:**

  - [`Data/parse.py`](Data/parse.py)
  - [`Data/refine.py`](Data/refine.py)
  - [`Data/embeddings.py`](Data/embeddings.py)

- **Backend:**

  - [`backend/main.py`](backend/main.py)
  - [`backend/router/chat.py`](backend/router/chat.py)
  - [`backend/core/`](backend/core/)
  - [`backend/utils/query.py`](backend/utils/query.py)

- **Frontend:**
  - [`backend/frontend/index.html`](backend/frontend/index.html)
  - [`backend/frontend/style.css`](backend/frontend/style.css)
  - [`backend/frontend/script.js`](backend/frontend/script.js)

---
