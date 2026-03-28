// Import the lib directly to avoid pdf-parse/index.js which tries to
// read a test PDF file on import (breaks on Vercel serverless)
// eslint-disable-next-line @typescript-eslint/no-require-imports
const pdf = require("pdf-parse/lib/pdf-parse.js") as (buffer: Buffer) => Promise<{
  text: string;
  numpages: number;
  info: Record<string, string>;
}>;

export interface ParsedPage {
  pageNumber: number;
  content: string;
}

export async function parsePdf(buffer: Buffer): Promise<{
  pages: ParsedPage[];
  pageCount: number;
  metadata: Record<string, unknown>;
}> {
  // max: 20 tells pdf-parse/PDF.js to stop after 20 pages — it won't
  // load the rest of the document into memory at all.
  const data = await pdf(buffer, { max: 20 });

  // pdf-parse gives us the full text. We split by form feeds if available,
  // otherwise treat the entire content as one "page" per ~3000 chars.
  const rawPages = data.text.split(/\f/);
  const pages: ParsedPage[] = rawPages
    .map((content: string, i: number) => ({
      pageNumber: i + 1,
      content: content.trim(),
    }))
    .filter((p: ParsedPage) => p.content.length > 0);

  return {
    pages,
    pageCount: data.numpages,
    metadata: {
      title: data.info?.Title || null,
      author: data.info?.Author || null,
      subject: data.info?.Subject || null,
    },
  };
}
