"""Fetch the public GitHub contribution calendar and save data/contributions.json."""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "CodeRuNNer-ai"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    # Counts live in <tool-tip for="<cell id>">3 contributions on ...</tool-tip>
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        text = tips.get(td.get("id"), "")
        m = re.match(r"(\d+)\s+contribution", text)
        count = int(m.group(1)) if m else 0
        days.append({"date": d, "count": count, "level": int(td.get("data-level", 0))})
    days.sort(key=lambda x: x["date"])
    return days


def stats(days: list[dict]) -> dict:
    today = date.today()
    by_date = {d["date"]: d["count"] for d in days}

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    # Current streak: count back from today (or yesterday if today is still empty)
    cursor = today
    if by_date.get(cursor.isoformat(), 0) == 0:
        cursor -= timedelta(days=1)
    current = 0
    while by_date.get(cursor.isoformat(), 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    best = max(days, key=lambda x: x["count"]) if days else {"date": "", "count": 0}
    monthly: dict[str, int] = {}
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]

    return {
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly,
    }


def main() -> None:
    url = f"https://github.com/users/{USERNAME}/contributions"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (profile-art)"}, timeout=30)
    r.raise_for_status()
    days = parse(r.text)
    if not days:
        sys.exit("No contribution cells found - GitHub's HTML may have changed.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"username": USERNAME, "days": days, "stats": stats(days)}, indent=1))
    print(f"Saved {len(days)} days to {OUT}")


if __name__ == "__main__":
    main()
