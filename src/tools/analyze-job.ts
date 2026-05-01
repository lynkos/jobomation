import { z } from "zod";
import Anthropic from "@anthropic-ai/sdk";
import { getDb, logEvent } from "../data/database.js";
import { fetchJobDescription } from "../services/job-scraper.js";
import { loadProfile, loadResume } from "../services/resume.js";

export const AnalyzeJobInput = z.object({
  job_id: z.string().describe("The job ID from search_jobs (e.g. 'linkedin:3876543210')"),
});

export type AnalyzeJobInput = z.infer<typeof AnalyzeJobInput>;

const anthropic = new Anthropic();

/**
 * analyze_job — MCP Tool Handler
 *
 * 1. Fetches the full job description if not already cached.
 * 2. Sends resume + job description to Claude to get a structured fit score (0–100)
 *    and a JSON list of strengths, gaps, and a recommended approach.
 * 3. Persists the score back to the database.
 */
export async function analyzeJobHandler(input: AnalyzeJobInput): Promise<string> {
  const db = getDb();
  const profile = loadProfile();

  // Load job from DB
  const job = db.prepare("SELECT * FROM jobs WHERE id = ?").get(input.job_id) as Record<string, unknown> | undefined;
  if (!job) return `Job "${input.job_id}" not found. Run search_jobs first.`;

  // Lazily fetch full description if missing
  let description = (job.description as string | null) ?? null;
  if (!description) {
    console.error(`[analyze_job] Fetching full description for ${input.job_id}...`);
    description = await fetchJobDescription(job.url as string, job.source as string);
    if (description) {
      db.prepare("UPDATE jobs SET description = ? WHERE id = ?").run(description, input.job_id);
    }
  }

  if (!description) {
    return `Could not fetch the job description for ${input.job_id}. The URL may require login or the page structure changed.`;
  }

  // Load resume
  const resumeText = await loadResume((profile.resume_path as string) ?? "./config/resume.pdf");

  // Ask Claude to score the fit
  const prompt = `
You are a professional career coach and recruiter. Analyze how well this candidate fits the job.

## Job Listing
Title: ${job.title}
Company: ${job.company}
Location: ${job.location ?? "Not specified"}
Description:
${description.slice(0, 4000)}

## Candidate Resume
${resumeText.slice(0, 3000)}

## Candidate Profile
Skills: ${(profile.skills as string[]).join(", ")}
Experience: ${profile.experience_years} years
Target salary: $${profile.target && (profile.target as Record<string, unknown>).min_salary}–$${profile.target && (profile.target as Record<string, unknown>).max_salary}

## Task
Respond ONLY with a valid JSON object (no markdown fences) matching this shape:
{
  "score": <0-100 integer>,
  "verdict": "<Strong Match | Good Match | Weak Match | Poor Match>",
  "strengths": ["<reason1>", "<reason2>", ...],
  "gaps": ["<gap1>", "<gap2>", ...],
  "salary_match": <true|false|null if unknown>,
  "recommendation": "<one sentence on whether and how to apply>"
}
`.trim();

  const response = await anthropic.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 512,
    messages: [{ role: "user", content: prompt }],
  });

  const raw = response.content.find((b) => b.type === "text")?.text ?? "{}";

  let analysis: {
    score: number;
    verdict: string;
    strengths: string[];
    gaps: string[];
    salary_match: boolean | null;
    recommendation: string;
  };

  try {
    analysis = JSON.parse(raw);
  } catch {
    return `Claude returned an unparseable analysis. Raw response:\n${raw}`;
  }

  // Persist to DB
  const fitScore = analysis.score / 100;
  db.prepare("UPDATE jobs SET fit_score = ?, fit_notes = ? WHERE id = ?").run(
    fitScore,
    JSON.stringify({ strengths: analysis.strengths, gaps: analysis.gaps, recommendation: analysis.recommendation }),
    input.job_id
  );
  logEvent(db, input.job_id, "scored", `Score: ${analysis.score}/100 — ${analysis.verdict}`);

  // Format human-readable output
  const scoreBar = buildScoreBar(analysis.score);
  const salaryTag = analysis.salary_match === true ? "✅ In range" : analysis.salary_match === false ? "❌ Out of range" : "❓ Unknown";

  return [
    `## ${job.title} @ ${job.company}`,
    `${scoreBar}  ${analysis.score}/100 — **${analysis.verdict}**`,
    `Salary: ${salaryTag}`,
    "",
    "**Strengths**",
    analysis.strengths.map((s) => `  • ${s}`).join("\n"),
    "",
    "**Gaps**",
    analysis.gaps.length ? analysis.gaps.map((g) => `  • ${g}`).join("\n") : "  • None identified",
    "",
    `**Recommendation:** ${analysis.recommendation}`,
    "",
    `Next: Run apply_to_job ${input.job_id} to generate a cover letter and apply.`,
  ].join("\n");
}

/** Builds a simple ASCII progress bar for the score, e.g. [████████░░] */
function buildScoreBar(score: number): string {
  const filled = Math.round(score / 10);
  return `[${"█".repeat(filled)}${"░".repeat(10 - filled)}]`;
}
