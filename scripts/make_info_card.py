"""Generate info-card.svg: a neofetch-style terminal card (860px wide).

EDIT THE `ROWS` LIST BELOW to change the text, then run:

    python scripts/make_info_card.py

Output: info-card.svg (lines fade in one after another, plays once, then stays).
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"

USER_HOST = "coderunner@github"
TITLE = "neofetch"

# (label, text, label colour)  <- edit freely, add or remove rows
ROWS = [
    ("Name",       "Abhijeet  (CodeRuNNer-ai)",                                   "#7ee787"),
    ("Now",        "MCA student · building frontend + backend web apps",          "#79c0ff"),
    ("Languages",  "JavaScript · HTML · CSS · EJS",                               "#ffa657"),
    ("Stack",      "React · Node.js · MongoDB",                                   "#79c0ff"),
    ("Tools",      "n8n · Git · GitHub Actions",                                  "#d2a8ff"),
    ("Projects",   "Personalized-Learning-System · Hospital-Appointment-App",     "#ff7b72"),
    ("Highlights", "9 public repos · learning something new every week",          "#7ee787"),
]

WIDTH = 860
PAD_X = 28
BAR_H = 38
ROW_H = 30
FONT = 15
KEY_W = 130          # width reserved for labels
BG, BAR, BORDER, TXT, DIM = "#0d1117", "#161b22", "#30363d", "#c9d1d9", "#8b949e"
STEP, DUR = 0.35, 0.45


def main() -> None:
    top = BAR_H + 22
    height = top + (len(ROWS) + 2) * ROW_H + 28
    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="Consolas,Menlo,\'DejaVu Sans Mono\',monospace" '
        f'font-size="{FONT}">',
        "<style>"
        ".l{animation:in .45s ease-out backwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}"
        "</style>",
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        f'<path d="M0.5 {BAR_H} V10.5 a10 10 0 0 1 10 -10 H{WIDTH - 10.5} a10 10 0 0 1 10 10 V{BAR_H} Z" fill="{BAR}"/>',
        f'<circle cx="24" cy="{BAR_H / 2}" r="6" fill="#ff5f56"/>',
        f'<circle cx="46" cy="{BAR_H / 2}" r="6" fill="#ffbd2e"/>',
        f'<circle cx="68" cy="{BAR_H / 2}" r="6" fill="#27c93f"/>',
        f'<text x="{WIDTH / 2}" y="{BAR_H / 2 + 5}" text-anchor="middle" fill="{DIM}" font-size="13">'
        f'{escape(USER_HOST)}: ~ — {escape(TITLE)}</text>',
    ]

    y = top + ROW_H
    s.append(
        f'<text class="l" style="animation-delay:0s" x="{PAD_X}" y="{y}">'
        f'<tspan fill="#7ee787">{escape(USER_HOST)}</tspan><tspan fill="{TXT}"> ~ $ </tspan>'
        f'<tspan fill="{TXT}">neofetch</tspan></text>'
    )
    y += ROW_H
    s.append(
        f'<text class="l" style="animation-delay:{STEP:.2f}s" x="{PAD_X}" y="{y}" fill="{DIM}">'
        f'{"─" * 52}</text>'
    )
    for i, (label, text, color) in enumerate(ROWS, start=2):
        y += ROW_H
        d = i * STEP
        s.append(
            f'<g class="l" style="animation-delay:{d:.2f}s">'
            f'<text x="{PAD_X}" y="{y}" fill="{color}" font-weight="bold">{escape(label)}</text>'
            f'<text x="{PAD_X + KEY_W}" y="{y}" fill="{TXT}">{escape(text)}</text></g>'
        )
    s.append("</svg>")
    OUT.write_text("\n".join(s), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
