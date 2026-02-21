import matplotlib.pyplot as plt


def plot_diff_map(gdf, column: str = "diff", title: str = "Accessibility Change"):
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(column=column, cmap="RdBu", legend=True, ax=ax)
    ax.set_axis_off()
    ax.set_title(title)
    plt.tight_layout()
    return fig, ax
