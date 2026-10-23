"""Plot the saved exact census; rounding occurs only in figure presentation."""

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


HERE = Path(__file__).resolve().parent
INPUT = HERE / "profile_heterogeneity_census.v1.json"
OUTPUT = HERE.parent / "figures"


def save(fig, name, source_sha):
    OUTPUT.mkdir(exist_ok=True)
    description = f"Exact profile census SHA-256: {source_sha}"
    fig.savefig(OUTPUT / f"{name}.png", dpi=320,
                metadata={"SourceSHA256": source_sha, "Description": description})
    fig.savefig(OUTPUT / f"{name}.svg",
                metadata={"Date": None, "Description": description,
                          "Creator": "plot_profile_heterogeneity.py"})
    plt.close(fig)


def main():
    raw = INPUT.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw)
    soma, superclass = (data["partitions"][key] for key in ("somaSide", "superclass"))
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": "#24282c", "text.color": "#24282c",
        "svg.hashsalt": "profile-census-v1",
    })
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(4.96, 5.2), layout="constrained",
                                 gridspec_kw={"height_ratios": [0.85, 1.4]})
    items = soma["by_source_sector"]
    positions = np.arange(len(items))
    for offset, field, color, label in (
        (-0.18, "eligible_sources", "#88939b", "Eligible sources"),
        (0.18, "exact_profile_classes", "#168779", "Exact profile classes"),
    ):
        values = [row[field] for row in items]
        ax.barh(positions + offset, values, height=0.32, color=color, label=label)
        for y, value in zip(positions + offset, values):
            ax.text(value * 1.10, y, f"{value:,}", va="center", fontsize=8)
    ax.set(yticks=positions, yticklabels=[r["source_sector"] for r in items],
           xscale="log", xlim=(40, 160000),
           xlabel="Count (log scale)")
    ax.invert_yaxis()
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.24), frameon=False,
              fontsize=8, ncol=2)
    points = [row for row in superclass["by_source_sector"] if row["eligible_sources"]]
    bx.plot([0.7, 150000], [0.7, 150000], color="#aab1b6", lw=1, ls="--", zorder=0)
    bx.scatter([r["eligible_sources"] for r in points],
               [r["exact_profile_classes"] for r in points],
               s=40, color="#286caa", edgecolor="white", lw=0.6)
    labels = {
        "ol_intrinsic": (-47, 16), "cb_intrinsic": (-62, 7),
        "visual_centrifugal": (6, -15), "<missing>": (-45, 13),
    }
    for row in points:
        if row["source_sector"] in labels:
            bx.annotate(row["source_sector"],
                        (row["eligible_sources"], row["exact_profile_classes"]),
                        xytext=labels[row["source_sector"]], textcoords="offset points",
                        fontsize=7.5,
                        arrowprops={"arrowstyle": "-", "color": "#87939b", "lw": 0.6})
    bx.set(xscale="log", yscale="log", xlim=(0.7, 150000), ylim=(0.7, 150000),
           xlabel="Eligible sources in observed sector",
           ylabel="Distinct exact positive profiles",
           title="b   superclass observation fibers")
    save(fig, "profile_multiplicity", digest)

    fig, (ax, bx) = plt.subplots(2, 1, figsize=(4.96, 4.8), layout="constrained",
                                 gridspec_kw={"height_ratios": [1, 1.2]})
    grid = np.array([[c["separated_unordered_source_pairs"]
                      / r["unordered_same_observation_source_pairs"]
                      for c in r["coordinates"]] for r in soma["by_source_sector"]])
    image = ax.imshow(grid, vmin=0, vmax=1, cmap="cividis", aspect="equal")
    labels = soma["labels"]
    ax.set(xticks=range(4), yticks=range(4), xticklabels=labels, yticklabels=labels,
           xlabel="Target coordinate", ylabel="Observed source sector",
           title="a   somaSide: pair split within each fiber")
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{100 * grid[i, j]:.1f}%", ha="center", va="center",
                    color="white" if grid[i, j] < 0.5 else "#162027", fontsize=8)
    bar = fig.colorbar(image, ax=ax, shrink=0.72, pad=0.03)
    bar.ax.yaxis.set_major_formatter(PercentFormatter(1))
    targets = sorted(superclass["target_coordinate_splits"],
                     key=lambda r: r["separated_unordered_source_pairs"], reverse=True)[:10]
    rates = [r["separated_unordered_source_pairs"]
             / r["denominator_all_same_observation_source_pairs"] for r in targets]
    bx.barh(range(len(targets)), rates, color="#286caa", height=0.7)
    for y, rate in enumerate(rates):
        bx.text(rate + 0.012, y, f"{100 * rate:.1f}%", va="center", fontsize=8)
    bx.set(yticks=range(len(targets)), yticklabels=[r["target_sector"] for r in targets],
           xlim=(0, 1.04), xlabel="Share of all within-sector source pairs split",
           title="b   superclass: leading target coordinates")
    bx.invert_yaxis()
    bx.xaxis.set_major_formatter(PercentFormatter(1))
    save(fig, "coordinate_profile_splits", digest)
    print(json.dumps({"status": "PASS", "source_sha256": digest,
                      "figures": ["profile_multiplicity", "coordinate_profile_splits"]}))


if __name__ == "__main__":
    main()
