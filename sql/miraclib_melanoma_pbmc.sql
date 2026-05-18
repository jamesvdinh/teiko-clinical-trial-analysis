SELECT
    sample_id,
    subject_id,
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
  AND response IS NOT NULL
