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

# ── Session state defaults ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "English"
if "verse_of_day" not in st.session_state:
    st.session_state.verse_of_day = None  # set after gita_data loads
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"name": "", "situation": "", "mood": ""}
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # dark by default


# ── Theme palette ──────────────────────────────────────────────
def get_theme_css(dark: bool) -> str:
    """Return the full CSS block for the chosen theme."""

    if dark:
        main_bg = "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)"
        sidebar_bg = "linear-gradient(180deg, #1a0533 0%, #0d1f2d 100%)"
        text_primary = "#e8e0f0"
        text_muted = "#9a8cbf"
        card_hover_bg = "rgba(255,255,255,0.10)"
        mood_card_bg = "rgba(107, 79, 160, 0.18)"
        mood_card_border = "rgba(107, 79, 160, 0.35)"
        mood_card_text = "#d4c6f0"
        tip_bg = "rgba(17, 153, 142, 0.12)"
        tip_border = "rgba(17, 153, 142, 0.30)"
        tip_text = "#7ee8d8"
        source_bg = "rgba(17, 153, 142, 0.10)"
        source_border = "#11998e"
        source_text = "#7ee8d8"
        input_bg = "rgba(255,255,255,0.06)"
        input_border = "rgba(255,255,255,0.12)"
        input_text = "#e8e0f0"
        scrollbar_thumb = "rgba(107,79,160,0.4)"
    else:
        main_bg = "linear-gradient(135deg, #f5f0ff 0%, #eef9f6 50%, #f0e6ff 100%)"
        sidebar_bg = "linear-gradient(180deg, #3d1d72 0%, #1a8a7e 100%)"
        text_primary = "#1a1a2e"
        text_muted = "#7a7a9a"
        card_hover_bg = "rgba(255,255,255,0.95)"
        mood_card_bg = "rgba(107, 79, 160, 0.08)"
        mood_card_border = "rgba(107, 79, 160, 0.20)"
        mood_card_text = "#5a3e8a"
        tip_bg = "rgba(17, 153, 142, 0.08)"
        tip_border = "rgba(17, 153, 142, 0.25)"
        tip_text = "#0d5952"
        source_bg = "rgba(17, 153, 142, 0.06)"
        source_border = "#11998e"
        source_text = "#0d5952"
        input_bg = "rgba(255,255,255,0.70)"
        input_border = "rgba(45, 27, 105, 0.15)"
        input_text = "#1a1a2e"
        scrollbar_thumb = "rgba(107,79,160,0.25)"

    return f"""
<style>
/* ═══════════════════════════════════════════
   MindGita Theme — {"Dark" if dark else "Light"} Mode
   ═══════════════════════════════════════════ */

/* ── Global ── */
html, body, [class*="css"] {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    transition: background 0.4s ease, color 0.4s ease;
}}

/* ── Main area background ── */
.stApp {{
    background: {main_bg};
    background-attachment: fixed;
}}
.stApp > header {{
    background: transparent !important;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
/* [data-testid="stHeader"] {{visibility: hidden; height: 0; position: fixed;}} */
/* Commented out above line to avoid hiding main header and controls */
[data-testid="collapsedControl"] {{
    visibility: visible !important;
    display: flex !important;
    color: white !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {scrollbar_thumb}; border-radius: 3px; }}

/* ── Text colours — Main area ── */
.stApp .stMarkdown, .stApp .stMarkdown p,
.stApp .stMarkdown li, .stApp .stMarkdown span {{
    color: {text_primary} !important;
}}
.stApp .stMarkdown h1, .stApp .stMarkdown h2, .stApp .stMarkdown h3 {{
    color: {text_primary} !important;
}}
.stApp .stCaption {{
    color: {text_muted} !important;
}}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {{
    background: {sidebar_bg};
    border-right: 1px solid rgba(255,255,255,0.08);
}}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown strong,
section[data-testid="stSidebar"] .stMarkdown em,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stExpanderToggleDetails"] {{
    color: #e2d9f3 !important;
}}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stTextArea label {{
    color: #c4b5e0 !important;
    font-size: 0.82rem !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(107, 79, 160, 0.30) !important;
}}
section[data-testid="stSidebar"] .stButton button {{
    background: rgba(107, 79, 160, 0.30) !important;
    border: 1px solid rgba(107, 79, 160, 0.50) !important;
    color: #e2d9f3 !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    transition: all 0.25s ease !important;
    backdrop-filter: blur(8px) !important;
}}
section[data-testid="stSidebar"] .stButton button:hover {{
    background: rgba(107, 79, 160, 0.50) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(107, 79, 160, 0.25) !important;
}}
section[data-testid="stSidebar"] [data-testid="stToggle"] label span {{
    color: #e2d9f3 !important;
}}
section[data-testid="stSidebar"] .streamlit-expanderHeader {{
    color: #e2d9f3 !important;
    background: rgba(107, 79, 160, 0.15) !important;
    border-radius: 10px !important;
}}

/* ── HERO HEADER ── */
.hero {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #11998e 100%);
    background-size: 200% 200%;
    animation: heroShift 8s ease infinite;
    border-radius: 18px;
    padding: 32px 36px 24px 36px;
    margin-bottom: 22px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    position: relative;
    overflow: hidden;
}}
.hero::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.08);
    border-radius: 18px;
}}
.hero h1 {{
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
    position: relative;
    color: white !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.15);
}}
.hero p {{
    font-size: 1.05rem;
    opacity: 0.92;
    margin: 0;
    position: relative;
    color: rgba(255,255,255,0.92) !important;
    font-weight: 400;
}}
@keyframes heroShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* ── MOOD CARD ── */
.mood-card {{
    background: {mood_card_bg};
    border: 1px solid {mood_card_border};
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 18px;
    text-align: center;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    transition: all 0.3s ease;
}}
.mood-card:hover {{
    background: {card_hover_bg};
}}
.mood-card p {{
    font-size: 0.9rem;
    color: {mood_card_text} !important;
    margin: 0;
    font-weight: 600;
    letter-spacing: 0.3px;
}}

/* ── TIP BOX (welcome) ── */
.tip-box {{
    background: {tip_bg};
    border: 1px solid {tip_border};
    border-radius: 14px;
    padding: 16px 20px;
    font-size: 0.88rem;
    color: {tip_text} !important;
    margin-top: 8px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    line-height: 1.6;
}}
.tip-box b {{
    color: {tip_text} !important;
}}

/* ── SOURCE CARDS ── */
.source-card {{
    background: {source_bg};
    border-left: 3px solid {source_border};
    border-radius: 10px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.84rem;
    color: {source_text} !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: all 0.25s ease;
}}
.source-card:hover {{
    transform: translateX(4px);
}}
.source-card i {{
    color: {source_text} !important;
}}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {{
    border-radius: 14px;
    padding: 6px;
    margin-bottom: 6px;
    transition: all 0.3s ease;
}}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] textarea {{
    background: {input_bg} !important;
    border: 1px solid {input_border} !important;
    border-radius: 14px !important;
    color: {input_text} !important;
    transition: all 0.3s ease !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color: #667eea !important;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.20) !important;
}}

/* ── Streamlit widget overrides — main area ── */
.stApp .stTextInput input,
.stApp .stTextArea textarea,
.stApp .stSelectbox > div > div {{
    background: {input_bg} !important;
    border-color: {input_border} !important;
    color: {input_text} !important;
    border-radius: 10px !important;
}}

/* ── Fade-in animation ── */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.hero, .mood-card, .tip-box {{
    animation: fadeIn 0.5s ease-out;
}}

</style>
"""


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

# init verse of day after gita data loads
if st.session_state.verse_of_day is None:
    ch, v = get_random_verse()
    st.session_state.verse_of_day = (ch, v)


# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧘 MindGita")
    st.caption("Your AI Wellness Companion")
    st.divider()

    # Theme toggle
    st.session_state.dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode,
    )

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
    st.markdown(f"> _{v.get('sanskrit', '')[:60]}_")
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

# ── Inject theme CSS (after sidebar so toggle value is read) ──
st.markdown(get_theme_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ── Main area ──────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🧘 MindGita</h1>
  <p>AI-powered psychological support · Grounded in Bhagavad Gita wisdom</p>
</div>
""", unsafe_allow_html=True)

# Mood acknowledgement pill
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
