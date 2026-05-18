"""
Standalone pipeline script — no Streamlit dependency.
Reads from the SQLite database, writes outputs to output/.
"""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import mannwhitneyu

DB_PATH = Path(__file__).parent.parent / "clinical_trials.db"
SQL_DIR = Path(__file__).parent.parent / "sql"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

CELL_POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
CELL_LABELS = {
    "b_cell": "B Cell",
    "cd8_t_cell": "CD8 T Cell",
    "cd4_t_cell": "CD4 T Cell",
    "nk_cell": "NK Cell",
    "monocyte": "Monocyte",
}
SIGNIFICANCE_THRESHOLD = 0.05
RESPONSE_COLORS = {"yes": "#2196F3", "no": "#F44336"}


def load_query(filename: str) -> str:
    return (SQL_DIR / filename).read_text()


def compute_frequencies(df: pd.DataFrame) -> pd.DataFrame:
    total = df[CELL_POPULATIONS].sum(axis=1)
    for col in CELL_POPULATIONS:
        df[f"{col}_freq"] = df[col] / total * 100
    return df


def compute_statistics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pop in CELL_POPULATIONS:
        freq_col = f"{pop}_freq"
        responders = df.loc[df["response"] == "yes", freq_col]
        non_responders = df.loc[df["response"] == "no", freq_col]
        _, p_value = mannwhitneyu(responders, non_responders, alternative="two-sided")
        rows.append(
            {
                "cell_population": CELL_LABELS[pop],
                "responders_median_pct": round(responders.median(), 2),
                "non_responders_median_pct": round(non_responders.median(), 2),
                "p_value": round(p_value, 4),
                "significant": p_value < SIGNIFICANCE_THRESHOLD,
            }
        )
    return pd.DataFrame(rows).sort_values("p_value")


def build_boxplot(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=1,
        cols=len(CELL_POPULATIONS),
        subplot_titles=[CELL_LABELS[p] for p in CELL_POPULATIONS],
    )
    legend_added = set()
    for col_idx, pop in enumerate(CELL_POPULATIONS, start=1):
        freq_col = f"{pop}_freq"
        for response_val, color in RESPONSE_COLORS.items():
            label = "Responder" if response_val == "yes" else "Non-Responder"
            fig.add_trace(
                go.Box(
                    y=df[df["response"] == response_val][freq_col],
                    name=label,
                    marker_color=color,
                    boxmean=True,
                    showlegend=label not in legend_added,
                    legendgroup=label,
                ),
                row=1,
                col=col_idx,
            )
            legend_added.add(label)
        fig.update_yaxes(title_text="Relative Frequency (%)", row=1, col=col_idx)

    fig.update_layout(
        height=500,
        title_text="Cell Population Relative Frequencies: Responders vs Non-Responders",
        boxmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=80, b=80),
    )
    return fig


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(load_query("miraclib_melanoma_pbmc.sql"), conn)
        baseline_df = pd.read_sql_query(load_query("miraclib_melanoma_pbmc_baseline.sql"), conn)

    df = compute_frequencies(df)

    # --- Statistics (Parts 2 & 4) ---
    stats_df = compute_statistics(df)
    stats_path = OUTPUT_DIR / "statistics.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"Wrote {stats_path}")

    sig = stats_df[stats_df["significant"]]["cell_population"].tolist()
    if sig:
        print(f"\nSignificant populations (p < {SIGNIFICANCE_THRESHOLD}): {', '.join(sig)}")
    else:
        print(f"\nNo populations reached significance at p < {SIGNIFICANCE_THRESHOLD}")

    # --- Boxplot (Part 3) ---
    fig = build_boxplot(df)
    plot_path = OUTPUT_DIR / "boxplot.html"
    fig.write_html(plot_path)
    print(f"Wrote {plot_path}")

    # --- Baseline summary ---
    samples_per_project = (
        baseline_df.groupby("project_id").size().reset_index(name="samples")
    )
    response_counts = (
        baseline_df.dropna(subset=["response"])
        .drop_duplicates("subject_id")
        .groupby("response")
        .size()
        .reset_index(name="subjects")
    )
    sex_counts = (
        baseline_df.drop_duplicates("subject_id")
        .groupby("sex")
        .size()
        .reset_index(name="subjects")
    )

    baseline_path = OUTPUT_DIR / "baseline_summary.csv"
    samples_per_project.to_csv(baseline_path, index=False)
    print(f"Wrote {baseline_path}")

    print("\n--- Baseline: Samples per Project ---")
    print(samples_per_project.to_string(index=False))
    print("\n--- Baseline: Subjects by Response ---")
    print(response_counts.to_string(index=False))
    print("\n--- Baseline: Subjects by Sex ---")
    print(sex_counts.to_string(index=False))


if __name__ == "__main__":
    main()
