import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text
from dotenv import load_dotenv
from urllib.parse import quote
from supabase import create_client

load_dotenv()
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
TIMEOUT = 200

# set_page_config must be called once, and before any other st.* call.
st.set_page_config(
    page_title="DocuChat AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
    st.error(
        "Supabase is not configured. "
        "Please check SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in your .env file."
    )
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)

# ---------- THEME: CLASSIC MEETS MODERN ----------
# Ivory paper, deep navy ink, antique-gold accents, serif headings, clean sans body.

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
  --paper: #faf6ee;
  --paper-2: #f3ecdd;
  --card: #fffdf8;
  --ink: #14213d;
  --ink-soft: #4a5775;
  --line: #e6dcc6;
  --gold: #b08d3c;
  --gold-dark: #8c6d22;
  --navy: #14213d;
  --navy-2: #1f3158;
}

html, body, .stApp {
  background: var(--paper) !important;
  color: var(--ink);
  font-family: 'Inter', sans-serif;
}

.block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 7rem; }
header[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }

h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: var(--ink) !important; letter-spacing: -.3px; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--navy) 0%, #0d1730 100%);
  border-right: 3px solid var(--gold);
}
[data-testid="stSidebar"] * { color: #efe8d6 !important; }
[data-testid="stSidebar"] h4 { color: #e3c77a !important; font-size: 1.05rem; }
[data-testid="stSidebar"] hr { border-color: rgba(227,199,122,.25); }

.brand { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 1.7rem; color: #fff !important; }
.brand span { color: #e3c77a !important; font-style: italic; }
.tagline { font-size: .72rem; letter-spacing: 2.4px; color: #b9b19a !important; margin-top: .15rem; }

/* Buttons */
div.stButton > button, [data-testid="stDownloadButton"] button, .stFormSubmitButton > button {
  background: var(--card) !important; color: var(--ink) !important;
  border: 1px solid var(--line) !important; border-radius: 10px !important;
  font-weight: 600 !important; min-height: 2.5rem; transition: all .2s ease;
}
div.stButton > button:hover, [data-testid="stDownloadButton"] button:hover, .stFormSubmitButton > button:hover {
  border-color: var(--gold) !important; color: var(--gold-dark) !important;
  box-shadow: 0 4px 14px rgba(176,141,60,.18); transform: translateY(-1px);
}
div.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%) !important;
  color: #fff !important; border: none !important;
}
div.stButton > button[kind="primary"]:hover { color: #fff !important; filter: brightness(1.07); }
[data-testid="stSidebar"] div.stButton > button {
  background: rgba(255,255,255,.06) !important; color: #efe8d6 !important;
  border: 1px solid rgba(227,199,122,.3) !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="primary"] { background: linear-gradient(135deg, var(--gold), var(--gold-dark)) !important; color:#fff !important; }

/* Inputs */
.stTextInput input, .stTextArea textarea {
  background: var(--card) !important; color: var(--ink) !important;
  border: 1px solid var(--line) !important; border-radius: 10px !important;
}
.stTextInput input:focus { border-color: var(--gold) !important; box-shadow: 0 0 0 2px rgba(176,141,60,.2) !important; }
[data-baseweb="select"] > div { background: var(--card) !important; color: var(--ink) !important; border-color: var(--line) !important; }
[data-baseweb="select"] * { color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; }
[data-baseweb="popover"], [role="listbox"], [role="option"] { background: var(--card) !important; color: var(--ink) !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background: var(--paper-2) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: rgba(255,255,255,.08) !important; border-color: rgba(227,199,122,.3) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #efe8d6 !important; -webkit-text-fill-color: #efe8d6 !important; }

/* Uploader */
[data-testid="stFileUploader"] section, [data-testid="stFileUploaderDropzone"] {
  background: rgba(255,255,255,.06) !important; border: 1px dashed rgba(227,199,122,.5) !important; border-radius: 12px;
}
[data-testid="stFileUploaderDropzone"] button { background: rgba(227,199,122,.15) !important; color: #efe8d6 !important; border: 1px solid rgba(227,199,122,.4) !important; }

/* Hero */
.hero {
  position: relative; overflow: hidden;
  padding: 2.2rem 2.4rem; border-radius: 22px; margin-bottom: 1.2rem;
  background: linear-gradient(125deg, var(--navy) 0%, var(--navy-2) 60%, #2b4272 100%);
  border: 1px solid #0c1530; box-shadow: 0 14px 40px rgba(20,33,61,.22);
}
.hero::after {
  content: ""; position: absolute; right: -60px; top: -60px; width: 240px; height: 240px;
  border-radius: 50%; border: 1px solid rgba(227,199,122,.35);
  box-shadow: 0 0 0 28px rgba(227,199,122,.06), 0 0 0 60px rgba(227,199,122,.04);
}
.hero .eyebrow { font-size: .75rem; letter-spacing: 3px; font-weight: 600; color: #e3c77a !important; }
.hero h1 { font-family: 'Playfair Display', serif; color: #fff !important; font-size: 2.5rem; line-height: 1.15; margin: .6rem 0 .7rem; }
.hero h1 em { color: #e3c77a; font-style: italic; }
.hero p { color: #cdd5e6 !important; max-width: 560px; margin: 0; }

/* Cards */
.card {
  background: var(--card); border: 1px solid var(--line); border-top: 3px solid var(--gold);
  border-radius: 14px; padding: 1.1rem 1.2rem; min-height: 104px;
  box-shadow: 0 2px 10px rgba(20,33,61,.05);
}
.card b { font-family: 'Playfair Display', serif; font-size: 1.05rem; color: var(--ink); }
.card p { color: var(--ink-soft); font-size: .85rem; margin: .4rem 0 0; }

.section-title { font-family: 'Playfair Display', serif; font-size: 1.25rem; color: var(--ink); margin: .6rem 0 .3rem; }
.divider { height: 1px; background: linear-gradient(90deg, var(--gold), transparent); margin: .2rem 0 .8rem; border: 0; }

/* Chat */
[data-testid="stChatMessage"] {
  background: var(--card) !important; border: 1px solid var(--line); border-radius: 16px;
  padding: 1rem 1.2rem; margin-bottom: .9rem; box-shadow: 0 2px 10px rgba(20,33,61,.05);
}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { color: var(--ink) !important; line-height: 1.65; }
[data-testid="stChatInput"] { background: var(--card) !important; border: 1px solid var(--gold) !important; border-radius: 16px !important; }
[data-testid="stChatInput"] textarea { color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; background: var(--card) !important; caret-color: var(--gold-dark) !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #8a8576 !important; -webkit-text-fill-color: #8a8576 !important; }
[data-testid="stChatInput"] button { background: var(--navy) !important; color: #fff !important; border-radius: 10px !important; }

/* Metrics, expanders, tabs */
[data-testid="stMetric"] { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: .8rem; }
[data-testid="stMetric"] * { color: var(--ink) !important; }
[data-testid="stMetricValue"] { font-family: 'Playfair Display', serif; color: var(--gold-dark) !important; }
[data-testid="stExpander"] { background: var(--card); border: 1px solid var(--line); border-radius: 12px; }
[data-testid="stExpander"] summary p { color: var(--ink) !important; font-weight: 600; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-family: 'Playfair Display', serif; font-size: 1.05rem; color: var(--ink-soft); }
.stTabs [aria-selected="true"] { color: var(--gold-dark) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--gold) !important; }

/* Login */
.login-wrap { text-align: center; margin: 1.5rem 0 1rem; }
.login-wrap .logo { font-family: 'Playfair Display', serif; font-size: 2.6rem; font-weight: 700; color: var(--ink); }
.login-wrap .logo span { color: var(--gold-dark); font-style: italic; }
.login-wrap p { color: var(--ink-soft); }
[data-testid="stForm"] { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 1.4rem; box-shadow: 0 8px 28px rgba(20,33,61,.08); }

.muted { color: var(--ink-soft); font-size: .82rem; text-align: center; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------- SESSION DEFAULTS ----------

for key, default in {
    "access_token": None,
    "auth_user": None,
    "messages": [],
    "documents": [],
    "last_answer": "",
    "show_sources": True,
    "top_k": 3,
    "answer_style": "Balanced",
    "response_format": "Paragraph",
    "pending_question": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------- AUTHENTICATION ----------

def _store_session(result):
    st.session_state.access_token = result.session.access_token
    st.session_state.auth_user = {"id": result.user.id, "email": result.user.email}


if not st.session_state.access_token:
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown(
            '<div class="login-wrap"><div class="logo">DocuChat <span>AI</span></div>'
            "<p>Your personal document assistant</p></div>",
            unsafe_allow_html=True,
        )
        login_tab, register_tab = st.tabs(["Sign in", "Create account"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                login_clicked = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if login_clicked:
                if not email.strip() or not password:
                    st.warning("Enter your email and password.")
                else:
                    try:
                        result = supabase.auth.sign_in_with_password(
                            {"email": email.strip(), "password": password}
                        )
                        if result.session and result.user:
                            _store_session(result)
                            st.rerun()
                        else:
                            st.error("Login was unsuccessful. Check your credentials.")
                    except Exception as exc:
                        st.error(f"Login failed: {exc}")

        with register_tab:
            with st.form("register_form"):
                new_email = st.text_input("Email address", key="register_email")
                new_password = st.text_input(
                    "Password (at least 8 characters)", type="password", key="register_password"
                )
                confirm_password = st.text_input("Confirm password", type="password", key="confirm_password")
                register_clicked = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if register_clicked:
                if not new_email.strip():
                    st.warning("Enter your email address.")
                elif len(new_password) < 8:
                    st.warning("Use a password with at least 8 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        result = supabase.auth.sign_up(
                            {"email": new_email.strip(), "password": new_password}
                        )
                        if result.session and result.user:
                            _store_session(result)
                            st.success("Account created successfully.")
                            st.rerun()
                        else:
                            st.success(
                                "Registration submitted. Check your email to confirm your account, then sign in."
                            )
                    except Exception as exc:
                        st.error(f"Registration failed: {exc}")
    st.stop()


# ---------- API HELPERS ----------

def api_request(method, path, *, params=None, files=None, timeout=TIMEOUT):
    """Call FastAPI with the logged-in user's Supabase access token."""
    headers = {}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(
            method=method, url=f"{API_BASE}{path}", params=params,
            files=files, headers=headers, timeout=timeout,
        )
    except requests.RequestException as exc:
        return None, (
            f"Cannot connect to FastAPI at {API_BASE}. "
            f"Start it with: uvicorn main:app --reload. Details: {exc}"
        )
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
    st.session_state.documents = data.get("documents", []) if isinstance(data, dict) else []


def render_sources(sources):
    if not sources:
        return
    with st.expander(f"📚 Sources consulted ({len(sources)})"):
        for i, source in enumerate(sources, 1):
            if isinstance(source, dict):
                name = source.get("filename", f"Source {i}")
                snippet = source.get("text", source.get("content", ""))
                st.markdown(f"**{i}. {name}**")
                if snippet:
                    st.caption(str(snippet)[:900])
            else:
                st.write(f"{i}. {source}")


def render_listen_buttons(answer, uid):
    speech_text = json.dumps(answer).replace("</", "<\\/")
    components.html(
        f"""
        <div style="display:flex; gap:10px; font-family:Inter,sans-serif;">
          <button id="speak{uid}" style="padding:8px 16px;border-radius:10px;cursor:pointer;
            border:1px solid #e6dcc6;background:#fffdf8;color:#14213d;font-weight:600;">🔊 Listen</button>
          <button id="stop{uid}" style="padding:8px 16px;border-radius:10px;cursor:pointer;
            border:1px solid #e6dcc6;background:#fffdf8;color:#14213d;font-weight:600;">⏹ Stop</button>
        </div>
        <script>
          const text{uid} = {speech_text};
          document.getElementById("speak{uid}").onclick = function() {{
            const synth = window.speechSynthesis; synth.cancel();
            const u = new SpeechSynthesisUtterance(text{uid}); u.lang = "en-IN"; synth.speak(u);
          }};
          document.getElementById("stop{uid}").onclick = function() {{ window.speechSynthesis.cancel(); }};
        </script>
        """,
        height=52,
    )


# ---------- SIDEBAR ----------

with st.sidebar:
    st.markdown(
        '<div class="brand">DocuChat <span>AI</span></div>'
        '<div class="tagline">YOUR DOCUMENT LIBRARY</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Signed in as {st.session_state.auth_user.get('email', 'User')}")

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

    st.markdown("---")
    st.markdown("#### Your documents")
    uploads = st.file_uploader(
        "Upload PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True,
        help="Use text-based PDFs or TXT files. Scanned/image-only PDFs need OCR first.",
    )
    if st.button("Upload and index files", type="primary", use_container_width=True):
        if not uploads:
            st.warning("Choose at least one PDF or TXT file first.")
        else:
            succeeded = failed = 0
            progress = st.progress(0, text="Preparing uploads…")
            for n, file in enumerate(uploads, start=1):
                content = file.getvalue()
                if not content:
                    failed += 1
                    st.error(f"{file.name}: this file is empty (0 bytes).")
                    progress.progress(n / len(uploads), text=f"Checked {n} of {len(uploads)}")
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
                        extra = f" · {data.get('total_chunks', 0)} chunks" if isinstance(data, dict) else ""
                        st.success(f"{file.name}: indexed{extra}")
                except Exception as exc:
                    failed += 1
                    st.error(f"{file.name}: upload failed: {exc}")
                progress.progress(n / len(uploads), text=f"Processed {n} of {len(uploads)}")

            if succeeded:
                _, index_error = api_request("POST", "/index-uploaded-documents", timeout=300)
                if index_error:
                    st.warning(f"Uploaded, but the final index refresh failed: {index_error}")
                refresh_documents(show_error=True)
            if failed:
                st.warning(f"{failed} file(s) could not be uploaded.")
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
            doc_col, del_col = st.columns([5, 1])
            with doc_col:
                st.markdown(f"📄 **{filename}**")
                st.caption(f"{doc.get('text_length', 0):,} characters")
            with del_col:
                if st.button("🗑️", key=f"delete_document_{filename}", help=f"Delete {filename}"):
                    st.session_state[f"confirm_doc_delete_{filename}"] = True
            if st.session_state.get(f"confirm_doc_delete_{filename}", False):
                st.warning(f"Delete **{filename}**? The index will be rebuilt.")
                yes_col, no_col = st.columns(2)
                with yes_col:
                    if st.button("Yes, delete", key=f"confirm_delete_doc_{filename}", type="primary"):
                        _, error = api_request(
                            "DELETE", f"/uploaded-documents/{quote(filename, safe='')}", timeout=300
                        )
                        if error:
                            st.error(f"Could not delete {filename}: {error}")
                        else:
                            st.session_state[f"confirm_doc_delete_{filename}"] = False
                            refresh_documents()
                            st.rerun()
                with no_col:
                    if st.button("Cancel", key=f"cancel_delete_doc_{filename}"):
                        st.session_state[f"confirm_doc_delete_{filename}"] = False
                        st.rerun()
    else:
        st.caption("No uploaded documents yet.")

    st.markdown("---")
    st.markdown("#### Preferences")
    st.session_state.show_sources = st.toggle("Show source references", value=st.session_state.show_sources)
    st.session_state.answer_style = st.selectbox("Answer style", ["Balanced", "Concise", "Detailed"])
    st.session_state.response_format = st.selectbox("Response format", ["Paragraph", "Bullet points", "Step-by-step"])
    st.session_state.top_k = st.select_slider("Relevant sections", options=[1, 3, 5, 7, 10], value=st.session_state.top_k)

    st.markdown("---")
    if st.button("Log out", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        for k in ("access_token", "auth_user"):
            st.session_state[k] = None
        st.session_state.messages = []
        st.session_state.documents = []
        st.session_state.last_answer = ""
        st.rerun()


# ---------- MAIN ----------

main_col, info_col = st.columns([3.2, 1.05], gap="large")

with main_col:
    st.markdown(
        """<div class="hero">
        <div class="eyebrow">✦ AN AI LIBRARIAN FOR YOUR FILES</div>
        <h1>Ask <em>better</em> questions.<br>Find answers faster.</h1>
        <p>Query your uploaded documents in plain language and review the exact passages behind every answer.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in [
        (c1, "🔎", "Smart retrieval", "Surfaces the most relevant passages from your files."),
        (c2, "✨", "Clear answers", "Concise, well-reasoned replies from your AI model."),
        (c3, "📚", "Cited sources", "Inspect the snippets used to build each answer."),
    ]:
        with col:
            st.markdown(f'<div class="card"><b>{icon}&nbsp; {title}</b><p>{desc}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Try asking</div><hr class="divider">', unsafe_allow_html=True)
    prompt_cols = st.columns(4)
    for col, prompt in zip(
        prompt_cols,
        ["Summarize my documents", "What are the key points?", "Explain this simply", "Compare my documents"],
    ):
        with col:
            if st.button(prompt, key=f"prompt_{prompt}", use_container_width=True):
                st.session_state.pending_question = prompt
                st.rerun()

    if not st.session_state.messages:
        st.info("Upload a PDF or TXT file in the sidebar, then ask a question below.")

    # Render conversation
    i = 0
    while i < len(st.session_state.messages):
        msg = st.session_state.messages[i]
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources") and st.session_state.show_sources:
                render_sources(msg["sources"])
            if msg["role"] == "assistant" and not msg.get("error"):
                render_listen_buttons(msg["content"], i)
            if msg["role"] == "user":
                if st.button("🗑️ Delete this exchange", key=f"delete_exchange_{i}"):
                    del st.session_state.messages[i]
                    if i < len(st.session_state.messages) and st.session_state.messages[i].get("role") == "assistant":
                        del st.session_state.messages[i]
                    st.session_state.last_answer = next(
                        (m["content"] for m in reversed(st.session_state.messages) if m.get("role") == "assistant"), ""
                    )
                    st.rerun()
        i += 1

    voice_question = speech_to_text(
        language="en-IN",
        start_prompt="🎙️ Ask by voice",
        stop_prompt="⏹️ Stop recording",
        just_once=True,
        key="docuchat_voice_input",
    )
    typed_question = st.chat_input("Ask a question about your documents…")
    question = typed_question or voice_question or st.session_state.pending_question

    if question:
        st.session_state.pending_question = None
        question = question.strip()
        if question:
            history_lines = [
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in st.session_state.messages[-10:]
            ]
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Searching your documents and composing an answer…"):
                    params = {
                        "question": question,
                        "top_k": int(st.session_state.top_k),
                        "history": "\n".join(history_lines),
                    }
                    result, error = api_request("GET", "/ask", params=params)
                if error:
                    st.error(error)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Request failed: {error}", "error": True}
                    )
                else:
                    answer = str(result.get("answer", result.get("response", result.get("text", "")))).strip()
                    sources = result.get("sources", [])
                    if not answer:
                        answer = "The backend responded, but did not return an answer field. Check /docs."
                    st.session_state.last_answer = answer
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )
            st.rerun()

with info_col:
    st.markdown('<div class="card"><b>Workspace</b><p>Your private reading room.</p></div>', unsafe_allow_html=True)
    st.write("")
    st.metric("Documents", len(st.session_state.documents))
    st.metric("Messages", len(st.session_state.messages))
    if st.session_state.last_answer:
        st.download_button(
            "↓ Download last answer", st.session_state.last_answer,
            file_name="docuchat_answer.txt", mime="text/plain", use_container_width=True,
        )
    st.write("")
    st.markdown(
        '<div class="card"><b>A helpful tip</b><p>Upload your files and wait for the indexing '
        "confirmation before asking questions.</p></div>",
        unsafe_allow_html=True,
    )

st.markdown('<p class="muted">DocuChat AI · Your documents, thoughtfully answered</p>', unsafe_allow_html=True)

# Run with:  python -m streamlit run app_classic.py