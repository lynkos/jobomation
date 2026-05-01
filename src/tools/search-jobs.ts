import { z } from "zod";
import { getDb, upsertJob, logEvent } from "../data/database.js";
import { searchJobs } from "../services/job-scraper.js";
import { loadProfile } from "../services/resume.js";

// The input schema that OpenCode (via MCP) will validate against
export const SearchJobsInput = z.object({
  query: z.string().describe("Job title or keywords, e.g. 'Senior TypeScript Engineer'"),
  location: z.string().optional().describe("City/state or 'Remote'. Defaults to profile location."),
  remote: z.boolean().optional().describe("Filter for remote-only jobs"),
  limit: z.number().int().min(1).max(50).default(20).describe("Max jobs to return per source"),
});

export type SearchJobsInput = z.infer<typeof SearchJobsInput>;

/**
 * search_jobs — MCP Tool Handler
 *
 * Hits LinkedIn, Indeed, and Greenhouse in parallel, deduplicates results,
 * persists them to the local SQLite database, and returns a summary table.
 *
 * The jobs are stored with status="new" so the user can later run
 * analyze_jobs to score them against their resume, or apply_to_job to apply.
 */
export async function searchJobsHandler(input: SearchJobsInput): Promise<string> {
  const profile = loadProfile();
  const db = getDb();

  const params = {
    query: input.query,
    // profile.target.locations is unknown at this point (loadProfile returns a generic object),
    // so we narrow it explicitly: check it's an array, then take the first element if it's a string.
    location: input.location ?? (() => {
      const locs = (profile.target as Record<string, unknown>)?.locations;
      return Array.isArray(locs) && typeof locs[0] === "string" ? locs[0] : undefined;
    })(),
    remote: input.remote,
    limit: input.limit,
  };

  console.error(`[search_jobs] Searching: "${params.query}" in ${params.location ?? "any location"}`);

  const jobs = await searchJobs(params);

  if (jobs.length === 0) {
    return "No jobs found. Try a different query or broader location.";
  }

  // Persist to DB
  for (const job of jobs) {
    upsertJob(db, job);
    logEvent(db, job.id, "searched", `Found via ${job.source}`);
  }

  // Format a readable summary table
  const rows = jobs.slice(0, 25).map((j) => {
    const salary = j.salary_min
      ? `$${(j.salary_min / 1000).toFixed(0)}k–$${(j.salary_max! / 1000).toFixed(0)}k`
      : "—";
    const remote = j.remote ? "🌐" : "🏢";
    return `${remote} [${j.id}]\n  ${j.title} @ ${j.company}\n  ${j.location ?? "Location not listed"} | ${salary} | ${j.source}\n  ${j.url}`;
  });

  return [
    `Found ${jobs.length} jobs (showing first ${Math.min(jobs.length, 25)}). All saved to database.`,
    "",
    rows.join("\n\n"),
    "",
    "Next steps:",
    "  • Run analyze_job <job_id>    — score fit & fetch full description",
    "  • Run analyze_all_jobs        — score all new jobs at once",
    "  • Run apply_to_job <job_id>   — generate cover letter & apply",
  ].join("\n");
}
