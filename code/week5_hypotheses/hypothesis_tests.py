from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MERGED_DIR = DATA_DIR / "merged"
MERGED_DIR.mkdir(parents=True, exist_ok=True)

LABEL_ORDER = ["negative", "neutral", "positive"]

# H5: subreddit → category mapping (per hypothesis spec)
H5_SUBREDDIT_MAP: Dict[str, str] = {
    "TropicalWeather": "expert",
    "tampa": "local",
    "sarasota": "local",
    "florida": "statewide",
}


def encode_roberta_labels(labels: List[str] | pd.Series | np.ndarray) -> List[float]:
    mapping = {"neg": -1, "negative": -1, "neu": 0, "neutral": 0, "pos": 1, "positive": 1}
    normalized: List[float] = []
    for value in labels:
        if pd.isna(value):
            normalized.append(float("nan"))
            continue
        key = str(value).strip().lower()
        normalized.append(float(mapping.get(key, float("nan"))))
    return normalized


def rank_biserial_effect_size(u_stat: float, n1: int, n2: int) -> float:
    return 2 * u_stat / (n1 * n2) - 1


def normalize_hurricane_name(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower()


def load_comment_frames() -> Dict[str, pd.DataFrame]:
    fb = pd.read_csv(PROCESSED_DIR / "facebook_comments_vader_roberta_topics_labeled.csv")
    reddit = pd.read_csv(PROCESSED_DIR / "reddit_relevant_comments_vader_roberta_topics_labeled.csv")
    wh = pd.read_csv(PROCESSED_DIR / "whitehouse_threads_comments_vader_roberta_topics_labeled.csv")

    for frame in (fb, reddit, wh):
        frame["hurricane_norm"] = normalize_hurricane_name(frame["hurricane"])

    return {
        "facebook": fb,
        "reddit": reddit,
        "whitehouse": wh,
        "facebook_roberta": fb,
        "reddit_roberta": reddit,
        "whitehouse_roberta": wh,
    }


def clean_for_model(df: pd.DataFrame, model: str) -> pd.DataFrame:
    out = df.copy()
    out = out.dropna(subset=["text"]).copy()
    if model == "vader":
        out["score"] = pd.to_numeric(out["vader_compound"], errors="coerce")
        out["label"] = out["vader_label"].astype(str).str.strip().str.lower()
    elif model == "roberta":
        out["score"] = (
            pd.to_numeric(out["roberta_pos"], errors="coerce")
            - pd.to_numeric(out["roberta_neg"], errors="coerce")
        )
        out["label"] = out["roberta_label"].astype(str).str.strip().str.lower()
    else:
        raise ValueError(f"unsupported model {model}")

    out["label"] = out["label"].map(
        lambda s: "negative" if str(s) in {"neg", "negative"} else "neutral" if str(s) in {"neu", "neutral", "neutural"} else "positive" if str(s) in {"pos", "positive"} else np.nan
    )
    out = out.dropna(subset=["score", "label"])
    return out


def mann_whitney_result(x: pd.Series, y: pd.Series) -> Dict[str, float]:
    x = pd.to_numeric(x, errors="coerce").dropna().to_numpy()
    y = pd.to_numeric(y, errors="coerce").dropna().to_numpy()
    if len(x) == 0 or len(y) == 0:
        return {"u": np.nan, "p": np.nan, "rank_biserial": np.nan}
    stat, p = stats.mannwhitneyu(x, y, alternative="two-sided", method="auto")
    effect = rank_biserial_effect_size(float(stat), len(x), len(y))
    return {"u": float(stat), "p": float(p), "rank_biserial": float(effect)}


def chi_square_result(df: pd.DataFrame) -> Dict[str, float]:
    counts = pd.crosstab(df["platform"], df["label"])
    counts = counts.reindex(index=["facebook", "reddit"], columns=LABEL_ORDER, fill_value=0)
    if counts.shape[0] == 0 or counts.shape[1] == 0:
        return {"chi2": np.nan, "p": np.nan}
    chi2, p, _, _ = stats.chi2_contingency(counts)
    return {"chi2": float(chi2), "p": float(p)}


def format_p(p: float) -> str:
    if np.isnan(p):
        return "n/a"
    return f"{p:.3e}"


def run_h1(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for model in ("vader", "roberta"):
        fb = frames["facebook"] if model == "vader" else frames["facebook_roberta"]
        rd = frames["reddit"] if model == "vader" else frames["reddit_roberta"]
        fb_clean = clean_for_model(fb, model).assign(platform="facebook")
        rd_clean = clean_for_model(rd, model).assign(platform="reddit")
        combined = pd.concat([fb_clean, rd_clean], ignore_index=True)

        overall = mann_whitney_result(fb_clean["score"], rd_clean["score"])
        chi = chi_square_result(combined)
        rows.append(
            {
                "hypothesis": "H1",
                "model": model,
                "subset": "overall",
                "u": overall["u"],
                "p": overall["p"],
                "rank_biserial": overall["rank_biserial"],
                "chi2": chi["chi2"],
                "chi2_p": chi["p"],
            }
        )

        for hurricane in sorted(sorted(combined["hurricane_norm"].dropna().unique().tolist()), key=lambda s: (s != "debby", s != "helene", s != "milton", s)):
            if hurricane not in {"debby", "helene", "milton"}:
                continue
            subset = combined[combined["hurricane_norm"] == hurricane]
            fb_h = subset[subset["platform"] == "facebook"]
            rd_h = subset[subset["platform"] == "reddit"]
            if len(fb_h) == 0 or len(rd_h) == 0:
                continue
            result = mann_whitney_result(fb_h["score"], rd_h["score"])
            rows.append(
                {
                    "hypothesis": "H1",
                    "model": model,
                    "subset": hurricane,
                    "u": result["u"],
                    "p": result["p"],
                    "rank_biserial": result["rank_biserial"],
                    "chi2": np.nan,
                    "chi2_p": np.nan,
                }
            )
    return rows


def run_h2(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, object]]:
    """OLS temporal regression: compound ~ days_from_landfall, per model/platform/interaction."""
    rows: List[Dict[str, object]] = []

    for model in ("vader", "roberta"):
        fb_key = "facebook" if model == "vader" else "facebook_roberta"
        rd_key = "reddit" if model == "vader" else "reddit_roberta"
        fb_base = clean_for_model(frames[fb_key], model).copy()
        rd_base = clean_for_model(frames[rd_key], model).copy()
        fb_base["days_from_landfall"] = pd.to_numeric(fb_base["days_from_landfall"], errors="coerce")
        rd_base["days_from_landfall"] = pd.to_numeric(rd_base["days_from_landfall"], errors="coerce")

        subsets = [("overall", None)] + [(h, h) for h in ("debby", "helene", "milton")]
        for subset_label, hurricane in subsets:
            if hurricane:
                fb_sub = fb_base[fb_base["hurricane_norm"] == hurricane].dropna(subset=["days_from_landfall"]).copy()
                rd_sub = rd_base[rd_base["hurricane_norm"] == hurricane].dropna(subset=["days_from_landfall"]).copy()
            else:
                fb_sub = fb_base.dropna(subset=["days_from_landfall"]).copy()
                rd_sub = rd_base.dropna(subset=["days_from_landfall"]).copy()

            for platform_label, df_sub in (("facebook", fb_sub), ("reddit", rd_sub)):
                if len(df_sub) < 3:
                    rows.append({
                        "hypothesis": "H2", "model": model, "subset": subset_label, "platform": platform_label,
                        "n": len(df_sub), "slope": np.nan, "slope_p": np.nan,
                        "ci_low": np.nan, "ci_high": np.nan, "r2": np.nan,
                        "interaction_coef": np.nan, "interaction_p": np.nan,
                    })
                    continue
                try:
                    m = smf.ols("score ~ days_from_landfall", data=df_sub).fit()
                    lo, hi = m.conf_int().loc["days_from_landfall"]
                    rows.append({
                        "hypothesis": "H2",
                        "model": model,
                        "subset": subset_label,
                        "platform": platform_label,
                        "n": int(m.nobs),
                        "slope": float(m.params["days_from_landfall"]),
                        "slope_p": float(m.pvalues["days_from_landfall"]),
                        "ci_low": float(lo),
                        "ci_high": float(hi),
                        "r2": float(m.rsquared),
                        "interaction_coef": np.nan,
                        "interaction_p": np.nan,
                    })
                except Exception:
                    rows.append({
                        "hypothesis": "H2", "model": model, "subset": subset_label, "platform": platform_label,
                        "n": len(df_sub), "slope": np.nan, "slope_p": np.nan,
                        "ci_low": np.nan, "ci_high": np.nan, "r2": np.nan,
                        "interaction_coef": np.nan, "interaction_p": np.nan,
                    })

            # Combined interaction model: compound ~ days_from_landfall * platform
            combined = pd.concat([
                fb_sub[["score", "days_from_landfall"]].assign(platform="facebook"),
                rd_sub[["score", "days_from_landfall"]].assign(platform="reddit"),
            ], ignore_index=True).dropna(subset=["score", "days_from_landfall"])
            if subset_label == "overall" and len(combined) >= 4:
                try:
                    m_int = smf.ols(
                        "score ~ days_from_landfall * C(platform, Treatment('facebook'))",
                        data=combined,
                    ).fit()
                    iname = next(c for c in m_int.params.index if "days_from_landfall:" in c)
                    rows.append({
                        "hypothesis": "H2",
                        "model": model,
                        "subset": subset_label,
                        "platform": "interaction",
                        "n": int(m_int.nobs),
                        "slope": np.nan,
                        "slope_p": np.nan,
                        "ci_low": np.nan,
                        "ci_high": np.nan,
                        "r2": float(m_int.rsquared),
                        "interaction_coef": float(m_int.params[iname]),
                        "interaction_p": float(m_int.pvalues[iname]),
                    })
                except Exception:
                    pass

    return rows


def bootstrap_gap_difference(fb: pd.Series, rd: pd.Series, n_boot: int = 10000, seed: int = 42) -> Dict[str, float]:
    fb_vals = pd.to_numeric(fb, errors="coerce").dropna().to_numpy(dtype=float)
    rd_vals = pd.to_numeric(rd, errors="coerce").dropna().to_numpy(dtype=float)
    if len(fb_vals) == 0 or len(rd_vals) == 0:
        return {"gap": np.nan, "p": np.nan, "ci_low": np.nan, "ci_high": np.nan}
    gap = float(np.mean(fb_vals) - np.mean(rd_vals))
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_boot):
        fb_boot = rng.choice(fb_vals, size=len(fb_vals), replace=True)
        rd_boot = rng.choice(rd_vals, size=len(rd_vals), replace=True)
        diffs.append(float(np.mean(fb_boot) - np.mean(rd_boot)))
    diffs = np.array(diffs)
    p = float(np.mean(diffs <= 0))
    ci_low, ci_high = np.percentile(diffs, [2.5, 97.5])
    return {"gap": gap, "p": p, "ci_low": float(ci_low), "ci_high": float(ci_high)}


def run_h3(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for model in ("vader", "roberta"):
        fb_key = "facebook" if model == "vader" else "facebook_roberta"
        rd_key = "reddit" if model == "vader" else "reddit_roberta"
        fb_all = clean_for_model(frames[fb_key], model)
        rd_all = clean_for_model(frames[rd_key], model)

        model_gaps: Dict[str, float] = {}
        for hurricane in ("debby", "helene", "milton"):
            fb_h = fb_all[fb_all["hurricane_norm"] == hurricane]
            rd_h = rd_all[rd_all["hurricane_norm"] == hurricane]
            gap = bootstrap_gap_difference(fb_h["score"], rd_h["score"], seed=100 + hash(hurricane) % 100)
            model_gaps[hurricane] = gap["gap"]
            rows.append({"hypothesis": "H3", "model": model, "hurricane": hurricane, "gap": gap["gap"], "bootstrap_p": gap["p"], "ci_low": gap["ci_low"], "ci_high": gap["ci_high"]})

    return rows


def run_h4(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for model in ("vader", "roberta"):
        for platform, key in (("reddit", "reddit" if model == "vader" else "reddit_roberta"),
                               ("facebook", "facebook" if model == "vader" else "facebook_roberta")):
            df = clean_for_model(frames[key], model)
            groups = {h: df.loc[df["hurricane_norm"] == h, "score"].dropna().to_numpy() for h in ("debby", "helene", "milton") if (df["hurricane_norm"] == h).any()}
            if len(groups) < 2:
                continue
            stat, p = stats.kruskal(*groups.values())
            rows.append({"hypothesis": "H4", "model": model, "platform": platform, "test": "kruskal_wallis", "stat": float(stat), "p": float(p)})
            if p < 0.05:
                names = list(groups.keys())
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        a, b = names[i], names[j]
                        u_stat, p_pair = stats.mannwhitneyu(groups[a], groups[b], alternative="two-sided", method="auto")
                        rows.append(
                            {
                                "hypothesis": "H4",
                                "model": model,
                                "platform": platform,
                                "test": "pairwise_mann_whitney",
                                "group_a": a,
                                "group_b": b,
                                "u": float(u_stat),
                                "p": float(p_pair),
                                "p_bonferroni": min(float(p_pair) * 3.0, 1.0),
                            }
                        )
    return rows


def _drop_largest_threads(df: pd.DataFrame) -> pd.DataFrame:
    """Exclude the largest thread (by comment count) per subreddit."""
    if "parent_post_id" not in df.columns or df.empty:
        return df
    exclude_ids: set = set()
    for _sub, g in df.groupby("subreddit"):
        counts = g["parent_post_id"].value_counts()
        if len(counts):
            exclude_ids.add(counts.index[0])
    return df[~df["parent_post_id"].isin(exclude_ids)].copy()


def run_h5(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, object]]:
    """Kruskal-Wallis and pairwise Mann-Whitney across Reddit subreddit categories."""
    rows: List[Dict[str, object]] = []
    for model in ("vader", "roberta"):
        rd_key = "reddit" if model == "vader" else "reddit_roberta"
        rd = clean_for_model(frames[rd_key], model).copy()
        rd["h5_category"] = rd["subreddit"].map(H5_SUBREDDIT_MAP)
        rd = rd[rd["h5_category"].notna()]

        subsets = [(h, h) for h in ("debby", "helene", "milton")]

        for subset_label, hurricane in subsets:
            sub_base = rd[rd["hurricane_norm"] == hurricane].copy()

            for variant_label in ("full", "excl_largest_thread"):
                if variant_label == "excl_largest_thread":
                    sub = _drop_largest_threads(sub_base)
                else:
                    sub = sub_base

                groups = {
                    cat: sub[sub["h5_category"] == cat]["score"].dropna().to_numpy()
                    for cat in ("expert", "local", "statewide")
                }
                present = {k: v for k, v in groups.items() if len(v) > 0}
                if len(present) < 2:
                    continue

                stat, p = stats.kruskal(*present.values())
                rows.append({
                    "hypothesis": "H5",
                    "model": model,
                    "subset": subset_label,
                    "variant": variant_label,
                    "test": "kruskal_wallis",
                    "category_a": np.nan,
                    "category_b": np.nan,
                    "stat": float(stat),
                    "p": float(p),
                    "p_bonferroni": np.nan,
                    "rank_biserial": np.nan,
                    "n_a": int(sum(len(v) for v in present.values())),
                    "n_b": np.nan,
                })

                skip_pairwise = (
                    model == "vader"
                    and subset_label == "helene"
                    and variant_label == "excl_largest_thread"
                )

                if p < 0.05 and not skip_pairwise:
                    pairs = [(a, b) for i, a in enumerate(sorted(present)) for b in sorted(present)[i + 1:]]
                    m_count = len(pairs)
                    for a, b in pairs:
                        u_stat, p_pair = stats.mannwhitneyu(
                            present[a],
                            present[b],
                            alternative="two-sided",
                            method="auto",
                        )
                        effect = rank_biserial_effect_size(float(u_stat), len(present[a]), len(present[b]))
                        rows.append({
                            "hypothesis": "H5",
                            "model": model,
                            "subset": subset_label,
                            "variant": variant_label,
                            "test": "pairwise_mann_whitney",
                            "category_a": a,
                            "category_b": b,
                            "stat": float(u_stat),
                            "p": float(p_pair),
                            "p_bonferroni": min(float(p_pair) * m_count, 1.0),
                            "rank_biserial": float(effect),
                            "n_a": int(len(present[a])),
                            "n_b": int(len(present[b])),
                        })

    return rows


def run_h7(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for model in ("vader", "roberta"):
        wh_key = "whitehouse" if model == "vader" else "whitehouse_roberta"
        rd_key = "reddit" if model == "vader" else "reddit_roberta"
        fb_key = "facebook" if model == "vader" else "facebook_roberta"
        wh = clean_for_model(frames[wh_key], model)
        reddit = clean_for_model(frames[rd_key], model)
        facebook = clean_for_model(frames[fb_key], model)

        wh_score = wh["score"].dropna().to_numpy()
        reddit_score = reddit["score"].dropna().to_numpy()
        fb_score = facebook["score"].dropna().to_numpy()

        u_wh_reddit, p_wh_reddit = stats.mannwhitneyu(wh_score, reddit_score, alternative="two-sided", method="auto")
        levene_stat, levene_p = stats.levene(wh_score, reddit_score, center="median")
        rows.append({"hypothesis": "H7", "model": model, "comparison": "whitehouse_vs_reddit", "u": float(u_wh_reddit), "p": float(p_wh_reddit), "levene_stat": float(levene_stat), "levene_p": float(levene_p)})

        u_wh_fb, p_wh_fb = stats.mannwhitneyu(wh_score, fb_score, alternative="two-sided", method="auto")
        rows.append({"hypothesis": "H7", "model": model, "comparison": "whitehouse_vs_facebook", "u": float(u_wh_fb), "p": float(p_wh_fb)})

        keyword_terms = ["fema", "biden", "trump", "government", "conspiracy"]
        wh = wh.copy()
        text_lower = wh["text"].fillna("").astype(str).str.lower()
        wh["political_keyword"] = text_lower.apply(lambda value: any(term in value for term in keyword_terms))
        wh_keyword = wh.loc[wh["political_keyword"], "score"]
        wh_nonkeyword = wh.loc[~wh["political_keyword"], "score"]
        u_kw, p_kw = stats.mannwhitneyu(wh_keyword, wh_nonkeyword, alternative="two-sided", method="auto")
        rows.append({"hypothesis": "H7", "model": model, "comparison": "whitehouse_political_keywords", "u": float(u_kw), "p": float(p_kw), "keyword_n": int(len(wh_keyword)), "non_keyword_n": int(len(wh_nonkeyword))})
    return rows


def write_markdown(results: List[Dict[str, object]], out_path: Path) -> None:
    lines = ["# Hypothesis Testing Results", "", "Results generated from the VADER and RoBERTa sentiment files in the repository.", ""]

    h1_rows = [row for row in results if row["hypothesis"] == "H1"]
    if h1_rows:
        lines.extend(["## H1: Platform difference", "", "### Mann-Whitney U and rank-biserial effect size", "", "| model | subset | U | p-value | rank-biserial |", "| --- | --- | ---: | ---: | ---: |"])
        for row in h1_rows:
            lines.append(f"| {row['model']} | {row['subset']} | {row['u']:.3f} | {format_p(float(row['p']))} | {float(row['rank_biserial']):.3f} |")
        lines.extend(["", "### Chi-square on platform × sentiment label", "", "| model | subset | chi-square | p-value |", "| --- | --- | ---: | ---: |"])
        for row in h1_rows:
            if not np.isnan(row.get("chi2", np.nan)):
                lines.append(f"| {row['model']} | {row['subset']} | {float(row['chi2']):.3f} | {format_p(float(row['chi2_p']))} |")
        lines.append("")

    h2_rows = [row for row in results if row["hypothesis"] == "H2"]
    if h2_rows:
        lines.extend(["## H2: Temporal trajectory (OLS)", "",
                       "### OLS regression: compound ~ days_from_landfall", "",
                       "| model | subset | platform | N | slope (per day) | 95% CI | p | R² |",
                       "| --- | --- | --- | ---: | ---: | --- | ---: | ---: |"])
        for row in h2_rows:
            if row.get("platform") in ("facebook", "reddit") and not np.isnan(row.get("slope", float("nan"))):
                lines.append(
                    f"| {row['model']} | {row['subset']} | {row['platform']} | {int(row['n'])} |"
                    f" {float(row['slope']):+.5f} |"
                    f" [{float(row['ci_low']):+.5f}, {float(row['ci_high']):+.5f}] |"
                    f" {format_p(float(row['slope_p']))} | {float(row['r2']):.4f} |"
                )
        lines.extend(["", "### Interaction model: compound ~ days_from_landfall × platform", "",
                       "| model | subset | interaction coef (reddit − facebook slope) | interaction p | R² |",
                       "| --- | --- | ---: | ---: | ---: |"])
        for row in h2_rows:
            if row.get("platform") == "interaction" and not np.isnan(row.get("interaction_coef", float("nan"))):
                lines.append(
                    f"| {row['model']} | {row['subset']} | {float(row['interaction_coef']):+.5f} |"
                    f" {format_p(float(row['interaction_p']))} | {float(row['r2']):.4f} |"
                )
        lines.append("")

    h3_rows = [row for row in results if row["hypothesis"] == "H3"]
    if h3_rows:
        lines.extend(["## H3: Storm intensity interaction", "", "| model | hurricane | mean Facebook-Reddit gap | bootstrap p-value | 95% CI |", "| --- | --- | ---: | ---: | --- |"])
        for row in h3_rows:
            if "comparison" in row:
                continue
            lines.append(f"| {row['model']} | {row['hurricane']} | {float(row['gap']):.3f} | {format_p(float(row['bootstrap_p']))} | [{float(row['ci_low']):.3f}, {float(row['ci_high']):.3f}] |")
        lines.append("")
        for row in h3_rows:
            if "comparison" in row:
                lines.append(f"- [{row['model']}] {row['comparison']}: observed gap difference = {float(row['observed_diff']):.3f}; bootstrap p = {format_p(float(row['p']))}")
        lines.append("")

    h4_rows = [row for row in results if row["hypothesis"] == "H4"]
    if h4_rows:
        lines.extend(["## H4: Sequential exposure", "", "| model | platform | test | stat | p-value | details |", "| --- | --- | --- | ---: | ---: | --- |"])
        for row in h4_rows:
            if row.get("test") == "kruskal_wallis":
                lines.append(f"| {row['model']} | {row['platform']} | Kruskal-Wallis | {float(row['stat']):.3f} | {format_p(float(row['p']))} | 3 storms |")
            else:
                lines.append(f"| {row['model']} | {row['platform']} | pairwise MW | {float(row['u']):.3f} | {format_p(float(row['p']))} | {row['group_a']} vs {row['group_b']} (Bonferroni p = {format_p(float(row['p_bonferroni']))}) |")
        lines.append("")

    h5_rows = [row for row in results if row["hypothesis"] == "H5"]
    if h5_rows:
        lines.extend(["## H5: Reddit subreddit-category differences", "",
                       "Subreddit mapping — expert: r/TropicalWeather; local: r/tampa, r/sarasota; statewide: r/florida.", "",
                       "| model | subset | variant | test | category A | category B | statistic | p-value | Bonferroni p | rank-biserial |",
                       "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |"])
        for row in h5_rows:
            if row.get("test") == "kruskal_wallis":
                lines.append(
                    f"| {row['model']} | {row['subset']} | {row.get('variant', 'full')} | Kruskal-Wallis | — | — |"
                    f" H = {float(row['stat']):.3f} | {format_p(float(row['p']))} | — | — |"
                )
            else:
                lines.append(
                    f"| {row['model']} | {row['subset']} | {row.get('variant', 'full')} | pairwise MW | {row['category_a']} | {row['category_b']} |"
                    f" U = {float(row['stat']):.3f} | {format_p(float(row['p']))} |"
                    f" {format_p(float(row['p_bonferroni']))} | {float(row['rank_biserial']):.3f} |"
                )
        lines.append("")

    h7_rows = [row for row in results if row["hypothesis"] == "H7"]
    if h7_rows:
        lines.extend(["## H7: Government communication", "", "| model | comparison | statistic | p-value | details |", "| --- | --- | ---: | ---: | --- |"])
        for row in h7_rows:
            if row["comparison"] == "whitehouse_vs_reddit":
                lines.append(f"| {row['model']} | WH comments vs Reddit community | U = {float(row['u']):.3f}; Levene statistic = {float(row['levene_stat']):.3f} | p(U) = {format_p(float(row['p']))}; p(Levene) = {format_p(float(row['levene_p']))} | variance/polarization check |")
            elif row["comparison"] == "whitehouse_vs_facebook":
                lines.append(f"| {row['model']} | WH comments vs Phillips Facebook | U = {float(row['u']):.3f} | p = {format_p(float(row['p']))} | direct platform comparison |")
            else:
                lines.append(f"| {row['model']} | WH comments with political keywords vs without | U = {float(row['u']):.3f} | p = {format_p(float(row['p']))} | n(keyword) = {row['keyword_n']}; n(non-keyword) = {row['non_keyword_n']} |")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    frames = load_comment_frames()
    results = []
    results.extend(run_h1(frames))
    results.extend(run_h2(frames))
    results.extend(run_h3(frames))
    results.extend(run_h4(frames))
    results.extend(run_h5(frames))
    results.extend(run_h7(frames))
    write_markdown(results, MERGED_DIR / "hypothesis_tests_results_angelo.md")
    pd.DataFrame(results).to_csv(MERGED_DIR / "hypothesis_tests_results_angelo.csv", index=False)
    print(f"Wrote {MERGED_DIR / 'hypothesis_tests_results_angelo.md'}")
    print(f"Wrote {MERGED_DIR / 'hypothesis_tests_results_angelo.csv'}")


if __name__ == "__main__":
    main()
