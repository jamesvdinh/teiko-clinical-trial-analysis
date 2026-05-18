import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analysis import CELL_LABELS, CELL_POPULATIONS

# Use blue for "yes"; red for "no"
RESPONSE_COLORS = {"yes": "#2196F3", "no": "#F44336"}


def build_boxplot(df: pd.DataFrame) -> go.Figure:
    n_pops = len(CELL_POPULATIONS)
    fig = make_subplots(
        rows=1,
        cols=n_pops,
        subplot_titles=[CELL_LABELS[p] for p in CELL_POPULATIONS],
        shared_yaxes=False,
    )

    legend_added = set()
    for col_idx, pop in enumerate(CELL_POPULATIONS, start=1):
        freq_col = f"{pop}_freq"
        for response_val, color in RESPONSE_COLORS.items():
            subset = df[df["response"] == response_val][freq_col]
            label = "Responder" if response_val == "yes" else "Non-Responder"
            show_legend = label not in legend_added
            legend_added.add(label)

            fig.add_trace(
                go.Box(
                    y=subset,
                    name=label,
                    marker_color=color,
                    boxmean=True,
                    showlegend=show_legend,
                    legendgroup=label,
                ),
                row=1,
                col=col_idx,
            )
        fig.update_yaxes(title_text="Relative Frequency (%)",
                         row=1, col=col_idx)

    fig.update_layout(
        height=500,
        title_text="Cell Population Relative Frequencies: Responders vs Non-Responders",
        title_font_size=16,
        boxmode="group",
        legend=dict(orientation="h", yanchor="bottom",
                    y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=80, b=80),
    )
    return fig
