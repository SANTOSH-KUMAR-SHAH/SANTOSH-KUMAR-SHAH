#!/usr/bin/env python3
"""Build about-life.svg: 'What I actually do' + 'Beyond the screen'.
Copy: Steve Jobs style — short, direct, personal.
Animations: sequential row entrance with smooth slide + fade, continuous ambient badge pulse,
smooth crossfade slides, held daily rings.
Typography: Embedded Syne 800 (Display), Plus Jakarta Sans (Body), Space Mono (Code).
CSS + SMIL only, fully self-contained."""
import math
import os
from fonts_def import FONTS_STYLE_ESCAPED

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "about-life.svg")

BG, CYAN, VIOLET, PINK, TEXT, MUTED = "#0d0e16","#22d3ee","#a78bfa","#f472b6","#e7e9f3","#8b90a8"
W, H = 900, 430

# ---- LEFT CARD: what I actually do -----------------------------------------
rows = [
    ("Reach more customers",
     ("Turn physical presence into digital reach.",
      "Built for people to discover you anywhere."),
     CYAN,
     '<path d="M-6 -4 L-10 0 L-6 4 M6 -4 L10 0 L6 4 M-1 6 L1 -6" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'),
    ("Own your identity",
     ("Look like where you're going,",
      "not where you've been."),
     VIOLET,
     '<circle cx="0" cy="0" r="7" fill="none" stroke="{c}" stroke-width="1.8"/><circle cx="-2.5" cy="-2" r="1.4" fill="{c}"/><circle cx="3" cy="-1" r="1.4" fill="{c}"/><circle cx="0" cy="3.5" r="1.4" fill="{c}"/>'),
    ("Be remembered",
     ("Interfaces crafted to evoke feeling",
      "and bring customers back."),
     PINK,
     '<path d="M-4 -6 L7 0 L-4 6 Z" fill="{c}"/>'),
]

FADE_DUR = 1.8  # total anim span covering all 3 rows
row_svg = []
for i, (title, sub, col, glyph) in enumerate(rows):
    y  = 188 + i * 74
    t0 = 0.2 + i * 0.25          # stagger: 0.2 / 0.45 / 0.7 s
    t1 = min(t0 + 0.45, FADE_DUR)
    k0 = round(t0 / FADE_DUR, 3)
    k1 = round(t1 / FADE_DUR, 3)
    row_svg.append(
        f'<g transform="translate(52,{y})">'
        f'<g opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{k0};{k1};1" dur="{FADE_DUR}s" begin="0s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 14;0 14;0 0;0 0" keyTimes="0;{k0};{k1};1" dur="{FADE_DUR}s" begin="0s" fill="freeze"/>'
        f'<rect x="0" y="-22" width="44" height="44" rx="12" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-opacity="0.4">'
        f'<animate attributeName="stroke-opacity" values="0.4;0.85;0.4" dur="3.2s" begin="{t1}s" repeatCount="indefinite"/>'
        f'</rect>'
        f'<g transform="translate(22,0)">{glyph.format(c=col)}</g>'
        f'<text x="60" y="-4" class="sans" font-size="16" font-weight="700" fill="{TEXT}">{title}</text>'
        f'<text x="60" y="14" class="sans" font-size="12.5" font-weight="400" fill="{MUTED}">'
        f'<tspan x="60" dy="0">{sub[0]}</tspan>'
        f'<tspan x="60" dy="17">{sub[1]}</tspan>'
        f'</text>'
        f'</g>'
        f'</g>'
    )
rows_svg = "\n      ".join(row_svg)


# ---- RIGHT CARD: beyond the screen -----------------------------------------
hobbies = [
    ("Deep thinking",  "I sit with a problem until it opens itself."),
    ("Philosophy",     "First principles. Always."),
    ("Poetry",         "Code and verse: structure, rhythm, and meaning."),
    ("Electronics",    "Understanding systems, not just using them."),
    ("Business",       "Building what lasts long after launch day."),
]
N      = len(hobbies)
TOTAL  = 20.0
RX0, RY0, RW = 490, 92, 362
seg_gap = 5
seg_w   = (RW - seg_gap * (N - 1)) / N

# segment tracks + fills (each fills left-to-right during its active slot)
segs = []
for i in range(N):
    x   = RX0 + i * (seg_w + seg_gap)
    kt  = f"0;{i/N:.3f};{(i+1)/N:.3f};1"
    segs.append(
        f'<rect x="{x:.1f}" y="{RY0}" width="{seg_w:.1f}" height="4" rx="2" fill="#ffffff" opacity="0.14"/>'
        f'<rect x="{x:.1f}" y="{RY0}" width="0" height="4" rx="2" fill="{CYAN}">'
        f'<animate attributeName="width" values="0;0;{seg_w:.1f};{seg_w:.1f}" keyTimes="{kt}" '
        f'dur="{TOTAL}s" begin="0s" repeatCount="indefinite" fill="both"/></rect>'
    )
segs_svg = "\n      ".join(segs)

# hobby slides with buttery smooth crossfading
def make_smooth_crossfade(idx, total_slides, total_dur):
    slot = total_dur / total_slides
    t_start = idx * slot
    t_end = (idx + 1) * slot
    fade = 0.5
    if idx == 0:
        k1 = round((t_end - fade) / total_dur, 4)
        k2 = round(t_end / total_dur, 4)
        k3 = round((total_dur - fade) / total_dur, 4)
        times = f"0.0;{k1};{k2};{k3};1.0"
        vals = "1;1;0;0;1"
    elif idx == total_slides - 1:
        k0 = round(t_start / total_dur, 4)
        k1 = round((t_start + fade) / total_dur, 4)
        k2 = round((t_end - fade) / total_dur, 4)
        times = f"0.0;{k0};{k1};{k2};1.0"
        vals = "0;0;1;1;0"
    else:
        k0 = round(t_start / total_dur, 4)
        k1 = round((t_start + fade) / total_dur, 4)
        k2 = round((t_end - fade) / total_dur, 4)
        k3 = round(t_end / total_dur, 4)
        times = f"0.0;{k0};{k1};{k2};{k3};1.0"
        vals = "0;0;1;1;0;0"
    return times, vals

slides = []
for i, (name, cap) in enumerate(hobbies):
    kt_str, val_str = make_smooth_crossfade(i, N, TOTAL)
    op0 = "1" if i == 0 else "0"
    slides.append(
        f'<g opacity="{op0}">'
        f'<animate attributeName="opacity" values="{val_str}" keyTimes="{kt_str}" '
        f'dur="{TOTAL}s" begin="0s" repeatCount="indefinite" fill="both"/>'
        f'<text x="{RX0}" y="210" class="display" font-size="30" fill="url(#hobbyGrad)">{name}</text>'
        f'<text x="{RX0}" y="244" class="sans" font-size="13.5" font-weight="500" fill="{TEXT}" opacity="0.88">{cap}</text>'
        f'<text x="{RX0}" y="150" class="mono" font-size="13" fill="{MUTED}">0{i+1} / 0{N}</text>'
        f'</g>'
    )
slides_svg = "\n      ".join(slides)

# daily rings — hold at target, subtle breathing
rings = [("Read", 0.78, CYAN), ("Write", 0.55, VIOLET), ("Build", 0.9, PINK)]
RR    = 26
C     = 2 * math.pi * RR
ring_items = []
for i, (lab, pct, col) in enumerate(rings):
    cx     = RX0 + 20 + i * 120
    cy     = 340
    target = C * (1 - pct)
    ring_items.append(
        f'<g transform="translate({cx},{cy})">'
        f'<circle r="{RR}" fill="none" stroke="#ffffff" stroke-opacity="0.1" stroke-width="6"/>'
        f'<circle r="{RR}" fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round" '
        f'stroke-dasharray="{C:.1f}" stroke-dashoffset="{target:.1f}" transform="rotate(-90)">'
        f'<animate attributeName="stroke-dashoffset" values="{C:.1f};{target:.1f};{target:.1f}" '
        f'keyTimes="0;0.7;1" dur="4.5s" begin="0s" repeatCount="indefinite" fill="both"/></circle>'
        f'<text x="0" y="5" text-anchor="middle" class="display" font-size="13" fill="{TEXT}">{int(pct*100)}</text>'
        f'<text x="0" y="{RR+22}" text-anchor="middle" class="mono" font-size="12" fill="{MUTED}">{lab}</text>'
        f'</g>'
    )
rings_svg = "\n      ".join(ring_items)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100%" viewBox="0 0 {W} {H}" role="img" aria-label="What I do and who I am">
  <defs>
    <linearGradient id="hobbyGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
    <linearGradient id="hairline2" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.6"/><stop offset="1" stop-color="{PINK}" stop-opacity="0.6"/></linearGradient>
    <pattern id="dots2" width="18" height="18" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1" fill="#ffffff" opacity="0.025"/></pattern>
    <style>
      {FONTS_STYLE_ESCAPED}
    </style>
  </defs>

  <!-- LEFT CARD -->
  <g>
    <rect x="24" y="24" width="420" height="382" rx="18" fill="{BG}"/>
    <rect x="24" y="24" width="420" height="382" rx="18" fill="url(#dots2)"/>
    <rect x="25.5" y="25.5" width="417" height="379" rx="17" fill="none"
          stroke="url(#hairline2)" stroke-width="1.5"/>
    <!-- fake browser bar -->
    <rect x="44" y="46" width="380" height="34" rx="10" fill="#12141f" stroke="#ffffff" stroke-opacity="0.07"/>
    <circle cx="62" cy="63" r="5" fill="#ff5f57"/><circle cx="78" cy="63" r="5" fill="#febc2e"/><circle cx="94" cy="63" r="5" fill="#28c840"/>
    <rect x="112" y="53" width="300" height="20" rx="10" fill="#0b0d15"/>
    <text x="124" y="67" class="mono" font-size="12" fill="{MUTED}">santoshkumarshah.me<tspan fill="{CYAN}">/work</tspan></text>
    <rect x="232" y="55" width="1.6" height="16" fill="{CYAN}">
      <animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>

    <!-- heading -->
    <text x="46" y="118" class="display" font-size="22" fill="{TEXT}">What I actually do</text>

    <!-- rule that draws in left→right -->
    <line x1="46" y1="132" x2="46" y2="132" stroke="url(#hobbyGrad)" stroke-width="1.5" opacity="0.5">
      <animate attributeName="x2" values="46;404" dur="0.8s" begin="0s" fill="freeze"
               calcMode="spline" keySplines="0.16 1 0.3 1"/>
    </line>

    <text x="46" y="154" class="sans" font-size="13" font-weight="500" fill="{MUTED}">I begin with your problem. Then I decide what to build.</text>

    <g>
      {rows_svg}
    </g>
  </g>

  <!-- RIGHT CARD -->
  <g>
    <rect x="462" y="24" width="414" height="382" rx="18" fill="{BG}"/>
    <rect x="462" y="24" width="414" height="382" rx="18" fill="url(#dots2)"/>
    <rect x="463.5" y="25.5" width="411" height="379" rx="17" fill="none"
          stroke="url(#hairline2)" stroke-width="1.5"/>
    <text x="490" y="66" class="display" font-size="22" fill="{TEXT}">Beyond the screen</text>

    <!-- rule draws in -->
    <line x1="490" y1="78" x2="490" y2="78" stroke="url(#hobbyGrad)" stroke-width="1.5" opacity="0.5">
      <animate attributeName="x2" values="490;844" dur="0.8s" begin="0s" fill="freeze"
               calcMode="spline" keySplines="0.16 1 0.3 1"/>
    </line>

    <g>
      {segs_svg}
    </g>
    <g>
      {slides_svg}
    </g>
    <text x="490" y="300" class="mono" font-size="12" fill="{MUTED}">Daily rhythms</text>
    <g>
      {rings_svg}
    </g>
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(svg)
print("wrote", OUT, f"{os.path.getsize(OUT)/1024:.0f} KB")
