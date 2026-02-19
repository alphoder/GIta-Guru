# 🧘 MindGita — AI Wellness Companion

MindGita is a RAG-powered AI wellness companion that combines **evidence-based psychological therapy** (CBT, ACT, DBT, mindfulness) with the timeless wisdom of the **Bhagavad Gita**. It listens, empathises, and guides you through life's challenges with compassion and science-backed insights.

## Features

- **Therapist-first AI** — responds with empathy, psychological techniques, and actionable advice
- **Gita wisdom** — cites relevant Bhagavad Gita verses with Sanskrit and English translation
- **Dark / Light mode** — toggle between themes with gradient UI and glassmorphism effects
- **Mood check-in** — select your current mood for personalised responses
- **Quick therapy topics** — one-click buttons for Anxiety, Burnout, Grief, Relationships, and more
- **Verse of the Day** — random Gita verse displayed in the sidebar
- **Bilingual support** — responds in English, Hindi, or both
- **User profile** — remembers your name and situation for context-aware guidance
- **Chat history** — maintains conversation context within the session

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq (Llama 3.3 70B) |
| Framework | LangChain |
| Vector DB | ChromaDB |
| Embeddings | HuggingFace (`all-MiniLM-L6-v2`) |
| Frontend | Streamlit |
| Data | Bhagavad Gita JSON + Psychology references |

## Quick Setup

```bash
# Clone the repository
git clone https://github.com/alphoder/GIta-Guru.git
cd gita-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your Groq API key:
#   GROQ_API_KEY=your_key_here
#   GROQ_MODEL=llama-3.3-70b-versatile

# Run the app
streamlit run app.py
```

The vector store (ChromaDB) auto-builds on first run — no manual data loading required.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key (required) | — |
| `GROQ_MODEL` | Groq model to use | `llama-3.3-70b-versatile` |

Get a free Groq API key at [console.groq.com](https://console.groq.com).

## Project Structure

```
gita-agent/
├── app.py                 # Streamlit UI (themes, sidebar, chat)
├── src/
│   ├── chain.py           # RAG chain orchestration
│   ├── config.py          # Configuration and env vars
│   ├── embeddings.py      # HuggingFace embedding setup
│   ├── llm.py             # Groq LLM initialisation
│   ├── prompts.py         # System prompt and templates
│   └── vector_store.py    # ChromaDB vector store
├── data/
│   ├── bhagavad_gita.json # Gita text corpus
│   └── psychology_books.json
├── scripts/
│   └── load_data.py       # Data loading utility
├── requirements.txt
└── .env.example
```

## Psychology References

MindGita draws on these therapeutic frameworks and researchers:

- **CBT** (Cognitive Behavioural Therapy) — for anxiety, depression, negative thought patterns
- **ACT** (Acceptance and Commitment Therapy) — for values clarification and psychological flexibility
- **DBT** (Dialectical Behaviour Therapy) — for emotion regulation and distress tolerance
- **Logotherapy** (Viktor Frankl) — for meaning-making and purpose
- **Self-Compassion** (Kristin Neff) — for self-esteem and inner critic work
- **Gottman Method** — for relationship guidance
- **Mindfulness** — grounding techniques and present-moment awareness

## Reset Vector Store

```bash
python scripts/load_data.py --reset
```

## License

This project is for educational and personal wellness purposes. It is not a substitute for professional mental health care.
