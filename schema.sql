CREATE TABLE IF NOT EXISTS clinical_trial_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id TEXT NOT NULL,
    trial_arm TEXT NOT NULL,
    visit_date TEXT NOT NULL,
    immune_cell_type TEXT NOT NULL,
    cell_count INTEGER NOT NULL,
    biomarker_level REAL NOT NULL,
    adverse_event TEXT
);
