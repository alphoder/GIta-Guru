"""
MindGita — AI Wellness Companion
Psychological therapy meets ancient Gita wisdom.
"""

import sys
import json
import random
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import GITA_JSON_PATH
from src.chain import ask_gita

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="MindGita — AI Wellness Companion",
    page_icon="🧘",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* ── Hide default Streamlit header/footer ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Keep the sidebar collapse/expand toggle always visible ── */
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: flex !important;
}

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #2d1b69 0%, #11998e 100%);
    border-radius: 16px;
    padding: 28px 32px 20px 32px;
    margin-bottom: 20px;
    text-align: center;
    color: white;
}
.hero h1 {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.hero p {
    font-size: 1rem;
    opacity: 0.88;
    margin: 0;
}

/* ── Mood card ── */
.mood-card {
    background: #f8f4ff;
    border: 1px solid #e2d9f3;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 18px;
    text-align: center;
}
.mood-card p {
    font-size: 0.88rem;
    color: #6b5b95;
    margin: 0 0 8px 0;
    font-weight: 600;
    letter-spacing: 0.3px;
}

/* ── Chat message bubbles ── */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 4px;
}

/* ── Source cards ── */
.source-card {
    background: #f0fdf4;
    border-left: 3px solid #11998e;
    border-radius: 8px;
    padding: 8px 12px;
    margin: 4px 0;
    font-size: 0.82rem;
    color: #166534;
}

/* ── Sidebar styling ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a0533 0%, #0d1f2d 100%);
}
section[data-testid="stSidebar"] * {
    color: #e2d9f3 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stTextArea label {
    color: #c4b5e0 !important;
    font-size: 0.82rem !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #3d2b6b !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: #3d2b6b !important;
    border: 1px solid #6b4fa0 !important;
    color: #e2d9f3 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #5a3e8a !important;
}

/* ── Wellness tip box ── */
.tip-box {
    background: rgba(17,153,142,0.12);
    border: 1px solid rgba(17,153,142,0.3);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #0d5952;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Load Gita data ─────────────────────────────────────────────
@st.cache_data
def load_gita_data():
    with open(GITA_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

gita_data = load_gita_data()

def get_random_verse():
    chapters = gita_data["chapters"]
    chapter = random.choice(chapters)
    verse = random.choice(chapter["verses"])
    return chapter, verse

# ── Session state ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "English"
if "verse_of_day" not in st.session_state:
    ch, v = get_random_verse()
    st.session_state.verse_of_day = (ch, v)
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"name": "", "situation": "", "mood": ""}

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧘 MindGita")
    st.caption("Your AI Wellness Companion")
    st.divider()

    # Mood check-in
    st.markdown("**How are you feeling right now?**")
    mood_options = {
        "😔 Low / Sad": "feeling low and sad",
        "😰 Anxious": "feeling anxious and worried",
        "😤 Frustrated": "feeling frustrated or angry",
        "😕 Confused": "feeling confused and lost",
        "😐 Okay": "feeling okay, just need clarity",
        "🙂 Good": "feeling good and reflective",
    }
    selected_mood = st.selectbox("Mood", list(mood_options.keys()), label_visibility="collapsed")
    mood_text = mood_options[selected_mood]

    st.divider()

    # User profile
    st.markdown("**🧑 About You**")
    st.caption("Help me understand you better.")
    user_name = st.text_input("Your name", value=st.session_state.user_profile.get("name", ""), placeholder="e.g. Arjun")
    user_situation = st.text_area(
        "What's bothering you?",
        value=st.session_state.user_profile.get("situation", ""),
        placeholder="e.g. I've been feeling overwhelmed at work and it's affecting my relationships...",
        height=90,
    )
    st.session_state.user_profile = {
        "name": user_name.strip(),
        "situation": user_situation.strip(),
        "mood": mood_text,
    }

    st.divider()

    # Language
    st.markdown("**🌐 Language**")
    st.session_state.language = st.selectbox(
        "Respond in",
        options=["English", "Hindi", "Both"],
        label_visibility="collapsed",
    )

    st.divider()

    # Verse of the Day
    st.markdown("**📖 Gita Verse of the Day**")
    ch, v = st.session_state.verse_of_day
    st.markdown(f"*Ch. {ch['chapter_number']}, Verse {v['verse_number']} — {ch['chapter_name']}*")
    st.markdown(f"> _{v.get('sanskrit', ''[:60])}_")
    st.caption(v["english_translation"][:180] + "...")
    if st.button("🔄 New Verse", use_container_width=True):
        ch, v = get_random_verse()
        st.session_state.verse_of_day = (ch, v)
        st.rerun()

    st.divider()

    # Quick therapy topics
    st.markdown("**🩺 Quick Topics**")
    topics = {
        "😰 Anxiety": "I'm dealing with anxiety and constant worry. Help me manage it.",
        "🔥 Burnout": "I feel burned out and exhausted. I have no energy left.",
        "💔 Relationships": "I'm struggling with a painful relationship situation.",
        "🪞 Self-Worth": "I'm struggling with low self-esteem and confidence.",
        "😢 Grief": "I'm going through grief and loss and don't know how to cope.",
        "😠 Anger": "I struggle with anger and losing control of my emotions.",
        "🧭 Purpose": "I feel lost and have no sense of purpose or direction.",
        "😴 Loneliness": "I feel deeply lonely and disconnected from people.",
    }
    cols = st.columns(2)
    for i, (label, prompt) in enumerate(topics.items()):
        with cols[i % 2]:
            if st.button(label, key=f"topic_{label}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.pending_topic = prompt
                st.rerun()

    st.divider()

    with st.expander("ℹ️ About MindGita"):
        st.markdown(
            "**MindGita** is your AI wellness companion — combining evidence-based "
            "psychological therapy with the timeless wisdom of the Bhagavad Gita. "
            "It listens, understands, and guides you through life's challenges "
            "with compassion and science-backed insights."
        )

    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main area ──────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🧘 MindGita</h1>
  <p>AI-powered psychological support · Grounded in Bhagavad Gita wisdom</p>
</div>
""", unsafe_allow_html=True)

# Mood acknowledgement pill
mood_emoji = selected_mood.split()[0]
st.markdown(
    f'<div class="mood-card"><p>Current mood: {selected_mood}</p></div>',
    unsafe_allow_html=True,
)

# Welcome message for new sessions
if not st.session_state.messages:
    name_part = f", {user_name}" if user_name else ""
    st.markdown(f"""
<div class="tip-box">
👋 <b>Welcome{name_part}!</b> I'm here to listen — with no judgment, just compassion.
You can share what's on your mind, pick a topic from the sidebar, or simply start talking.
I blend psychological therapy with Bhagavad Gita wisdom to give you practical, heartfelt guidance.
</div>
""", unsafe_allow_html=True)
    st.markdown("")

# Display chat history
for msg in st.session_state.messages:
    avatar = "🧘" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Pending topic from sidebar
pending = st.session_state.pop("pending_topic", None)

# Chat input
user_input = st.chat_input("Share what's on your mind... I'm here to listen.")
question = pending or user_input

if question:
    if not pending:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(question)

    # Add language and mood context
    lang = st.session_state.language
    enriched_question = question
    if lang == "Hindi":
        enriched_question += " (Please respond in Hindi.)"
    elif lang == "Both":
        enriched_question += " (Please respond in both Hindi and English.)"

    # Add mood context if it's the first message
    if len(st.session_state.messages) <= 1 and mood_text:
        enriched_question = f"[User is currently {mood_text}] {enriched_question}"

    with st.chat_message("assistant", avatar="🧘"):
        with st.spinner("Reflecting with you..."):
            try:
                result = ask_gita(
                    question=enriched_question,
                    chat_history=st.session_state.messages,
                    user_profile=st.session_state.user_profile,
                )
                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)

                # Gita verse references
                gita_sources = [s for s in sources if s.get("chapter") != "?"]
                if gita_sources:
                    st.markdown("")
                    st.markdown("**📚 Gita Verses Referenced:**")
                    for src in gita_sources[:3]:
                        st.markdown(
                            f'<div class="source-card">📖 Chapter {src["chapter"]}, '
                            f'Verse {src["verse"]} — <i>{src["chapter_name"]}</i></div>',
                            unsafe_allow_html=True,
                        )

                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"I'm having trouble connecting right now.\n\n**Error:** {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
