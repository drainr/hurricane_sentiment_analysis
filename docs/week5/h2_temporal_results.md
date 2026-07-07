# H2 — Temporal Trajectory Results

Unit: audience comments. Facebook = Phillips comments; Reddit = community_discussion comments.
Compound scores in event windows (Debby -5..0, Helene -4..+1, Milton -5..0).
N: Facebook comments = 59,736; Reddit community comments = 121,053.

## VADER (compound)

| platform | N | slope (per day toward +) | 95% CI | p | R^2 |
|---|---|---|---|---|---|
| Facebook | 59,736 | -0.00279 | [-0.00500, -0.00057] | 1.36e-02 | 0.0001 |
| Reddit | 121,053 | +0.00256 | [+0.00068, +0.00444] | 7.50e-03 | 0.0001 |

**Interaction (Reddit slope − Facebook slope):** +0.00535 [+0.00229, +0.00841], p = 6.13e-04 → Reddit slope significantly more POSITIVE than Facebook (Reddit declines LESS / rises) ⇒ H2 NOT supported; runs opposite to the prediction.
  (Facebook slope -0.00279, Reddit slope +0.00256; R² ≈ 0.0001/0.0001 — the linear day-effect is very weak either way.)

Per-hurricane slopes:

| hurricane | FB slope (p) | Reddit slope (p) |
|---|---|---|
| debby | -0.01370 (4.0e-10) | -0.00663 (7.1e-02) |
| helene | -0.00814 (4.4e-03) | -0.01617 (2.9e-14) |
| milton | +0.00642 (5.4e-05) | +0.00488 (1.7e-04) |

## RoBERTa (pos − neg)

| platform | N | slope (per day toward +) | 95% CI | p | R^2 |
|---|---|---|---|---|---|
| Facebook | 59,736 | +0.00436 | [+0.00132, +0.00741] | 4.99e-03 | 0.0001 |
| Reddit | 121,053 | +0.00800 | [+0.00597, +0.01003] | 1.09e-14 | 0.0005 |

**Interaction (Reddit slope − Facebook slope):** +0.00364 [+0.00008, +0.00721], p = 4.54e-02 → Reddit slope significantly more POSITIVE than Facebook (Reddit declines LESS / rises) ⇒ H2 NOT supported; runs opposite to the prediction.
  (Facebook slope +0.00436, Reddit slope +0.00800; R² ≈ 0.0001/0.0005 — the linear day-effect is very weak either way.)

Per-hurricane slopes:

| hurricane | FB slope (p) | Reddit slope (p) |
|---|---|---|
| debby | -0.02290 (2.0e-13) | -0.00512 (2.1e-01) |
| helene | -0.01086 (5.9e-03) | -0.02234 (4.6e-21) |
| milton | +0.03022 (5.0e-46) | +0.01230 (4.6e-19) |

## VADER vs RoBERTa cross-check

- Interaction sign agrees across methods: YES (VADER +0.00535 p=6.1e-04; RoBERTa +0.00364 p=4.5e-02).
- Both methods give a **positive** Reddit−Facebook interaction, i.e. Reddit does NOT decline more steeply than Facebook over the window — **H2 is not supported** in the pooled linear model (and R² is ~0, so the linear day-trend is weak for both).
- The picture is storm-dependent (see per-hurricane tables): Debby shows a Facebook decline, Helene a sharp Reddit decline, Milton a rise on both — so a single pooled slope conflates approach and post-landfall recovery (Helene/Milton windows include day +1 / day 0).

## In-window White House comments (plotted on F2)

- Debby window (-5, 0): 0 in-window (WH activity outside window)
- Helene window (-4, 1): 0 in-window (WH activity outside window)
- Milton window (-5, 0): 140 in-window (day 0: 140)

## Figures
- `figures/h2_temporal_curves.png/.pdf` (VADER) — 3 panels, FB+Reddit all panels, WH on Milton only.
- `figures/h2_temporal_curves_roberta.png/.pdf` (RoBERTa cross-check).
- Note: in-window WH comments exist only for Milton (day 0 only — the 140 government_response comments on landfall day; the other 90 WH Milton comments fall on days 1–7, post-landfall and outside the −5..0 window, so they are correctly clipped from this figure). Helene WH activity is outside the −4..+1 window.
