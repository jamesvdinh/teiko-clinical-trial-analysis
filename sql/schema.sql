CREATE TABLE IF NOT EXISTS clinical_trial_observations (
    sample_id TEXT NOT NULL PRIMARY KEY,
    project_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    age INTEGER NOT NULL,
    sex TEXT NOT NULL,
    treatment TEXT NOT NULL,
    response TEXT,
    sample_type TEXT NOT NULL,
    time_from_treatment_start INTEGER NOT NULL,
    b_cell INTEGER NOT NULL,
    cd8_t_cell INTEGER NOT NULL,
    cd4_t_cell INTEGER NOT NULL,
    nk_cell INTEGER NOT NULL,
    monocyte INTEGER NOT NULL
)