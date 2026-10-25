"""Convert source-prepped.png into a self-typing ASCII-art SVG.

Usage:   python scripts/make_ascii_svg.py
Output:  ascii-portrait.svg   (animated, plays once and freezes)
Preview: set STATIC=1 to write a frozen, fully-printed frame instead
         (PowerShell:  $env:STATIC=1; python scripts/make_ascii_svg.py)
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "ascii-portrait.svg"

COLS = 100               # characters per row
RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space = blank
FILL = "#c9d1d9"         # one light-gray colour (monochrome looks cleaner)
BG = "#0d1117"
CHAR_W, ROW_H, FONT = 6.0, 10.0, 10
PAD = 14
ROW_DUR, ROW_STAGGER = 0.7, 0.06   # seconds per row wipe / delay between rows
STATIC = os.environ.get("STATIC") == "1"


KEEP_HEIGHT = 0.60   # keep the top 60% of the photo (head + shoulders)
LIGHTEST = 225       # brightest printed tone (255 would vanish into the background)


def to_rows() -> list[str]:
    img = Image.open(SRC).convert("L")

    # Keep head and shoulders, then trim blank white margins
    img = img.crop((0, 0, img.width, int(img.height * KEEP_HEIGHT)))
    box = img.point(lambda p: 255 if p < 245 else 0).getbbox()
    if box:
        img = img.crop(box)

    # Stretch contrast over the subject only (background stays pure white)
    a = np.array(img, dtype=np.float32)
    subject = a < 245
    if subject.sum() > 100:
        lo, hi = np.percentile(a[subject], [2, 98])
        scaled = np.clip((a - lo) / max(hi - lo, 1.0), 0, 1) * LIGHTEST
        a = np.where(subject, scaled, 255.0)
    img = Image.fromarray(a.astype(np.uint8), "L")

    # characters are ~1.67x taller than wide, so squash the height to match
    rows = max(1, round(COLS * img.height / img.width * (CHAR_W / ROW_H)))
    img = img.resize((COLS, rows), Image.LANCZOS)
    px = img.load()
    out = []
    for y in range(rows):
        line = ""
        for x in range(COLS):
            idx = int((255 - px[x, y]) / 255 * (len(RAMP) - 1) + 0.5)
            line += RAMP[idx]
        out.append(line)
    return out


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"{SRC.name} not found. Run prep_photo.py first.")
    rows = to_rows()
    row_w = COLS * CHAR_W
    width = row_w + PAD * 2
    height = len(rows) * ROW_H + PAD * 2

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">',
        f'<rect width="{width:.0f}" height="{height:.0f}" rx="10" fill="{BG}"/>',
        "<defs>",
    ]
    for i in range(len(rows)):
        w0 = row_w if STATIC else 0
        begin = i * ROW_STAGGER
        anim = "" if STATIC else (
            f'<animate attributeName="width" from="0" to="{row_w}" begin="{begin:.2f}s" '
            f'dur="{ROW_DUR}s" fill="freeze"/>'
        )
        s.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{PAD + i * ROW_H}" width="{w0}" '
            f'height="{ROW_H}">{anim}</rect></clipPath>'
        )
    s.append("</defs>")

    s.append(f'<g font-family="Consolas,Menlo,monospace" font-size="{FONT}" fill="{FILL}" xml:space="preserve">')
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        y = PAD + i * ROW_H + ROW_H * 0.8
        s.append(
            f'<text x="{PAD}" y="{y:.1f}" textLength="{row_w}" lengthAdjust="spacing" '
            f'clip-path="url(#r{i})">{escape(line)}</text>'
        )
    s.append("</g>")

    if not STATIC:  # block cursor riding the wipe edge of each row
        for i, line in enumerate(rows):
            if not line.strip():
                continue
            b = i * ROW_STAGGER
            y = PAD + i * ROW_H
            s.append(
                f'<rect x="{PAD}" y="{y}" width="{CHAR_W}" height="{ROW_H}" fill="{FILL}" opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{b:.2f}s"/>'
                f'<animate attributeName="x" from="{PAD}" to="{PAD + row_w - CHAR_W}" begin="{b:.2f}s" '
                f'dur="{ROW_DUR}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0" begin="{b + ROW_DUR:.2f}s"/></rect>'
            )

    s.append("</svg>")
    OUT.write_text("\n".join(s), encoding="utf-8")
    print(f"Wrote {OUT} ({COLS}x{len(rows)} characters{', static' if STATIC else ''})")


if __name__ == "__main__":
    main()
