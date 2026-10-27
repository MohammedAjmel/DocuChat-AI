# DocuChat AI — Chat with Your Documents

DocuChat AI is a document-based question-answering application built with Python, FastAPI, Streamlit, and Retrieval-Augmented Generation (RAG). It allows users to upload documents and ask questions about their content through a conversational interface.

## Features

* **User Authentication:** Sign-up, login, and logout using Supabase authentication.
* **Multiple File Upload:** Upload multiple PDF and TXT documents.
* **Document Question Answering:** Ask questions about uploaded documents.
* **Semantic Search:** Use Sentence Transformers to create document embeddings and FAISS to retrieve relevant content.
* **AI-Powered Responses:** Generate answers using a local language model through Ollama.
* **Document Management:** View and delete uploaded documents.
* **Voice Input:** Ask questions using voice input.
* **Read Aloud:** Listen to generated answers using browser text-to-speech.
* **REST API:** Use FastAPI endpoints to handle document uploads and questions.

## Technologies Used

* Python
* FastAPI
* Streamlit
* REST APIs
* Sentence Transformers
* FAISS
* PyMuPDF
* Retrieval-Augmented Generation (RAG)
* Ollama
* Supabase Authentication
* Git and GitHub

## Project Structure

```text
DocuChat-RAG/
├── main.py
├── app_fixed.py
├── auth.py
├── test_supabase.py
├── requirements.txt
├── README.md
├── .gitignore
├── uploads/
├── storage/
└── user_data/
```

The `uploads/`, `storage/`, and `user_data/` directories are used for application data where applicable. Their contents should not be committed to GitHub.

## Prerequisites

Install the following before running the project:

* Python 3.11 or another Python version supported by the project's dependencies.
* Git
* Ollama
* A compatible local language model
* A Supabase project with authentication configured

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mohammedajmel/DocuChat-AI.git
```

### 2. Open the project directory

```bash
cd DocuChat-AI
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root if the application uses one.

Configure the Supabase credentials and other settings required by `auth.py`, `main.py`, and `app_fixed.py`.

**Security:** Never commit `.env` files, API keys, passwords, access tokens, or private user documents to GitHub.

### 6. Set up Ollama

Install Ollama and download the model used by the application. The current project configuration uses `llama3.2:3b`.

```bash
ollama pull llama3.2:3b
```

Ensure Ollama is running before asking questions that require the local language model.

## Running the Application

Open two terminals in the project directory.

### Terminal 1: Start the FastAPI backend

```bash
uvicorn main:app --reload
```

FastAPI should be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is normally available at:

```text
http://127.0.0.1:8000/docs
```

### Terminal 2: Start the Streamlit frontend

```bash
streamlit run app_fixed.py
```

Streamlit will display the local address where you can open the application in your browser.

## How It Works

1. A user signs in to the application.
2. The user uploads one or more supported documents.
3. The application extracts text from the uploaded files.
4. The text is divided into smaller chunks.
5. Sentence Transformers generates embeddings for the text.
6. FAISS searches for relevant document chunks.
7. The retrieved information is used to prepare context for the language model.
8. The application presents the generated answer in the chat interface.

## Privacy and Security

Authentication and document access controls must be configured correctly before deploying the application for multiple users.

For a production deployment, verify that:

* Users can access only their own documents and conversations.
* Backend endpoints enforce authentication and ownership checks.
* Uploaded documents are stored securely.
* Secrets are supplied through environment variables.
* Temporary files and indexes do not expose another user's data.

## Future Improvements

* Improve retrieval relevance and answer accuracy.
* Add document citations to generated answers.
* Improve conversation history management.
* Strengthen document isolation and authorization.
* Deploy the application with persistent, secure storage.

## Author

**Mohammed Ajmel S**

* GitHub: https://github.com/MohammedAjmel
* LinkedIn: https://www.linkedin.com/in/mohammed-ajmel-57970b326/

## License

Choose and add an appropriate open-source license before distributing the project.
