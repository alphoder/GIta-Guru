# 🙏 GitaGuru — Bhagavad Gita AI Agent

A RAG-powered AI agent that answers life questions using only Bhagavad Gita wisdom, citing specific chapters and verses.

## Tech Stack
Python, LangChain, ChromaDB, HuggingFace Embeddings, Streamlit. Supports **Ollama** (free/local) or **Anthropic Claude** as LLM.

## Quick Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Load Gita data into ChromaDB
python scripts/load_data.py

# Run the app
streamlit run app.py
```

## LLM Options

- **Ollama (default):** Install [Ollama](https://ollama.ai), then `ollama pull llama3`. No API key needed.
- **Claude API:** Copy `.env.example` to `.env`, add your `ANTHROPIC_API_KEY`, set `LLM_PROVIDER=anthropic`.

Switch providers anytime via the sidebar dropdown or by editing `.env`.

## Features
Verse-of-the-Day, quick topic buttons (Karma, Dharma, Peace, Meditation), bilingual Hindi/English support, Sanskrit shloka citations, and chat history.

## Recommended Psychology Books

These books complement the Gita's teachings and help understand human behaviour, emotions, and mental patterns — useful for building deeper empathy into the agent's guidance.

- **Man's Search for Meaning** — Viktor Frankl. Finding purpose through suffering; aligns with the Gita's teachings on duty and meaning.
- **Thinking, Fast and Slow** — Daniel Kahneman. How the mind makes decisions; connects to the Gita's concept of buddhi (intellect) vs impulse.
- **The Power of Now** — Eckhart Tolle. Present-moment awareness; mirrors the Gita's teachings on meditation and mindfulness (Chapter 6).
- **Emotional Intelligence** — Daniel Goleman. Managing emotions and self-awareness; relates to the Gita's sthitaprajna (steady-minded person, Chapter 2).
- **Atomic Habits** — James Clear. Building discipline through small actions; complements Karma Yoga (Chapter 3).
- **The Body Keeps the Score** — Bessel van der Kolk. How trauma affects the mind and body; useful for understanding emotional distress.
- **Ikigai** — Héctor García & Francesc Miralles. Finding life purpose; parallels the Gita's concept of svadharma (one's own duty).
- **Meditations** — Marcus Aurelius. Stoic philosophy on detachment and inner peace; deeply resonates with Gita Chapter 2 and 6.
- **The Courage to Be Disliked** — Ichiro Kishimi & Fumitake Koga. Adlerian psychology on freedom and self-acceptance; connects to the Gita's teaching on acting without fear of judgment.
- **Feeling Good** — David Burns. Cognitive behavioural therapy for negative thought patterns; aligns with Krishna's guidance on mastering the mind (Chapter 6, Verse 6).

## Reset Data
```bash
python scripts/load_data.py --reset
```
