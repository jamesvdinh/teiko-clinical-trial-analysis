WITH totals AS (
    SELECT
        sample_id,
        b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte AS total_count,
        b_cell,
        cd8_t_cell,
        cd4_t_cell,
        nk_cell,
        monocyte
    FROM clinical_trial_observations
),
unpivoted AS (
    SELECT sample_id, total_count, 'b_cell' AS population, b_cell AS count FROM totals
    UNION ALL
    SELECT sample_id, total_count, 'cd8_t_cell' AS population, cd8_t_cell AS count FROM totals
    UNION ALL
    SELECT sample_id, total_count, 'cd4_t_cell' AS population, cd4_t_cell AS count FROM totals
    UNION ALL
    SELECT sample_id, total_count, 'nk_cell' AS population, nk_cell AS count FROM totals
    UNION ALL
    SELECT sample_id, total_count, 'monocyte' AS population, monocyte AS count FROM totals
)
SELECT
    sample_id AS sample,
    total_count,
    population,
    count,
    ROUND(100.0 * count / total_count, 2) AS percentage
FROM unpivoted
ORDER BY sample, population
LIMIT 10;