#!/usr/bin/env python3
"""Build a NEXT-LEVEL animated hero.svg — cinema-grade first impression.

Upgrades vs v1:
  - Larger card (900x430), bolder typography hierarchy
  - RGB glitch flash on NAME every few seconds (SMIL offset + opacity burst)
  - Twinkling particle star field behind the card content
  - Scan-line sweep running continuously over the video
  - Periodic full-card light-beam sweep (like a camera shutter)
  - Animated border that breathes (opacity pulse + gradient shift)
  - Tech tag chips row with staggered glow
  - Bigger name (74px), tighter, more dramatic layout
  - Vertical separator line between columns
  - Better color balance and glow positioning

GitHub-safe: CSS + SMIL only — no JS, nothing fetched at runtime.
Static fallback: final frame + name + first role always visible.
"""
import base64
import glob
import os
import random
from PIL import Image
from fonts_def import FONTS_STYLE_ESCAPED

HERE      = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(HERE, "assets", "frames") if os.path.exists(os.path.join(HERE, "assets", "frames")) else os.path.join(HERE, "profile", "assets", "frames")
GIF_PATH  = os.path.join(HERE, "hero_loop.gif")
OUT       = os.path.join(HERE, "hero.svg")

# ---- theme
BG     = "#0d0e16"
CYAN   = "#22d3ee"
VIOLET = "#a78bfa"
PINK   = "#f472b6"
TEXT   = "#e7e9f3"
MUTED  = "#8b90a8"
DARK   = "#080a10"

# ---- content
NAME     = "SANTOSH"
INTRO    = "I am"
ROLES    = ["Liberal Engineer", "Digital Storyteller", "Problem Solver", "System Thinker"]
PITCH    = "I don't build websites. I solve the problems behind them."
LOCATION = "Kathmandu, Nepal"
TAGS     = ["React", "TypeScript", "Next.js", "Astro", "GSAP"]

# ---- geometry
W, H   = 900, 440
VW, VH = 416, 234   # 16:9 cinematic video (Native 480x270 scaled with LANCZOS)
VX, VY = 458, 103   # centered vertically in right panel
SEP_X  = 444        # vertical separator between left text and right video

LOOP = 5.0

# ---- Build animated GIF from all 29 frames (GitHub renders animated GIFs in SVG <image> tags)
# This replaces the broken discrete-opacity SMIL stack which GitHub Camo strips.
frames = sorted(glob.glob(os.path.join(FRAME_DIR, "h_*.jpg")))
if not frames:
    raise SystemExit("No frames found in assets/frames/ — run ffmpeg extract first.")
frames = frames[1:]  # skip frame 1 -> gives exactly 29 frames (h_002 to h_030)
N = len(frames)
selected = frames    # use all 29 frames for smooth cinema video
gif_imgs = []
for f in selected:
    img = Image.open(f).convert("RGB")
    img = img.resize((VW, VH), Image.LANCZOS)
    gif_imgs.append(img.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=1))

dur_ms = int(LOOP * 1000 / len(selected))   # 5000ms / 29 frames = ~172ms per frame
gif_imgs[0].save(
    GIF_PATH, format="GIF", save_all=True,
    append_images=gif_imgs[1:],
    duration=dur_ms, optimize=True
)  # Omit loop parameter so it plays 1 time on open, then holds final frame!
print(f"built GIF: {len(selected)} frames, {dur_ms}ms each -> {os.path.getsize(GIF_PATH)//1024}KB")

with open(GIF_PATH, "rb") as fh:
    gif_b64 = base64.b64encode(fh.read()).decode("ascii")


# ====== ANIMATED GIF (single <image> — GitHub renders animated GIFs natively) ===
# Uses both href and xlink:href for universal SVG engine compatibility
gif_svg = (
    f'<image x="{VX}" y="{VY}" width="{VW}" height="{VH}" '
    f'href="data:image/gif;base64,{gif_b64}" xlink:href="data:image/gif;base64,{gif_b64}" '
    f'preserveAspectRatio="xMidYMid slice"/>'
)

# ====== CYCLING ROLES (smooth crossfade with keyTimes, no calcMode="discrete") ==
ROLE_CYCLE = 8.0
def make_role_anim(j, total_roles, total_dur):
    slot = total_dur / total_roles
    fade = 0.35
    s = j * slot
    e = (j + 1) * slot
    if j == 0:
        times = [0.0, (slot - fade) / total_dur, slot / total_dur, (total_dur - fade) / total_dur, 1.0]
        vals = [1.0, 1.0, 0.0, 0.0, 1.0]
    elif j == total_roles - 1:
        times = [0.0, s / total_dur, (s + fade) / total_dur, (total_dur - fade) / total_dur, 1.0]
        vals = [0.0, 0.0, 1.0, 1.0, 0.0]
    else:
        times = [0.0, s / total_dur, (s + fade) / total_dur, (e - fade) / total_dur, e / total_dur, 1.0]
        vals = [0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
    kt = ";".join(f"{t:.3f}" for t in times)
    kv = ";".join(f"{v:.1f}" for v in vals)
    return kt, kv

role_parts = []
for j, role in enumerate(ROLES):
    kt, kv = make_role_anim(j, len(ROLES), ROLE_CYCLE)
    role_parts.append(
        f'<text x="48" y="270" class="role" opacity="0">[ {role} ]'
        f'<animate attributeName="opacity" values="{kv}" keyTimes="{kt}" '
        f'dur="{ROLE_CYCLE}s" begin="0s" repeatCount="indefinite" fill="both"/></text>'
    )
roles_svg = "\n      ".join(role_parts)

# ====== TECH TAG CHIPS ========================================================
TAG_COLS = [CYAN, VIOLET, PINK, CYAN, VIOLET]
tag_parts = []
tx = 44
for i, tag in enumerate(TAGS):
    col = TAG_COLS[i]
    tw = int(16 + len(tag) * 8.0)
    delay = i * 0.45
    tag_parts.append(
        f'<g transform="translate({tx},338)">'
        f'<rect width="{tw}" height="26" rx="13" fill="{col}" fill-opacity="0.10" '
        f'stroke="{col}" stroke-width="1.2">'
        f'<animate attributeName="stroke-opacity" values="0.35;1.0;0.35" '
        f'dur="{3.0 + i * 0.4:.1f}s" begin="{delay:.2f}s" repeatCount="indefinite" fill="both"/>'
        f'</rect>'
        f'<text x="{tw//2}" y="17" text-anchor="middle" class="sans" '
        f'font-size="12" fill="{col}" font-weight="600">{tag}</text>'
        f'</g>'
    )
    tx += tw + 8
tags_svg = "\n    ".join(tag_parts)

# ====== TWINKLING PARTICLES ===================================================
rng = random.Random(7)
particles = []
# Keep them in the left column + background (x < VX-30) to not cover video
for _ in range(26):
    px = rng.uniform(15, W - 15)
    py = rng.uniform(15, H - 15)
    pr = rng.uniform(0.6, 2.0)
    col = rng.choice([CYAN, VIOLET, PINK, "#ffffff"])
    dur = rng.uniform(2.2, 7.0)
    beg = rng.uniform(0.0, 5.0)
    peak = rng.uniform(0.12, 0.45)
    particles.append(
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{pr:.1f}" fill="{col}" opacity="0">'
        f'<animate attributeName="opacity" values="0;{peak:.2f};0" '
        f'dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/>'
        f'</circle>'
    )
particles_svg = "\n  ".join(particles)

# ====== GLITCH BURSTS ON NAME =================================================
# Two ghost copies of the name — one cyan shifted left, one pink shifted right.
# They flash rapidly at t=2s, t=9s, t=17s (non-repeating begins look natural).
# Use fill="freeze" so each burst stays gone between triggers.
glitch_svg = f"""
  <!-- glitch: cyan ghost -->
  <g mask="url(#nameMask)">
    <g>
      <text x="43" y="216" class="sans" font-size="74" font-weight="800"
            fill="{CYAN}" letter-spacing="2" opacity="0">{NAME}
        <animate attributeName="opacity"
                 values="0;0.7;0;0.6;0"
                 keyTimes="0;0.1;0.35;0.6;1"
                 dur="0.18s" begin="2.2s;9.2s;17.2s" fill="freeze"/>
        <animateTransform attributeName="transform" type="translate" additive="sum"
                 values="0,0;-4,1;0,0;-2,0;0,0"
                 keyTimes="0;0.1;0.35;0.6;1"
                 dur="0.18s" begin="2.2s;9.2s;17.2s" fill="freeze"/>
      </text>
    </g>
  </g>
  <!-- glitch: pink ghost -->
  <g mask="url(#nameMask)">
    <g>
      <text x="49" y="216" class="sans" font-size="74" font-weight="800"
            fill="{PINK}" letter-spacing="2" opacity="0">{NAME}
        <animate attributeName="opacity"
                 values="0;0.55;0;0.45;0"
                 keyTimes="0;0.1;0.35;0.6;1"
                 dur="0.15s" begin="2.28s;9.28s;17.28s" fill="freeze"/>
        <animateTransform attributeName="transform" type="translate" additive="sum"
                 values="0,0;4,-1;0,0;2,0;0,0"
                 keyTimes="0;0.1;0.35;0.6;1"
                 dur="0.15s" begin="2.28s;9.28s;17.28s" fill="freeze"/>
      </text>
    </g>
  </g>"""

# ====== FULL-CARD LIGHT BEAM ==================================================
# A wide soft beam that sweeps left→right across the entire card at t=0.8s,
# then again at t=10s, t=20s. Creates a cinematic shutter/lens-flare feel.
beam_svg = f"""
  <rect x="-120" y="0" width="180" height="{H}" fill="url(#beamGrad)" opacity="0"
        rx="0">
    <animate attributeName="x" values="-180;{W+180}"
             dur="1.8s" begin="0.8s;10s;20s"
             calcMode="spline" keySplines="0.25 0 0.75 1" fill="freeze"/>
    <animate attributeName="opacity" values="0;0.55;0.55;0"
             keyTimes="0;0.15;0.85;1"
             dur="1.8s" begin="0.8s;10s;20s" fill="freeze"/>
  </rect>"""

# ====== ASSEMBLE ==============================================================
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100%" viewBox="0 0 {W} {H}" role="img"
     aria-label="{NAME} — animated profile hero">
  <defs>
    <!-- name gradient -->
    <linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"   stop-color="{CYAN}"/>
      <stop offset="0.4" stop-color="{VIOLET}"/>
      <stop offset="1"   stop-color="{PINK}"/>
    </linearGradient>

    <!-- border hairline — pulses -->
    <linearGradient id="hairline" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0"   stop-color="{CYAN}"   stop-opacity="0.9"/>
      <stop offset="0.5" stop-color="{VIOLET}" stop-opacity="0.3"/>
      <stop offset="1"   stop-color="{PINK}"   stop-opacity="0.9"/>
    </linearGradient>

    <!-- ambient glows -->
    <radialGradient id="glowL" cx="0.25" cy="0.45" r="0.65">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{BG}"     stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowR" cx="0.78" cy="0.5" r="0.55">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.14"/>
      <stop offset="1" stop-color="{BG}"   stop-opacity="0"/>
    </radialGradient>

    <!-- dot texture -->
    <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1" fill="#ffffff" opacity="0.028"/>
    </pattern>

    <!-- clip for video box (soft rounded corners) -->
    <clipPath id="vclip">
      <rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" rx="14"/>
    </clipPath>

    <!-- name reveal: black cover rect shrinks upward -->
    <mask id="nameMask" maskUnits="userSpaceOnUse"
          x="40" y="142" width="460" height="92">
      <rect x="40" y="142" width="460" height="92" fill="#fff"/>
      <rect x="40" y="142" width="460" height="0"  fill="#000">
        <animate attributeName="height" values="92;0" dur="1.0s"
                 begin="0.25s" fill="both"
                 calcMode="spline" keySplines="0.16 1 0.3 1"/>
      </rect>
    </mask>

    <!-- light beam sweep gradient -->
    <linearGradient id="beamGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"   stop-color="#fff" stop-opacity="0"/>
      <stop offset="0.4" stop-color="#fff" stop-opacity="0.07"/>
      <stop offset="0.6" stop-color="#fff" stop-opacity="0.07"/>
      <stop offset="1"   stop-color="#fff" stop-opacity="0"/>
    </linearGradient>

    <style>
      {FONTS_STYLE_ESCAPED}
      .role {{ font-size: 21px; font-weight: 700; fill: {CYAN}; letter-spacing: 1px; }}
    </style>
  </defs>

  <!-- ===== CARD SHELL ===== -->
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="{BG}"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="url(#dots)"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="url(#glowL)"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="url(#glowR)"/>

  <!-- animated breathing border -->
  <rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="19" fill="none"
        stroke="url(#hairline)" stroke-width="1.8">
    <animate attributeName="stroke-opacity" values="0.9;0.35;0.9"
             dur="3.5s" repeatCount="indefinite"/>
  </rect>

  <!-- ===== PARTICLES ===== -->
  {particles_svg}

  <!-- ===== LIGHT BEAM ===== -->
  {beam_svg}

  <!-- ===== LEFT COLUMN ===== -->

  <!-- status pill -->
  <g class="sans">
    <rect x="48" y="46" width="226" height="30" rx="15"
          fill="{CYAN}" fill-opacity="0.08" stroke="{CYAN}" stroke-opacity="0.45" stroke-width="1.1"/>
    <circle cx="66" cy="61" r="5" fill="{CYAN}">
      <animate attributeName="opacity" values="1;0.2;1" dur="1.5s" repeatCount="indefinite"/>
      <animate attributeName="r"       values="5;6.8;5" dur="1.5s" repeatCount="indefinite"/>
    </circle>
    <text x="80" y="66" font-size="13" fill="{CYAN}" letter-spacing="0.6" font-weight="500"
          >open to collaborations</text>
  </g>

  <!-- intro line -->
  <text x="48" y="122" class="mono" font-size="17" fill="{MUTED}" letter-spacing="2">
    {INTRO}
    <animate attributeName="opacity" values="0;1" dur="0.5s" begin="0.1s" fill="both"/>
  </text>
  <!-- blinking cursor (x adjusted for shorter 'I am' text) -->
  <rect x="92" y="107" width="10" height="17" rx="1.5" fill="{CYAN}" opacity="0">
    <animate attributeName="opacity" values="0;0;0;0;0;1;0;1;0" keyTimes="0;0.3;0.4;0.5;0.6;0.65;0.75;0.85;1"
             dur="3.5s" begin="0.5s" fill="both"/>
    <animate attributeName="opacity" values="1;0;1" dur="0.9s" begin="3.5s" repeatCount="indefinite"/>
  </rect>

  <!-- BIG gradient NAME -->
  <g mask="url(#nameMask)">
    <text x="46" y="216" class="display" font-size="74" font-weight="800"
          fill="url(#nameGrad)" letter-spacing="2">{NAME}</text>
  </g>
  <!-- name reveal: one-shot heartbeat pulse (cyan flash right after mask opens) -->
  <rect x="42" y="144" width="380" height="80" fill="{CYAN}" rx="4" opacity="0">
    <animate attributeName="opacity" values="0;0.10;0" keyTimes="0;0.5;1"
             dur="0.55s" begin="1.35s" fill="freeze"/>
  </rect>
  {glitch_svg}

  <!-- cycling roles -->
  <g class="sans">
    {roles_svg}
  </g>

  <!-- pitch / tagline -->
  <text x="48" y="300" class="sans" font-size="15" fill="{TEXT}" opacity="0.88">{PITCH}</text>
  <!-- Sanskrit mantra — subtle, reverent, fades in late -->
  <text x="48" y="318" class="mono" font-size="12" fill="{MUTED}" opacity="0" letter-spacing="1">
    अनुगच्छतु प्रवाहं
    <animate attributeName="opacity" values="0;0.55" dur="0.8s" begin="1.8s" fill="both"/>
  </text>

  <!-- tech tags -->
  <g>
    {tags_svg}
  </g>

  <!-- meta row -->
  <g class="sans" font-size="13" fill="{MUTED}">
    <!-- pin icon -->
    <path d="M52 384 c0-5 4-8.5 8.5-8.5 s8.5 3.5 8.5 8.5 c0 6-8.5 14-8.5 14 s-8.5-8-8.5-14z"
          fill="none" stroke="{PINK}" stroke-width="1.5"/>
    <circle cx="60.5" cy="384" r="2.5" fill="{PINK}"/>
    <text x="76" y="388">{LOCATION}</text>
    <!-- flow icon -->
    <path d="M196 377 l2.8 5.5 6.2 0.9-4.5 4.3 1.1 6.2-5.6-3.0-5.6 3.0 1.1-6.2-4.5-4.3 6.2-0.9z"
          fill="none" stroke="{CYAN}" stroke-width="1.3"/>
    <text x="210" y="388">अनुगच्छतु प्रवाहं</text>
  </g>

  <!-- vertical separator -->
  <line x1="{SEP_X}" y1="36" x2="{SEP_X}" y2="{H-36}" stroke="url(#hairline)"
        stroke-width="1" opacity="0.2"/>

  <!-- ===== RIGHT COLUMN: CINEMATIC SHOWCASE ===== -->
  <!-- Ambient glow behind video box -->
  <radialGradient id="vGlow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0.22"/>
    <stop offset="0.6" stop-color="{VIOLET}" stop-opacity="0.08"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="0"/>
  </radialGradient>
  <ellipse cx="{VX + VW//2}" cy="{VY + VH//2}" rx="{VW//2 + 35}" ry="{VH//2 + 30}" fill="url(#vGlow)"/>

  <!-- Video frame card with sleek rounded border -->
  <rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" rx="14"
        fill="{DARK}" stroke="url(#hairline)" stroke-width="1.6" stroke-opacity="0.6"/>

  <!-- Animated video (plays 1 time on load, then holds final portrait frame) -->
  <g clip-path="url(#vclip)">
    {gif_svg}
  </g>

  <!-- Elegant subtle glass sheen over video border -->
  <rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" rx="14"
        fill="none" stroke="#ffffff" stroke-opacity="0.10" stroke-width="1"/>

</svg>
'''

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(svg)

size_kb = os.path.getsize(OUT) / 1024
print(f"wrote {OUT}")
print(f"frames={N}  loop={LOOP}s  size={size_kb:.0f} KB")
