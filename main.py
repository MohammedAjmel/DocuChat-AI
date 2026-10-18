import fitz
import json
import requests
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import shutil
from fastapi import UploadFile, File

from pathlib import Path
from fastapi import FastAPI, HTTPException

app = FastAPI(title="DocuChat AI")

# Get the project folder

BASE_DIR = Path(__file__).resolve().parent

# Get the document path
model = SentenceTransformer("all-MiniLM-L6-v2")

DOCUMENT_PATH = BASE_DIR / "documents" / "sample"
#storage
STORAGE_DIR = BASE_DIR / "storage"

FAISS_INDEX_PATH = STORAGE_DIR / "document.index"
CHUNKS_PATH = STORAGE_DIR / "chunks.json"

UPLOAD_DIR = BASE_DIR / "uploads"

STORAGE_DIR.mkdir(exist_ok=True)

UPLOAD_DIR.mkdir(exist_ok=True)

# Read the document

def read_document():
    if not DOCUMENT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="sample not found. Check your documents folder."
        )

    with open(DOCUMENT_PATH, "r", encoding="utf-8") as file:
        return file.read()


# Split text into smaller chunks

def split_into_chunks(text, chunk_size=100, overlap=20):
    words = text.split()
    chunks = []


    if not words:
        return chunks

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks

def create_and_save_index():
    text = read_document()
    chunks = split_into_chunks(text)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="The document is empty."
        )

    embeddings = model.encode(chunks)

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    index = faiss.IndexFlatL2(
        embeddings.shape[1]
    )

    index.add(embeddings)

    faiss.write_index(
        index,
        str(FAISS_INDEX_PATH)
    )

    with open(CHUNKS_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    return {
        "total_chunks": len(chunks),
        "embedding_dimensions": int(embeddings.shape[1]),
        "vectors_stored": int(index.ntotal)
    }


def create_uploaded_documents_index():
    # Step 1: Read all uploaded documents
    documents = read_uploaded_documents()

    if not documents:
        raise HTTPException(
            status_code=400,
            detail="No readable PDF or TXT documents found in uploads."
        )

    # Step 2: Create chunks and preserve source filenames
    chunks = []
    chunk_size = 500
    overlap = 100

    for document in documents:
        filename = document["filename"]
        text = document["text"].strip()

        if not text:
            continue

        start = 0

        while start < len(text):
            chunk_text = text[start:start + chunk_size]

            if chunk_text.strip():
                chunks.append({
                    "filename": filename,
                    "text": chunk_text
                })

            start += chunk_size - overlap

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No text chunks could be created from the documents."
        )

    # Step 3: Generate embeddings
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    embeddings = np.asarray(embeddings, dtype=np.float32)

    # Step 4: Create a new FAISS index
    new_index = faiss.IndexFlatL2(embeddings.shape[1])
    new_index.add(embeddings)

    # Step 5: Save the new index and its matching chunks
    faiss.write_index(new_index, str(FAISS_INDEX_PATH))

    with CHUNKS_PATH.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    # Step 6: Return indexing information
    return {
        "message": "All uploaded documents indexed successfully!",
        "total_documents": len(documents),
        "filenames": [document["filename"] for document in documents],
        "total_chunks": len(chunks),
        "index_vectors": new_index.ntotal
    }


def load_saved_index():
    if not FAISS_INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        raise HTTPException(
            status_code=400,
            detail="Index not found. Call POST /index-document first."
        )

    index = faiss.read_index(str(FAISS_INDEX_PATH))

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    return index, chunks


def read_uploaded_documents():
    documents = []

    for file_path in UPLOAD_DIR.iterdir():

        if not file_path.is_file():
            continue

        # Read TXT files
        if file_path.suffix.lower() == ".txt":
            text = file_path.read_text(
                encoding="utf-8",
                errors="replace"
            )

        # Read PDF files
        elif file_path.suffix.lower() == ".pdf":
            text_parts = []

            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text_parts.append(page.get_text())

            text = "\n".join(text_parts)

        else:
            continue

        if text.strip():
            documents.append({
                "filename": file_path.name,
                "text": text
            })

    return documents

# Home endpoint

@app.get("/")
def home():
    return {
        "message": "Welcome to DocuChat AI!",
        "status": "Application is running successfully"
    }

# Read the complete document

@app.get("/read-document")
def get_document():
    text = read_document()


    return {
    "filename": DOCUMENT_PATH.name,
    "content": text
}


# Display document chunks

@app.get("/chunks")
def get_chunks():
    text = read_document()
    chunks = split_into_chunks(text)
    return {
    "filename": DOCUMENT_PATH.name,
    "total_chunks": len(chunks),
    "chunks": chunks
}
#embeddingd
@app.get("/embeddings")
def get_embeddings():
    text = read_document()
    chunks = split_into_chunks(text)

    embeddings = model.encode(chunks)

    return {
        "total_chunks": len(chunks),
        "embedding_dimensions": int(embeddings.shape[1]),
        "first_chunk": chunks[0],
        "first_embedding": embeddings[0].tolist()
    }
#fastapi
@app.get("/build-index")
def build_index():
    text = read_document()
    chunks = split_into_chunks(text)

    embeddings = model.encode(chunks)

    embeddings = np.array(embeddings, dtype="float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return {
        "message": "FAISS index created successfully",
        "total_chunks": len(chunks),
        "embedding_dimensions": dimension,
        "vectors_stored": index.ntotal
    }

#semantic search

@app.get("/search")
def semantic_search(question: str, top_k: int = 3):
    text = read_document()
    chunks = split_into_chunks(text)

    # Convert document chunks into embeddings
    document_embeddings = model.encode(chunks)
    document_embeddings = np.array(
        document_embeddings,
        dtype="float32"
    )

    # Create the FAISS index
    dimension = document_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(document_embeddings)

    # Convert the user's question into an embedding
    question_embedding = model.encode([question])
    question_embedding = np.array(
        question_embedding,
        dtype="float32"
    )

    # Search for the most relevant chunks
    top_k = max(1, min(top_k, len(chunks)))
    distances, indices = index.search(question_embedding, top_k)

    results = []

    for rank, chunk_index in enumerate(indices[0]):
        results.append({
            "rank": rank + 1,
            "chunk": chunks[int(chunk_index)],
            "distance": float(distances[0][rank])
        })

    return {
        "question": question,
        "results": results
    }

#request
@app.get("/ask")
def ask_question(
    question: str,
    top_k: int = 3,
    history: str = ""
):
    # Step 1: Load the saved FAISS index and chunks
    index, chunks = load_saved_index()

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No document chunks are available."
        )

    if index.ntotal == 0:
        raise HTTPException(
            status_code=400,
            detail="The FAISS index is empty."
        )

    # Step 2: Convert the question into an embedding
    search_question = rewrite_question(question, history)

    question_embedding = model.encode([search_question])

    question_embedding = np.asarray(
        question_embedding,
        dtype="float32"
    )

    # Step 3: Search the saved FAISS index
    top_k = max(1, min(top_k, index.ntotal))

    distances, indices = index.search(
        question_embedding,
        top_k
    )

    # Step 4: Retrieve relevant chunks
    relevant_chunks = [
        chunks[int(i)]
        for i in indices[0]
        if 0 <= int(i) < len(chunks)
    ]

    # Step 5: Prepare document context
    context_parts = []

    for chunk in relevant_chunks:
        if isinstance(chunk, dict):
            filename = chunk.get("filename", "Unknown")
            text = chunk.get("text", "")

            context_parts.append(
                f"Source document: {filename}\n{text}"
            )
        else:
            context_parts.append(str(chunk))

    context = "\n\n".join(context_parts)

    # Step 6: Prepare the prompt with conversation history
    prompt = f"""
You are DocuChat AI, a document question-answering assistant.

Use the conversation history to understand follow-up questions.
Answer factual questions using only the provided document context.

If the answer is not available in the context, say:
"I could not find the answer in the provided document."

Conversation history:
{history if history.strip() else "No previous conversation."}

Document context:
{context}

Current question:
{question}

Answer:
"""

    # Step 7: Ask Ollama to generate an answer
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()
        result = response.json()

    except requests.RequestException as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to Ollama: {error}"
        )

    # Step 8: Return the answer and sources
    return {
        "question": question,
        "answer": result.get("response", "").strip(),
        "history_used": bool(history.strip()),
        "sources": [
            {
                "filename": chunk.get("filename", "Unknown"),
                "text": chunk.get("text", "")
            }
            for chunk in relevant_chunks
            if isinstance(chunk, dict)
        ],
        "source_chunks": relevant_chunks
    }



def rewrite_question(question: str, history: str = "") -> str:
    """
    Rewrite a follow-up question into a standalone question
    using the conversation history.
    """

    if not history.strip():
        return question

    prompt = f"""
You rewrite questions for a document search system.

Use the conversation history to understand the user's
latest question.

Rules:
- Rewrite the latest question as a standalone question.
- Preserve the user's original meaning.
- Do not answer the question.
- Do not add information that is not supported by the history.
- If the question is already clear, return it unchanged.
- Return only the rewritten question.

Conversation history:
{history}

Latest question:
{question}

Standalone question:
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        rewritten_question = (
            response.json().get("response", "").strip()
        )

        return rewritten_question or question

    except requests.RequestException:
        # Fall back to the original question if rewriting fails.
        return question



@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):

    # Step 1: Check the file extension
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    filename = Path(file.filename).name
    file_extension = Path(filename).suffix.lower()

    if file_extension not in [".pdf", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are allowed."
        )

    # Step 2: Create the destination path
    file_path = UPLOAD_DIR / filename

    # Step 3: Save the uploaded file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()

    # Step 4: Automatically rebuild the index
    try:
        index_result = create_uploaded_documents_index()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"File saved, but indexing failed: {error}"
        )

    # Step 5: Return the result
    return {
        "message": "Document uploaded and indexed successfully!",
        "filename": filename,
        "total_documents": index_result["total_documents"],
        "total_chunks": index_result["total_chunks"],
        "index_vectors": index_result["index_vectors"]
    }

@app.post("/index-document")
def index_document():
    result = create_and_save_index()

    return {
        "message": "Document indexed and saved successfully",
        **result
    }

@app.get("/uploaded-documents")
def get_uploaded_documents():
    documents = read_uploaded_documents()

    return {
        "total_documents": len(documents),
        "documents": [
            {
                "filename": document["filename"],
                "text_length": len(document["text"]),
                "preview": document["text"][:200]
            }
            for document in documents
        ]
    }

@app.post("/index-uploaded-documents")
def index_uploaded_documents():
    return create_uploaded_documents_index()



@app.delete("/uploaded-documents/{filename}")
def delete_uploaded_document(filename: str):

    # Step 1: Validate the filename
    safe_filename = Path(filename).name

    if safe_filename != filename or safe_filename in ("", ".", ".."):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    # Step 2: Find the uploaded file
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Uploaded document not found."
        )

    # Step 3: Delete the file
    try:
        file_path.unlink()

        # Step 4: Read the remaining uploaded documents
        remaining_documents = read_uploaded_documents()

        # Step 5: Rebuild the index if documents remain
        if remaining_documents:
            index_result = create_uploaded_documents_index()

            return {
                "message": "Document deleted successfully.",
                "deleted_filename": safe_filename,
                "remaining_documents": len(remaining_documents),
                "total_chunks": index_result["total_chunks"]
            }

        # Step 6: Remove the old index if no documents remain
        for index_file in (FAISS_INDEX_PATH, CHUNKS_PATH):
            if index_file.exists():
                index_file.unlink()

        return {
            "message": "Document deleted successfully. No documents remain.",
            "deleted_filename": safe_filename,
            "remaining_documents": 0,
            "total_chunks": 0
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error while deleting document: {error}"
        )

#uvicorn main:app --reload