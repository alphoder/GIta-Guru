export interface ParsedPage {
  pageNumber: number;
  content: string;
}

/**
 * Parse a PDF by sending it to the Railway pdf-parser service.
 * This keeps heavy PDF.js memory usage off the Vercel serverless function.
 */
export async function parsePdf(buffer: Buffer): Promise<{
  pages: ParsedPage[];
  pageCount: number;
  metadata: Record<string, unknown>;
}> {
  const parserUrl = process.env.PDF_PARSER_URL;
  if (!parserUrl) {
    throw new Error("PDF_PARSER_URL environment variable is not set. Deploy the pdf-parser service to Railway first.");
  }

  const formData = new FormData();
  const blob = new Blob([buffer], { type: "application/pdf" });
  formData.append("file", blob, "upload.pdf");

  const headers: Record<string, string> = {};
  if (process.env.PARSER_SECRET) {
    headers["x-parser-secret"] = process.env.PARSER_SECRET;
  }

  const res = await fetch(`${parserUrl}/parse`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: "Parser service error" }));
    throw new Error(err.error || `Parser returned ${res.status}`);
  }

  return res.json();
}
