#!/usr/bin/env python3
"""
build.py — generate every sound effect into output/<group>/<category>/, sorted.

Sounds are split into two use cases (the generator's GROUP):
    interface/  — computer & UI interaction sounds
    music/      — FL-Studio-style music-production samples

Usage:
    python3 build.py                 # build everything (WAV only)
    python3 build.py --list          # list groups, categories & sounds, build nothing
    python3 build.py -g music        # only this group (interface | music)
    python3 build.py -c drums ui     # only these categories
    python3 build.py --mp3           # also encode an MP3 copy (needs ffmpeg)

Output layout:
    output/
      <group>/
        <category>/
          <name>.wav
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

GROUP_DESCRIPTIONS = {
    "interface": "Computer & UI interaction sounds.",
    "music": "FL-Studio-style music-production samples.",
}
GROUP_ORDER = {"interface": 0, "music": 1}


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


def group_of(m):
    return getattr(m, "GROUP", "misc")


def main():
    ap = argparse.ArgumentParser(description="Generate UI & music sound effects.")
    ap.add_argument("-g", "--group", nargs="+", metavar="GRP",
                    help="only build these groups (interface | music)")
    ap.add_argument("-c", "--category", nargs="+", metavar="CAT",
                    help="only build these categories")
    ap.add_argument("--list", action="store_true",
                    help="list everything and exit (no generation)")
    ap.add_argument("--mp3", action="store_true",
                    help="also encode an MP3 copy alongside each WAV (needs ffmpeg)")
    args = ap.parse_args()

    mods = generators.discover()
    if args.group:
        wanted = set(args.group)
        mods = [m for m in mods if group_of(m) in wanted]
    if args.category:
        wanted = set(args.category)
        mods = [m for m in mods if m.CATEGORY in wanted]
    if not mods:
        avail_g = sorted({group_of(m) for m in generators.discover()})
        avail_c = sorted(m.CATEGORY for m in generators.discover())
        print("No matching generators.")
        print("  groups:    ", ", ".join(avail_g))
        print("  categories:", ", ".join(avail_c))
        return 1

    # Stable order: interface group first, then music, categories alphabetical.
    mods.sort(key=lambda m: (GROUP_ORDER.get(group_of(m), 9), m.CATEGORY))

    if args.list:
        total = 0
        cur_group = None
        for m in mods:
            g = group_of(m)
            if g != cur_group:
                cur_group = g
                print(f"\n\033[1;4m{g}\033[0m — {GROUP_DESCRIPTIONS.get(g, '')}")
            print(f"  \033[1m{m.CATEGORY}\033[0m — {m.DESCRIPTION}")
            for name, desc, _ in m.SOUNDS:
                print(f"      {name:<18} {desc}")
                total += 1
        n_groups = len({group_of(m) for m in mods})
        print(f"\n{n_groups} groups, {len(mods)} categories, {total} sounds.")
        return 0

    make_mp3 = args.mp3 and have_ffmpeg()
    if args.mp3 and not make_mp3:
        print("note: ffmpeg not found — generating WAV only.\n")

    os.makedirs(OUT, exist_ok=True)
    # Merge into an existing manifest so partial builds don't drop groups.
    manifest_path = os.path.join(OUT, "manifest.json")
    groups = {}  # group name -> {name, description, categories: {cat -> entry}}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path) as f:
                prev = json.load(f)
            for g in prev.get("groups", []):
                groups[g["name"]] = {
                    "name": g["name"], "description": g.get("description", ""),
                    "categories": {c["name"]: c for c in g.get("categories", [])},
                }
        except (json.JSONDecodeError, OSError):
            groups = {}
    grand_total = 0
    cur_group = None

    for m in mods:
        g = group_of(m)
        if g != cur_group:
            cur_group = g
            print(f"\033[1;4m{g}\033[0m — {GROUP_DESCRIPTIONS.get(g, '')}")
        cat_dir = os.path.join(OUT, g, m.CATEGORY)
        os.makedirs(cat_dir, exist_ok=True)
        cat_entry = {"name": m.CATEGORY, "description": m.DESCRIPTION, "sounds": []}
        print(f"  \033[1m{m.CATEGORY}\033[0m — {m.DESCRIPTION}")

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
        grp = groups.setdefault(g, {"name": g, "categories": {}})
        grp["description"] = GROUP_DESCRIPTIONS.get(g, grp.get("description", ""))
        grp["categories"][m.CATEGORY] = cat_entry
        print()

    # Serialize manifest: groups in canonical order, categories sorted.
    out_groups = []
    for g in sorted(groups.values(), key=lambda x: GROUP_ORDER.get(x["name"], 9)):
        cats = sorted(g["categories"].values(), key=lambda c: c["name"])
        out_groups.append({
            "name": g["name"], "description": g["description"], "categories": cats,
        })
    total_sounds = sum(len(c["sounds"]) for g in out_groups for c in g["categories"])
    manifest = {
        "sample_rate": SR,
        "total_sounds": total_sounds,
        "groups": out_groups,
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    n_groups = len({group_of(m) for m in mods})
    print(f"Done: {grand_total} sounds across {len(mods)} categories "
          f"in {n_groups} group(s) → {os.path.relpath(OUT, ROOT)}/")
    print("Wrote output/manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
