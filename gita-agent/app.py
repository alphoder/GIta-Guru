"""
GitaGuru — Streamlit Chat Interface
A personal spiritual counselor powered by the Bhagavad Gita.
"""

import sys
import json
import random
from pathlib import Path

import streamlit as st

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import GITA_JSON_PATH
from src.chain import ask_gita

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="GitaGuru — Your Personal Guide",
    page_icon="🙏",
    layout="centered",
)

# ── Load Gita data for Verse of the Day ───────────────────────
@st.cache_data
def load_gita_data():
    with open(GITA_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

gita_data = load_gita_data()


def get_random_verse():
    """Pick a random verse for Verse of the Day."""
    chapters = gita_data["chapters"]
    chapter = random.choice(chapters)
    verse = random.choice(chapter["verses"])
    return chapter, verse


# ── Session state init ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "English"
if "verse_of_day" not in st.session_state:
    ch, v = get_random_verse()
    st.session_state.verse_of_day = (ch, v)
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"name": "", "situation": ""}

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")

    # Language preference
    st.session_state.language = st.selectbox(
        "Language Preference",
        options=["English", "Hindi", "Both"],
    )

    st.divider()

    # ── User Profile Section ───────────────────────────────────
    st.subheader("🧑 Tell Me About You")
    st.caption("Share a little so I can guide you personally.")

    user_name = st.text_input(
        "Your name",
        value=st.session_state.user_profile.get("name", ""),
        placeholder="e.g. Arjun",
    )
    user_situation = st.text_area(
        "What's on your mind?",
        value=st.session_state.user_profile.get("situation", ""),
        placeholder="e.g. I'm feeling lost in my career and don't know what my purpose is...",
        height=100,
    )
    st.session_state.user_profile = {
        "name": user_name.strip(),
        "situation": user_situation.strip(),
    }

    st.divider()

    # Verse of the Day
    st.subheader("📖 Verse of the Day")
    ch, v = st.session_state.verse_of_day
    st.markdown(f"**Chapter {ch['chapter_number']}, Verse {v['verse_number']}**")
    st.markdown(f"*{ch['chapter_name']}*")
    st.markdown(f"> {v['sanskrit']}")
    st.caption(v["english_translation"])
    if st.button("🔄 New Verse"):
        ch, v = get_random_verse()
        st.session_state.verse_of_day = (ch, v)
        st.rerun()

    st.divider()

    # Quick topic buttons
    st.subheader("🔍 Quick Topics")
    topics = ["Karma", "Dharma", "Peace", "Meditation", "Detachment", "Devotion"]
    cols = st.columns(2)
    for i, topic in enumerate(topics):
        with cols[i % 2]:
            if st.button(topic, key=f"topic_{topic}", use_container_width=True):
                prompt = f"I want to understand {topic} — how does it apply to my life right now?"
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.pending_topic = prompt
                st.rerun()

    st.divider()

    # About section
    with st.expander("ℹ️ About"):
        st.markdown(
            "**GitaGuru** is your personal spiritual counselor. It listens to your "
            "situation, remembers your context, and gives practical life guidance "
            "rooted in Bhagavad Gita wisdom — not just theory, but advice you can "
            "act on today."
        )

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main chat area ─────────────────────────────────────────────
st.title("🙏 GitaGuru")
st.caption("Tell me what you're going through. I'll listen first, then guide you with the wisdom of the Gita.")

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🙏" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# Handle pending topic from sidebar button
pending = st.session_state.pop("pending_topic", None)

# Chat input
user_input = st.chat_input("Tell me what's on your mind...")

# Determine the question to answer
question = pending or user_input

if question:
    # Add user message if it came from chat input (sidebar topics already added)
    if not pending:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

    # Add language hint if user chose Hindi or Both
    lang = st.session_state.language
    if lang == "Hindi":
        question += " (Please respond in Hindi.)"
    elif lang == "Both":
        question += " (Please respond in both Hindi and English.)"

    # Generate response with full context
    with st.chat_message("assistant", avatar="🙏"):
        with st.spinner("Listening and reflecting..."):
            try:
                result = ask_gita(
                    question=question,
                    chat_history=st.session_state.messages,
                    user_profile=st.session_state.user_profile,
                )
                answer = result["answer"]
                sources = result["sources"]

                # Display main answer
                st.markdown(answer)

                # Display related verses (compact)
                if sources:
                    st.divider()
                    st.markdown("**📚 Verses Referenced:**")
                    for src in sources[:3]:
                        st.caption(
                            f"Chapter {src['chapter']}, Verse {src['verse']} "
                            f"— {src['chapter_name']}"
                        )

                # Store in history
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"🙏 I'm having trouble connecting. Please check your setup.\n\n**Error:** {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
