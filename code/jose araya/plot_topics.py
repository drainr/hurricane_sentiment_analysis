"""
plot_topics.py
Week 4 topic figures from master_vader_roberta_topics.csv.

Writes to figures/topics/ at 300 dpi (PNG + PDF). Color convention:
  Facebook = blue, Reddit community = orange, White House/government = green.

Figures:
  1. topic_dist_by_source_type     -- grouped bar, 9 shared categories
  2. topic_heatmap_by_hurricane    -- topic_category x hurricane proportions
  3. topic_temporal_evolution      -- topic share by days_from_landfall (Reddit)
  4. wh_topic_breakout             -- WH comment 6-category break-out (H7)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MASTER = os.path.join(ROOT, "data", "merged", "master_vader_roberta_topics.csv")
OUTDIR = os.path.join(ROOT, "figures", "topics")
os.makedirs(OUTDIR, exist_ok=True)

COLORS = {"facebook": "#1f77b4", "community_discussion": "#ff7f0e",
          "government_response": "#2ca02c", "government": "#2ca02c"}
SRC_LABEL = {"facebook": "Facebook", "community_discussion": "Reddit community",
             "government_response": "White House comments"}

SHARED9 = [
    "gratitude", "preparedness", "forecast analysis", "evacuation logistics",
    "political / FEMA criticism", "misinformation", "government resources",
    "personal experience", "emotional response",
]


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUTDIR, f"{name}.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def main():
    m = pd.read_csv(MASTER, low_memory=False)
    m["source_bucket"] = m["source_type"].fillna("facebook")
    shared = m[m["topic_category"].isin(SHARED9)].copy()

    # ---- Fig 1: grouped bar, topic distribution by source_type ----
    src = shared[shared["source_bucket"].isin(
        ["facebook", "community_discussion", "government_response"])]
    ct = pd.crosstab(src["topic_category"], src["source_bucket"]).reindex(SHARED9).fillna(0)
    prop = ct.div(ct.sum(axis=0), axis=1)
    cats = [c for c in SHARED9 if ct.loc[c].sum() > 0]
    prop = prop.loc[cats]
    x = np.arange(len(cats))
    order = ["facebook", "community_discussion", "government_response"]
    w = 0.26
    fig, ax = plt.subplots(figsize=(13, 6))
    for i, s in enumerate(order):
        ax.bar(x + (i - 1) * w, prop[s].values, w, label=SRC_LABEL[s], color=COLORS[s])
    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=35, ha="right")
    ax.set_ylabel("Proportion within source")
    ax.set_title("Topic distribution by source type (nine shared categories)")
    ax.legend()
    save(fig, "topic_dist_by_source_type")

    # ---- Fig 2: heatmap topic_category x hurricane ----
    cth = pd.crosstab(shared["topic_category"], shared["hurricane"]).reindex(SHARED9).fillna(0)
    cth = cth.loc[[c for c in SHARED9 if cth.loc[c].sum() > 0]]
    ph = cth.div(cth.sum(axis=0), axis=1)
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(ph.values, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(ph.columns)))
    ax.set_xticklabels([c.capitalize() for c in ph.columns])
    ax.set_yticks(range(len(ph.index)))
    ax.set_yticklabels(ph.index)
    for i in range(ph.shape[0]):
        for j in range(ph.shape[1]):
            v = ph.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color="white" if v < 0.5 else "black", fontsize=8)
    ax.set_title("Topic proportion by hurricane")
    fig.colorbar(im, ax=ax, label="Proportion within hurricane")
    save(fig, "topic_heatmap_by_hurricane")

    # ---- Fig 3: temporal topic evolution by days_from_landfall (Reddit community) ----
    red = shared[shared["source_bucket"] == "community_discussion"].copy()
    red = red[red["days_from_landfall"].between(-5, 1)]
    top_cats = red["topic_category"].value_counts().head(5).index.tolist()
    fig, ax = plt.subplots(figsize=(10, 6))
    for c in top_cats:
        share = (red.assign(hit=(red["topic_category"] == c))
                 .groupby("days_from_landfall")["hit"].mean())
        ax.plot(share.index, share.values, marker="o", label=c)
    ax.axvline(0, ls="--", color="grey", alpha=0.7, label="landfall (day 0)")
    ax.set_xlabel("Days from landfall")
    ax.set_ylabel("Topic share (Reddit community)")
    ax.set_title("Temporal topic evolution -- Reddit community")
    ax.legend(fontsize=8)
    save(fig, "topic_temporal_evolution")

    # ---- Fig 4: WH comment 6-category break-out (H7) ----
    wh = m[m["source_type"] == "government_response"].copy()
    counts = wh["topic_category"].value_counts()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(counts.index[::-1], counts.values[::-1], color=COLORS["government_response"])
    for i, v in enumerate(counts.values[::-1]):
        ax.text(v + max(counts) * 0.01, i, str(v), va="center", fontsize=9)
    ax.set_xlabel("White House comments")
    ax.set_title("White House comment categories (H7 break-out)")
    save(fig, "wh_topic_breakout")


if __name__ == "__main__":
    main()
