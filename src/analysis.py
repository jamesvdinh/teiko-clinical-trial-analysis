import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from scipy.stats import mannwhitneyu

DB_PATH = Path(__file__).parent.parent / "clinical_trials.db"
CELL_POPULATIONS = ["b_cell", "cd8_t_cell",
                    "cd4_t_cell", "nk_cell", "monocyte"]
CELL_LABELS = {
    "b_cell": "B Cell",
    "cd8_t_cell": "CD8 T Cell",
    "cd4_t_cell": "CD4 T Cell",
    "nk_cell": "NK Cell",
    "monocyte": "Monocyte",
}
# standard p-value threshold for statistical significance
SIGNIFICANCE_THRESHOLD = 0.05


@st.cache_data
def load_data() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            """
            SELECT sample_id, subject_id, response,
                   b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
            FROM clinical_trial_observations
            WHERE treatment = 'miraclib'
              AND sample_type = 'PBMC'
              AND condition = 'melanoma'
              AND response IS NOT NULL
            """,
            conn,
        )

    total = df[CELL_POPULATIONS].sum(axis=1)
    for col in CELL_POPULATIONS:
        df[f"{col}_freq"] = df[col] / total * 100

    return df


@st.cache_data
def load_baseline_data() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            """
            SELECT sample_id, project_id, subject_id, sex, response
            FROM clinical_trial_observations
            WHERE treatment = 'miraclib'
              AND sample_type = 'PBMC'
              AND condition = 'melanoma'
              AND time_from_treatment_start = 0
            """,
            conn,
        )


def compute_statistics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pop in CELL_POPULATIONS:
        freq_col = f"{pop}_freq"
        responders = df.loc[df["response"] == "yes", freq_col]
        non_responders = df.loc[df["response"] == "no", freq_col]
        _, p_value = mannwhitneyu(
            responders, non_responders, alternative="two-sided")
        rows.append(
            {
                "Cell Population": CELL_LABELS[pop],
                "Responders (median %)": round(responders.median(), 2),
                "Non-Responders (median %)": round(non_responders.median(), 2),
                "p-value": round(p_value, 4),
                "Significant": "Yes" if p_value < SIGNIFICANCE_THRESHOLD else "No",
            }
        )
    return pd.DataFrame(rows).sort_values("p-value")


def style_stats_table(df: pd.DataFrame) -> pd.DataFrame.style:
    def highlight_significant(row):
        color = "background-color: #E8F5E9" if row["Significant"] == "Yes" else ""
        return [color] * len(row)

    return (
        df.style.apply(highlight_significant, axis=1)
        .format({"p-value": "{:.4f}"})
        .hide(axis="index")
    )
