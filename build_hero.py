#!/usr/bin/env python3
"""Build cinema-grade hero.svg with a 50/50 split:
Left half:  Spacious, high-end editorial bio, typography, roles, pitch, chips, and mantra.
Right half: Full-height, full-bleed video that seamlessly blends into the dark card canvas.
            Plays smoothly 1 time on open, then holds the final portrait frame.
            Zero blank space. Zero player chrome. Pure cinema.

Transition: Diagonal slash cut between left and right — design-genius seam.
"""
import base64
import glob
import os
import random
import numpy as np
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

# ---- geometry: 50 / 50 split
W, H   = 900, 410
VW, VH = 450, 410   # right half is filled 100% by the video (no blank borders!)
VX, VY = 450, 0
SEP_X  = 450

# ---- Diagonal slash: the "design genius" transition
# The diagonal goes from (SEP_X - SLASH, 0) to (SEP_X + SLASH, H)
# This creates a parallelogram-shaped video panel with a cinematic angled cut
SLASH  = 28   # how many px the diagonal sweeps across (bigger = more dramatic)
# Top-left corner of the diagonal video panel starts at (SEP_X - SLASH, 0)
DIAG_TOP_LEFT  = SEP_X - SLASH   # 422
DIAG_BOT_LEFT  = SEP_X + SLASH   # 478
# The video clipPath polygon (covers the right half with a diagonal left edge):
VIDEO_CLIP_POLY = f"{DIAG_TOP_LEFT},0 {W},0 {W},{H} {DIAG_BOT_LEFT},{H}"
# The glowing seam line follows the diagonal:
SEAM_X1, SEAM_Y1 = DIAG_TOP_LEFT, 0
SEAM_X2, SEAM_Y2 = DIAG_BOT_LEFT, H
# Gradient feather: in the video, fade from BG color to transparent over ~60px from the diagonal edge
# We simulate this with a polygon gradient overlay placed on top of the video

# ---- Build seamless full-height video GIF from all 29 frames
frames = sorted(glob.glob(os.path.join(FRAME_DIR, "h_*.jpg")))
if not frames:
    raise SystemExit("No frames found in assets/frames/ — check assets directory.")
frames = frames[1:]  # skip frame 1 -> gives exactly 29 frames (h_002 to h_030)
N = len(frames)

# Scale frames so height matches card height (410px), crop width to 450px centered on Santosh & neon sign
scale = VH / 270.0               # 410 / 270 = 1.5185
scaled_w = int(480 * scale)       # 728px
x0 = 200                         # sweet spot: Santosh on left (x~50-180), Neon on right (x~220-410)
fade_w = 45                      # soften left seam into card background #0d0e16
bg_color = np.array([13, 14, 22], dtype=np.float32)
ramp = np.linspace(0.0, 1.0, fade_w, endpoint=True).reshape((1, fade_w, 1))

gif_imgs = []
for f in frames:
    im = Image.open(f).convert("RGB")
    scaled = im.resize((scaled_w, VH), Image.LANCZOS)
    cropped = scaled.crop((x0, 0, x0 + VW, VH))
    arr = np.array(cropped, dtype=np.float32)
    # Blend leftmost 45 pixels smoothly into #0d0e16
    arr[:, :fade_w, :] = bg_color * (1.0 - ramp) + arr[:, :fade_w, :] * ramp
    blended = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    gif_imgs.append(blended.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=1))

dur_ms = int(4600 / len(frames))   # ~158ms per frame, ~4.6s total playback
gif_imgs[0].save(
    GIF_PATH, format="GIF", save_all=True,
    append_images=gif_imgs[1:],
    duration=dur_ms, optimize=True
)  # Note: loop parameter omitted -> plays 1 time on load, then holds final frame!

with open(GIF_PATH, "rb") as fh:
    gif_b64 = base64.b64encode(fh.read()).decode("ascii")

print(f"built seamless full-bleed GIF: {len(frames)} frames, {dur_ms}ms each -> {os.path.getsize(GIF_PATH)//1024}KB")


# ====== ANIMATED GIF EMBED (clipped to diagonal right panel) ==================
gif_svg = (
    f'<image x="{VX}" y="{VY}" width="{VW}" height="{VH}" '
    f'href="data:image/gif;base64,{gif_b64}" xlink:href="data:image/gif;base64,{gif_b64}" '
    f'preserveAspectRatio="none" clip-path="url(#videoClip)"/>'
)

# ====== CYCLING ROLES (smooth crossfade, zero discrete pops) ==================
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
        f'<text x="44" y="210" class="sans" font-size="19" font-weight="700" fill="{CYAN}" letter-spacing="0.8" opacity="0">[ {role} ]'
        f'<animate attributeName="opacity" values="{kv}" keyTimes="{kt}" '
        f'dur="{ROLE_CYCLE}s" begin="0s" repeatCount="indefinite" fill="both"/></text>'
    )
roles_svg = "\n      ".join(role_parts)

# ====== TECH TAG CHIPS (left column, perfectly fitted) ========================
TAG_COLS = [CYAN, VIOLET, PINK, CYAN, VIOLET]
tag_parts = []
tx = 44
for i, tag in enumerate(TAGS):
    col = TAG_COLS[i]
    tw = int(16 + len(tag) * 8.0)
    delay = i * 0.45
    tag_parts.append(
        f'<g transform="translate({tx},300)">'
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

# ====== TWINKLING PARTICLES (kept in left column to avoid covering subject) ==
rng = random.Random(7)
particles = []
for _ in range(22):
    px = rng.uniform(15, SEP_X - 25)
    py = rng.uniform(15, H - 15)
    pr = rng.uniform(0.6, 1.8)
    col = rng.choice([CYAN, VIOLET, PINK, "#ffffff"])
    dur = rng.uniform(2.5, 6.5)
    beg = rng.uniform(0.0, 5.0)
    peak = rng.uniform(0.12, 0.45)
    particles.append(
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{pr:.1f}" fill="{col}" opacity="0">'
        f'<animate attributeName="opacity" values="0;{peak:.2f};0" '
        f'dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/>'
        f'</circle>'
    )
particles_svg = "\n  ".join(particles)

# ====== FULL-CARD LIGHT BEAM ==================================================
beam_svg = f"""
  <rect x="-140" y="0" width="180" height="{H}" fill="url(#beamGrad)" opacity="0">
    <animate attributeName="x" values="-180;{W+180}"
             dur="1.8s" begin="0.8s;10s;20s"
             calcMode="spline" keySplines="0.25 0 0.75 1" fill="freeze"/>
    <animate attributeName="opacity" values="0;0.55;0.55;0"
             keyTimes="0;0.15;0.85;1"
             dur="1.8s" begin="0.8s;10s;20s" fill="freeze"/>
  </rect>"""

# ====== DIAGONAL SEAM: the glowing angled line between left and right panels ==
# A thin glowing line following the diagonal, with animated pulse + glow spread
seam_svg = f"""
  <!-- ===== DESIGN GENIUS DIAGONAL SEAM ===== -->
  <!-- Main glowing seam line -->
  <line x1="{SEAM_X1}" y1="{SEAM_Y1}" x2="{SEAM_X2}" y2="{SEAM_Y2}"
        stroke="url(#seamGrad)" stroke-width="1.6" opacity="0">
    <animate attributeName="opacity" values="0;0.9;0.55;0.85;0.55"
             keyTimes="0;0.08;0.3;0.55;1"
             dur="4s" begin="0.3s" repeatCount="indefinite" fill="both"/>
  </line>
  <!-- Wide soft halo around the seam (glow bloom) -->
  <line x1="{SEAM_X1}" y1="{SEAM_Y1}" x2="{SEAM_X2}" y2="{SEAM_Y2}"
        stroke="url(#seamGlowWide)" stroke-width="22" opacity="0">
    <animate attributeName="opacity" values="0;0.18;0.06;0.14;0.06"
             keyTimes="0;0.08;0.3;0.55;1"
             dur="4s" begin="0.3s" repeatCount="indefinite" fill="both"/>
  </line>
  <!-- Seam sparkle: a tiny bright point travels down the seam -->
  <circle r="3.5" fill="{CYAN}" filter="url(#seamSparkBlur)" opacity="0">
    <animateMotion dur="2.2s" begin="0.5s;5s;10s;17s" fill="freeze"
                   calcMode="spline" keySplines="0.42 0 0.58 1">
      <mpath href="#seamPath"/>
    </animateMotion>
    <animate attributeName="opacity" values="0;0;0.9;0.9;0" keyTimes="0;0.05;0.15;0.85;1"
             dur="2.2s" begin="0.5s;5s;10s;17s" fill="freeze"/>
  </circle>
  <!-- Path for animateMotion (must match the seam diagonal exactly) -->
  <path id="seamPath" d="M{SEAM_X1},{SEAM_Y1} L{SEAM_X2},{SEAM_Y2}" fill="none" stroke="none"/>
  <!-- Left-side feather gradient: BG fades into the seam -->
  <polygon points="{DIAG_TOP_LEFT - 60},0 {DIAG_TOP_LEFT},0 {DIAG_BOT_LEFT},{H} {DIAG_BOT_LEFT - 60},{H}"
           fill="url(#leftFeather)" opacity="0.92"/>"""

# ====== ASSEMBLE SVG ==========================================================
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100%" viewBox="0 0 {W} {H}" role="img"
     aria-label="{NAME} — animated profile hero">
  <defs>
    <!-- name gradient -->
    <linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"   stop-color="{CYAN}"/>
      <stop offset="0.45" stop-color="{VIOLET}"/>
      <stop offset="1"   stop-color="{PINK}"/>
    </linearGradient>

    <!-- border hairline — breathing pulse -->
    <linearGradient id="hairline" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0"   stop-color="{CYAN}"   stop-opacity="0.9"/>
      <stop offset="0.5" stop-color="{VIOLET}" stop-opacity="0.3"/>
      <stop offset="1"   stop-color="{PINK}"   stop-opacity="0.9"/>
    </linearGradient>

    <!-- ambient background glows -->
    <radialGradient id="glowL" cx="0.2" cy="0.45" r="0.6">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{BG}"     stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowStudio" cx="0.75" cy="0.5" r="0.6">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.16"/>
      <stop offset="0.6" stop-color="{VIOLET}" stop-opacity="0.06"/>
      <stop offset="1" stop-color="{BG}"   stop-opacity="0"/>
    </radialGradient>

    <!-- subtle dot texture on left canvas -->
    <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1" fill="#ffffff" opacity="0.028"/>
    </pattern>

    <!-- outer card clip (gives the full-bleed video perfect rounded corners) -->
    <clipPath id="cardClip">
      <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="19"/>
    </clipPath>

    <!-- DIAGONAL video panel clip — the design-genius angled cut -->
    <clipPath id="videoClip">
      <polygon points="{VIDEO_CLIP_POLY}"/>
    </clipPath>

    <!-- name reveal: smooth height unveil -->
    <mask id="nameMask" maskUnits="userSpaceOnUse"
          x="38" y="100" width="400" height="76">
      <rect x="38" y="100" width="400" height="76" fill="#fff"/>
      <rect x="38" y="100" width="400" height="0"  fill="#000">
        <animate attributeName="height" values="76;0" dur="0.9s"
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

    <!-- SEAM GRADIENTS: diagonal glow transition between panels -->
    <!-- Main seam line gradient: cyan→violet→pink from top to bottom -->
    <linearGradient id="seamGrad" x1="{SEAM_X1}" y1="{SEAM_Y1}" x2="{SEAM_X2}" y2="{SEAM_Y2}"
                    gradientUnits="userSpaceOnUse">
      <stop offset="0"   stop-color="{CYAN}"   stop-opacity="0.95"/>
      <stop offset="0.4" stop-color="{VIOLET}" stop-opacity="0.80"/>
      <stop offset="0.7" stop-color="{PINK}"   stop-opacity="0.90"/>
      <stop offset="1"   stop-color="{CYAN}"   stop-opacity="0.70"/>
    </linearGradient>
    <!-- Wide soft halo around seam -->
    <linearGradient id="seamGlowWide" x1="{SEAM_X1}" y1="{SEAM_Y1}" x2="{SEAM_X2}" y2="{SEAM_Y2}"
                    gradientUnits="userSpaceOnUse">
      <stop offset="0"   stop-color="{CYAN}"   stop-opacity="1"/>
      <stop offset="0.5" stop-color="{VIOLET}" stop-opacity="1"/>
      <stop offset="1"   stop-color="{PINK}"   stop-opacity="1"/>
    </linearGradient>
    <!-- Left feather: dark BG fades to transparent as you approach the seam -->
    <linearGradient id="leftFeather" x1="{DIAG_TOP_LEFT - 60}" y1="0" x2="{DIAG_TOP_LEFT}" y2="0"
                    gradientUnits="userSpaceOnUse">
      <stop offset="0"   stop-color="{BG}" stop-opacity="1"/>
      <stop offset="1"   stop-color="{BG}" stop-opacity="0"/>
    </linearGradient>

    <!-- Blur filter for seam sparkle -->
    <filter id="seamSparkBlur" x="-200%" y="-200%" width="500%" height="500%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <style>
      {FONTS_STYLE_ESCAPED}
    </style>
  </defs>

  <!-- ===== CARD SHELL ===== -->
  <g clip-path="url(#cardClip)">
    <rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>
    <rect x="0" y="0" width="{SEP_X}" height="{H}" fill="url(#dots)"/>
    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#glowL)"/>
    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#glowStudio)"/>

    <!-- ===== RIGHT HALF: SEAMLESS FULL-BLEED VIDEO ===== -->
    <!-- Plays smoothly 1 time on open, then holds final portrait frame -->
    {gif_svg}

    <!-- ===== DESIGN GENIUS DIAGONAL TRANSITION SEAM ===== -->
    {seam_svg}

    <!-- ===== PARTICLES ===== -->
    {particles_svg}

    <!-- ===== LIGHT BEAM ===== -->
    {beam_svg}

    <!-- ===== LEFT COLUMN ===== -->

    <!-- status pill -->
    <g class="sans">
      <rect x="44" y="34" width="206" height="28" rx="14"
            fill="{CYAN}" fill-opacity="0.08" stroke="{CYAN}" stroke-opacity="0.4" stroke-width="1.1"/>
      <circle cx="58" cy="48" r="4.5" fill="{CYAN}">
        <animate attributeName="opacity" values="1;0.2;1" dur="1.5s" repeatCount="indefinite"/>
        <animate attributeName="r"       values="4.5;6.0;4.5" dur="1.5s" repeatCount="indefinite"/>
      </circle>
      <text x="70" y="53" font-size="12" fill="{CYAN}" letter-spacing="0.5" font-weight="600"
            >open to collaborations</text>
    </g>

    <!-- intro line -->
    <text x="44" y="96" class="mono" font-size="15" fill="{MUTED}" letter-spacing="2">
      {INTRO}
      <animate attributeName="opacity" values="0;1" dur="0.5s" begin="0.1s" fill="both"/>
    </text>
    <!-- blinking cursor -->
    <rect x="88" y="83" width="8" height="15" rx="1.5" fill="{CYAN}" opacity="0">
      <animate attributeName="opacity" values="0;0;0;0;0;1;0;1;0" keyTimes="0;0.3;0.4;0.5;0.6;0.65;0.75;0.85;1"
               dur="3.5s" begin="0.5s" fill="both"/>
      <animate attributeName="opacity" values="1;0;1" dur="0.9s" begin="3.5s" repeatCount="indefinite"/>
    </rect>

    <!-- BIG gradient NAME (Single, pristine display title in Syne 800) -->
    <g mask="url(#nameMask)">
      <text x="42" y="164" class="display" font-size="64" font-weight="800"
            fill="url(#nameGrad)" letter-spacing="2">{NAME}</text>
    </g>
    <!-- subtle cyan reveal pulse -->
    <rect x="42" y="106" width="340" height="68" fill="{CYAN}" rx="4" opacity="0">
      <animate attributeName="opacity" values="0;0.08;0" keyTimes="0;0.5;1"
               dur="0.55s" begin="1.2s" fill="freeze"/>
    </rect>

    <!-- cycling roles -->
    <g class="sans">
      {roles_svg}
    </g>

    <!-- pitch / tagline -->
    <text x="44" y="246" class="sans" font-size="13.5" font-weight="500" fill="{TEXT}" opacity="0.9">{PITCH}</text>

    <!-- Sanskrit mantra -->
    <text x="44" y="270" class="mono" font-size="12" fill="{MUTED}" opacity="0.7" letter-spacing="1">
      अनुगच्छतु प्रवाहं
      <animate attributeName="opacity" values="0;0.7" dur="0.8s" begin="1.5s" fill="both"/>
    </text>

    <!-- tech tags -->
    <g>
      {tags_svg}
    </g>

    <!-- meta row -->
    <g class="sans" font-size="12.5" fill="{MUTED}">
      <!-- pin icon -->
      <path d="M48 358 c0-4.5 3.5-8 8-8 s8 3.5 8 8 c0 5.5-8 13-8 13 s-8-7.5-8-13z"
            fill="none" stroke="{PINK}" stroke-width="1.4"/>
      <circle cx="56" cy="358" r="2.2" fill="{PINK}"/>
      <text x="70" y="362">{LOCATION}</text>
      <!-- flow icon -->
      <path d="M192 352 l2.6 5.2 5.8 0.8-4.2 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.2-4.1 5.8-0.8z"
            fill="none" stroke="{CYAN}" stroke-width="1.3"/>
      <text x="206" y="362">अनुगच्छतु प्रवाहं</text>
    </g>
  </g>

  <!-- animated breathing border around entire card -->
  <rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="19" fill="none"
        stroke="url(#hairline)" stroke-width="1.8">
    <animate attributeName="stroke-opacity" values="0.9;0.35;0.9"
             dur="3.5s" repeatCount="indefinite"/>
  </rect>

</svg>
'''

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(svg)

size_kb = os.path.getsize(OUT) / 1024
print(f"wrote {OUT}")
print(f"frames={N}  size={size_kb:.0f} KB")
