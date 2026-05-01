import * as cheerio from "cheerio";
import type { JobRecord } from "../data/database.js";

// fetched_at is omitted alongside the other DB-managed fields because it's set
// automatically by SQLite's DEFAULT datetime('now') — scrapers never provide it.
type RawJob = Omit<JobRecord, "fit_score" | "fit_notes" | "status" | "applied_at" | "cover_letter" | "error_msg" | "fetched_at">;

export type SearchParams = {
  query: string;          // e.g. "Senior TypeScript Engineer"
  location?: string;      // e.g. "San Francisco, CA" or "Remote"
  remote?: boolean;
  limit?: number;         // max results per source (default: 20)
};

// ─────────────────────────────────────────────
// Public entry point — aggregates all sources
// ─────────────────────────────────────────────

export async function searchJobs(params: SearchParams): Promise<RawJob[]> {
  const limit = params.limit ?? 20;

  const results = await Promise.allSettled([
    scrapeLinkedIn(params, limit),
    scrapeIndeed(params, limit),
    scrapeGreenhouseBoards(params, limit),
  ]);

  const jobs: RawJob[] = [];
  for (const r of results) {
    if (r.status === "fulfilled") jobs.push(...r.value);
    else console.error("[scraper] source failed:", r.reason);
  }

  // Deduplicate by URL
  const seen = new Set<string>();
  return jobs.filter((j) => {
    if (seen.has(j.url)) return false;
    seen.add(j.url);
    return true;
  });
}

// ─────────────────────────────────────────────
// LinkedIn Jobs (public search, no auth required)
// ─────────────────────────────────────────────

async function scrapeLinkedIn(params: SearchParams, limit: number): Promise<RawJob[]> {
  const q = encodeURIComponent(params.query);
  const loc = encodeURIComponent(params.location ?? (params.remote ? "Remote" : ""));
  const remoteFilter = params.remote ? "&f_WT=2" : "";

  // LinkedIn paginates in pages of 25; start=0 is the first page
  const url = `https://www.linkedin.com/jobs/search/?keywords=${q}&location=${loc}${remoteFilter}&start=0`;
  const html = await fetchHtml(url, {
    "User-Agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  });

  const $ = cheerio.load(html);
  const jobs: RawJob[] = [];

  $("div.base-card").each((_, el) => {
    if (jobs.length >= limit) return false; // cheerio each() respects false as break

    const title = $(el).find("h3.base-search-card__title").text().trim();
    const company = $(el).find("h4.base-search-card__subtitle a").text().trim();
    const location = $(el).find("span.job-search-card__location").text().trim();
    const href = $(el).find("a.base-card__full-link").attr("href") ?? "";
    const postedAt = $(el).find("time").attr("datetime") ?? null;
    const jobUrl = href.split("?")[0]; // strip tracking params

    if (!title || !company || !jobUrl) return;

    // Extract the LinkedIn job ID from the URL (/jobs/view/1234567890/)
    const match = jobUrl.match(/\/jobs\/view\/(\d+)/);
    const externalId = match ? match[1] : jobUrl;

    jobs.push({
      id: `linkedin:${externalId}`,
      title,
      company,
      location: location || null,
      url: jobUrl,
      description: null, // fetched lazily when user calls analyze-job
      salary_min: null,
      salary_max: null,
      remote: /remote/i.test(location) ? 1 : 0,
      source: "linkedin",
      posted_at: postedAt,
    });
  });

  return jobs;
}

// ─────────────────────────────────────────────
// Indeed (public RSS — no scraping needed)
// ─────────────────────────────────────────────

async function scrapeIndeed(params: SearchParams, limit: number): Promise<RawJob[]> {
  const q = encodeURIComponent(params.query);
  const loc = encodeURIComponent(params.location ?? (params.remote ? "Remote" : ""));
  const rssUrl = `https://www.indeed.com/rss?q=${q}&l=${loc}&sort=date&limit=${limit}`;

  const xml = await fetchHtml(rssUrl, {
    "User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0)",
    Accept: "application/rss+xml, application/xml",
  });

  const $ = cheerio.load(xml, { xmlMode: true });
  const jobs: RawJob[] = [];

  $("item").each((_, el) => {
    if (jobs.length >= limit) return false;

    const title = $(el).find("title").first().text().trim();
    const link = $(el).find("link").text().trim();
    const description = $(el).find("description").text().trim();
    const company = $(el).find("source").text().trim();
    const pubDate = $(el).find("pubDate").text().trim();

    // Indeed RSS link contains the job key, e.g. ?jk=abc123
    const jk = new URL(link).searchParams.get("jk") ?? link;

    if (!title || !link) return;

    jobs.push({
      id: `indeed:${jk}`,
      title,
      company: company || "Unknown",
      location: params.location ?? null,
      url: link,
      description: description.replace(/<[^>]+>/g, "").trim() || null,
      salary_min: null,
      salary_max: null,
      remote: /remote/i.test(title + description) ? 1 : 0,
      source: "indeed",
      posted_at: pubDate ? new Date(pubDate).toISOString() : null,
    });
  });

  return jobs;
}

// ─────────────────────────────────────────────
// Greenhouse job boards (many companies use this ATS)
// We scrape their public JSON API — no auth needed.
// ─────────────────────────────────────────────

// Sample of companies using Greenhouse — add more as needed
const GREENHOUSE_COMPANIES = [
  "anthropic", "stripe", "airbnb", "notion", "figma",
  "linear", "vercel", "planetscale", "clerk", "render",
  "fly", "supabase", "turso", "modal",
];

async function scrapeGreenhouseBoards(params: SearchParams, limit: number): Promise<RawJob[]> {
  const queryLower = params.query.toLowerCase();
  const jobs: RawJob[] = [];

  // Fetch all companies in parallel (with a concurrency cap)
  const chunks = chunk(GREENHOUSE_COMPANIES, 5);
  for (const batch of chunks) {
    if (jobs.length >= limit) break;

    const results = await Promise.allSettled(
      batch.map((company) => fetchGreenhouseJobs(company, queryLower))
    );

    for (const r of results) {
      if (r.status === "fulfilled") {
        for (const j of r.value) {
          if (jobs.length < limit) jobs.push(j);
        }
      }
    }
  }

  return jobs;
}

async function fetchGreenhouseJobs(company: string, queryLower: string): Promise<RawJob[]> {
  const url = `https://boards-api.greenhouse.io/v1/boards/${company}/jobs?content=true`;
  const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
  if (!res.ok) return [];

  const data = (await res.json()) as { jobs?: GreenhouseJob[] };
  if (!data.jobs) return [];

  return data.jobs
    .filter((j) => j.title.toLowerCase().includes(queryLower.split(" ")[0]!))
    .map((j): RawJob => {
      const salaryMatch = j.content?.match(/\$([0-9,]+)\s*[-–]\s*\$([0-9,]+)/);
      return {
        id: `greenhouse:${j.id}`,
        title: j.title,
        company: capitalize(company),
        location: j.location?.name ?? null,
        url: j.absolute_url,
        description: j.content?.replace(/<[^>]+>/g, "").trim() ?? null,
        salary_min: salaryMatch ? parseInt(salaryMatch[1]!.replace(/,/g, "")) : null,
        salary_max: salaryMatch ? parseInt(salaryMatch[2]!.replace(/,/g, "")) : null,
        remote: /remote/i.test(j.location?.name ?? "") ? 1 : 0,
        source: "greenhouse",
        posted_at: j.updated_at ?? null,
      };
    });
}

type GreenhouseJob = {
  id: number;
  title: string;
  location: { name: string } | null;
  absolute_url: string;
  content?: string;
  updated_at?: string;
};

// ─────────────────────────────────────────────
// Fetch a full job description by URL (lazy load)
// Called by the analyze-job tool
// ─────────────────────────────────────────────

export async function fetchJobDescription(url: string, source: string): Promise<string | null> {
  try {
    const html = await fetchHtml(url, {
      "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36",
    });

    const $ = cheerio.load(html);

    // Remove noise
    $("script, style, nav, header, footer, .cookie-banner, .newsletter").remove();

    if (source === "linkedin") {
      return $("div.description__text").text().trim() || $("article").text().trim();
    }
    if (source === "greenhouse") {
      return $("div#content").text().trim() || $("div.job-description").text().trim();
    }

    // Generic: grab the biggest text block
    return $("main, article, .job-description, #jobDescriptionText").first().text().trim();
  } catch {
    return null;
  }
}

// ─────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────

async function fetchHtml(url: string, headers: Record<string, string> = {}): Promise<string> {
  const res = await fetch(url, {
    headers,
    signal: AbortSignal.timeout(15000),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} fetching ${url}`);
  return res.text();
}

function chunk<T>(arr: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
