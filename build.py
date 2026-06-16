#!/usr/bin/env python3
"""
build.py — generate every sound effect into output/<category>/, sorted.

Usage:
    python3 build.py                 # build everything (WAV + MP3 if ffmpeg)
    python3 build.py --list          # list categories & sounds, generate nothing
    python3 build.py -c clicks ui    # only these categories
    python3 build.py --no-mp3        # WAV only
    python3 build.py --wav-only      # alias for --no-mp3

Output layout:
    output/
      <category>/
        <name>.wav
        <name>.mp3
      manifest.json                  # machine-readable index of everything
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from synth.core import SR, write_wav          # noqa: E402
import generators                              # noqa: E402

OUT = os.path.join(ROOT, "output")


def have_ffmpeg():
    return shutil.which("ffmpeg") is not None


def to_mp3(wav_path):
    mp3_path = wav_path[:-4] + ".mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
         "-codec:a", "libmp3lame", "-qscale:a", "4", mp3_path],
        check=True,
    )
    return mp3_path


def human(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def main():
    ap = argparse.ArgumentParser(description="Generate UI sound effects.")
    ap.add_argument("-c", "--category", nargs="+", metavar="CAT",
                    help="only build these categories")
    ap.add_argument("--list", action="store_true",
                    help="list everything and exit (no generation)")
    ap.add_argument("--no-mp3", "--wav-only", dest="no_mp3", action="store_true",
                    help="skip MP3 encoding")
    args = ap.parse_args()

    mods = generators.discover()
    if args.category:
        wanted = set(args.category)
        mods = [m for m in mods if m.CATEGORY in wanted]
        if not mods:
            print("No matching categories. Available:",
                  ", ".join(sorted(m.CATEGORY for m in generators.discover())))
            return 1

    if args.list:
        total = 0
        for m in mods:
            print(f"\n\033[1m{m.CATEGORY}\033[0m — {m.DESCRIPTION}")
            for name, desc, _ in m.SOUNDS:
                print(f"    {name:<18} {desc}")
                total += 1
        print(f"\n{len(mods)} categories, {total} sounds.")
        return 0

    make_mp3 = not args.no_mp3 and have_ffmpeg()
    if not args.no_mp3 and not make_mp3:
        print("note: ffmpeg not found — generating WAV only.\n")

    os.makedirs(OUT, exist_ok=True)
    manifest = {"sample_rate": SR, "categories": []}
    grand_total = 0

    for m in mods:
        cat_dir = os.path.join(OUT, m.CATEGORY)
        os.makedirs(cat_dir, exist_ok=True)
        cat_entry = {"name": m.CATEGORY, "description": m.DESCRIPTION, "sounds": []}
        print(f"\033[1m{m.CATEGORY}\033[0m — {m.DESCRIPTION}")

        for name, desc, fn in m.SOUNDS:
            samples = fn()
            wav_path = os.path.join(cat_dir, name + ".wav")
            dur = write_wav(wav_path, samples)
            files = {"wav": os.path.relpath(wav_path, ROOT)}
            size = os.path.getsize(wav_path)
            if make_mp3:
                mp3_path = to_mp3(wav_path)
                files["mp3"] = os.path.relpath(mp3_path, ROOT)
            cat_entry["sounds"].append({
                "name": name, "description": desc,
                "duration_s": round(dur, 3), "files": files,
            })
            print(f"    \033[32m✓\033[0m {name:<18} {dur:0.2f}s  {human(size):>7}  {desc}")
            grand_total += 1

        cat_entry["sounds"].sort(key=lambda x: x["name"])
        manifest["categories"].append(cat_entry)
        print()

    manifest["categories"].sort(key=lambda c: c["name"])
    manifest["total_sounds"] = grand_total
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Done: {grand_total} sounds across {len(mods)} categories "
          f"→ {os.path.relpath(OUT, ROOT)}/")
    print("Wrote output/manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
