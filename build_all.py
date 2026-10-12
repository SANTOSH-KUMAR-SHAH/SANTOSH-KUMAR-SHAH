#!/usr/bin/env python3
"""Build all 5 animated SVG cards for Santosh's GitHub Profile."""
import subprocess
import sys
import time

SCRIPTS = [
    ("Hero (video, name reveal, mantra)", "build_hero.py"),
    ("About & Habits (value props, carousel, daily rings)", "build_about.py"),
    ("Stack (planetary orbit, categorized chips)", "build_stack.py"),
    ("Dashboard (holographic ID badge, verified stats)", "build_idash.py"),
    ("Connect (character spotlight, social cards)", "build_connect.py"),
]

def main():
    print("=" * 60)
    print(" BUILDING ANIMATED GITHUB PROFILE CARDS")
    print("=" * 60)
    t0 = time.time()
    for name, script in SCRIPTS:
        print(f"\n-> Building: {name} ({script})...")
        res = subprocess.run([sys.executable, script], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"ERROR building {script}:")
            print(res.stderr)
            sys.exit(1)
        else:
            print(res.stdout.strip())

    total_time = time.time() - t0
    print("\n" + "=" * 60)
    print(f" ALL 5 SVGs BUILT CLEANLY in {total_time:.1f}s!")
    print(" Preview file: profile/preview_full.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
