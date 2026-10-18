# DocuChat AI – Document Question-Answering System

DocuChat AI is an AI-powered application that allows users to
upload PDF and TXT documents and ask questions about their content.

The application uses Retrieval-Augmented Generation (RAG) concepts
to retrieve relevant document passages and support question-answering.

## Features

- Upload PDF and TXT documents
- Extract text from uploaded documents
- Split documents into smaller text chunks
- Generate embeddings using Sentence Transformers
- Retrieve relevant content using FAISS similarity search
- Ask questions about uploaded documents
- Manage and delete uploaded documents
- Rebuild the search index when documents change
- Interactive user interface built with Streamlit

## Technologies Used

- Python
- FastAPI
- Streamlit
- REST APIs
- Sentence Transformers
- FAISS
- PyMuPDF
- Retrieval-Augmented Generation (RAG)

## Project Structure

    DocuChat-AI/
    ├── main.py
    ├── app.py
    ├── requirements.txt
    ├── README.md
    ├── uploads/
    └── storage/

## How It Works

1. The user uploads a PDF or TXT document.
2. FastAPI processes the uploaded document.
3. The document text is divided into smaller chunks.
4. Sentence Transformers converts the chunks into embeddings.
5. FAISS retrieves relevant chunks based on the user's question.
6. The application uses the retrieved information to support
   question-answering.

## Installation

1. Clone the repository:

   git clone YOUR_GITHUB_REPOSITORY_URL

2. Open the project folder:

   cd DocuChat-AI

3. Create a virtual environment:

   python -m venv .venv

4. Activate the environment on Windows:

   .venv\Scripts\activate

5. Install dependencies:

   pip install -r requirements.txt

## Running the Application

Start the FastAPI backend in one terminal:

    uvicorn main:app --reload

Start the Streamlit frontend in another terminal:

    streamlit run app.py

Open the local URLs displayed in the terminal.

## Future Improvements

- Improve document retrieval accuracy
- Add automated tests
- Deploy the application online
- Improve document-processing performance