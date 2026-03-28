import * as cheerio from "cheerio";
import { ApifyClient } from "apify-client";

export interface ScrapedPage {
  title: string;
  content: string;
  url: string;
}

export class ScrapeError extends Error {
  public readonly reason: string;
  constructor(reason: string, url: string) {
    super(`Failed to scrape ${url}: ${reason}`);
    this.reason = reason;
  }
}

export async function scrapeUrl(url: string): Promise<ScrapedPage> {
  // 1. Validate the URL is reachable before doing anything heavy
  await checkUrlReachable(url);

  // 2. Try Apify first if available, then fall back to fetch
  if (process.env.APIFY_API_TOKEN) {
    try {
      return await scrapeWithApify(url);
    } catch {
      // Apify failed — fall back to basic fetch
      return await scrapeWithFetch(url);
    }
  }

  return scrapeWithFetch(url);
}

// ─── Reachability Check ───

async function checkUrlReachable(url: string): Promise<void> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    const res = await fetch(url, {
      method: "HEAD",
      signal: controller.signal,
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      },
      redirect: "follow",
    });

    clearTimeout(timeout);

    if (!res.ok) {
      const reasons: Record<number, string> = {
        401: "This site requires authentication.",
        403: "This site is blocking access.",
        404: "Page not found. Check the URL and try again.",
        429: "Too many requests. Try again later.",
        500: "The website's server is having issues.",
        502: "The website's server is unreachable.",
        503: "The website is temporarily unavailable.",
      };
      throw new ScrapeError(
        reasons[res.status] || `Site returned HTTP ${res.status}.`,
        url
      );
    }

    // Check content type — skip non-HTML
    const contentType = res.headers.get("content-type") || "";
    if (
      contentType &&
      !contentType.includes("text/html") &&
      !contentType.includes("application/xhtml")
    ) {
      throw new ScrapeError(
        `This URL points to a ${contentType.split(";")[0]} file, not a web page. Upload it as a file instead.`,
        url
      );
    }
  } catch (err) {
    if (err instanceof ScrapeError) throw err;

    const message = err instanceof Error ? err.message : String(err);

    if (message.includes("abort") || message.includes("AbortError")) {
      throw new ScrapeError(
        "The website took too long to respond (10s timeout).",
        url
      );
    }
    if (message.includes("ENOTFOUND") || message.includes("getaddrinfo")) {
      throw new ScrapeError(
        "Domain not found. Check the URL for typos.",
        url
      );
    }
    if (message.includes("ECONNREFUSED")) {
      throw new ScrapeError(
        "Connection refused. The site may be down.",
        url
      );
    }
    if (message.includes("CERT") || message.includes("SSL")) {
      throw new ScrapeError(
        "SSL certificate error. The site's security certificate is invalid.",
        url
      );
    }

    throw new ScrapeError(
      `Could not reach this URL: ${message}`,
      url
    );
  }
}

// ─── Apify Scraper ───

async function scrapeWithApify(url: string): Promise<ScrapedPage> {
  const client = new ApifyClient({ token: process.env.APIFY_API_TOKEN });

  const run = await client.actor("apify/website-content-crawler").call({
    startUrls: [{ url }],
    maxCrawlPages: 1,
    crawlerType: "cheerio",
    maxCrawlDepth: 0,
  });

  const { items } = await client.dataset(run.defaultDatasetId).listItems();

  if (!items || items.length === 0) {
    throw new ScrapeError("Crawler returned no results.", url);
  }

  const item = items[0] as Record<string, unknown>;
  const content = (item.text as string) || (item.markdown as string) || "";
  const title =
    (item.metadata as Record<string, string>)?.title ||
    (item.title as string) ||
    new URL(url).hostname;

  if (!content || content.length < 20) {
    throw new ScrapeError(
      "The page exists but has no extractable text content (may be an image-heavy or JS-only site).",
      url
    );
  }

  return { title, content, url };
}

// ─── Basic Fetch Scraper ───

async function scrapeWithFetch(url: string): Promise<ScrapedPage> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  const res = await fetch(url, {
    signal: controller.signal,
    headers: {
      "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      Accept:
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.5",
    },
  });

  clearTimeout(timeout);

  if (!res.ok) {
    throw new ScrapeError(`Site returned HTTP ${res.status}.`, url);
  }

  const html = await res.text();

  if (!html || html.length < 100) {
    throw new ScrapeError("The page returned empty or minimal HTML.", url);
  }

  const $ = cheerio.load(html);

  // Remove non-content elements
  $(
    "script, style, nav, footer, header, aside, iframe, noscript, svg, img, video, audio, canvas, .nav, .footer, .header, .sidebar, .menu, .ad, .advertisement, .cookie-banner, [aria-hidden='true']"
  ).remove();

  const title =
    $("title").text().trim() ||
    $("h1").first().text().trim() ||
    new URL(url).hostname;

  const mainSelectors = [
    "main",
    "article",
    "[role='main']",
    ".content",
    ".post-content",
    ".article-content",
    ".article-body",
    ".entry-content",
    ".post-body",
    ".page-content",
    "#content",
    "#main",
    "#article",
    ".prose",
    ".markdown-body",
  ];

  let content = "";
  for (const selector of mainSelectors) {
    const el = $(selector);
    if (el.length > 0) {
      content = extractText($, el);
      if (content.length > 50) break;
    }
  }

  if (content.length < 50) {
    content = extractText($, $("body"));
  }

  if (content.length < 20) {
    throw new ScrapeError(
      "Could not extract meaningful text. The site may rely heavily on JavaScript to render content.",
      url
    );
  }

  return { title, content, url };
}

function extractText(
  $: cheerio.CheerioAPI,
  el: ReturnType<typeof $>
): string {
  el.find(
    "p, div, br, h1, h2, h3, h4, h5, h6, li, tr, blockquote, pre"
  ).each((_, elem) => {
    $(elem).prepend("\n");
    $(elem).append("\n");
  });

  let text = el.text();

  text = text
    .split("\n")
    .map((line) => line.replace(/\s+/g, " ").trim())
    .filter((line) => line.length > 0)
    .join("\n");

  text = text.replace(/\n{3,}/g, "\n\n");

  return text.trim();
}
