# Hypothesis Tests — H1, H3, H4, H7 (VADER + RoBERTa)

Comments only. FB=Phillips, Reddit=community_discussion, WH=government_response.
Effect size = rank-biserial (MWU); positive ⇒ first group scores higher.

## H1 — FB (Phillips) vs Reddit community compound

Prediction: Reddit shows significantly LOWER compound than Facebook.

### VADER
| scope | n(FB) | n(Reddit) | mean FB | mean Reddit | U | p | rank-biserial |
|---|---|---|---|---|---|---|---|
| overall | 59,736 | 121,053 | 0.170 | 0.059 | 4080853682 | 0.00e+00 | +0.129 |
| debby | 16,199 | 8,766 | 0.199 | 0.086 | 80092146 | 1.06e-64 | +0.128 |
| helene | 14,229 | 32,948 | 0.192 | 0.078 | 266146258 | 6.92e-124 | +0.135 |
| milton | 29,308 | 79,339 | 0.144 | 0.048 | 1288405580 | 3.62e-169 | +0.108 |

Chi-square platform×vader_label: χ²(2)=4492.4, p=0.00e+00, Cramér's V=0.158.

### RoBERTa
| scope | n(FB) | n(Reddit) | mean FB | mean Reddit | U | p | rank-biserial |
|---|---|---|---|---|---|---|---|
| overall | 59,736 | 121,053 | 0.048 | -0.232 | 4683262614 | 0.00e+00 | +0.295 |
| debby | 16,199 | 8,766 | 0.115 | -0.203 | 94042964 | 0.00e+00 | +0.325 |
| helene | 14,229 | 32,948 | 0.087 | -0.199 | 305703714 | 0.00e+00 | +0.304 |
| milton | 29,308 | 79,339 | -0.008 | -0.248 | 1464275248 | 0.00e+00 | +0.259 |

Chi-square platform×roberta_label: χ²(2)=9059.5, p=0.00e+00, Cramér's V=0.224.

## H3 — FB−Reddit compound gap by storm (Debby < Helene, Debby < Milton)

### VADER
| gap_debby | gap_helene | gap_milton | Debby smallest? |
|---|---|---|---|
| 0.113 | 0.114 | 0.096 | NO → not supported |

### RoBERTa
| gap_debby | gap_helene | gap_milton | Debby smallest? |
|---|---|---|---|
| 0.318 | 0.286 | 0.240 | NO → not supported |

## H4 — Cross-storm differences within each platform (Kruskal-Wallis)

Prediction: Reddit accumulates negativity across the sequence while FB stays stable.

### VADER
- **Reddit community**: KW H=115.6, p=7.80e-26; means debby=0.086, helene=0.078, milton=0.048.
  - pairwise (Bonferroni×3): debbyvshelene p=1.9e-01 (r=+0.01); debbyvsmilton p=2.1e-12 (r=+0.05); helenevsmilton p=2.6e-19 (r=+0.03)
- **Facebook**: KW H=248.7, p=1.01e-54; means debby=0.199, helene=0.192, milton=0.144.
  - pairwise (Bonferroni×3): debbyvshelene p=2.6e-01 (r=+0.01); debbyvsmilton p=7.5e-44 (r=+0.08); helenevsmilton p=7.1e-31 (r=+0.07)

### RoBERTa
- **Reddit community**: KW H=245.1, p=5.95e-54; means debby=-0.203, helene=-0.199, milton=-0.248.
  - pairwise (Bonferroni×3): debbyvshelene p=1.0e+00 (r=-0.01); debbyvsmilton p=4.9e-14 (r=+0.05); helenevsmilton p=8.4e-49 (r=+0.06)
- **Facebook**: KW H=644.0, p=1.41e-140; means debby=0.115, helene=0.087, milton=-0.008.
  - pairwise (Bonferroni×3): debbyvshelene p=2.8e-06 (r=+0.03); debbyvsmilton p=4.4e-119 (r=+0.13); helenevsmilton p=3.7e-67 (r=+0.10)

## H7 — White House thread comments polarization

(1) WH vs Reddit community, (2) WH vs FB Phillips, (3) within WH political vs non-political.

### VADER
- **WH vs Reddit community**: MWU U=128427604, p=8.56e-03, r=-0.032 (mean WH=0.024, Reddit=0.059); variance SD WH=0.516 vs Reddit=0.468, Levene W=62.7, p=2.40e-15.
- **WH vs FB Phillips**: MWU U=55524380, p=2.04e-35, r=-0.152 (mean WH=0.024, FB=0.170).
- **Within WH, political-keyword vs not** (644 vs 1549): MWU U=466718, p=1.72e-02, r=-0.064 (mean political=-0.022, non=0.043).

### RoBERTa
- **WH vs Reddit community**: MWU U=109785884, p=6.51e-44, r=-0.173 (mean WH=-0.363, Reddit=-0.232); variance SD WH=0.512 vs Reddit=0.506, Levene W=1.1, p=2.97e-01.
- **WH vs FB Phillips**: MWU U=36921021, p=1.04e-264, r=-0.436 (mean WH=-0.363, FB=0.048).
- **Within WH, political-keyword vs not** (644 vs 1549): MWU U=417404, p=1.69e-09, r=-0.163 (mean political=-0.476, non=-0.316).

