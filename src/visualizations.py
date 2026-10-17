"""Reusable Matplotlib figures shared by Streamlit and the notebook."""
import matplotlib.pyplot as plt
import pandas as pd

BLUE = '#2563eb'


def bar_chart(labels, values, title: str, ylabel: str = 'Students', horizontal: bool = False):
    """Return a labeled figure; the caller owns closing it."""
    with plt.rc_context({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False}):
        fig, ax = plt.subplots(figsize=(8, 4.5), layout='constrained')
        if horizontal:
            bars = ax.barh([str(x) for x in labels], values, color=BLUE, height=.65)
            ax.set_xlabel(ylabel)
            ax.invert_yaxis()
            ax.set_xlim(0, max(list(values) + [1]) * 1.20)
        else:
            bars = ax.bar([str(x) for x in labels], values, color=BLUE, width=.65)
            ax.set_ylabel(ylabel)
            ax.tick_params(axis='x', labelrotation=20)
            ax.set_ylim(0, max(list(values) + [1]) * 1.20)
        ax.bar_label(bars, fmt='%.1f', padding=3, fontsize=9)
        ax.set_title(title, loc='left', fontweight='bold', pad=16)
        ax.grid(axis='x' if horizontal else 'y', alpha=.15)
        ax.set_axisbelow(True)
        return fig


def scatter_chart(data: pd.DataFrame, column: str, xlabel: str, title: str):
    """Show observations and a pass boundary; no causal trend is implied."""
    fig, ax = plt.subplots(figsize=(8, 4.5), layout='constrained')
    colors = data.at_risk.map({True: '#dc6846', False: BLUE})
    ax.scatter(data[column], data.academic_score, c=colors, alpha=.65, s=30,
               edgecolors='white', linewidths=.3)
    ax.axhline(50, color='#64748b', linestyle='--', linewidth=1, label='Pass threshold (50)')
    ax.set(xlabel=xlabel, ylabel='Academic score', title=title, ylim=(0, 103))
    ax.grid(alpha=.15)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False)
    return fig
