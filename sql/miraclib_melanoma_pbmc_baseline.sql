SELECT
    sample_id,
    project_id,
    subject_id,
    sex,
    response
FROM clinical_trial_observations
WHERE treatment = 'miraclib'
  AND sample_type = 'PBMC'
  AND condition = 'melanoma'
  AND time_from_treatment_start = 0
