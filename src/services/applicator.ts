import { chromium, type Browser, type Page } from "playwright";

/**
 * The Applicator wraps Playwright and knows how to navigate ATS (Applicant Tracking
 * Systems) like LinkedIn Easy Apply and Greenhouse forms, filling them with the
 * user's profile data and submitting.
 *
 * IMPORTANT: This module runs a real Chromium browser. It is intentionally
 * slow and deliberate — it adds random delays between actions to avoid
 * bot-detection and never runs concurrently across multiple jobs.
 */

export type ApplicationData = {
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
  resume_path: string;
  cover_letter: string;
  linkedin_email?: string;
  linkedin_password?: string;
};

export type ApplyResult =
  | { success: true; confirmation?: string }
  | { success: false; error: string; screenshot?: string };

// ─────────────────────────────────────────────
// Public entry point
// ─────────────────────────────────────────────

export async function applyToJob(
  url: string,
  source: string,
  data: ApplicationData,
  headless = true
): Promise<ApplyResult> {
  const browser = await chromium.launch({ headless });
  try {
    const ctx = await browser.newContext({
      // Realistic viewport — helps avoid bot detection
      viewport: { width: 1440, height: 900 },
      userAgent:
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    });
    const page = await ctx.newPage();

    if (source === "linkedin") {
      return await applyLinkedIn(page, url, data);
    } else if (source === "greenhouse") {
      return await applyGreenhouse(page, url, data);
    } else {
      return await applyGeneric(page, url, data);
    }
  } catch (err) {
    return { success: false, error: String(err) };
  } finally {
    await browser.close();
  }
}

// ─────────────────────────────────────────────
// LinkedIn Easy Apply
// ─────────────────────────────────────────────

async function applyLinkedIn(
  page: Page,
  jobUrl: string,
  data: ApplicationData
): Promise<ApplyResult> {
  // Step 1: Log in if credentials provided
  if (data.linkedin_email && data.linkedin_password) {
    await page.goto("https://www.linkedin.com/login");
    await humanType(page, "#username", data.linkedin_email);
    await humanType(page, "#password", data.linkedin_password);
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ timeout: 15000 }).catch(() => {});
    await randomDelay(1500, 2500);
  }

  // Step 2: Navigate to job and find Easy Apply button
  await page.goto(jobUrl, { waitUntil: "domcontentloaded" });
  await randomDelay(1000, 2000);

  const easyApplyBtn = page.locator("button.jobs-apply-button", { hasText: "Easy Apply" }).first();
  if (!(await easyApplyBtn.isVisible({ timeout: 5000 }).catch(() => false))) {
    return { success: false, error: "No Easy Apply button found — this job may require an external application." };
  }
  await easyApplyBtn.click();
  await randomDelay(1000, 1500);

  // Step 3: Walk through the multi-step modal
  let step = 0;
  const MAX_STEPS = 12;

  while (step < MAX_STEPS) {
    step++;

    // Fill any visible text/email/tel inputs
    const inputs = page.locator("div.jobs-easy-apply-form-section input:visible");
    for (const input of await inputs.all()) {
      const label = await getInputLabel(page, input);
      const value = resolveField(label, data);
      if (value && !(await input.inputValue())) {
        await humanType(page, input, value);
      }
    }

    // Fill textareas (cover letter, additional questions)
    const textareas = page.locator("div.jobs-easy-apply-form-section textarea:visible");
    for (const ta of await textareas.all()) {
      const label = await getInputLabel(page, ta);
      const isCoverLetter = /cover|letter|motivation/i.test(label);
      if (isCoverLetter && !(await ta.inputValue())) {
        await humanType(page, ta, data.cover_letter);
      }
    }

    // Upload resume if a file input appears
    const fileInput = page.locator('input[type="file"]:visible').first();
    if (await fileInput.isVisible({ timeout: 1000 }).catch(() => false)) {
      await fileInput.setInputFiles(data.resume_path);
      await randomDelay(1000, 2000);
    }

    // Decide next action
    const submitBtn = page.locator("button[aria-label='Submit application']");
    const nextBtn = page.locator("button[aria-label='Continue to next step']");
    const reviewBtn = page.locator("button[aria-label='Review your application']");

    if (await submitBtn.isVisible({ timeout: 500 }).catch(() => false)) {
      await submitBtn.click();
      await randomDelay(2000, 3000);
      return { success: true, confirmation: "LinkedIn Easy Apply submitted successfully." };
    } else if (await reviewBtn.isVisible({ timeout: 500 }).catch(() => false)) {
      await reviewBtn.click();
    } else if (await nextBtn.isVisible({ timeout: 500 }).catch(() => false)) {
      await nextBtn.click();
    } else {
      break; // No navigation button found — likely done or stuck
    }

    await randomDelay(800, 1500);
  }

  return { success: false, error: "Could not complete LinkedIn Easy Apply flow — too many steps or unexpected modal state." };
}

// ─────────────────────────────────────────────
// Greenhouse ATS (used by hundreds of companies)
// ─────────────────────────────────────────────

async function applyGreenhouse(
  page: Page,
  jobUrl: string,
  data: ApplicationData
): Promise<ApplyResult> {
  // Greenhouse job pages have a single "Apply for this Job" button that
  // opens an application form on the same page or a /apply/ sub-URL.
  await page.goto(jobUrl, { waitUntil: "networkidle" });
  await randomDelay(1000, 2000);

  const applyBtn = page.locator("a#apply_button, a:has-text('Apply for this Job')").first();
  if (await applyBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
    await applyBtn.click();
    await page.waitForLoadState("networkidle");
    await randomDelay(1000, 1500);
  }

  // Standard Greenhouse fields
  const fieldMap: Record<string, string> = {
    "first name": data.name.split(" ")[0] ?? data.name,
    "last name": data.name.split(" ").slice(1).join(" "),
    email: data.email,
    phone: data.phone,
    location: data.location,
    linkedin: data.linkedin ?? "",
    github: data.github ?? "",
    website: data.portfolio ?? "",
    portfolio: data.portfolio ?? "",
    "cover letter": data.cover_letter,
  };

  // Fill text inputs
  const inputs = page.locator("input[type='text'], input[type='email'], input[type='tel']");
  for (const input of await inputs.all()) {
    const label = await getInputLabel(page, input);
    const key = Object.keys(fieldMap).find((k) => label.toLowerCase().includes(k));
    if (key && !(await input.inputValue())) {
      await humanType(page, input, fieldMap[key]!);
    }
  }

  // Cover letter textarea
  const coverLetterTa = page.locator("textarea").first();
  if (await coverLetterTa.isVisible({ timeout: 2000 }).catch(() => false)) {
    if (!(await coverLetterTa.inputValue())) {
      await humanType(page, coverLetterTa, data.cover_letter);
    }
  }

  // Resume upload
  const fileInput = page.locator('input[type="file"]').first();
  if (await fileInput.isVisible({ timeout: 2000 }).catch(() => false)) {
    await fileInput.setInputFiles(data.resume_path);
    await randomDelay(2000, 3000);
  }

  // Submit
  const submitBtn = page.locator("button[type='submit'], input[type='submit']").first();
  if (!(await submitBtn.isVisible({ timeout: 5000 }).catch(() => false))) {
    return { success: false, error: "Submit button not found on Greenhouse form." };
  }

  await submitBtn.click();
  await page.waitForLoadState("networkidle", { timeout: 15000 });

  // Check for confirmation
  const pageText = await page.textContent("body");
  if (/thank you|application received|submitted|confirmed/i.test(pageText ?? "")) {
    return { success: true, confirmation: "Greenhouse application submitted." };
  }

  return { success: false, error: "Application submitted but no confirmation text detected — please verify manually." };
}

// ─────────────────────────────────────────────
// Generic fallback — attempts best-effort form fill
// ─────────────────────────────────────────────

async function applyGeneric(
  page: Page,
  jobUrl: string,
  data: ApplicationData
): Promise<ApplyResult> {
  await page.goto(jobUrl, { waitUntil: "networkidle" });

  // This is a best-effort approach for ATS platforms we don't have
  // specific adapters for (Lever, Workday, BambooHR, etc.)
  return {
    success: false,
    error:
      `Generic auto-apply is not supported for this URL (${jobUrl}). ` +
      "The job has been saved to your tracker. " +
      "Open the URL in your browser and apply manually — your cover letter is saved in the database.",
  };
}

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────

/**
 * Finds the visible label text for a form control.
 * Checks: aria-label, aria-labelledby, associated <label>, placeholder.
 */
async function getInputLabel(page: Page, locator: ReturnType<Page["locator"]>): Promise<string> {
  try {
    const ariaLabel = await locator.getAttribute("aria-label");
    if (ariaLabel) return ariaLabel;

    const labelledBy = await locator.getAttribute("aria-labelledby");
    if (labelledBy) {
      const labelEl = page.locator(`#${labelledBy}`);
      const text = await labelEl.textContent();
      if (text) return text;
    }

    const id = await locator.getAttribute("id");
    if (id) {
      const labelEl = page.locator(`label[for="${id}"]`);
      const text = await labelEl.textContent();
      if (text) return text;
    }

    return (await locator.getAttribute("placeholder")) ?? "";
  } catch {
    return "";
  }
}

/** Maps a label string to a value from the ApplicationData object. */
function resolveField(label: string, data: ApplicationData): string | null {
  const l = label.toLowerCase();
  if (l.includes("first name")) return data.name.split(" ")[0] ?? data.name;
  if (l.includes("last name")) return data.name.split(" ").slice(1).join(" ");
  if (l.includes("name")) return data.name;
  if (l.includes("email")) return data.email;
  if (l.includes("phone") || l.includes("mobile")) return data.phone;
  if (l.includes("location") || l.includes("city")) return data.location;
  if (l.includes("linkedin")) return data.linkedin ?? "";
  if (l.includes("github")) return data.github ?? "";
  if (l.includes("website") || l.includes("portfolio")) return data.portfolio ?? "";
  return null;
}

/** Simulates human-like typing with small random delays. */
async function humanType(
  page: Page,
  target: string | ReturnType<Page["locator"]>,
  text: string
): Promise<void> {
  const locator = typeof target === "string" ? page.locator(target).first() : target;
  await locator.focus();
  await locator.fill(text); // fill() is faster; use type() with delay for stricter bot evasion
  await randomDelay(200, 600);
}

function randomDelay(minMs: number, maxMs: number): Promise<void> {
  const ms = minMs + Math.random() * (maxMs - minMs);
  return new Promise((r) => setTimeout(r, ms));
}
