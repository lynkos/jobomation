import { z } from "zod";
import { getDb } from "../data/database.js";
import type { JobRecord } from "../data/database.js";

export const ListApplicationsInput = z.object({
  status: z
    .enum(["all", "new", "queued", "applied", "skipped", "failed"])
    .default("all")
    .describe("Filter by application status"),
  min_score: z
    .number()
    .min(0)
    .max(1)
    .optional()
    .describe("Only show jobs with fit_score >= this value (0.0–1.0)"),
  limit: z.number().int().default(30).describe("Max rows to show"),
});

export type ListApplicationsInput = z.infer<typeof ListApplicationsInput>;

/**
 * list_applications — MCP Tool Handler
 *
 * Displays the local job tracker as a formatted report.
 * Shows score, status, company, title, and application date for each job.
 * Useful for reviewing your pipeline and deciding what to apply to next.
 */
export async function listApplicationsHandler(input: ListApplicationsInput): Promise<string> {
  const db = getDb();

  const conditions: string[] = [];
  // node:sqlite's .all() requires SQLInputValue[] — the union of types SQLite can
  // actually store: string, number, bigint, Uint8Array (BLOBs), or null.
  // Using unknown[] would let us accidentally pass an object or array, which SQLite
  // can't bind, so narrowing the type here catches that class of bug at compile time.
  const params: (string | number | bigint | Uint8Array | null)[] = [];

  if (input.status !== "all") {
    conditions.push("status = ?");
    params.push(input.status);
  }
  if (input.min_score !== undefined) {
    conditions.push("fit_score >= ?");
    params.push(input.min_score);
  }

  const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";
  const jobs = db
    .prepare(`SELECT * FROM jobs ${where} ORDER BY fit_score DESC, fetched_at DESC LIMIT ?`)
    .all(...params, input.limit) as JobRecord[];

  if (jobs.length === 0) {
    return "No jobs found matching the filter. Try search_jobs to populate the tracker.";
  }

  // Summary stats
  const stats = db
    .prepare(
      `SELECT
        COUNT(*) as total,
        SUM(CASE WHEN status='applied' THEN 1 ELSE 0 END) as applied,
        SUM(CASE WHEN status='new' THEN 1 ELSE 0 END) as new_count,
        SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
        AVG(fit_score) as avg_score
      FROM jobs`
    )
    .get() as { total: number; applied: number; new_count: number; failed: number; avg_score: number };

  const statLine = `Total: ${stats.total} | Applied: ${stats.applied} | New: ${stats.new_count} | Failed: ${stats.failed} | Avg score: ${stats.avg_score ? (stats.avg_score * 100).toFixed(0) : "—"}`;

  const rows = jobs.map((j) => {
    const score = j.fit_score !== null ? `${(j.fit_score * 100).toFixed(0).padStart(3)}%` : " — ";
    const statusIcon: Record<string, string> = {
      new: "🆕",
      queued: "⏳",
      applied: "✅",
      skipped: "⏭️",
      failed: "❌",
    };
    const icon = statusIcon[j.status] ?? "❓";
    const date = j.applied_at ?? j.fetched_at?.slice(0, 10) ?? "?";
    return `${icon} [${score}] ${j.title.padEnd(35)} @ ${j.company.padEnd(20)} | ${date} | ${j.id}`;
  });

  return [
    `## Job Application Tracker`,
    statLine,
    "─".repeat(80),
    rows.join("\n"),
    "",
    "Commands:",
    "  analyze_job <job_id>   — score a specific job",
    "  apply_to_job <job_id>  — apply to a specific job",
    "  apply_to_job <job_id> dry_run=true  — preview cover letter only",
  ].join("\n");
}
