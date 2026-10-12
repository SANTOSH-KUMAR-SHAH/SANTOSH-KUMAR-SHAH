#!/usr/bin/env python3
"""Build connect.svg: pointing character (me2.png, downscaled + inlined) on the
left, link cards with brand icons and nudging arrows on the right."""
import base64
import io
import json
import os
from PIL import Image
from fonts_def import FONTS_STYLE_ESCAPED

HERE = os.path.dirname(os.path.abspath(__file__))
icons_path = os.path.join(HERE, "assets", "icons.json") if os.path.exists(os.path.join(HERE, "assets", "icons.json")) else os.path.join(HERE, "profile", "assets", "icons.json")
ICONS = json.load(open(icons_path))
OUT = os.path.join(HERE, "connect.svg")

BG, CYAN, VIOLET, PINK, TEXT, MUTED = "#0d0e16", "#22d3ee", "#a78bfa", "#f472b6", "#e7e9f3", "#8b90a8"
W, H = 900, 360


def lum(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000


def color_for(slug, fb="#dfe3ff"):
    hx = ICONS.get(slug, {}).get("hex") or "ffffff"
    return fb if (lum(hx) < 95 or lum(hx) > 235) else "#" + hx


def icon(slug, size, color, cx=0, cy=0):
    s = size / 24.0
    return (f'<g transform="translate({cx},{cy}) scale({s:.4f}) translate(-12,-12)">'
            f'<path d="{ICONS[slug]["path"]}" fill="{color}"/></g>')


# ---- inline pointing character --------------------------------------------
me2_path = os.path.join(HERE, "assets", "me2.png") if os.path.exists(os.path.join(HERE, "assets", "me2.png")) else os.path.join(HERE, "profile", "assets", "me2.png")
img = Image.open(me2_path).convert("RGBA")
img.thumbnail((300, 330))
buf = io.BytesIO()
img.save(buf, "PNG", optimize=True)
CHAR = base64.b64encode(buf.getvalue()).decode("ascii")
print("character bytes:", len(buf.getvalue()))

# ---- link cards ------------------------------------------------------------
links = [
    ("github", "GitHub", "github.com/SANTOSH-KUMAR-SHAH", "https://github.com/SANTOSH-KUMAR-SHAH"),
    ("globe", "Website", "santoshkumarshah.me", "https://santoshkumarshah.me"),
    ("gmail", "Email", "santoshkumarshah266@gmail.com", "mailto:santoshkumarshah266@gmail.com"),
    ("linkedin", "LinkedIn", "in/santosh-kumar-shah", "https://www.linkedin.com/in/santosh-kumar-shah-liberal-engineer-9250503a4/"),
    ("whatsapp", "WhatsApp", "+977 9845067005", "https://wa.me/9779845067005"),
]

# Stagger offset so all 5 cards don't animate simultaneously on GitHub.
CARD_DELAY = 3.2  # seconds

CX0, CY0, CW, CH = 330, 88, 540, 44
CARD_DUR = 1.5  # total span covering all 5 card fades
cards = []
for i, (ic, name, sub, url) in enumerate(links):
    y = CY0 + i * 50
    accent = [CYAN, VIOLET, PINK, CYAN, VIOLET][i]
    if ic == "globe":
        cy = CH / 2
        glyph = (f'<circle cx="22" cy="{cy}" r="12" fill="none" stroke="{TEXT}" stroke-width="1.6"/>'
                 f'<ellipse cx="22" cy="{cy}" rx="5" ry="12" fill="none" stroke="{TEXT}" stroke-width="1.2"/>'
                 f'<line x1="10" y1="{cy}" x2="34" y2="{cy}" stroke="{TEXT}" stroke-width="1.2"/>')
    else:
        glyph = icon(ic, 20, color_for(ic), 22, CH / 2)
    t0 = 0.1 + i * 0.15
    t1 = min(t0 + 0.35, CARD_DUR)
    k0 = round(t0 / CARD_DUR, 3)
    k1 = round(t1 / CARD_DUR, 3)
    cards.append(
        f'<a href="{url}" target="_blank">'
        # outer g: static position — no animation
        f'<g transform="translate({CX0},{y})">'
        # inner g: slide + fade with begin=CARD_DELAY and keyTimes
        f'<g opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{k0};{k1};1" dur="{CARD_DUR}s" begin="{CARD_DELAY}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="14 0;14 0;0 0;0 0" keyTimes="0;{k0};{k1};1" dur="{CARD_DUR}s" begin="{CARD_DELAY}s" fill="freeze"/>'
        f'<rect x="0" y="0" width="{CW}" height="{CH}" rx="12" fill="#12141f" '
        f'stroke="{accent}" stroke-opacity="0.35" stroke-width="1.3">'
        f'<animate attributeName="stroke-opacity" values="0.35;0.75;0.35" dur="3s" begin="{t1}s" repeatCount="indefinite"/>'
        f'</rect>'
        f'<circle cx="22" cy="{CH/2}" r="18" fill="{accent}" fill-opacity="0.10"/>'
        f'{glyph}'
        f'<text x="52" y="21" class="sans" font-size="16" font-weight="700" fill="{TEXT}">{name}</text>'
        f'<text x="52" y="38" class="mono" font-size="12" fill="{MUTED}">{sub}</text>'
        f'<g transform="translate({CW-34},{CH/2})"><path d="M-5 -6 L4 0 L-5 6" fill="none" stroke="{accent}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        f'<animateTransform attributeName="transform" type="translate" values="0,0;5,0;0,0" dur="1.6s" begin="0s" repeatCount="indefinite" fill="both"/></path></g>'
        f'</g></g></a>')
cards_svg = "\n      ".join(cards)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100%" viewBox="0 0 {W} {H}" role="img" aria-label="Connect with Santosh">
  <defs>
    <linearGradient id="hairline4" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.6"/><stop offset="1" stop-color="{PINK}" stop-opacity="0.6"/></linearGradient>
    <radialGradient id="charGlow" cx="0.5" cy="0.6" r="0.6">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.25"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
    <pattern id="dots4" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="#ffffff" opacity="0.03"/></pattern>
    <style>
      {FONTS_STYLE_ESCAPED}
    </style>
  </defs>

  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="{BG}"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="url(#dots4)"/>
  <rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="17" fill="none" stroke="url(#hairline4)" stroke-width="1.5"/>

  <!-- character -->
  <!-- drifting spotlight over character -->
  <radialGradient id="spotLight" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.12"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </radialGradient>
  <ellipse cx="160" cy="260" rx="130" ry="100" fill="url(#charGlow)"/>
  <ellipse cx="160" cy="200" rx="100" ry="80" fill="url(#spotLight)">
    <animate attributeName="cx" values="120;190;140;160" dur="8s" begin="0s" repeatCount="indefinite"
             calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"/>
    <animate attributeName="cy" values="180;230;200;180" dur="8s" begin="0s" repeatCount="indefinite"
             calcMode="spline" keySplines="0.5 0 0.5 1;0.5 0 0.5 1;0.5 0 0.5 1"/>
  </ellipse>
  <image href="data:image/png;base64,{CHAR}" xlink:href="data:image/png;base64,{CHAR}"
         x="10" y="30" width="300" height="330" preserveAspectRatio="xMidYMax meet"/>

  <!-- heading + subtitle + cards -->
  <text x="{CX0}" y="48" class="display" font-size="22" fill="{TEXT}">Find me where the flow goes</text>
  <text x="{CX0}" y="70" class="sans" font-size="13" font-weight="500" fill="{MUTED}">Message me. I respond to humans.</text>
  <g>
      {cards_svg}
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(svg)
print("wrote", OUT, f"{os.path.getsize(OUT)/1024:.0f} KB")
