import { z } from "zod";
import Anthropic from "@anthropic-ai/sdk";
import { getDb, logEvent } from "../data/database.js";
import { loadProfile, loadResume } from "../services/resume.js";
import { applyToJob } from "../services/applicator.js";
import type { ApplicationData } from "../services/applicator.js";

export const ApplyToJobInput = z.object({
  job_id: z.string().describe("Job ID from search_jobs (e.g. 'linkedin:3876543210')"),
  dry_run: z
    .boolean()
    .default(false)
    .describe("If true, generates the cover letter but does NOT submit the application"),
  headless: z
    .boolean()
    .default(true)
    .describe("If false, opens a visible browser window so you can watch the automation"),
});

export type ApplyToJobInput = z.infer<typeof ApplyToJobInput>;

const anthropic = new Anthropic();

/**
 * apply_to_job — MCP Tool Handler
 *
 * Phase 1 — Cover Letter Generation
 *   Uses Claude to write a tailored, specific cover letter grounded in the
 *   job description and resume. The letter avoids generic filler and instead
 *   references concrete skills and experiences that map to the role.
 *
 * Phase 2 — Browser Automation
 *   Launches Playwright (Chromium), navigates to the job URL, and fills in
 *   all form fields using the user's profile. Supports LinkedIn Easy Apply
 *   and Greenhouse ATS natively.
 *
 * Phase 3 — Tracking
 *   Persists the application outcome (applied / failed) to the local database
 *   and logs every step for auditability.
 */
export async function applyToJobHandler(input: ApplyToJobInput): Promise<string> {
  const db = getDb();
  const profile = loadProfile();

  // ── Load job from database ──────────────────────────────────────────────
  const job = db.prepare("SELECT * FROM jobs WHERE id = ?").get(input.job_id) as
    | Record<string, unknown>
    | undefined;

  if (!job) return `Job "${input.job_id}" not found. Run search_jobs first.`;
  if (job.status === "applied") {
    return `You already applied to ${job.title} @ ${job.company} on ${job.applied_at}. Skipping.`;
  }

  // ── Phase 1: Generate tailored cover letter ─────────────────────────────
  console.error(`[apply_to_job] Generating cover letter for ${input.job_id}...`);

  const resumeText = await loadResume((profile.resume_path as string) ?? "./config/resume.pdf");
  const description = (job.description as string | null) ?? "Description not available.";

  const coverLetter = await generateCoverLetter({
    jobTitle: job.title as string,
    company: job.company as string,
    description: description.slice(0, 5000),
    resumeText: resumeText.slice(0, 3000),
    profileSummary: profile.summary as string,
    name: profile.name as string,
    email: profile.email as string,
  });

  // Save cover letter to DB immediately (before applying) so it's never lost
  db.prepare("UPDATE jobs SET cover_letter = ?, status = 'queued' WHERE id = ?").run(
    coverLetter,
    input.job_id
  );
  logEvent(db, input.job_id, "cover_letter", "Generated tailored cover letter");

  if (input.dry_run) {
    return [
      `## Cover Letter (Dry Run — Not Submitted)`,
      `**Job:** ${job.title} @ ${job.company}`,
      `**URL:** ${job.url}`,
      "",
      coverLetter,
      "",
      "To actually apply, run: apply_to_job " + input.job_id,
    ].join("\n");
  }

  // ── Phase 2: Auto-apply via Playwright ─────────────────────────────────
  console.error(`[apply_to_job] Starting browser automation...`);

  const linkedInCreds = profile.linkedin_credentials as Record<string, string> | undefined;
  const appData: ApplicationData = {
    name: profile.name as string,
    email: profile.email as string,
    phone: profile.phone as string,
    location: profile.location as string,
    linkedin: profile.linkedin as string | undefined,
    github: profile.github as string | undefined,
    portfolio: profile.portfolio as string | undefined,
    resume_path: profile.resume_path as string,
    cover_letter: coverLetter,
    linkedin_email: linkedInCreds?.email,
    linkedin_password: linkedInCreds?.password,
  };

  const result = await applyToJob(
    job.url as string,
    job.source as string,
    appData,
    input.headless
  );

  // ── Phase 3: Persist outcome ────────────────────────────────────────────
  if (result.success) {
    db.prepare(
      "UPDATE jobs SET status = 'applied', applied_at = datetime('now'), error_msg = NULL WHERE id = ?"
    ).run(input.job_id);
    logEvent(db, input.job_id, "applied", result.confirmation);

    return [
      `✅ **Application submitted!**`,
      `  Job: ${job.title} @ ${job.company}`,
      `  Source: ${job.source}`,
      result.confirmation ? `  Confirmation: ${result.confirmation}` : "",
      "",
      `Your cover letter has been saved. Run list_applications to see your tracker.`,
    ]
      .filter(Boolean)
      .join("\n");
  } else {
    db.prepare(
      "UPDATE jobs SET status = 'failed', error_msg = ? WHERE id = ?"
    ).run(result.error, input.job_id);
    logEvent(db, input.job_id, "error", result.error);

    return [
      `❌ **Application failed**`,
      `  Job: ${job.title} @ ${job.company}`,
      `  Error: ${result.error}`,
      "",
      "Your cover letter was generated and saved. You can apply manually:",
      `  URL: ${job.url}`,
      "",
      "Cover letter:",
      coverLetter,
    ].join("\n");
  }
}

// ─────────────────────────────────────────────
// Cover letter generation
// ─────────────────────────────────────────────

type CoverLetterParams = {
  jobTitle: string;
  company: string;
  description: string;
  resumeText: string;
  profileSummary: string;
  name: string;
  email: string;
};

async function generateCoverLetter(p: CoverLetterParams): Promise<string> {
  const prompt = `
You are an expert career coach helping write highly personalized cover letters.

Write a cover letter for the following job. Requirements:
- 3–4 short paragraphs, conversational but professional tone
- DO NOT use generic filler phrases like "I am excited to apply" or "I am a quick learner"
- Instead, reference SPECIFIC technologies, responsibilities, or company details from the job description
- Connect the candidate's concrete experience to 2–3 of the job's key requirements
- Close with a confident, direct call to action
- Do NOT include "Dear Hiring Manager" header or date/address blocks — just the body paragraphs
- Plain text only, no markdown

Job Title: ${p.jobTitle}
Company: ${p.company}

Job Description:
${p.description}

Candidate Resume:
${p.resumeText}

Candidate Summary:
${p.profileSummary}
`.trim();

  const response = await anthropic.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 700,
    messages: [{ role: "user", content: prompt }],
  });

  return response.content.find((b) => b.type === "text")?.text?.trim() ?? "";
}
