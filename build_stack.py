#!/usr/bin/env python3
"""Build self-contained animated stack.svg (tech orbit + chip grid).

Guide rules honoured: CSS + SMIL only, everything inlined (brand icon paths
are baked in from icons.json at build time, nothing fetched at runtime),
entrance/loop timelines start at 0s, and a renderer that ignores animation
still shows a complete card.
"""
import json
import os
from fonts_def import FONTS_STYLE_ESCAPED

HERE = os.path.dirname(os.path.abspath(__file__))
icons_path = os.path.join(HERE, "assets", "icons.json") if os.path.exists(os.path.join(HERE, "assets", "icons.json")) else os.path.join(HERE, "profile", "assets", "icons.json")
ICONS = json.load(open(icons_path))
OUT = os.path.join(HERE, "stack.svg")

BG, CYAN, VIOLET, PINK, TEXT, MUTED = "#0d0e16", "#22d3ee", "#a78bfa", "#f472b6", "#e7e9f3", "#8b90a8"
W, H = 900, 470
CX, CY = 250, 240


def lum(hexs):
    h = hexs.lstrip("#")
    if len(h) != 6:
        return 255
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000


def color_for(slug, fallback="#dfe3ff"):
    hexs = ICONS.get(slug, {}).get("hex") or "ffffff"
    # brand colours that are near-black/near-white are unreadable on dark bg
    if lum(hexs) < 95 or lum(hexs) > 235:
        return fallback
    return "#" + hexs


def icon(slug, size, color, cx=0, cy=0):
    d = ICONS[slug]["path"]
    s = size / 24.0
    return (f'<g transform="translate({cx},{cy}) scale({s:.4f}) translate(-12,-12)">'
            f'<path d="{d}" fill="{color}"/></g>')


def ellipse(rx, ry):
    return f"M {CX - rx} {CY} a {rx} {ry} 0 1 0 {2*rx} 0 a {rx} {ry} 0 1 0 {-2*rx} 0"


def circle(r):
    return f"M {r} 0 a {r} {r} 0 1 0 {-2*r} 0 a {r} {r} 0 1 0 {2*r} 0"


def traveler(slug, orbit, dur, r, begin="0s", ring=None):
    col = color_for(slug)
    ring = ring or col
    return (f'<g><circle r="{r}" fill="#12141f" stroke="{ring}" stroke-opacity="0.55" stroke-width="1.5"/>'
            f'{icon(slug, r*1.55, col)}'
            f'<animateMotion dur="{dur}s" begin="{begin}" repeatCount="indefinite" rotate="0">'
            f'<mpath href="#{orbit}" xlink:href="#{orbit}"/></animateMotion></g>')


# ---- orbit geometry --------------------------------------------------------
orbits = {
    "orb1": (150, 52, -18),
    "orb2": (118, 92, 35),
    "orb3": (178, 40, 6),
}
orbit_defs = "\n    ".join(f'<path id="{k}" d="{ellipse(rx, ry)}"/>' for k, (rx, ry, _) in orbits.items())
orbit_paths = "\n      ".join(
    f'<use href="#{k}" xlink:href="#{k}" fill="none" stroke="{CYAN}" stroke-opacity="0.16" stroke-width="1.2" '
    f'stroke-dasharray="2 5" transform="rotate({rot} {CX} {CY})"/>'
    for k, (rx, ry, rot) in orbits.items())

# ---- React planet + two moons (framer, gsap) ------------------------------
react_planet = f'''
      <g>
        <g><circle r="30" fill="#0f1523" stroke="{CYAN}" stroke-opacity="0.6" stroke-width="1.6"/>
           {icon("react", 40, color_for("react"))}</g>
        <g><circle r="10" fill="none" stroke="{VIOLET}" stroke-opacity="0.4"/>
           {icon("framer", 15, "#ffffff")}
           <animateMotion dur="3.2s" begin="0s" repeatCount="indefinite" rotate="0">
             <mpath href="#moonA" xlink:href="#moonA"/></animateMotion></g>
        <g><circle r="10" fill="none" stroke="{PINK}" stroke-opacity="0.4"/>
           {icon("greensock", 15, color_for("greensock"))}
           <animateMotion dur="4.6s" begin="-1.5s" repeatCount="indefinite" rotate="0">
             <mpath href="#moonB" xlink:href="#moonB"/></animateMotion></g>
        <animateMotion dur="20s" begin="0s" repeatCount="indefinite" rotate="0">
          <mpath href="#orb1" xlink:href="#orb1"/></animateMotion>
      </g>'''

# moon orbit paths live in the planet's local space (centred on 0,0)
moon_defs = f'<path id="moonA" d="{circle(46)}"/><path id="moonB" d="{circle(60)}"/>'

# ---- orbit travellers ------------------------------------------------------
orb2_riders = traveler("threedotjs", "orb2", 15, 17) + traveler("nextdotjs", "orb2", 15, 17, begin="-7.5s")
orb3_riders = (traveler("typescript", "orb3", 18, 16)
               + traveler("nodedotjs", "orb3", 18, 16, begin="-6s")
               + traveler("tailwindcss", "orb3", 18, 16, begin="-12s"))

orbit_groups = f'''
    <g transform="rotate({orbits['orb1'][2]} {CX} {CY})">
      <use href="#orb1" xlink:href="#orb1" fill="none" stroke="{CYAN}" stroke-opacity="0.16" stroke-width="1.2" stroke-dasharray="2 5"/>
      {react_planet}
    </g>
    <g transform="rotate({orbits['orb2'][2]} {CX} {CY})">
      <use href="#orb2" xlink:href="#orb2" fill="none" stroke="{VIOLET}" stroke-opacity="0.16" stroke-width="1.2" stroke-dasharray="2 5"/>
      {orb2_riders}
    </g>
    <g transform="rotate({orbits['orb3'][2]} {CX} {CY})">
      <use href="#orb3" xlink:href="#orb3" fill="none" stroke="{PINK}" stroke-opacity="0.16" stroke-width="1.2" stroke-dasharray="2 5"/>
      {orb3_riders}
    </g>'''

# ---- glowing core ----------------------------------------------------------
core = f'''
    <circle cx="{CX}" cy="{CY}" r="52" fill="url(#coreGlow)">
      <animate attributeName="r" values="48;56;48" dur="3.4s" repeatCount="indefinite" fill="both"/>
    </circle>
    <circle cx="{CX}" cy="{CY}" r="20" fill="url(#coreGrad)" stroke="{CYAN}" stroke-opacity="0.5"/>
    <circle cx="{CX}" cy="{CY}" r="20" fill="none" stroke="{PINK}" stroke-opacity="0.6" stroke-width="1.5"
            stroke-dasharray="18 106">
      <animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}"
                        dur="6s" repeatCount="indefinite"/>
    </circle>
    <text x="{CX}" y="{CY+5}" text-anchor="middle" class="mono" font-size="12" fill="#04121a" font-weight="700">&lt;/&gt;</text>'''

# ---- chip grid -------------------------------------------------------------
groups = [
    ("FRONTEND", ["react", "nextdotjs", "typescript", "tailwindcss"]),
   ("MOTION &amp; 3D", ["framer", "greensock", "threedotjs"]),
    ("DATA", ["nodedotjs", "postgresql", "firebase"]),
    ("AI", ["openai", "pytorch", "tensorflow"]),
]
labels = {"react": "React", "nextdotjs": "Next.js", "typescript": "TypeScript",
          "tailwindcss": "Tailwind", "framer": "Framer", "greensock": "GSAP",
          "threedotjs": "Three.js", "nodedotjs": "Node.js", "postgresql": "Postgres",
          "firebase": "Firebase", "openai": "OpenAI", "pytorch": "PyTorch",
          "tensorflow": "TensorFlow"}

GX = 450
GY = 66
CHIP_DUR = 2.5  # total span covering all chip fades
# chip grid — outer g: static pos, inner g: opacity fade (begin=0s+keyTimes trick)
chip_index = 0
chips = []
for gi, (gname, slugs) in enumerate(groups):
    gy = GY + gi * 100
    chips.append(f'<text x="{GX}" y="{gy}" class="mono" font-size="12" fill="{MUTED}" letter-spacing="1.5">{gname}</text>')
    cx = GX
    for s in slugs:
        lab    = labels[s]
        wch    = int(36 + len(lab) * 7.5)
        accent = [CYAN, VIOLET, PINK, CYAN][gi]
        t0 = chip_index * 0.08
        t1 = min(t0 + 0.35, CHIP_DUR)
        k0 = round(t0 / CHIP_DUR, 3)
        k1 = round(t1 / CHIP_DUR, 3)
        chips.append(
            f'<g transform="translate({cx},{gy+14})">'
            f'<g opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{k0};{k1};1" dur="{CHIP_DUR}s" begin="0s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="10 0;10 0;0 0;0 0" keyTimes="0;{k0};{k1};1" dur="{CHIP_DUR}s" begin="0s" fill="freeze"/>'
            f'<rect width="{wch}" height="34" rx="17" fill="#12141f" stroke="{accent}" stroke-width="1.4" stroke-opacity="0.35">'
            f'<animate attributeName="stroke-opacity" values="0.35;0.75;0.35" dur="3.5s" begin="{t1}s" repeatCount="indefinite"/>'
            f'</rect>'
            f'{icon(s, 16, color_for(s), 20, 17)}'
            f'<text x="34" y="22" class="sans" font-size="13" font-weight="600" fill="{TEXT}">{lab}</text>'
            f'</g></g>'
        )
        cx += wch + 8
        chip_index += 1
chips_svg = "\n      ".join(chips)


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100%" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack orbit and skill chips">
  <defs>
    <radialGradient id="coreGlow"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.35"/>
      <stop offset="0.6" stop-color="{VIOLET}" stop-opacity="0.12"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
    <linearGradient id="coreGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
    <linearGradient id="hairline" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.7"/><stop offset="0.5" stop-color="{VIOLET}" stop-opacity="0.2"/>
      <stop offset="1" stop-color="{PINK}" stop-opacity="0.7"/></linearGradient>
    <pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="#ffffff" opacity="0.03"/></pattern>
    {orbit_defs}
    {moon_defs}
    <style>
      {FONTS_STYLE_ESCAPED}
    </style>
  </defs>

  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="{BG}"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="url(#dots)"/>
  <rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="17" fill="none" stroke="url(#hairline)" stroke-width="1.5"/>

  <text x="40" y="46" class="display" font-size="22" fill="{TEXT}">The Stack</text>
  <text x="40" y="440" class="mono" font-size="12" fill="{MUTED}">The tools follow the problem, not the other way around.</text>

  <!-- orbit fades in on load -->
  <g opacity="0">
    <animate attributeName="opacity" values="0;1" dur="1.2s" begin="0s" fill="freeze"
             calcMode="spline" keySplines="0.25 0 0.75 1"/>
    <g>{orbit_groups}</g>
    <g>{core}</g>
  </g>

  <!-- heartbeat ripple from core every 6s -->
  <circle cx="{CX}" cy="{CY}" r="20" fill="none" stroke="{CYAN}" stroke-opacity="0" stroke-width="2">
    <animate attributeName="r"             values="20;80;20"    dur="2s" begin="2s;8s;14s;20s" fill="freeze"/>
    <animate attributeName="stroke-opacity" values="0.35;0;0.35" dur="2s" begin="2s;8s;14s;20s" fill="freeze"/>
  </circle>

  <g>{chips_svg}</g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(svg)
print("wrote", OUT, f"{os.path.getsize(OUT)/1024:.0f} KB")
