# DeepRead AI: AI-Powered Research & Analysis Agent

DeepRead AI is a RAG (Retrieval-Augmented Generation) based research and analysis agent that lets users upload any book (PDF, DOCX, TXT) or provide a website URL, and the system automatically ingests, indexes, and learns the content. Once processed, the agent answers any question strictly based on the ingested source material — acting as an expert on that specific book or website with full knowledge of every detail, chapter, paragraph, and data point within it.

The agent does NOT hallucinate or pull from general knowledge. Every answer is grounded in the uploaded source, with citations pointing back to exact pages, chapters, sections, or URLs where the information was found.

## Core Concept

Traditional search gives you links. ChatGPT gives you general answers. DeepRead AI gives you precise, source-grounded answers from YOUR specific documents and websites. Think of it as having a personal research assistant who has read and memorized your entire book or website, and can instantly answer any question about it with page-level citations.

**Use cases:**
- Upload a textbook → ask questions, get answers with page references
- Provide a documentation website → query any API detail instantly
- Upload a research paper → extract methodology, findings, comparisons
- Provide a competitor's website → analyze their offerings in detail
- Upload legal documents → find specific clauses and terms
- Provide a blog/news site → summarize and cross-reference articles

## Tech Stack

- **Frontend:** Next.js 14+, React 18+, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** Next.js API Routes, LangChain.js, Groq SDK
- **Database:** Neon (Serverless PostgreSQL) with pgvector, Drizzle ORM
- **Authentication:** NextAuth.js v5 (Auth.js) with Google OAuth 2.0
- **File Storage:** Vercel Blob or AWS S3
- **Document Parsing:** pdf-parse, cheerio, mammoth
- **Embedding:** OpenAI text-embedding-3-small or HuggingFace via Transformers.js
- **Deployment:** Vercel, Neon

## Getting Started

### Prerequisites

- Node.js (v18.17 or later)
- npm

### 1. Clone the repository

```bash
git clone https://github.com/your-username/deepread-ai.git
cd deepread-ai
```

### 2. Install dependencies

```bash
npm install
```

### 3. Set up environment variables

Create a `.env.local` file in the root of your project and add the following variables:

```env
# Database (Neon serverless PostgreSQL)
DATABASE_URL="postgresql://<username>:<password>@<host>/<db>?sslmode=require"

# Auth (Google OAuth via NextAuth.js)
GOOGLE_CLIENT_ID="<your-google-client-id>"
GOOGLE_CLIENT_SECRET="<your-google-client-secret>"
NEXTAUTH_SECRET="<generate-a-secret>" # openssl rand -base64 32
NEXTAUTH_URL="http://localhost:3000"

# LLM (Groq - free tier)
GROQ_API_KEY="<your-groq-api-key>"

# File Storage (Vercel Blob)
BLOB_READ_WRITE_TOKEN="<your-vercel-blob-token>"

# Embeddings (if using OpenAI)
OPENAI_API_KEY="<your-openai-api-key>"
```

### 4. Set up the database

1.  Create a new project on [Neon](https://neon.tech).
2.  Enable the `pgvector` extension.
3.  Get your database connection string and add it to `DATABASE_URL` in your `.env.local` file.
4.  Push the database schema:

```bash
npx drizzle-kit push
```

### 5. Run the development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the result.

## Project Structure

```
.
├── drizzle.config.ts
├── next.config.ts
├── package.json
├── postcss.config.mjs
├── tsconfig.json
├── public/
└── src/
    ├── app/
    │   ├── api/
    │   ├── auth/
    │   ├── dashboard/
    │   └── source/
    ├── components/
    │   ├── chat/
    │   ├── layout/
    │   ├── providers/
    │   └── ui/
    ├── lib/
    │   ├── auth.ts
    │   ├── utils.ts
    │   ├── db/
    │   ├── ingest/
    │   └── rag/
    └── types/
```

## Key Features

- **Book Upload & Ingestion:** Upload PDF, DOCX, and TXT files. The system extracts text, splits it into chunks, generates embeddings, and stores them in the database.
- **Website URL Ingestion:** Paste a URL, and the system will crawl, extract, and index the content.
- **Source-Grounded Q&A:** Get answers based strictly on the ingested content, with citations for every response.
- **Per-User Knowledge Base:** Each user has their own isolated library of sources and conversations.
- **Smart Chunking & Retrieval:** Recursive text splitting and efficient similarity search using pgvector.
- **Analysis & Summarization:** Generate summaries, breakdowns, and extract key themes and concepts.
- **Modern UI:** Clean, responsive, and mobile-friendly interface with dark/light mode.

## Supported Input Formats

- **Documents:** PDF (.pdf), Word (.docx), Plain Text (.txt)
- **Websites:** Static HTML pages, server-rendered sites, blogs, and documentation sites.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
