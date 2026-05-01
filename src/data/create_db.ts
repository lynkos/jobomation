import Database from "better-sqlite3";

const DATABASE_PATH = "db/jobs.db";
const CACHE_SIZE = 32000;

const OPTIONS = {
    verbose: console.log,
    readonly: false,
    timeout: 5000
};

function createDatabase(db_path = DATABASE_PATH, options = OPTIONS) {
    let db = new Database(db_path, options);

    db.pragma("journal_mode = WAL");
    db.pragma(`cache_size = ${CACHE_SIZE}`);

    db.exec(`
        CREATE TABLE IF NOT EXISTS jobs (
            id           TEXT PRIMARY KEY,          -- Unique job ID (source:externalId)
            title        TEXT NOT NULL,
            company      TEXT NOT NULL,
            location     TEXT,
            url          TEXT NOT NULL,
            description  TEXT,
            salary_min   REAL,
            salary_max   REAL,
            remote       BOOLEAN DEFAULT FALSE CHECK (remote IN (FALSE, TRUE)),
            source       TEXT,                      -- "linkedin" | "indeed" | "greenhouse" etc.
            posted_at    TEXT,
            fetched_at   TEXT DEFAULT (datetime('now')),

            -- Scoring
            fit_score    REAL,                      -- 0.0 - 1.0, null = not yet scored
            fit_notes    TEXT,                      -- JSON array of reasons

            -- Application state
            status       TEXT DEFAULT 'new',        -- "new" | "queued" | "applied" | "skipped" | "failed"
            applied_at   TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_jobs_status    ON jobs(status);
        CREATE INDEX IF NOT EXISTS idx_jobs_source    ON jobs(source);
        CREATE INDEX IF NOT EXISTS idx_jobs_fit_score ON jobs(fit_score DESC);
    `);

    return db;
}

const db = createDatabase();