import requests
import streamlit as st
from urllib.parse import quote

API_BASE = "http://127.0.0.1:8000"
TIMEOUT = 200

st.set_page_config(page_title="DocuChat AI", page_icon="📘", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp {background:#f5f7fc;color:#1b2540;font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"] {background:#fff;border-right:1px solid #e1e7f2}
[data-testid="stSidebar"] * {color:#25314d}
.brand {font-family:'Manrope',sans-serif;font-weight:800;font-size:1.55rem;color:#1b2540!important;letter-spacing:-.7px}
.brand span {color:#6254e8!important}.muted {color:#63718b!important;font-size:.85rem}
.hero {padding:1.6rem 1.8rem;border-radius:22px;border:1px solid #e1e6f5;background:linear-gradient(120deg,#fff,#f0efff 58%,#edf7ff);margin-bottom:1rem}
.hero .eyebrow {font-size:.8rem;font-weight:700;color:#5547d5!important}.hero h1 {font-family:'Manrope',sans-serif;color:#1b2540!important;font-size:2rem;line-height:1.2;margin:.45rem 0}.hero p {color:#5e6b85!important;margin:0}
.card {background:white;border:1px solid #e1e7f2;border-radius:16px;padding:1rem;min-height:94px}.card b {color:#25314d}.card p {color:#65728b;font-size:.83rem;margin:.35rem 0 0}
[data-testid="stChatMessage"] {background:#fff!important;border:1px solid #e1e7f2;border-radius:16px;padding:1rem;color:#1b2540!important}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li {color:#1b2540!important}
[data-testid="stChatInput"] {background:#fff!important;border:1px solid #cbd5e7!important;border-radius:15px!important}
[data-testid="stChatInput"] textarea {color:#17213b!important;-webkit-text-fill-color:#17213b!important;caret-color:#5547d5!important;background:#fff!important}
[data-testid="stChatInput"] textarea::placeholder {color:#68758e!important;-webkit-text-fill-color:#68758e!important;opacity:1!important}
[data-testid="stChatInput"] button {background:#6254e8!important;color:#fff!important;border-radius:10px!important}
div.stButton>button,[data-testid="stDownloadButton"] button {background:#fff!important;color:#25314d!important;border:1px solid #cbd5e7!important;border-radius:11px!important;font-weight:600!important;min-height:2.4rem}
div.stButton>button:hover,[data-testid="stDownloadButton"] button:hover {background:#f0efff!important;color:#4d40c9!important;border-color:#6254e8!important}
div.stButton>button[kind="primary"] {background:#6254e8!important;color:#fff!important;border:1px solid #6254e8!important}
div.stButton>button[kind="primary"]:hover {background:#4e40ce!important;color:#fff!important}
.stTextInput input,[data-baseweb="select"]>div {background:#fff!important;color:#25314d!important}
[data-testid="stFileUploader"] {background:#fff;border:1px dashed #aebbd3;border-radius:13px;padding:.5rem}
[data-testid="stMetric"] {background:#fff;border:1px solid #e1e7f2;border-radius:13px;padding:.7rem}
[data-testid="stMetric"] * {color:#25314d!important}
[data-testid="stExpander"] {background:#fff;border:1px solid #e1e7f2;border-radius:12px}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p {color:#25314d!important}
/* Force readable light styling for Streamlit/BaseWeb controls, regardless of OS dark mode. */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {
  background:#ffffff !important; color:#25314d !important; border-color:#cbd5e7 !important;
}
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploader"] button {
  background:#f1f3fa !important; color:#25314d !important;
  border:1px solid #cbd5e7 !important; opacity:1 !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploader"] button:hover {
  background:#e9e7ff !important; color:#493bc9 !important;
}
/* Select box closed state and its menu/options */
[data-baseweb="select"] > div,
[data-baseweb="select"] div,
[data-baseweb="select"] input,
[data-baseweb="select"] span,
[data-baseweb="select"] svg {
  background-color:#ffffff !important; color:#25314d !important;
  -webkit-text-fill-color:#25314d !important; border-color:#cbd5e7 !important;
}
[data-baseweb="popover"], [data-baseweb="popover"] > div,
[data-baseweb="menu"], [role="listbox"], [role="option"] {
  background:#ffffff !important; color:#25314d !important;
}
[role="option"] *, [role="listbox"] * {
  color:#25314d !important; -webkit-text-fill-color:#25314d !important;
}
[role="option"]:hover, [role="option"][aria-selected="true"] {
  background:#efedff !important; color:#3e32b7 !important;
}
/* Labels, captions and interactive control text */
[data-testid="stWidgetLabel"] *,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
[data-testid="stMarkdownContainer"] { color:#25314d; }
[data-testid="stToggle"] *, [data-testid="stSlider"] *,
[data-testid="stSelectSlider"] *, [data-testid="stRadio"] * {
  color:#25314d;
}
hr {border-color:#e1e7f2} footer {visibility:hidden}
</style>
""", unsafe_allow_html=True)

for key, default in {
    "messages": [], "documents": [], "last_answer": "", "show_sources": True,
    "top_k": 3, "answer_style": "Balanced", "response_format": "Paragraph",
    "pending_question": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def api_request(method, path, *, params=None, files=None, timeout=TIMEOUT):
    """Call the existing FastAPI backend and return JSON or a readable error."""
    try:
        response = requests.request(
            method, f"{API_BASE}{path}", params=params, files=files, timeout=timeout
        )
    except requests.RequestException as exc:
        return None, f"Cannot connect to FastAPI at {API_BASE}. Start it with: uvicorn main:app --reload. Details: {exc}"
    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        return None, f"API error {response.status_code}: {detail}"
    try:
        return response.json(), None
    except ValueError:
        return {"text": response.text}, None


def refresh_documents(show_error=False):
    data, error = api_request("GET", "/uploaded-documents")
    if error:
        if show_error:
            st.error(error)
        return
    docs = data.get("documents", []) if isinstance(data, dict) else []
    st.session_state.documents = docs


def render_sources(sources):
    if not sources:
        return
    with st.expander(f"📚 Sources used ({len(sources)})"):
        for i, source in enumerate(sources, 1):
            if isinstance(source, dict):
                name = source.get("filename", f"Source {i}")
                snippet = source.get("text", source.get("content", ""))
                st.markdown(f"**{i}. {name}**")
                if snippet:
                    st.caption(str(snippet)[:900])
            else:
                st.write(f"{i}. {source}")


with st.sidebar:
    st.markdown('<div class="brand">DocuChat <span>AI</span></div><div class="muted">YOUR DOCUMENT WORKSPACE</div>', unsafe_allow_html=True)
    st.write("")
    if st.button("＋ New conversation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.pending_question = None
        st.rerun()
    if st.button("🧹 Clear current chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.pending_question = None
        st.rerun()
    st.markdown("#### Your documents")
    uploads = st.file_uploader(
        "Upload PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True,
        help="Use text-based PDFs or TXT files. Scanned/image-only PDFs need OCR first."
    )
    if st.button("Upload and index files", type="primary", use_container_width=True):
        if not uploads:
            st.warning("Choose at least one PDF or TXT file first.")
        else:
            succeeded = 0
            failed = 0
            progress = st.progress(0, text="Preparing uploads…")
            for file_number, file in enumerate(uploads, start=1):
                content = file.getvalue()
                if not content:
                    failed += 1
                    st.error(f"{file.name}: this file is empty (0 bytes). Choose a file with content.")
                    progress.progress(file_number / len(uploads), text=f"Checked {file_number} of {len(uploads)} files")
                    continue
                try:
                    data, error = api_request(
                        "POST", "/upload-document",
                        files={"file": (file.name, content, file.type or "application/octet-stream")},
                        timeout=300,
                    )
                    if error:
                        failed += 1
                        st.error(f"{file.name}: {error}")
                    else:
                        succeeded += 1
                        details = ""
                        if isinstance(data, dict):
                            details = f" · {data.get('total_chunks', 0)} text chunks indexed"
                        st.success(f"{file.name}: uploaded and indexed{details}")
                except Exception as exc:
                    failed += 1
                    st.error(f"{file.name}: upload failed: {exc}")
                progress.progress(file_number / len(uploads), text=f"Processed {file_number} of {len(uploads)} files")

            # Rebuild the shared index once more after the batch, using every readable file in uploads/.
            # The current backend already indexes per upload; this extra call makes batch status explicit.
            if succeeded:
                index_data, index_error = api_request("POST", "/index-uploaded-documents", timeout=300)
                if index_error:
                    st.warning(f"Files were uploaded, but the final index refresh failed: {index_error}")
                else:
                    st.success("Document index refreshed with all readable uploaded files.")
                refresh_documents(show_error=True)
            if failed:
                st.warning(f"{failed} file(s) could not be uploaded. Read the error above for each file.")
            if succeeded:
                st.rerun()
    if st.button("↻ Refresh documents", use_container_width=True):
        refresh_documents(show_error=True)
        st.rerun()
    if not st.session_state.documents:
        refresh_documents()
    if st.session_state.documents:
        for doc in st.session_state.documents:
            filename = doc.get("filename", "Document")
            doc_col, delete_col = st.columns([5, 1])
            with doc_col:
                st.markdown(f"📄 **{filename}**")
                st.caption(f"{doc.get('text_length', 0):,} characters")
            with delete_col:
                if st.button("🗑️", key=f"delete_document_{filename}", help=f"Delete {filename}"):
                    st.session_state[f"confirm_doc_delete_{filename}"] = True
            if st.session_state.get(f"confirm_doc_delete_{filename}", False):
                st.warning(f"Delete **{filename}**? This removes the file and rebuilds the index.")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Yes, delete", key=f"confirm_delete_doc_{filename}", type="primary"):
                        result, error = api_request(
                            "DELETE", f"/uploaded-documents/{quote(filename, safe='')}", timeout=300
                        )
                        if error:
                            st.error(f"Could not delete {filename}: {error}")
                        else:
                            st.success(f"Deleted {filename}.")
                            st.session_state[f"confirm_doc_delete_{filename}"] = False
                            refresh_documents()
                            st.rerun()
                with cancel_col:
                    if st.button("Cancel", key=f"cancel_delete_doc_{filename}"):
                        st.session_state[f"confirm_doc_delete_{filename}"] = False
                        st.rerun()
    else:
        st.caption("No uploaded documents found yet.")
    st.markdown("---")
    st.markdown("#### Answer preferences")
    st.session_state.show_sources = st.toggle("Show source references", value=st.session_state.show_sources)
    st.session_state.answer_style = st.selectbox("Answer style", ["Balanced", "Concise", "Detailed"])
    st.session_state.response_format = st.selectbox("Response format", ["Paragraph", "Bullet points", "Step-by-step"])
    st.session_state.top_k = st.select_slider("Relevant sections", options=[1, 3, 5, 7, 10], value=st.session_state.top_k)
    st.caption("Single-user local app · No login required")

main_col, info_col = st.columns([3.2, 1.05], gap="large")
with main_col:
    st.markdown('''<div class="hero"><div class="eyebrow">✦ YOUR AI DOCUMENT ASSISTANT</div><h1>Ask better questions.<br>Find answers faster.</h1><p>Ask questions about your uploaded documents and review the sources behind each answer.</p></div>''', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in [
        (c1, "🔎", "Smart retrieval", "Search relevant passages in your files."),
        (c2, "✨", "Clear answers", "Get answers from your local AI model."),
        (c3, "📚", "Source references", "Inspect source snippets used for answers."),
    ]:
        with col:
            st.markdown(f'<div class="card"><b>{icon} &nbsp;{title}</b><p>{desc}</p></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("#### Try asking")
    prompt_cols = st.columns(4)
    for col, prompt in zip(prompt_cols, ["Summarize my documents", "What are the key points?", "Explain this simply", "Compare my documents"]):
        with col:
            if st.button(prompt, key=f"prompt_{prompt}", use_container_width=True):
                st.session_state.pending_question = prompt
                st.rerun()

    if not st.session_state.messages:
        st.info("Upload a PDF or TXT file in the sidebar, then ask a question below.")

    message_index = 0
    while message_index < len(st.session_state.messages):
        msg = st.session_state.messages[message_index]
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources") and st.session_state.show_sources and msg["role"] == "assistant":
                render_sources(msg["sources"])
            if msg["role"] == "user":
                if st.button("🗑️ Delete this question and answer", key=f"delete_exchange_{message_index}"):
                    # Remove this user question and its following answer, if present.
                    del st.session_state.messages[message_index]
                    if message_index < len(st.session_state.messages) and st.session_state.messages[message_index].get("role") == "assistant":
                        del st.session_state.messages[message_index]
                    st.session_state.last_answer = next(
                        (m.get("content", "") for m in reversed(st.session_state.messages) if m.get("role") == "assistant"),
                        ""
                    )
                    st.rerun()
        message_index += 1

    typed_question = st.chat_input("Ask a question about your documents…")
    question = typed_question or st.session_state.pending_question
    if question:
        st.session_state.pending_question = None
        question = question.strip()
        if question:
            # Append immediately so the user's exact text is visible even if the API fails.
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Searching your documents and generating an answer…"):
                    history_lines = []
                    for old in st.session_state.messages[:-1][-10:]:
                        prefix = "User" if old["role"] == "user" else "Assistant"
                        history_lines.append(f"{prefix}: {old['content']}")
                    params = {
                        "question": question,
                        "top_k": int(st.session_state.top_k),
                        "history": "\n".join(history_lines),
                    }
                    # The uploaded main.py defines GET /ask, not POST /ask.
                    result, error = api_request("GET", "/ask", params=params)
                if error:
                    st.error(error)
                    st.caption("The question is kept in this conversation. Fix the backend/API issue and try again.")
                    st.session_state.messages.append({"role": "assistant", "content": f"Request failed: {error}"})
                else:
                    answer = str(result.get("answer", result.get("response", result.get("text", "")))).strip()
                    sources = result.get("sources", [])
                    if not answer:
                        answer = "The backend responded, but did not return an answer field. Check the FastAPI response in /docs."
                    # The current backend accepts only question, top_k and history; style/format are UI preferences only.
                    st.markdown(answer)
                    if sources and st.session_state.show_sources:
                        render_sources(sources)
                    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
                    st.session_state.last_answer = answer
            st.rerun()

with info_col:
    st.markdown('<div class="card"><b>Workspace overview</b><p>Your local document assistant.</p></div>', unsafe_allow_html=True)
    st.metric("Documents", len(st.session_state.documents))
    st.metric("Messages in this chat", len(st.session_state.messages))
    if st.session_state.last_answer:
        st.download_button("↓ Download last answer", st.session_state.last_answer, file_name="docuchat_answer.txt", mime="text/plain", use_container_width=True)
    st.markdown('<div class="card"><b>Helpful tip</b><p>For best results, upload your files and wait for the indexing success message before asking questions.</p></div>', unsafe_allow_html=True)

st.markdown('<p class="muted">DocuChat AI · Runs locally · No login required</p>', unsafe_allow_html=True)


#streamlit run app_fixed.py