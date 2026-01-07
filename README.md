# Veritas AI

## Project Overview

Veritas AI is a Retrieval-Augmented Generation (RAG) based document
question-answering system. It allows users to upload one or more
documents and ask questions that are answered strictly based on the
content of the uploaded files. The system is designed to be accurate,
document-grounded, and suitable for enterprise or academic use cases
where factual correctness is critical.

### Project Structure

    veritas-ai/
     ├── backend/
     │   ├── app/
     │   │   ├── api/           # FastAPI endpoints (upload, chat)
     │   │   ├── ingestion/     # Document loading, parsing, chunking
     │   │   ├── embeddings/    # Embedding model logic
     │   │   ├── vectorstore/   # FAISS-based vector storage
     │   │   ├── retrieval/     # Retriever, filters, reranker
     │   │   ├── llm/           # Prompting and answer generation
     │   │   ├── validation/    # Confidence, coverage, refusal checks
     │   │   └── main.py        # FastAPI application entry point
     │   ├── data/              # Uploaded files and vector index
     │   └── requirements.txt
     ├── frontend/
     │   ├── static/
     │   │   ├── css/           # Stylesheets
     │   │   └── js/            # JavaScript files
     │   ├── templates/         # HTML files
     │   ├── app.py             # Flask application
     │   └── config.py
     ├── UI/
     │   └── streamlit.py       # Test UI for performance evaluation
     ├── .env
     ├── .gitignore
     └── README.md


## Key Features

-   Multi-document upload support
-   Document-grounded question answering using RAG
-   Strict refusal for questions not answerable from documents
-   FAISS-based semantic search for efficient retrieval
-   Clean ChatGPT-style conversational UI
-   Client-side validation for missing document uploads
-   Structured and readable AI responses


## System Architecture (High-Level)

The system follows a standard RAG pipeline:

-   User uploads documents through a Flask-based UI
-   Documents are parsed, cleaned, and chunked
-   Each chunk is converted into embeddings
-   Embeddings are stored in a FAISS vector store
-   User queries are embedded and matched against relevant chunks
-   Retrieved content is passed to the language model for answer
    generation
-   Validation layers ensure factual grounding and refusal when needed


## Tech Stack

-   **Frontend:** HTML, CSS, JavaScript, Flask
-   **Backend:** FastAPI, Python
-   **Vector Store:** FAISS
-   **Embeddings:** Transformer-based embedding model
-   **LLM Integration:** API-based language model


## Setup & Installation

1.  Clone the repository
2.  Create and activate a Python virtual environment
3.  Install required dependencies
4.  Start the FastAPI backend server
5.  Run the Flask frontend application
6.  Access the application via `http://127.0.0.1:5000`


## How the RAG System Works

When a user asks a question, the system retrieves the most relevant
document chunks using vector similarity search. These chunks are
supplied to the language model, which generates a response strictly
grounded in the retrieved content. If sufficient information is not
available, the system refuses to answer.


## Usage Instructions

1.  Upload one or more documents using the upload section
2.  Wait for successful indexing confirmation
3.  Enter a question related to the uploaded documents
4.  Review the generated answer or refusal message


## Limitations

-   Answers are limited strictly to uploaded document content
-   Complex tables or scanned PDFs may reduce retrieval accuracy
-   Long documents may require additional tuning for optimal chunking


## Future Improvements

-   Session-based chat memory
-   Temporary in-memory vector stores per session
-   Enhanced document format support
-   Improved UI feedback and analytics


## Author

**E S Abhijith**\
AI--ML Intern\
Pinesphere Solutions Pvt. Ltd., Coimbatore\
Email: abhijithsankar.66@gmail.com