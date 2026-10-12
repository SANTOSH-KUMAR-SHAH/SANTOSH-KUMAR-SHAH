#!/usr/bin/env python3
"""Build id-dashboard.svg: a lanyard ID badge that drops in and swings with
damped-pendulum motion (portrait, travelling frame light, gold chip, barcode,
holographic foil sweep) beside a dashboard (count-up KPIs, language bar chart,
'now' panel). Self-contained; portrait is downscaled + base64-inlined."""
import base64
import io
import json
import os
from PIL import Image
from fonts_def import FONTS_STYLE_ESCAPED

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "profile", "id-dashboard.svg")
REPOS = json.load(open(os.path.join(HERE, "profile", "assets", "repos.json")))

BG, CYAN, VIOLET, PINK, TEXT, MUTED = "#0d0e16", "#22d3ee", "#a78bfa", "#f472b6", "#e7e9f3", "#8b90a8"
W, H = 900, 470

# ---- real stats ------------------------------------------------------------
repos_n = len(REPOS)
stars_n = sum(r["stars"] for r in REPOS)
followers_n = 1  # from GitHub API
from collections import Counter
lang = Counter(r["lang"] for r in REPOS if r["lang"])
chart = lang.most_common(4)  # e.g. JavaScript, TypeScript, Astro

# ---- inline downscaled portrait -------------------------------------------
img = Image.open(os.path.join(HERE, "profile", "assets", "me.png")).convert("RGBA")
img.thumbnail((300, 300))
buf = io.BytesIO()
img.save(buf, "PNG", optimize=True)
PORTRAIT = base64.b64encode(buf.getvalue()).decode("ascii")
print("portrait bytes:", len(buf.getvalue()))

# ---- KPI count-up tiles ----------------------------------------------------
def kpi(x, y, val, label, color):
    rh = 40
    if val <= 0:
        num = f'<text x="{x+70}" y="{y+52}" text-anchor="middle" class="display" font-size="34" fill="{color}">0</text>'
    else:
        rows = "".join(
            f'<text x="{x+70}" y="{y+52 - n*rh}" text-anchor="middle" class="display" '
            f'font-size="34" fill="{color}">{n}</text>'
            for n in range(val + 1))
        num = (
            f'<clipPath id="kclip_{label[0]}{x}"><rect x="{x+14}" y="{y+22}" width="112" height="{rh}"/></clipPath>'
            f'<g clip-path="url(#kclip_{label[0]}{x})"><g transform="translate(0,{val*rh})">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,0;0,0;0,{val*rh}" keyTimes="0;0.25;1" dur="1.6s" begin="0s" '
            f'calcMode="spline" keySplines="0.16 1 0.3 1;0.16 1 0.3 1" fill="freeze"/>{rows}</g></g>')
    return (f'<g><rect x="{x}" y="{y}" width="140" height="80" rx="14" fill="#12141f" '
            f'stroke="{color}" stroke-opacity="0.35" stroke-width="1.3"/>'
            f'<text x="{x+14}" y="{y+22}" class="mono" font-size="11" fill="{MUTED}">{label}</text>'
            f'{num}</g>')

kpis = (kpi(392, 102, repos_n, "REPOSITORIES", CYAN)
        + kpi(546, 102, 5, "SHIPPED APPS", VIOLET)
        + kpi(700, 102, len(chart), "LANGUAGES", PINK))

# ---- language bar chart (with overshoot for energy) -----------------------
bx, by, bw_full, maxh = 392, 360, 448, 150
maxv = max(v for _, v in chart) or 1
bar_w = 60
gap = (bw_full - bar_w * len(chart)) / (len(chart) + 1)
bars = []
for i, (name, v) in enumerate(chart):
    x   = bx + gap + i * (bar_w + gap)
    hgt = maxh * v / maxv
    # overshoot: grow to 108% then settle at 100%
    overshoot = hgt * 1.08
    bars.append(
        f'<rect x="{x:.1f}" y="{by - hgt:.1f}" width="{bar_w}" height="{hgt:.1f}" rx="6" fill="{CYAN}" fill-opacity="0.85">'
        f'<animate attributeName="height" values="0;0;{overshoot:.1f};{hgt:.1f}" keyTimes="0;0.2;0.8;1" dur="1.3s" begin="0s" fill="both" '
        f'calcMode="spline" keySplines="0.5 0 0.5 1;0.16 1 0.3 1;0.5 0 0.5 1"/>'
        f'<animate attributeName="y" values="{by};{by};{by-overshoot:.1f};{by-hgt:.1f}" keyTimes="0;0.2;0.8;1" dur="1.3s" begin="0s" fill="both" '
        f'calcMode="spline" keySplines="0.5 0 0.5 1;0.16 1 0.3 1;0.5 0 0.5 1"/></rect>'
        f'<text x="{x+bar_w/2:.1f}" y="{by-hgt-8:.1f}" text-anchor="middle" class="display" font-size="13" fill="{TEXT}">{v}</text>'
        f'<text x="{x+bar_w/2:.1f}" y="{by+18}" text-anchor="middle" class="mono" font-size="11" fill="{MUTED}">{name}</text>')
bars_svg = "\n      ".join(bars)

# ---- badge (pivot at 200,34; drop + damped swing) --------------------------
# travelling light path around the portrait frame
frame = (120, 128, 160, 128)  # x, y, w, h
fx, fy, fw, fh = frame
light_path = f"M{fx} {fy} H{fx+fw} V{fy+fh} H{fx} Z"

barcode = "".join(
    f'<rect x="{158 + i*4}" y="300" width="{2 if i%3 else 1}" height="24" fill="{TEXT}" opacity="0.8"/>'
    for i in range(24))

badge = f'''
  <g>
    <animateTransform attributeName="transform" type="translate" values="0,-60;0,0"
      dur="0.9s" begin="0s" fill="both" calcMode="spline" keySplines="0.16 1 0.3 1"/>
    <g>
      <animateTransform attributeName="transform" type="rotate" additive="sum"
        values="-9 200 34; 7 200 34; -5 200 34; 3.5 200 34; -2 200 34; 1 200 34; 0 200 34"
        keyTimes="0;0.18;0.38;0.56;0.74;0.88;1" dur="5s" begin="0.9s" repeatCount="indefinite" fill="both"/>
      <!-- lanyard straps with subtle sway matching the badge swing -->
      <path d="M200 34 L150 96 M200 34 L250 96" stroke="{VIOLET}" stroke-width="3" fill="none" opacity="0.7">
        <animateTransform attributeName="transform" type="rotate" additive="sum"
          values="-4 200 34; 3 200 34; -2 200 34; 1 200 34; 0 200 34"
          keyTimes="0;0.25;0.55;0.8;1" dur="5s" begin="0.9s" repeatCount="indefinite" fill="both"/>
      </path>
      <circle cx="200" cy="34" r="6" fill="none" stroke="{CYAN}" stroke-width="2.5"/>
      <rect x="186" y="86" width="28" height="16" rx="4" fill="#c9cedb" stroke="#8b90a8"/>
      <!-- card body -->
      <rect x="96" y="100" width="208" height="248" rx="16" fill="#12141f" stroke="url(#hairline3)" stroke-width="1.5"/>
      <!-- header band -->
      <rect x="96" y="100" width="208" height="26" rx="16" fill="{CYAN}" fill-opacity="0.12"/>
      <text x="200" y="118" text-anchor="middle" class="mono" font-size="11" fill="{CYAN}" letter-spacing="3">SANTOSH · ID</text>
      <!-- portrait frame -->
      <rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="10" fill="#0b0d15" stroke="{VIOLET}" stroke-opacity="0.5"/>
      <clipPath id="pclip"><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="10"/></clipPath>
      <image href="data:image/png;base64,{PORTRAIT}" xlink:href="data:image/png;base64,{PORTRAIT}"
             x="{fx}" y="{fy}" width="{fw}" height="{fh}" preserveAspectRatio="xMidYMin slice" clip-path="url(#pclip)"/>
      <!-- travelling light around frame -->
      <circle r="4" fill="#ffffff">
        <animateMotion dur="4s" begin="0s" repeatCount="indefinite" path="{light_path}"/>
      </circle>
      <circle r="9" fill="{CYAN}" opacity="0.5">
        <animateMotion dur="4s" begin="0s" repeatCount="indefinite" path="{light_path}"/>
      </circle>
      <!-- name -->
      <text x="200" y="272" text-anchor="middle" class="display" font-size="15" fill="{TEXT}">SANTOSH KUMAR SHAH</text>
      <text x="200" y="288" text-anchor="middle" class="mono" font-size="10" fill="{MUTED}">LIBERAL ENGINEER · KATHMANDU</text>
      <!-- gold chip -->
      <rect x="112" y="300" width="34" height="24" rx="4" fill="url(#chipGrad)" stroke="#b8860b"/>
      <path d="M120 300 V324 M138 300 V324 M112 312 H146" stroke="#7a5c00" stroke-width="0.8"/>
      <!-- barcode -->
      {barcode}
      <!-- holographic foil sweep -->
      <rect x="96" y="100" width="208" height="248" rx="16" fill="url(#foil)" opacity="0.18" clip-path="url(#badgeclip)">
        <animate attributeName="x" values="-160;304" dur="4.5s" begin="0s" repeatCount="indefinite"/>
      </rect>
    </g>
  </g>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100%" viewBox="0 0 {W} {H}" role="img" aria-label="ID badge and stats dashboard">
  <defs>
    <linearGradient id="hairline3" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.6"/><stop offset="1" stop-color="{PINK}" stop-opacity="0.6"/></linearGradient>
    <linearGradient id="chipGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6d365"/><stop offset="1" stop-color="#b8860b"/></linearGradient>
    <linearGradient id="foil" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
    <linearGradient id="dashLine" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.6"/><stop offset="1" stop-color="{PINK}" stop-opacity="0.6"/></linearGradient>
    <pattern id="dots3" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="#ffffff" opacity="0.03"/></pattern>
    <clipPath id="badgeclip"><rect x="96" y="100" width="208" height="248" rx="16"/></clipPath>
    <style>
      {FONTS_STYLE_ESCAPED}
    </style>
  </defs>

  <!-- dashboard card (right) -->
  <rect x="368" y="40" width="508" height="392" rx="18" fill="{BG}"/>
  <rect x="368" y="40" width="508" height="392" rx="18" fill="url(#dots3)"/>
  <rect x="369.5" y="41.5" width="505" height="389" rx="17" fill="none" stroke="url(#dashLine)" stroke-width="1.5"/>
  <text x="392" y="72" class="display" font-size="22" fill="{TEXT}">By the numbers</text>
  <text x="392" y="90" class="mono" font-size="11" fill="{MUTED}">Baked at build time — honest, not live</text>

  {kpis}

  <line x1="392" y1="{by}" x2="{bx+bw_full}" y2="{by}" stroke="#ffffff" stroke-opacity="0.12"/>
  <g>
      {bars_svg}
  </g>

  <!-- now panel -->
  <g>
    <rect x="392" y="398" width="448" height="26" rx="13" fill="#12141f" stroke="{CYAN}" stroke-opacity="0.3"/>
    <!-- sonar ping: expanding ring from the dot -->
    <circle cx="410" cy="411" r="4" fill="{PINK}">
      <animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/></circle>
    <circle cx="410" cy="411" r="4" fill="none" stroke="{PINK}" stroke-opacity="0.6">
      <animate attributeName="r"       values="4;14;4"     dur="1.6s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0.6;0;0.6" dur="1.6s" repeatCount="indefinite"/>
    </circle>
    <text x="424" y="415" class="mono" font-size="12" fill="{MUTED}">now:</text>
    <text x="460" y="415" class="sans" font-size="12" fill="{TEXT}">engineering Sudhar — the internet hasn't seen this yet</text>
  </g>

  <!-- badge (left) -->
  <text x="200" y="392" text-anchor="middle" class="mono" font-size="11" fill="{MUTED}">अनुगच्छतु प्रवाहं — follow the flow</text>
  {badge}
</svg>
'''

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(svg)
print("wrote", OUT, f"{os.path.getsize(OUT)/1024:.0f} KB")
