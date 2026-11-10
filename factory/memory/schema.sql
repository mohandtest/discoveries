-- Algorithm-factory operational memory (SQLite; the FTS5 table is
-- created by memory.py when FTS5 is available).
--
-- Factory law encoded here:
--   * observations / hypotheses / conclusions / decisions / lessons are
--     DISTINCT kinds — a failed benchmark can never become a verified
--     algorithmic fact through repeated agent summaries;
--   * corrections supersede rows (nothing is rewritten);
--   * conclusions cite evidence;
--   * every row can carry provenance via the sources/links tables
--     (commit hash, file path, dataset, environment, seed).

CREATE TABLE IF NOT EXISTS findings (
  id INTEGER PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN
        ('observation','hypothesis','conclusion','decision','lesson')),
  status TEXT NOT NULL DEFAULT 'open',
  -- open | supported | refuted | superseded | abandoned
  pass TEXT,
  text TEXT NOT NULL,
  evidence INTEGER REFERENCES findings(id),
  supersedes INTEGER REFERENCES findings(id),
  created TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY,
  ref TEXT NOT NULL UNIQUE,      -- path | commit | url | env | dataset | seed
  note TEXT
);

CREATE TABLE IF NOT EXISTS links (
  finding_id INTEGER REFERENCES findings(id),
  source_id INTEGER REFERENCES sources(id),
  PRIMARY KEY (finding_id, source_id)
);

CREATE TABLE IF NOT EXISTS experiments (
  id INTEGER PRIMARY KEY,
  pass TEXT NOT NULL,
  name TEXT NOT NULL,
  hypothesis INTEGER REFERENCES findings(id),
  status TEXT NOT NULL DEFAULT 'RUNNING',
  -- RUNNING | SUPPORTED | REFUTED | INCONCLUSIVE | NO_ADVANTAGE | INCORRECT
  provenance TEXT,
  created TEXT NOT NULL DEFAULT (datetime('now'))
);
