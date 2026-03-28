import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { db } from "@/lib/db";
import { sources } from "@/lib/db/schema";
import { parsePdf } from "@/lib/ingest/pdf-loader";
import { parseTxt } from "@/lib/ingest/txt-loader";
import { parseDocx } from "@/lib/ingest/docx-loader";
import { chunkText } from "@/lib/rag/chunking";
import { parallelIngest } from "@/lib/rag/parallel-ingest";
import { eq } from "drizzle-orm";

export const maxDuration = 60;
export const runtime = "nodejs";

// PDF.js (used by pdf-parse) expands PDFs ~10-50x in memory.
// Keep PDF limit low to stay within Vercel's 1GB serverless limit.
const PDF_SIZE_LIMIT = 2 * 1024 * 1024; // 2 MB
const OTHER_SIZE_LIMIT = 10 * 1024 * 1024; // 10 MB
const MAX_CHUNKS = 100;
const MAX_PDF_PAGES = 30;

export async function POST(request: Request) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let sourceId: string | null = null;

  try {
    // Parse multipart form data
    let file: File | null = null;
    try {
      const formData = await request.formData();
      file = formData.get("file") as File | null;
    } catch {
      return NextResponse.json(
        { error: "Could not read file. Make sure it is under the size limit." },
        { status: 400 }
      );
    }

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    // Determine file type
    const name = file.name.toLowerCase();
    let type: "pdf" | "txt" | "docx";
    if (name.endsWith(".pdf")) type = "pdf";
    else if (name.endsWith(".txt")) type = "txt";
    else if (name.endsWith(".docx")) type = "docx";
    else {
      return NextResponse.json(
        { error: "Unsupported file type. Use PDF, TXT, or DOCX." },
        { status: 400 }
      );
    }

    // Per-type size limits
    const sizeLimit = type === "pdf" ? PDF_SIZE_LIMIT : OTHER_SIZE_LIMIT;
    if (file.size > sizeLimit) {
      const limitMB = sizeLimit / 1024 / 1024;
      return NextResponse.json(
        { error: `PDF files must be under ${limitMB}MB. For larger books, use a TXT or DOCX export.` },
        { status: 400 }
      );
    }

    // Read file into buffer
    let buffer: Buffer | null = Buffer.from(await file.arrayBuffer());

    // Create source record
    const [source] = await db
      .insert(sources)
      .values({
        userId: session.user.id,
        title: file.name.replace(/\.[^/.]+$/, ""),
        type,
        fileSize: buffer.length,
        status: "processing",
      })
      .returning({ id: sources.id });

    sourceId = source.id;

    // Parse file and collect chunks
    let allChunks: ReturnType<typeof chunkText> = [];
    let pageCount: number | null = null;
    let metadata: Record<string, unknown> = {};

    if (type === "pdf") {
      const parsed = await parsePdf(buffer);
      pageCount = parsed.pageCount;
      metadata = parsed.metadata;
      // Release buffer immediately after parsing
      buffer = null;
      for (const page of parsed.pages.slice(0, MAX_PDF_PAGES)) {
        if (allChunks.length >= MAX_CHUNKS) break;
        allChunks.push(...chunkText(page.content, { pageNumber: page.pageNumber }));
      }
    } else if (type === "txt") {
      const text = buffer.toString("utf-8");
      buffer = null;
      const parsed = parseTxt(text);
      for (const section of parsed.sections) {
        if (allChunks.length >= MAX_CHUNKS) break;
        allChunks.push(...chunkText(section.content));
      }
    } else if (type === "docx") {
      const parsed = await parseDocx(buffer);
      buffer = null;
      metadata = parsed.metadata;
      allChunks = chunkText(parsed.text);
    }

    if (allChunks.length === 0) {
      await db
        .update(sources)
        .set({ status: "failed" })
        .where(eq(sources.id, sourceId));
      return NextResponse.json(
        { error: "No content could be extracted from the file" },
        { status: 400 }
      );
    }

    // Re-index and cap
    allChunks = allChunks.slice(0, MAX_CHUNKS).map((c, i) => ({ ...c, index: i }));

    // Embed and insert in small sequential batches (avoids holding all vectors in memory)
    await parallelIngest(sourceId, allChunks);

    // Update source to ready
    await db
      .update(sources)
      .set({
        status: "ready",
        pageCount,
        metadata,
        updatedAt: new Date(),
      })
      .where(eq(sources.id, sourceId));

    return NextResponse.json({ sourceId });
  } catch (err) {
    console.error("Upload error:", err);

    if (sourceId) {
      await db
        .update(sources)
        .set({ status: "failed" })
        .where(eq(sources.id, sourceId))
        .catch(() => {});
    }

    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Upload failed" },
      { status: 500 }
    );
  }
}
