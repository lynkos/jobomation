import fs from "fs";
import path from "path";
import pdfParse from "pdf-parse";

/**
 * Loads the user's resume from disk and returns it as plain text.
 * Supports .pdf and .txt/.md files.
 * The text is used by the scoring and cover-letter tools as context for Claude.
 */
export async function loadResume(resumePath: string): Promise<string> {
  const absPath = path.resolve(resumePath);

  if (!fs.existsSync(absPath)) {
    throw new Error(
      `Resume not found at "${absPath}". ` +
        `Update resume_path in config/profile.json to point to your resume file.`
    );
  }

  const ext = path.extname(absPath).toLowerCase();

  if (ext === ".pdf") {
    const buffer = fs.readFileSync(absPath);
    const parsed = await pdfParse(buffer);
    return parsed.text.trim();
  }

  // Treat everything else (txt, md, rtf) as raw text
  return fs.readFileSync(absPath, "utf-8").trim();
}

/**
 * Loads and validates the user profile from config/profile.json.
 * Returns the raw object; callers can destructure what they need.
 */
export function loadProfile(profilePath = "./config/profile.json") {
  const absPath = path.resolve(profilePath);
  if (!fs.existsSync(absPath)) {
    throw new Error(`Profile not found at "${absPath}". Copy config/profile.json and fill in your details.`);
  }
  const raw = fs.readFileSync(absPath, "utf-8");
  return JSON.parse(raw) as Record<string, unknown>;
}
