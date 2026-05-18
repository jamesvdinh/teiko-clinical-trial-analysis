SELECT
    sample_id,
    project_id,
    subject_id,
    sex,
    response,
    b_cell,
    cd8_t_cell,
    cd4_t_cell,
    nk_cell,
    monocyte
FROM clinical_trial_observations
WHERE treatment = 'miraclib'
  AND sample_type = 'PBMC'
  AND condition = 'melanoma'
  AND time_from_treatment_start = 0
