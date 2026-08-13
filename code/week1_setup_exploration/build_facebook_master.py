"""
Build facebook_master.csv from the 6 raw xlsx files in DataFolder.

Schema (per the advisor's spec):
    id, type, platform, hurricane, days_from_landfall,
    source (phillips/dee), author, created_date, text

Decisions captured 2026-06-01 with Jose:
- author = "Denis Phillips" for phillips source, "Greg Dee" for dee source (Q1: A)
- comment created_date = parent post's date (Q2: inherit)
- Helene's embedded VADER columns dropped — schema doesn't include them; we re-score in Week 2
- Greg Dee files are posts-only (no comment threads in raw); we record that
"""
import pandas as pd, pathlib, re, datetime as dt, csv

# Paths anchor to the repo root so the script runs from any working directory
# (same idiom as the rest of code/). Recovered in the Week 8 reproducibility
# pass: the original constants were absolute paths into a scratch folder
# outside the repo and an Obsidian vault, neither of which a reader has.
REPO     = pathlib.Path(__file__).resolve().parents[2]
ROOT     = REPO / "data" / "facebook" / "raw_xlsx"
OUT_CSV  = REPO / "data" / "facebook" / "facebook_master.csv"
OUT_LOG  = REPO / "docs" / "week1" / "facebook_build_log.txt"

LANDFALL = {
    "Debby":  dt.date(2024, 8, 5),
    "Helene": dt.date(2024, 9, 26),
    "Milton": dt.date(2024, 10, 9),
}

logs = []
def log(msg):
    """Print a message and keep it for the build log written at the end."""
    print(msg); logs.append(msg)

def days_from_landfall(d: dt.date, hurricane: str) -> int:
    """Days between a date and the hurricane's landfall (negative = before)."""
    return (d - LANDFALL[hurricane]).days

def parse_helene_date(s: str) -> dt.date:
    """Parse Helene's string dates, e.g. 'Sep 23rd, 2024' -> date(2024, 9, 23).

    Helene's spreadsheet stores dates as text with an ordinal suffix, unlike
    Debby's and Milton's, which Excel stores as real dates.
    """
    # 'Sep 23rd, 2024' -> date(2024,9,23)
    m = re.match(r"([A-Za-z]+)\s+(\d+)\w*,\s*(\d{4})", str(s).strip())
    if not m: raise ValueError(f"bad Helene date: {s!r}")
    mo, day, yr = m.group(1), int(m.group(2)), int(m.group(3))
    return dt.datetime.strptime(f"{mo} {day} {yr}", "%b %d %Y").date()

def to_date(v) -> dt.date | None:
    """Coerce any of the spreadsheets' date representations to a date, or None.

    Handles real datetimes, pandas Timestamps, Helene's ordinal strings, and
    anything else pandas can parse. Returns None rather than raising so a bad
    cell skips one row instead of failing the whole build.
    """
    if v is None or (isinstance(v, float) and pd.isna(v)): return None
    if isinstance(v, dt.datetime): return v.date()
    if isinstance(v, dt.date): return v
    if isinstance(v, pd.Timestamp): return v.to_pydatetime().date()
    s = str(v).strip()
    if not s: return None
    try: return parse_helene_date(s)
    except Exception: pass
    try: return pd.to_datetime(s).date()
    except Exception: return None

def make_id(source, hurricane, post_id, kind, idx=None):
    """Build a stable row id, e.g. 'phi_deb_12' for a post, 'phi_deb_12_c003' for a comment."""
    base = f"{source[:3]}_{hurricane[:3].lower()}_{post_id}"
    return base if kind == "post" else f"{base}_c{idx:03d}"

_PLACEHOLDERS = {"", "n/a", "na", "nan", "none", "null", "-"}

def clean_text(v) -> str:
    """Strip a cell and blank out placeholder values.

    The raw files use 'N/A', 'none', '-' and similar to mean 'nothing here'.
    Leaving them in would create ghost rows, so they collapse to an empty string.
    """
    if v is None or (isinstance(v, float) and pd.isna(v)): return ""
    s = str(v).strip()
    if s.lower() in _PLACEHOLDERS: return ""
    return s

# ──────────────────────────────────────────────────────────────────────────
# Phillips readers
# ──────────────────────────────────────────────────────────────────────────
def read_phillips_debby(rows):
    """DebbySpreadsheetPhillips.xlsx: PostInfo (Post_ID, Date, Time, Text_Post) +
    one comment-sheet per post named like 'July31_1' where the post text is the
    column header and each row is a comment string."""
    path = ROOT / "DebbySpreadsheetPhillips.xlsx"
    xl = pd.ExcelFile(path)
    info = pd.read_excel(path, sheet_name="PostInfo")
    post_dates = {}
    for _, r in info.iterrows():
        pid = str(r["Post_ID"])
        d = to_date(r["Date"])
        if d is None: continue
        post_dates[pid] = d
        rows.append({
            "id": make_id("phillips", "Debby", pid, "post"),
            "type": "post", "platform": "facebook", "hurricane": "Debby",
            "days_from_landfall": days_from_landfall(d, "Debby"),
            "source": "phillips", "author": "Denis Phillips",
            "created_date": d.isoformat(),
            "text": clean_text(r["Text_Post"]),
        })
    # comments
    for sheet in xl.sheet_names:
        if sheet == "PostInfo": continue
        pid = sheet
        d = post_dates.get(pid)
        if d is None:
            log(f"  [Debby DP] comment sheet {sheet!r} has no parent in PostInfo — skipped")
            continue
        df = pd.read_excel(path, sheet_name=sheet)
        # the single column header IS the post text; the values are comments
        col = df.columns[0]
        for i, val in enumerate(df[col], 1):
            t = clean_text(val)
            if not t: continue
            rows.append({
                "id": make_id("phillips", "Debby", pid, "comment", i),
                "type": "comment", "platform": "facebook", "hurricane": "Debby",
                "days_from_landfall": days_from_landfall(d, "Debby"),
                "source": "phillips", "author": "Denis Phillips",
                "created_date": d.isoformat(), "text": t,
            })

def read_phillips_helene(rows):
    """HDPD_Data.xlsx: 'Fixed Post Details' (Post Text, _, Post ID, Date, Time, +VADER) +
    per-post sheets named with integers. Helene dates are STRINGS like 'Sep 23rd, 2024'."""
    path = ROOT / "HDPD_Data.xlsx"
    xl = pd.ExcelFile(path)
    info = pd.read_excel(path, sheet_name="Fixed Post Details")
    post_dates = {}
    for _, r in info.iterrows():
        pid_raw = r.get("Post ID")
        if pd.isna(pid_raw): continue
        pid = str(int(pid_raw)) if isinstance(pid_raw, (int, float)) else str(pid_raw).strip()
        d = to_date(r.get("Date"))
        if d is None: continue
        post_dates[pid] = d
        rows.append({
            "id": make_id("phillips", "Helene", pid, "post"),
            "type": "post", "platform": "facebook", "hurricane": "Helene",
            "days_from_landfall": days_from_landfall(d, "Helene"),
            "source": "phillips", "author": "Denis Phillips",
            "created_date": d.isoformat(),
            "text": clean_text(r.get("Post Text")),
        })
    # comments — sheets are bare integer names
    for sheet in xl.sheet_names:
        if sheet in {"Instructions", "Fixed Post Details"}: continue
        pid = str(sheet).strip()
        d = post_dates.get(pid)
        if d is None:
            log(f"  [Helene DP] comment sheet {sheet!r} has no parent post — skipped")
            continue
        df = pd.read_excel(path, sheet_name=sheet)
        col = df.columns[0]
        for i, val in enumerate(df[col], 1):
            t = clean_text(val)
            if not t: continue
            rows.append({
                "id": make_id("phillips", "Helene", pid, "comment", i),
                "type": "comment", "platform": "facebook", "hurricane": "Helene",
                "days_from_landfall": days_from_landfall(d, "Helene"),
                "source": "phillips", "author": "Denis Phillips",
                "created_date": d.isoformat(), "text": t,
            })

def read_phillips_milton(rows):
    """MiltonSentiment.xlsx: PostInfo (Post_ID, Date, Time, Text_Post, Shares) +
    per-post 'Milton_<n>' sheets."""
    path = ROOT / "MiltonSentiment.xlsx"
    xl = pd.ExcelFile(path)
    info = pd.read_excel(path, sheet_name="PostInfo")
    post_dates = {}
    for _, r in info.iterrows():
        pid_raw = r["Post_ID"]
        if pd.isna(pid_raw): continue
        pid = str(int(pid_raw)) if isinstance(pid_raw, (int, float)) else str(pid_raw).strip()
        d = to_date(r["Date"])
        if d is None: continue
        # Data-quality fix: PostInfo row for Post_ID=9 is dated 2025-10-05;
        # raw source typo by the Fall-24 student. Clamp 2025 → 2024.
        if d.year == 2025:
            log(f"  [Milton DP] FIX: post {pid} date {d} → 2024 (raw typo)")
            d = d.replace(year=2024)
        post_dates[pid] = d
        rows.append({
            "id": make_id("phillips", "Milton", pid, "post"),
            "type": "post", "platform": "facebook", "hurricane": "Milton",
            "days_from_landfall": days_from_landfall(d, "Milton"),
            "source": "phillips", "author": "Denis Phillips",
            "created_date": d.isoformat(),
            "text": clean_text(r["Text_Post"]),
        })
    for sheet in xl.sheet_names:
        if sheet == "PostInfo": continue
        m = re.match(r"Milton_(\d+)", sheet)
        if not m:
            log(f"  [Milton DP] unexpected sheet name {sheet!r} — skipped"); continue
        pid = m.group(1)
        d = post_dates.get(pid)
        if d is None:
            log(f"  [Milton DP] comment sheet {sheet!r} has no parent — skipped"); continue
        df = pd.read_excel(path, sheet_name=sheet)
        col = df.columns[0]
        for i, val in enumerate(df[col], 1):
            t = clean_text(val)
            if not t: continue
            rows.append({
                "id": make_id("phillips", "Milton", pid, "comment", i),
                "type": "comment", "platform": "facebook", "hurricane": "Milton",
                "days_from_landfall": days_from_landfall(d, "Milton"),
                "source": "phillips", "author": "Denis Phillips",
                "created_date": d.isoformat(), "text": t,
            })

# ──────────────────────────────────────────────────────────────────────────
# Greg Dee readers — posts-only, day-sheets, post-text-as-header convention
# ──────────────────────────────────────────────────────────────────────────
GD_DATE_PATTERNS = {
    # Debby — 'GregDeeJuly31st','GregDeeAug1'..'GregDeeAug5'
    "GregDeeDebbie.xlsx": {
        "GregDeeJuly31st": dt.date(2024, 7, 31),
        "GregDeeAug1": dt.date(2024, 8, 1), "GregDeeAug2": dt.date(2024, 8, 2),
        "GregDeeAug3": dt.date(2024, 8, 3), "GregDeeAug4": dt.date(2024, 8, 4),
        "GregDeeAug5": dt.date(2024, 8, 5),
    },
    # Helene — 'GregDee23'..'GregDee27' = Sep 23..27 2024
    "GregDeeHelene.xlsx": {f"GregDee{d}": dt.date(2024, 9, d) for d in range(23, 28)},
    # Milton — 'GregDeeOct5'..'GregDeeOct9'
    "GregDeeMilton.xlsx": {f"GregDeeOct{d}": dt.date(2024, 10, d) for d in range(5, 10)},
}
GD_HURRICANE = {"GregDeeDebbie.xlsx": "Debby",
                "GregDeeHelene.xlsx": "Helene",
                "GregDeeMilton.xlsx": "Milton"}

def read_greg_dee(rows):
    """Read all three Greg Dee workbooks into rows. Posts only.

    The raw files carry no comment threads for Dee, and each day-sheet uses the
    post text as the column header with further posts in the rows beneath it.
    """
    for fname, sheet_dates in GD_DATE_PATTERNS.items():
        path = ROOT / fname
        hurr = GD_HURRICANE[fname]
        xl = pd.ExcelFile(path)
        for sheet in xl.sheet_names:
            d = sheet_dates.get(sheet)
            if d is None:
                log(f"  [GD {hurr}] unknown sheet {sheet!r} — skipped"); continue
            df = pd.read_excel(path, sheet_name=sheet)
            col = df.columns[0]
            # post #1 lives in the column HEADER itself
            header_text = clean_text(col)
            post_counter = 0
            if header_text:
                post_counter += 1
                rows.append({
                    "id": make_id("dee", hurr, f"{sheet}_{post_counter}", "post"),
                    "type": "post", "platform": "facebook", "hurricane": hurr,
                    "days_from_landfall": days_from_landfall(d, hurr),
                    "source": "dee", "author": "Greg Dee",
                    "created_date": d.isoformat(), "text": header_text,
                })
            for val in df[col]:
                t = clean_text(val)
                if not t: continue
                post_counter += 1
                rows.append({
                    "id": make_id("dee", hurr, f"{sheet}_{post_counter}", "post"),
                    "type": "post", "platform": "facebook", "hurricane": hurr,
                    "days_from_landfall": days_from_landfall(d, hurr),
                    "source": "dee", "author": "Greg Dee",
                    "created_date": d.isoformat(), "text": t,
                })

# ──────────────────────────────────────────────────────────────────────────
def main():
    """Read all six workbooks, write facebook_master.csv, and save the build log."""
    rows = []
    log("Reading Phillips/Debby ..."); read_phillips_debby(rows);  log(f"  running total: {len(rows)}")
    log("Reading Phillips/Helene ..."); read_phillips_helene(rows); log(f"  running total: {len(rows)}")
    log("Reading Phillips/Milton ..."); read_phillips_milton(rows); log(f"  running total: {len(rows)}")
    log("Reading Greg Dee (all 3) ..."); read_greg_dee(rows);        log(f"  running total: {len(rows)}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    cols = ["id","type","platform","hurricane","days_from_landfall",
            "source","author","created_date","text"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows: w.writerow(r)
    log(f"\nWROTE {OUT_CSV}  ({len(rows)} rows)")

    OUT_LOG.write_text("\n".join(logs))

if __name__ == "__main__":
    main()
