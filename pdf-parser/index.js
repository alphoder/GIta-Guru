const express = require("express");
const multer = require("multer");
const cors = require("cors");

// Import pdf-parse lib directly (avoids test-file crash on cold start)
const pdf = require("pdf-parse/lib/pdf-parse.js");

const app = express();
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 20 * 1024 * 1024 } });

app.use(cors());
app.use(express.json());

// Health check
app.get("/", (req, res) => {
  res.json({ status: "ok", service: "pdf-parser" });
});

// Parse PDF — returns plain text split by page
app.post("/parse", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "No file provided" });
    }

    const secret = process.env.PARSER_SECRET;
    if (secret && req.headers["x-parser-secret"] !== secret) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    const data = await pdf(req.file.buffer, { max: 30 });

    const rawPages = data.text.split(/\f/);
    const pages = rawPages
      .map((content, i) => ({ pageNumber: i + 1, content: content.trim() }))
      .filter((p) => p.content.length > 0);

    return res.json({
      pages,
      pageCount: data.numpages,
      metadata: {
        title: data.info?.Title || null,
        author: data.info?.Author || null,
        subject: data.info?.Subject || null,
      },
    });
  } catch (err) {
    console.error("Parse error:", err);
    return res.status(500).json({ error: err.message || "Failed to parse PDF" });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`pdf-parser listening on port ${PORT}`);
});
