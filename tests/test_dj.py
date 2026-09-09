"""Tests for the DJ group — the constraints a sample-deck one-shot must meet.

A DJ sample is judged differently from a music-production sample. It has to be
short enough to trigger by hand, it has to start the instant it is fired, and
it has to sit in a mix without eating headroom. Those are the three things
pinned down here.
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
from build import GROUP_DESCRIPTIONS, GROUP_ORDER

DJ = {m.CATEGORY: m for m in generators.discover() if m.GROUP == "dj"}
OUT = os.path.join(ROOT, "output", "dj")

# Category name -> the prefix its sounds carry. They differ because a folder
# reads better plural and a filename reads better singular.
PREFIX = {"stabs": "stab_", "scratch": "scratch_", "horns": "horn_",
          "drops": "drop_", "vox": "vox_"}

MAX_SECONDS = 1.2


def read(path):
    with wave.open(path) as w:
        raw = w.readframes(w.getnframes())
    return [v / 32768.0 for v in struct.unpack("<%dh" % (len(raw) // 2), raw)]


def files():
    for cat in sorted(DJ):
        for name, _, _ in DJ[cat].SOUNDS:
            p = os.path.join(OUT, cat, name + ".wav")
            if os.path.exists(p):
                yield cat, name, p


class TestGroup(unittest.TestCase):
    def test_the_dj_group_is_registered_in_the_build(self):
        self.assertIn("dj", GROUP_DESCRIPTIONS)
        self.assertIn("dj", GROUP_ORDER)

    def test_all_five_categories_are_present(self):
        self.assertEqual(set(DJ), set(PREFIX))

    def test_each_category_ships_twenty_sounds(self):
        for cat, m in DJ.items():
            with self.subTest(category=cat):
                self.assertEqual(len(m.SOUNDS), 20)

    def test_names_carry_their_category_prefix(self):
        for cat, m in DJ.items():
            for name, _, _ in m.SOUNDS:
                with self.subTest(sound=name):
                    self.assertTrue(name.startswith(PREFIX[cat]))


class TestDJConstraints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = list(files())
        if len(cls.files) != 100:
            raise unittest.SkipTest("run build.py -g dj first")

    def test_nothing_runs_longer_than_a_trigger_should(self):
        for cat, name, p in self.files:
            xs = read(p)
            with self.subTest(sound=name):
                self.assertLessEqual(len(xs) / 44100, MAX_SECONDS)

    def test_the_group_averages_well_under_a_second(self):
        durs = [len(read(p)) / 44100 for _, _, p in self.files]
        self.assertLess(sum(durs) / len(durs), 0.60)

    def test_they_are_much_shorter_than_the_music_motifs(self):
        """The whole point of the group: these are triggered, not scheduled."""
        dj = sum(len(read(p)) / 44100 for _, _, p in self.files) / len(self.files)
        music = []
        for cat in ("piano", "harp", "brass", "strings"):
            d = os.path.join(ROOT, "output", "music", cat)
            music += [len(read(os.path.join(d, f))) / 44100
                      for f in os.listdir(d) if f.endswith(".wav")]
        self.assertLess(dj, 0.5 * (sum(music) / len(music)))

    def test_no_dead_head(self):
        """Silence at the start is latency a deck cannot compensate for."""
        for cat, name, p in self.files:
            xs = read(p)
            first = next((i for i, x in enumerate(xs) if abs(x) > 2e-4), len(xs))
            with self.subTest(sound=name):
                self.assertLess(first / 44100, 0.005)

    def test_no_dc_offset(self):
        """A DC step eats headroom in a mix and can click on trigger."""
        for cat, name, p in self.files:
            xs = read(p)
            with self.subTest(sound=name):
                self.assertLess(abs(sum(xs) / len(xs)), 0.005)

    def test_most_of_them_punch_at_the_front(self):
        """85 of 100 reach 70% of their peak inside 30 ms. The rest are the
        ones that are supposed to arrive rather than hit — risers, sweeps, a
        fog horn, and the shouts, which begin with a consonant."""
        front = 0
        for cat, name, p in self.files:
            xs = read(p)
            pk = max(abs(x) for x in xs)
            head = max(abs(x) for x in xs[:int(0.030 * 44100)])
            front += head >= 0.70 * pk
        self.assertGreaterEqual(front, 80)

    def test_stabs_and_scratches_all_punch(self):
        """Those two categories have no excuse: every one is a hit."""
        for cat, name, p in self.files:
            if cat not in ("stabs", "scratch"):
                continue
            xs = read(p)
            pk = max(abs(x) for x in xs)
            head = max(abs(x) for x in xs[:int(0.030 * 44100)])
            with self.subTest(sound=name):
                self.assertGreaterEqual(head, 0.70 * pk)


class TestScratchMotion(unittest.TestCase):
    """A scratch is a motion, so the properties worth pinning are about the
    platter, not the timbre."""

    def test_a_negative_speed_really_plays_backwards(self):
        from generators.scratch import _platter
        fwd = _platter(lambda t: 1.0, 0.10, gate=None, hiss=0.0)
        back = _platter(lambda t: -1.0, 0.10, gate=None, hiss=0.0)
        # same material, opposite direction: the waveforms must not agree
        self.assertGreater(max(abs(a - b) for a, b in zip(fwd, back)), 0.1)

    def test_the_fader_gate_actually_silences(self):
        from generators.scratch import _platter, _chop, _click
        open_ = _platter(lambda t: 1.0, 0.20, hiss=0.0)
        cut = _platter(lambda t: 1.0, 0.20, gate=_click(_chop([0.10], 0.20)),
                       hiss=0.0)
        tail_open = max(abs(x) for x in open_[int(0.15*44100):])
        tail_cut = max(abs(x) for x in cut[int(0.15*44100):])
        self.assertLess(tail_cut, 0.25 * tail_open)

    def test_platter_speed_sets_the_pitch(self):
        """The defining claim: the record read at speed s sounds at f0*s. A
        spectral centroid is the wrong instrument for this — the 7 kHz cabinet
        filter squashes it — so the fundamental is measured directly."""
        from generators.scratch import _platter
        from synth import note
        f0 = note("A2")                              # 110 Hz at normal speed

        def mag(xs, f):
            w = 2 * math.pi * f / 44100
            c = 2 * math.cos(w)
            s1 = s2 = 0.0
            for x in xs:
                s0 = x + c * s1 - s2
                s2, s1 = s1, s0
            return math.sqrt(abs(s1*s1 + s2*s2 - c*s1*s2)) / len(xs)

        normal = _platter(lambda t: 1.0, 0.25, hiss=0.0)
        octave = _platter(lambda t: 2.0, 0.25, hiss=0.0)
        self.assertGreater(mag(normal, f0), mag(normal, f0 * 2))
        self.assertGreater(mag(octave, f0 * 2), mag(octave, f0))


class TestVoxFormants(unittest.TestCase):
    """A vowel is its formant pattern, so different vowels must actually put
    their energy in different places."""

    def _mag(self, xs, f):
        w = 2 * math.pi * f / 44100
        c = 2 * math.cos(w)
        s1 = s2 = 0.0
        for x in xs:
            s0 = x + c * s1 - s2
            s2, s1 = s1, s0
        return math.sqrt(abs(s1*s1 + s2*s2 - c*s1*s2)) / len(xs)

    def _body(self, name):
        p = os.path.join(OUT, "vox", name + ".wav")
        if not os.path.exists(p):
            self.skipTest("run build.py -g dj first")
        return read(p)[int(0.02*44100):int(0.10*44100)]

    def test_eh_has_the_high_second_formant_that_ah_lacks(self):
        eh, ah = self._body("vox_chop_eh"), self._body("vox_chop_ah")
        self.assertGreater(self._mag(eh, 1840) / max(1e-9, self._mag(ah, 1840)), 4.0)

    def test_oo_is_missing_the_upper_formants(self):
        oo, ah = self._body("vox_chop_oo"), self._body("vox_chop_ah")
        self.assertGreater(self._mag(ah, 1090) / max(1e-9, self._mag(oo, 1090)), 3.0)

    def test_a_moving_tract_changes_the_spectrum_across_the_word(self):
        """"Hey" ends somewhere different from where it starts."""
        p = os.path.join(OUT, "vox", "vox_hey.wav")
        if not os.path.exists(p):
            self.skipTest("run build.py -g dj first")
        xs = read(p)
        head = xs[int(0.04*44100):int(0.10*44100)]
        tail = xs[int(0.16*44100):int(0.22*44100)]

        def norm(seg, f):
            return self._mag(seg, f) / max(1e-9, self._mag(seg, 400))
        self.assertNotAlmostEqual(norm(head, 1840), norm(tail, 1840), delta=0.05)


if __name__ == "__main__":
    unittest.main()
