"""Tests on the rendered audio itself.

These render sounds for real, so they take a few seconds. They assert the
properties a sample pack is judged on: nothing clips, nothing starts with a
gap, nothing is cut off mid-tail, and two builds of the same code produce
byte-identical files.
"""
import math
import os
import struct
import sys
import unittest
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import generators
from synth import SR, write_wav

MODS = {m.CATEGORY: m for m in generators.discover()}
OUT = os.path.join(ROOT, "output")


def read(path):
    with wave.open(path) as w:
        fmt = (w.getnchannels(), w.getsampwidth(), w.getframerate())
        raw = w.readframes(w.getnframes())
    return fmt, [v / 32768.0 for v in struct.unpack("<%dh" % (len(raw) // 2), raw)]


def built_files():
    # Groups come from the modules, not from a hand-typed list — adding a
    # group must not silently drop its files out of every test here.
    for group in sorted({m.GROUP for m in MODS.values()}):
        d = os.path.join(OUT, group)
        if not os.path.isdir(d):
            continue
        for cat in sorted(os.listdir(d)):
            cd = os.path.join(d, cat)
            if not os.path.isdir(cd):
                continue
            for f in sorted(os.listdir(cd)):
                if f.endswith(".wav"):
                    yield cat, f[:-4], os.path.join(cd, f)


class TestRenderedFiles(unittest.TestCase):
    """Runs over every WAV already on disk — cheap, and covers all of them."""

    @classmethod
    def setUpClass(cls):
        cls.files = list(built_files())
        if not cls.files:
            raise unittest.SkipTest("run build.py first")

    def test_all_are_mono_16_bit_44100(self):
        for cat, name, path in self.files:
            fmt, _ = read(path)
            with self.subTest(sound=name):
                self.assertEqual(fmt, (1, 2, SR))

    def test_nothing_clips(self):
        for cat, name, path in self.files:
            _, xs = read(path)
            with self.subTest(sound=name):
                self.assertEqual(sum(1 for x in xs if abs(x) >= 0.99969), 0)

    def test_nothing_is_silent(self):
        for cat, name, path in self.files:
            _, xs = read(path)
            with self.subTest(sound=name):
                self.assertGreater(max(abs(x) for x in xs), 0.1)

    def test_no_leading_silence(self):
        """A gap at the head, not a slow attack. A bow takes milliseconds to
        speak and a crescendo starts at nothing on purpose; both climb out of
        it, which a truncated or padded start does not."""
        for cat, name, path in self.files:
            _, xs = read(path)
            first = next((i for i, x in enumerate(xs) if abs(x) > 1e-4), len(xs))
            blocks = [max((abs(v) for v in xs[k*882:(k+1)*882]), default=0.0)
                      for k in range(15)]
            head, tail = sum(blocks[:5]) / 5, sum(blocks[10:]) / 5
            swell = blocks[0] > 0.0 and tail > 4.0 * head
            with self.subTest(sound=name):
                self.assertTrue(first / SR < 0.010 or swell,
                                "starts %.1f ms in without swelling" % (first/SR*1000))

    def test_tails_end_at_zero(self):
        """write_wav fades the last 30 ms, so no file can end on a step. Testing
        the tail's RMS instead would be wrong: a riser or a reverse cymbal is
        SUPPOSED to be at full level right up to its fade."""
        for cat, name, path in self.files:
            _, xs = read(path)
            peak = max(abs(x) for x in xs)
            with self.subTest(sound=name):
                self.assertLess(abs(xs[-1]), 0.01 * peak)
                back = min(int(0.03 * SR), len(xs) - 1)   # short UI blips exist
                self.assertLess(abs(xs[-1]), abs(xs[-back]) + 1e-9)

    def test_lengths_are_usable(self):
        for cat, name, path in self.files:
            _, xs = read(path)
            with self.subTest(sound=name):
                self.assertGreater(len(xs) / SR, 0.015)
                self.assertLess(len(xs) / SR, 5.0)

    def test_every_registered_sound_was_written(self):
        on_disk = {(c, n) for c, n, _ in self.files}
        for cat, m in MODS.items():
            for name, _, _ in m.SOUNDS:
                with self.subTest(sound=name):
                    self.assertIn((cat, name), on_disk)


class TestDeterminism(unittest.TestCase):
    """Seeded noise means a rebuild must reproduce the file exactly."""

    SAMPLE = [("guitar", "guitar_gallop"), ("harp", "harp_gliss_up"),
              ("piano", "piano_cadence"), ("choir", "choir_ah"),
              ("drums", "kick_808"), ("brass", "brass_triumph")]

    def test_rerendering_matches_the_file_on_disk(self):
        for cat, name in self.SAMPLE:
            path = os.path.join(OUT, MODS[cat].GROUP, cat, name + ".wav")
            if not os.path.exists(path):
                self.skipTest("run build.py first")
            fn = next(f for n, _, f in MODS[cat].SOUNDS if n == name)
            tmp = os.path.join(ROOT, ".determinism.wav")
            try:
                write_wav(tmp, fn())
                with open(path, "rb") as a, open(tmp, "rb") as b:
                    with self.subTest(sound=name):
                        self.assertEqual(a.read(), b.read())
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)

    def test_two_renders_in_one_process_agree(self):
        for cat, name in self.SAMPLE[:3]:
            fn = next(f for n, _, f in MODS[cat].SOUNDS if n == name)
            with self.subTest(sound=name):
                self.assertEqual(fn(), fn())


class TestMotifsAreMotifs(unittest.TestCase):
    """The instrument kits promise playable figures, not single hits.

    Counted from the event lists the generators hand to motif(), not from the
    audio: an envelope-based attack counter cannot see the notes of a walking
    bass line or a distorted riff, because compression and legato flatten
    exactly the transients it looks for (measured: it found 1 of 25 on ebass).
    """

    KITS = ("guitar", "ebass", "piano", "epiano", "strings", "mallets",
            "harp", "organ", "choir", "flute", "brass")

    def _event_counts(self, cat):
        """Call every sound with motif() stubbed out, recording event counts."""
        import generators._music as music
        mod = MODS[cat]
        real, seen = music.motif, []

        def spy(voice, steps, **kw):
            seen.append(len(list(steps)))
            return [0.0] * 512
        music.motif = spy
        # Modules may import it under another name (brass uses `motif as _motif`),
        # so rebind every alias the module actually holds.
        aliases = [a for a in dir(mod) if getattr(mod, a, None) is real]
        for a in aliases:
            setattr(mod, a, spy)
        try:
            counts = []
            for name, _, fn in mod.SOUNDS:
                seen.clear()
                fn()
                counts.append((name, max(seen) if seen else 0))
            return counts
        finally:
            music.motif = real
            for a in aliases:
                setattr(mod, a, real)

    def test_every_sound_is_built_from_at_least_one_event(self):
        for cat in self.KITS:
            for name, n in self._event_counts(cat):
                with self.subTest(sound=name):
                    self.assertGreaterEqual(n, 1)

    def test_most_of_each_kit_is_multi_note(self):
        """Each kit carries a handful of single-note articulations as building
        blocks; the rest are figures. Three fifths is the design."""
        for cat in self.KITS:
            counts = self._event_counts(cat)
            multi = sum(1 for _, n in counts if n >= 2)
            with self.subTest(kit=cat, multi=multi, total=len(counts)):
                self.assertGreaterEqual(multi, 8)

    def test_the_pack_as_a_whole_is_mostly_motifs(self):
        """Measured at 59% when written. The claim the pack makes is "more than
        half", not "almost all" — chords are a legitimate staple of a piano or
        organ kit and were never meant to be padded out into progressions."""
        multi = total = 0
        for cat in self.KITS:
            for _, n in self._event_counts(cat):
                total += 1
                multi += n >= 2
        self.assertGreater(multi / total, 0.5)


if __name__ == "__main__":
    unittest.main()
