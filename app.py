from src.charts import build_boxplot
from src.analysis import (
    CELL_LABELS,
    CELL_POPULATIONS,
    SIGNIFICANCE_THRESHOLD,
    compute_statistics,
    load_baseline_data,
    load_data,
    style_stats_table,
)
import streamlit as st
st.set_page_config(page_title="Miraclib Response Analysis", layout="wide")

# Header
st.title("Miraclib Treatment Response Analysis")
st.caption(
    "Melanoma patients · PBMC samples · Comparing immune cell population frequencies "
    "between responders and non-responders. Statistics: Mann-Whitney U test (two-sided)."
)

# Load in data
df = load_data()

# Overview statistics
col1, col2, col3 = st.columns(3)  # Set flex layout for overview statistics
col1.metric("Total Samples", len(df))
col2.metric("Responders", int((df["response"] == "yes").sum()))
col3.metric("Non-Responders", int((df["response"] == "no").sum()))

st.plotly_chart(build_boxplot(df), use_container_width=True)

# Boxplots
st.subheader("Statistical Summary")
st.markdown(
    f"Significant difference defined as p < {SIGNIFICANCE_THRESHOLD} "
    "(Mann-Whitney U, two-sided). Highlighted rows indicate significance."
)
stats_df = compute_statistics(df)
st.dataframe(style_stats_table(stats_df),
             use_container_width=True, hide_index=True)

sig_pops = stats_df[stats_df["Significant"]
                    == "Yes"]["Cell Population"].tolist()
if sig_pops:
    st.success(
        f"**Significant populations:** {', '.join(sig_pops)} show statistically significant "
        f"differences in relative frequency between responders and non-responders (p < {SIGNIFICANCE_THRESHOLD})."
    )
else:
    st.info(
        "No cell populations reached statistical significance at the p < 0.05 threshold.")

st.divider()

# Baseline sample explorer
st.header("Baseline Sample Explorer")
st.caption("Miraclib · melanoma · PBMC · time from treatment start = 0")

baseline_df = load_baseline_data()

b_col1, b_col2, b_col3 = st.columns(3)
b_col1.metric("Baseline Samples", len(baseline_df))
b_col2.metric("Subjects", baseline_df["subject_id"].nunique())
b_col3.metric("Projects", baseline_df["project_id"].nunique())

left, mid, right = st.columns(3)

with left:
    st.subheader("Samples per Project")
    st.dataframe(
        baseline_df.groupby("project_id")
        .size()
        .reset_index(name="Samples")
        .rename(columns={"project_id": "Project"}),
        use_container_width=True,
        hide_index=True,
    )

with mid:
    st.subheader("Subjects by Response")
    st.dataframe(
        baseline_df.dropna(subset=["response"])
        .drop_duplicates("subject_id")
        .groupby("response")
        .size()
        .reset_index(name="Subjects")
        .rename(columns={"response": "Response"})
        .replace({"yes": "Responder", "no": "Non-Responder"}),
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.subheader("Subjects by Sex")
    st.dataframe(
        baseline_df.drop_duplicates("subject_id")
        .groupby("sex")
        .size()
        .reset_index(name="Subjects")
        .rename(columns={"sex": "Sex"}),
        use_container_width=True,
        hide_index=True,
    )

# Raw data
with st.expander("Raw data"):
    display_cols = {"response": "Response"} | {
        f"{p}_freq": f"{CELL_LABELS[p]} (%)" for p in CELL_POPULATIONS
    }
    st.dataframe(
        df[["sample_id", "subject_id", "response"] +
            [f"{p}_freq" for p in CELL_POPULATIONS]]
        .rename(columns={"sample_id": "Sample", "subject_id": "Subject", **display_cols})
        .round(2),
        use_container_width=True,
        hide_index=True,
    )
