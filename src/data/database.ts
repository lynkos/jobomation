// node:sqlite ships inside Node itself since v22 — no native compilation needed.
import { DatabaseSync } from "node:sqlite";
import fs from "fs";
import path from "path";

const DB_PATH = "./db/jobs.db";

let _db: DatabaseSync | null = null;

export function getDb(): DatabaseSync {
  if (_db) return _db;

  // Ensure the data directory exists (sync this time — getDb() is called before any await)
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });

  _db = new DatabaseSync(DB_PATH);
  // node:sqlite has no .pragma() shorthand, but PRAGMA is just regular SQL
  _db.exec("PRAGMA journal_mode = WAL"); // Better concurrent read performance

  // --- Schema ---
  _db.exec(`
    CREATE TABLE IF NOT EXISTS jobs (
      id          TEXT PRIMARY KEY,          -- Unique job ID (source:externalId)
      title       TEXT NOT NULL,
      company     TEXT NOT NULL,
      location    TEXT,
      url         TEXT NOT NULL,
      description TEXT,
      salary_min  INTEGER,
      salary_max  INTEGER,
      remote      INTEGER DEFAULT 0,         -- boolean
      source      TEXT NOT NULL,             -- "linkedin" | "indeed" | "greenhouse" etc.
      posted_at   TEXT,
      fetched_at  TEXT DEFAULT (datetime('now')),

      -- Scoring
      fit_score   REAL,                      -- 0.0–1.0, null = not yet scored
      fit_notes   TEXT,                      -- JSON array of reasons

      -- Application state
      status      TEXT DEFAULT 'new',        -- new | queued | applied | skipped | failed
      applied_at  TEXT,
      cover_letter TEXT,
      error_msg   TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_jobs_status    ON jobs(status);
    CREATE INDEX IF NOT EXISTS idx_jobs_source    ON jobs(source);
    CREATE INDEX IF NOT EXISTS idx_jobs_fit_score ON jobs(fit_score DESC);

    -- Human-readable application log for debugging and auditing
    CREATE TABLE IF NOT EXISTS application_log (
      id         INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id     TEXT NOT NULL REFERENCES jobs(id),
      event      TEXT NOT NULL,   -- "searched" | "scored" | "cover_letter" | "applied" | "error"
      message    TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );
  `);

  return _db;
}

// --- Convenience helpers ---

export type JobRecord = {
  id: string;
  title: string;
  company: string;
  location: string | null;
  url: string;
  description: string | null;
  salary_min: number | null;
  salary_max: number | null;
  remote: number;
  source: string;
  posted_at: string | null;
  fetched_at: string | null;   // set automatically by SQLite DEFAULT datetime('now')
  fit_score: number | null;
  fit_notes: string | null;
  status: string;
  applied_at: string | null;
  cover_letter: string | null;
  error_msg: string | null;
};

export function upsertJob(db: DatabaseSync, job: Omit<JobRecord, "fit_score" | "fit_notes" | "status" | "applied_at" | "cover_letter" | "error_msg" | "fetched_at">): void {
  db.prepare(`
    INSERT INTO jobs (id, title, company, location, url, description, salary_min, salary_max, remote, source, posted_at)
    VALUES (@id, @title, @company, @location, @url, @description, @salary_min, @salary_max, @remote, @source, @posted_at)
    ON CONFLICT(id) DO UPDATE SET
      title       = excluded.title,
      description = excluded.description,
      salary_min  = excluded.salary_min,
      salary_max  = excluded.salary_max,
      remote      = excluded.remote,
      fetched_at  = datetime('now')
  `).run(job);
}

export function logEvent(db: DatabaseSync, jobId: string, event: string, message?: string): void {
  db.prepare(`INSERT INTO application_log (job_id, event, message) VALUES (?, ?, ?)`).run(jobId, event, message ?? null);
}
