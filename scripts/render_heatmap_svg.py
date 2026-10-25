"""Render data/contributions.json as an animated GitHub-style heatmap SVG."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 36, 44
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level(count: int, peak: int) -> int:
    if count <= 0:
        return 0
    if peak <= 4:
        return min(count, 4)
    q = count / peak
    return 1 if q <= 0.25 else 2 if q <= 0.5 else 3 if q <= 0.75 else 5 if q > 0.95 else 4


def main() -> None:
    data = json.loads(SRC.read_text())
    days, st = data["days"], data["stats"]
    peak = max((d["count"] for d in days), default=0)

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday = 0
    weeks = (offset + len(days) + 6) // 7
    width = LEFT + weeks * STEP + 20
    height = TOP + 7 * STEP + 56

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace,Consolas,monospace">',
        "<style>"
        ".c{animation:in .5s ease-out backwards}"
        "@keyframes in{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}"
        ".t{fill:#8b949e;font-size:10px}.s{fill:#c9d1d9;font-size:12px}"
        "</style>",
        f'<rect width="{width}" height="{height}" rx="10" fill="#0d1117"/>',
    ]

    for i, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text class="t" x="6" y="{TOP + i * STEP + 10}">{name}</text>')

    last_month = -1
    for i, d in enumerate(days):
        pos = i + offset
        col, row = pos // 7, pos % 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        dt = date.fromisoformat(d["date"])
        if dt.month != last_month and dt.day <= 7 and row <= 6:
            out.append(f'<text class="t" x="{x}" y="{TOP - 10}">{MONTHS[dt.month - 1]}</text>')
            last_month = dt.month
        lv = level(d["count"], peak)
        delay = round((col + row) * 0.018, 3)  # diagonal sweep
        out.append(
            f'<rect class="c" style="animation-delay:{delay}s" x="{x}" y="{y}" width="{CELL}" '
            f'height="{CELL}" rx="3" fill="{PALETTE[lv]}"><title>{d["count"]} on {d["date"]}</title></rect>'
        )

    fy = TOP + 7 * STEP + 24
    out.append(f'<text class="s" x="{LEFT}" y="{fy}">{st["total"]:,} contributions in the last year'
               f' · streak {st["current_streak"]}d · longest {st["longest_streak"]}d</text>')
    lx = width - 20 - (len(PALETTE) * STEP + 70)
    out.append(f'<text class="t" x="{lx}" y="{fy}">Less</text>')
    for i, c in enumerate(PALETTE):
        out.append(f'<rect x="{lx + 30 + i * STEP}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
    out.append(f'<text class="t" x="{lx + 34 + len(PALETTE) * STEP}" y="{fy}">More</text>')
    out.append("</svg>")

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
