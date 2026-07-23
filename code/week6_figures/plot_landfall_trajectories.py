"""
Landfall sentiment trajectories.

Two plots per hurricane (posts, comments). For each:
  x = days_from_landfall, restricted to the window -5 .. +1
  y = mean VADER compound score
  one line per source: Facebook, Reddit (community), White House

"""
import os
import pandas as pd
import matplotlib.pyplot as plt

# Week 8 reproducibility fix: this resolved to code/, not the repo root, so
# every path below became code/data/... and the script could not run at all.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTDIR = os.path.join(ROOT, "figures", "landfall_trajectories")
os.makedirs(OUTDIR, exist_ok=True)

XMIN, XMAX = -5, 1          # window: 5 days before .. 1 day after landfall
XTICKS = list(range(XMIN, XMAX + 1))

# source -> (posts file, comments file)
FILES = {
    "Facebook": (
        "data/vader/facebook_posts_vader.csv",
        "data/vader/facebook_comments_vader.csv",
    ),
    # Week 8 fix: these two were the pre-2026-07-05 filenames, which no longer
    # exist. The current files are the WH-deduplicated 3,413 / 121,053 ones.
    "Reddit": (
        "data/vader/reddit_relevant_vader_posts.csv",
        "data/vader/reddit_relevant_vader_comments.csv",
    ),
    "White House": (
        "data/vader/whitehouse_threads_posts_vader.csv",
        "data/vader/whitehouse_threads_comments_vader.csv",
    ),
}
COLORS = {"Facebook": "tab:blue", "Reddit": "tab:orange", "White House": "tab:green"}
HURRICANES = ["Debby", "Helene", "Milton"]


def load(path):
    """Load one VADER file, restricted to the plotted window and to complete rows."""
    d = pd.read_csv(os.path.join(ROOT, path), usecols=lambda c: c in
                    ("hurricane", "days_from_landfall", "vader_compound"))
    d["hurricane"] = d["hurricane"].str.capitalize()        # normalize casing
    d = d[d["days_from_landfall"].between(XMIN, XMAX)]
    d = d.dropna(subset=["vader_compound", "days_from_landfall"])
    d["days_from_landfall"] = d["days_from_landfall"].astype(int)
    return d


# preload all six files, split by unit
data = {unit: {src: load(FILES[src][i]) for src in FILES}
        for i, unit in enumerate(["posts", "comments"])}

summary_rows = []

for hurricane in HURRICANES:
    for unit in ["posts", "comments"]:
        fig, ax = plt.subplots(figsize=(8, 5))
        plotted = False
        for src in FILES:
            d = data[unit][src]
            d = d[d["hurricane"] == hurricane]
            if d.empty:
                continue
            g = d.groupby("days_from_landfall")["vader_compound"].agg(["mean", "size"])
            g = g.reindex(XTICKS)           # keep gaps as gaps, fixed axis
            for day, row in g.iterrows():
                if pd.notna(row["mean"]):
                    summary_rows.append([hurricane, unit, src, day,
                                         round(row["mean"], 4), int(row["size"])])
            ax.plot(g.index, g["mean"], marker="o", color=COLORS[src], label=src)
            plotted = True

        ax.axhline(0, color="grey", lw=0.8, ls="--", alpha=0.7)
        ax.set_xticks(XTICKS)
        ax.set_xlim(XMIN - 0.3, XMAX + 0.3)
        ax.set_xlabel("Days from landfall")
        ax.set_ylabel("Mean VADER compound")
        ax.set_title(f"{hurricane} — {unit}: mean sentiment by day from landfall")
        if plotted:
            ax.legend(title="Source")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = os.path.join(OUTDIR, f"{hurricane.lower()}_{unit}.png")
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print("saved", out)

summary = pd.DataFrame(summary_rows,
                       columns=["hurricane", "unit", "source", "day", "mean_compound", "n"])
summary.to_csv(os.path.join(OUTDIR, "per_day_means.csv"), index=False)
print("\nper-day means / counts:")
print(summary.to_string(index=False))
