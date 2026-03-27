# DeepRead-AI

DeepRead-AI is an advanced document understanding and conversational AI platform. It leverages LLMs (Groq API), serverless PostgreSQL (Neon), and Next.js to provide seamless document ingestion, chat, and summarization features. Authentication is handled via NextAuth.js with Google OAuth support.

## Features
- **Document Upload & Ingestion:** Supports PDF, DOCX, TXT, and web URLs for ingestion.
- **Conversational Chat:** Chat with your documents, with citation and context-aware responses.
- **Summarization & RAG:** Summarize documents and use Retrieval-Augmented Generation for accurate answers.
- **User Authentication:** Secure login with Google OAuth.
- **Serverless Database:** Uses Neon for scalable, serverless PostgreSQL.

## Environment Variables
Create a `.env.local` file in the `deepread-ai` directory with the following variables:

```env
# Database (Neon serverless PostgreSQL)
DATABASE_URL=postgresql://<username>:<password>@<host>/<db>?sslmode=require&channel_binding=require

# Auth (Google OAuth via NextAuth.js)
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
NEXTAUTH_SECRET=<your-nextauth-secret>
NEXTAUTH_URL=http://localhost:3000

# LLM (Groq - free tier)
GROQ_API_KEY=<your-groq-api-key>
```

## Getting Started

1. **Install dependencies:**
   ```bash
   npm install
   ```
2. **Set up environment:**
   - Copy the example above into `.env.local` and fill in your credentials.
3. **Run the development server:**
   ```bash
   npm run dev
   ```
4. **Open in browser:**
   - Visit [http://localhost:3000](http://localhost:3000)

## Project Structure
- `src/app/` — Next.js app directory (routes, API, pages)
- `src/components/` — UI components
- `src/lib/` — Utility libraries (auth, db, ingest, rag)
- `src/types/` — TypeScript types

## License
MIT
