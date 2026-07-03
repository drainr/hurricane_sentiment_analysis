from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
VADER_DIR = DATA_DIR / "vader"
ROBERTA_DIR = DATA_DIR / "roberta"
MERGED_DIR = DATA_DIR / "merged"
MERGED_DIR.mkdir(parents=True, exist_ok=True)

LABEL_ORDER = ["negative", "neutral", "positive"]


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
    fb = pd.read_csv(VADER_DIR / "facebook_comments_vader.csv")
    reddit = pd.read_csv(VADER_DIR / "reddit_relevant_vader_comments.csv")
    wh = pd.read_csv(VADER_DIR / "whitehouse_threads_comments_vader.csv")
    fb_roberta = pd.read_csv(ROBERTA_DIR / "facebook_comments_vader_roberta.csv")
    reddit_roberta = pd.read_csv(ROBERTA_DIR / "reddit_relevant_comments_vader_roberta.csv")
    wh_roberta = pd.read_csv(ROBERTA_DIR / "whitehouse_threads_comments_vader_roberta.csv")

    for frame in (fb, reddit, wh, fb_roberta, reddit_roberta, wh_roberta):
        frame["hurricane_norm"] = normalize_hurricane_name(frame["hurricane"])

    return {
        "facebook": fb,
        "reddit": reddit,
        "whitehouse": wh,
        "facebook_roberta": fb_roberta,
        "reddit_roberta": reddit_roberta,
        "whitehouse_roberta": wh_roberta,
    }


def clean_for_model(df: pd.DataFrame, model: str) -> pd.DataFrame:
    out = df.copy()
    out = out.dropna(subset=["text"]).copy()
    if model == "vader":
        out["score"] = pd.to_numeric(out["vader_compound"], errors="coerce")
        out["label"] = out["vader_label"].astype(str).str.strip().str.lower()
    elif model == "roberta":
        out["score"] = encode_roberta_labels(out["roberta_label"])
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
    for hurricane in ("debby", "helene", "milton"):
        fb = clean_for_model(frames["facebook"], "vader")
        rd = clean_for_model(frames["reddit"], "vader")
        fb_h = fb[fb["hurricane_norm"] == hurricane]
        rd_h = rd[rd["hurricane_norm"] == hurricane]
        gap = bootstrap_gap_difference(fb_h["score"], rd_h["score"], seed=100 + hash(hurricane) % 100)
        rows.append({"hypothesis": "H3", "hurricane": hurricane, "gap": gap["gap"], "bootstrap_p": gap["p"], "ci_low": gap["ci_low"], "ci_high": gap["ci_high"]})

    for other in ("helene", "milton"):
        debby = rows[0]
        other_row = next(item for item in rows if item["hurricane"] == other)
        observed_diff = other_row["gap"] - debby["gap"]
        fb_debby = clean_for_model(frames["facebook"], "vader")[clean_for_model(frames["facebook"], "vader")["hurricane_norm"] == "debby"]["score"]
        rd_debby = clean_for_model(frames["reddit"], "vader")[clean_for_model(frames["reddit"], "vader")["hurricane_norm"] == "debby"]["score"]
        fb_other = clean_for_model(frames["facebook"], "vader")[clean_for_model(frames["facebook"], "vader")["hurricane_norm"] == other]["score"]
        rd_other = clean_for_model(frames["reddit"], "vader")[clean_for_model(frames["reddit"], "vader")["hurricane_norm"] == other]["score"]
        result = bootstrap_gap_difference(fb_other, rd_other, seed=200 + hash(other) % 100)
        result["observed_diff"] = observed_diff
        result["comparison"] = f"debby_vs_{other}"
        rows.append({"hypothesis": "H3", **result})
    return rows


def run_h4(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for platform in ("reddit", "facebook"):
        df = clean_for_model(frames[platform], "vader")
        groups = {h: df.loc[df["hurricane_norm"] == h, "score"].dropna().to_numpy() for h in ("debby", "helene", "milton") if (df["hurricane_norm"] == h).any()}
        if len(groups) < 2:
            continue
        stat, p = stats.kruskal(*groups.values())
        rows.append({"hypothesis": "H4", "platform": platform, "test": "kruskal_wallis", "stat": float(stat), "p": float(p)})
        if p < 0.05:
            names = list(groups.keys())
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = names[i], names[j]
                    u_stat, p_pair = stats.mannwhitneyu(groups[a], groups[b], alternative="two-sided", method="auto")
                    rows.append(
                        {
                            "hypothesis": "H4",
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


def run_h7(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    wh = clean_for_model(frames["whitehouse"], "vader")
    reddit = clean_for_model(frames["reddit"], "vader")
    facebook = clean_for_model(frames["facebook"], "vader")

    wh_score = wh["score"].dropna().to_numpy()
    reddit_score = reddit["score"].dropna().to_numpy()
    fb_score = facebook["score"].dropna().to_numpy()

    u_wh_reddit, p_wh_reddit = stats.mannwhitneyu(wh_score, reddit_score, alternative="two-sided", method="auto")
    levene_stat, levene_p = stats.levene(wh_score, reddit_score, center="median")
    rows.append({"hypothesis": "H7", "comparison": "whitehouse_vs_reddit", "u": float(u_wh_reddit), "p": float(p_wh_reddit), "levene_stat": float(levene_stat), "levene_p": float(levene_p)})

    u_wh_fb, p_wh_fb = stats.mannwhitneyu(wh_score, fb_score, alternative="two-sided", method="auto")
    rows.append({"hypothesis": "H7", "comparison": "whitehouse_vs_facebook", "u": float(u_wh_fb), "p": float(p_wh_fb)})

    keyword_terms = ["fema", "biden", "trump", "government", "conspiracy"]
    text_lower = wh["text"].fillna("").astype(str).str.lower()
    wh["political_keyword"] = text_lower.apply(lambda value: any(term in value for term in keyword_terms))
    wh_keyword = wh.loc[wh["political_keyword"], "score"]
    wh_nonkeyword = wh.loc[~wh["political_keyword"], "score"]
    u_kw, p_kw = stats.mannwhitneyu(wh_keyword, wh_nonkeyword, alternative="two-sided", method="auto")
    rows.append({"hypothesis": "H7", "comparison": "whitehouse_political_keywords", "u": float(u_kw), "p": float(p_kw), "keyword_n": int(len(wh_keyword)), "non_keyword_n": int(len(wh_nonkeyword))})
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

    h3_rows = [row for row in results if row["hypothesis"] == "H3"]
    if h3_rows:
        lines.extend(["## H3: Storm intensity interaction", "", "| hurricane | mean Facebook-Reddit gap | bootstrap p-value | 95% CI |", "| --- | ---: | ---: | --- |"])
        for row in h3_rows:
            if "comparison" in row:
                continue
            lines.append(f"| {row['hurricane']} | {float(row['gap']):.3f} | {format_p(float(row['bootstrap_p']))} | [{float(row['ci_low']):.3f}, {float(row['ci_high']):.3f}] |")
        lines.append("")
        for row in h3_rows:
            if "comparison" in row:
                lines.append(f"- {row['comparison']}: observed gap difference = {float(row['observed_diff']):.3f}; bootstrap p = {format_p(float(row['p']))}")
        lines.append("")

    h4_rows = [row for row in results if row["hypothesis"] == "H4"]
    if h4_rows:
        lines.extend(["## H4: Sequential exposure", "", "| platform | test | stat | p-value | details |", "| --- | --- | ---: | ---: | --- |"])
        for row in h4_rows:
            if row.get("test") == "kruskal_wallis":
                lines.append(f"| {row['platform']} | Kruskal-Wallis | {float(row['stat']):.3f} | {format_p(float(row['p']))} | 3 storms |")
            else:
                lines.append(f"| {row['platform']} | pairwise MW | {float(row['u']):.3f} | {format_p(float(row['p']))} | {row['group_a']} vs {row['group_b']} (Bonferroni p = {format_p(float(row['p_bonferroni']))}) |")
        lines.append("")

    h7_rows = [row for row in results if row["hypothesis"] == "H7"]
    if h7_rows:
        lines.extend(["## H7: Government communication", "", "| comparison | statistic | p-value | details |", "| --- | ---: | ---: | --- |"])
        for row in h7_rows:
            if row["comparison"] == "whitehouse_vs_reddit":
                lines.append(f"| WH comments vs Reddit community | U = {float(row['u']):.3f}; Levene statistic = {float(row['levene_stat']):.3f} | p(U) = {format_p(float(row['p']))}; p(Levene) = {format_p(float(row['levene_p']))} | variance/polarization check |")
            elif row["comparison"] == "whitehouse_vs_facebook":
                lines.append(f"| WH comments vs Phillips Facebook | U = {float(row['u']):.3f} | p = {format_p(float(row['p']))} | direct platform comparison |")
            else:
                lines.append(f"| WH comments with political keywords vs without | U = {float(row['u']):.3f} | p = {format_p(float(row['p']))} | n(keyword) = {row['keyword_n']}; n(non-keyword) = {row['non_keyword_n']} |")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    frames = load_comment_frames()
    results = []
    results.extend(run_h1(frames))
    results.extend(run_h3(frames))
    results.extend(run_h4(frames))
    results.extend(run_h7(frames))
    write_markdown(results, MERGED_DIR / "hypothesis_tests_results.md")
    pd.DataFrame(results).to_csv(MERGED_DIR / "hypothesis_tests_results.csv", index=False)
    print(f"Wrote {MERGED_DIR / 'hypothesis_tests_results.md'}")
    print(f"Wrote {MERGED_DIR / 'hypothesis_tests_results.csv'}")


if __name__ == "__main__":
    main()
