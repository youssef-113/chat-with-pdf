"""
Production-quality Streamlit UI.
Runs with: streamlit run app/ui/streamlit_app.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from app.config.config import settings
from app.services.qa_service import QAService
from app.utils.logger import logger

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=settings.title,
    page_icon=settings.icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #e8e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ── Header ── */
.main-header {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.main-sub {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

/* ── Chat bubbles ── */
.chat-user {
    background: rgba(167, 139, 250, 0.15);
    border-left: 3px solid #a78bfa;
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.95rem;
}
.chat-bot {
    background: rgba(96, 165, 250, 0.1);
    border-left: 3px solid #60a5fa;
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.95rem;
    line-height: 1.6;
}
.chat-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    opacity: 0.6;
}

/* ── Input box ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    padding: 0.65rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.2) !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #a78bfa, #60a5fa) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.6rem !important;
    font-weight: 500 !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── File uploader ── */
.stFileUploader > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px dashed rgba(167,139,250,0.4) !important;
    border-radius: 12px !important;
}

/* ── Status / spinner ── */
.stSpinner > div { color: #a78bfa !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state helpers ─────────────────────────────────────────────────────

def _init_session() -> None:
    if "qa_service" not in st.session_state:
        st.session_state.qa_service = QAService()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []   # list of {"role": str, "text": str}


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _render_sidebar() -> object | None:
    with st.sidebar:
        st.markdown("## 📂 Upload Document")
        uploaded = st.file_uploader(
            "Drag & drop or click to browse",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
        )

        if uploaded:
            st.success(f"✓ {uploaded.name}")
            ftype = uploaded.name.rsplit(".", 1)[-1].upper()
            st.caption(f"Type: {ftype}")

        st.markdown("---")
        st.markdown("### Tips")
        st.markdown(
            "- Ask specific questions about the document content\n"
            "- Works with PDFs, Word docs, and plain text\n"
            "- Upload a new file to switch documents"
        )

        st.markdown("---")
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

        st.markdown(
            "<div style='margin-top:2rem;color:#4a5568;font-size:0.75rem;'>"
            "Powered by Groq + LangChain</div>",
            unsafe_allow_html=True,
        )

    return uploaded


# ── Main content ──────────────────────────────────────────────────────────────

def _render_chat_history() -> None:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user"><div class="chat-label">You</div>{msg["text"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bot"><div class="chat-label">Assistant</div>{msg["text"]}</div>',
                unsafe_allow_html=True,
            )


def main() -> None:
    _init_session()
    uploaded_file = _render_sidebar()

    # ── Header ──
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="main-header">Chat with your Documents</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-sub">Ask any question about your uploaded file — powered by Groq LLM</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Chat history ──
    _render_chat_history()

    # ── Input row ──
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        question = st.text_input(
            "Question",
            placeholder="e.g. What are the key findings in this document?",
            label_visibility="collapsed",
            key="question_input",
        )
    with col_btn:
        ask = st.button("Ask →", use_container_width=True)

    # ── Handle submission ──
    if ask:
        if not uploaded_file:
            st.warning("⬅  Please upload a document first.")
        elif not question.strip():
            st.warning("Please type a question.")
        else:
            st.session_state.chat_history.append({"role": "user", "text": question})
            with st.spinner("Thinking…"):
                try:
                    answer = st.session_state.qa_service.answer(question, uploaded_file)
                except Exception as exc:
                    logger.error(f"QA error: {exc}")
                    answer = f"⚠️ Error: {exc}"
            st.session_state.chat_history.append({"role": "bot", "text": answer})
            st.rerun()

    # ── Empty state ──
    if not st.session_state.chat_history:
        st.markdown(
            "<div style='text-align:center;margin-top:3rem;color:#4a5568;font-size:0.9rem;'>"
            "📎 Upload a document on the left, then ask your first question."
            "</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
