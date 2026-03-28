import { db } from "@/lib/db";
import { chunks } from "@/lib/db/schema";
import { generateEmbeddings } from "./embeddings";
import type { Chunk } from "./chunking";

/**
 * Embed and insert chunks in small batches sequentially.
 * Each batch is embedded, inserted, then discarded from memory.
 * This avoids accumulating all embeddings in memory at once.
 */
export async function parallelIngest(
  sourceId: string,
  allChunks: Chunk[]
): Promise<void> {
  if (allChunks.length === 0) return;

  const batchSize = 10;

  for (let i = 0; i < allChunks.length; i += batchSize) {
    const batch = allChunks.slice(i, i + batchSize);
    const texts = batch.map((c) => c.content);
    const embeddings = await generateEmbeddings(texts);

    const rows = batch.map((c, j) => ({
      sourceId,
      content: c.content,
      embedding: embeddings[j],
      pageNumber: c.pageNumber,
      chapter: c.chapter,
      section: c.section,
      chunkIndex: c.index,
      url: c.url,
    }));

    await db.insert(chunks).values(rows);
  }
}
