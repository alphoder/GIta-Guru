import * as cheerio from "cheerio";
import { ApifyClient } from "apify-client";

export interface ScrapedPage {
  title: string;
  content: string;
  url: string;
}

export async function scrapeUrl(url: string): Promise<ScrapedPage> {
  // Use Apify if API token is set, otherwise fall back to basic fetch
  if (process.env.APIFY_API_TOKEN) {
    return scrapeWithApify(url);
  }
  return scrapeWithFetch(url);
}

// ─── Apify Scraper (recommended) ───

async function scrapeWithApify(url: string): Promise<ScrapedPage> {
  const client = new ApifyClient({ token: process.env.APIFY_API_TOKEN });

  // Use Apify's Website Content Crawler
  const run = await client.actor("apify/website-content-crawler").call({
    startUrls: [{ url }],
    maxCrawlPages: 1,
    crawlerType: "cheerio",
    maxCrawlDepth: 0,
  });

  // Get results from the dataset
  const { items } = await client.dataset(run.defaultDatasetId).listItems();

  if (!items || items.length === 0) {
    throw new Error("Apify returned no results for this URL");
  }

  const item = items[0] as Record<string, unknown>;
  const content = (item.text as string) || (item.markdown as string) || "";
  const title = (item.metadata as Record<string, string>)?.title
    || (item.title as string)
    || new URL(url).hostname;

  return { title, content, url };
}

// ─── Basic Fetch Scraper (fallback) ───

async function scrapeWithFetch(url: string): Promise<ScrapedPage> {
  const res = await fetch(url, {
    headers: {
      "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      Accept:
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.5",
    },
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch ${url}: ${res.status} ${res.statusText}`);
  }

  const html = await res.text();
  const $ = cheerio.load(html);

  // Remove non-content elements
  $(
    "script, style, nav, footer, header, aside, iframe, noscript, svg, img, video, audio, canvas, .nav, .footer, .header, .sidebar, .menu, .ad, .advertisement, .cookie-banner, [aria-hidden='true']"
  ).remove();

  // Extract title
  const title =
    $("title").text().trim() ||
    $("h1").first().text().trim() ||
    new URL(url).hostname;

  // Try to find main content area
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

  // Fallback to body text
  if (content.length < 50) {
    content = extractText($, $("body"));
  }

  return { title, content, url };
}

function extractText($: cheerio.CheerioAPI, el: ReturnType<typeof $>): string {
  el.find("p, div, br, h1, h2, h3, h4, h5, h6, li, tr, blockquote, pre").each((_, elem) => {
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
