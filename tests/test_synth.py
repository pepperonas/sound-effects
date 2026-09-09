"""Unit tests for the synthesis engine (synth/core.py).

Stdlib only, like the rest of the project: `python3 -m unittest discover tests`.
"""
import math
import os
import struct
import sys
import tempfile
import unittest
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synth import (SR, Noise, perc, ad, adsr, bell, sine, square, saw, triangle,
                   noise_burst, pluck, fm, mix, silence, ring_mod, lowpass,
                   highpass, drive, reverse, note, chord, vibrato, fade_in,
                   fade_out, normalize, write_wav)


def goertzel(xs, f, sr=SR):
    """Magnitude of `xs` at frequency `f` — a single-bin DFT."""
    w = 2 * math.pi * f / sr
    c = 2 * math.cos(w)
    s1 = s2 = 0.0
    for x in xs:
        s0 = x + c * s1 - s2
        s2, s1 = s1, s0
    return math.sqrt(abs(s1 * s1 + s2 * s2 - c * s1 * s2)) / max(1, len(xs))


def cents_off(xs, f_exp, span=40, step=2):
    """How far the strongest partial near `f_exp` sits from it, in cents."""
    return max(((goertzel(xs, f_exp * 2 ** (c / 1200.0)), c)
                for c in range(-span, span + 1, step)))[1]


class TestNoise(unittest.TestCase):
    def test_is_deterministic_for_a_given_seed(self):
        self.assertEqual([Noise(7)() for _ in range(5)],
                         [Noise(7)() for _ in range(5)])

    def test_different_seeds_differ(self):
        self.assertNotEqual([Noise(1)() for _ in range(5)],
                            [Noise(2)() for _ in range(5)])

    def test_stays_inside_minus_one_to_one(self):
        n = Noise(99)
        self.assertTrue(all(-1.0 <= n() <= 1.0 for _ in range(2000)))


class TestEnvelopes(unittest.TestCase):
    def test_perc_starts_at_one_and_decays(self):
        e = perc(10.0)
        self.assertAlmostEqual(e(0.0), 1.0)
        self.assertLess(e(0.5), e(0.1))

    def test_ad_rises_over_the_attack(self):
        e = ad(0.1, 0.2)
        self.assertAlmostEqual(e(0.0), 0.0)
        self.assertAlmostEqual(e(0.05), 0.5)
        self.assertAlmostEqual(e(0.1), 1.0)

    def test_adsr_holds_the_sustain_then_releases_to_zero(self):
        e = adsr(0.05, 0.05, 0.4, 0.1, 1.0)
        self.assertAlmostEqual(e(0.05), 1.0)          # peak of the attack
        self.assertAlmostEqual(e(0.5), 0.4)           # sustain plateau
        self.assertAlmostEqual(e(1.0), 0.0)           # fully released
        self.assertGreater(e(0.92), e(0.98))          # falling through release

    def test_bell_peaks_in_the_middle(self):
        e = bell(1.0)
        self.assertAlmostEqual(e(0.5), 1.0)
        self.assertLess(e(0.05), 0.2)
        self.assertLess(e(0.95), 0.2)


class TestOscillators(unittest.TestCase):
    def test_lengths_follow_the_duration(self):
        for f in (sine, square, saw, triangle):
            self.assertEqual(len(f(440.0, 0.25)), int(0.25 * SR))

    def test_sine_lands_on_its_own_frequency(self):
        self.assertEqual(cents_off(sine(440.0, 0.5), 440.0), 0)

    def test_square_holds_only_two_values(self):
        self.assertEqual(sorted(set(square(200.0, 0.05))), [-1.0, 1.0])

    def test_saw_has_even_and_odd_harmonics_but_square_has_only_odd(self):
        sq = square(200.0, 0.5)
        sw = saw(200.0, 0.5)
        self.assertLess(goertzel(sq, 400.0), 0.1 * goertzel(sq, 600.0))
        self.assertGreater(goertzel(sw, 400.0), 0.3 * goertzel(sw, 600.0))

    def test_a_callable_frequency_glides(self):
        xs = osc_glide = sine(lambda t: 200.0 if t < 0.25 else 400.0, 0.5)
        self.assertEqual(cents_off(xs[:10000], 200.0), 0)
        self.assertEqual(cents_off(xs[13000:], 400.0), 0)

    def test_unknown_shape_is_rejected(self):
        from synth.core import osc
        with self.assertRaises(ValueError):
            osc("sawtooth", 440.0, 0.01)


class TestPluck(unittest.TestCase):
    """Karplus-Strong. Tuning is the property that matters: a delay line of
    whole samples would be tens of cents sharp in the top octaves."""

    def test_is_in_tune_across_five_octaves(self):
        for name in ("C1", "C2", "G2", "C3", "E3", "G3", "C4", "E4", "C5", "C6"):
            f = note(name)
            with self.subTest(note=name):
                self.assertLessEqual(abs(cents_off(pluck(f, 0.5)[2000:20000], f)), 6)

    def test_damping_shortens_the_decay(self):
        def energy_after(damp):
            xs = pluck(note("C3"), 0.6, damp=damp)
            return sum(abs(v) for v in xs[17640:22050])
        self.assertLess(energy_after(0.85), energy_after(0.2))

    def test_decay_controls_sustain(self):
        def energy_after(decay):
            xs = pluck(note("C3"), 0.6, decay=decay)
            return sum(abs(v) for v in xs[17640:22050])
        self.assertLess(energy_after(0.97), energy_after(0.9995))

    def test_a_callable_frequency_bends_the_string(self):
        f0, f1 = note("C3"), note("D3")

        def bend(t):
            if t <= 0.15:
                return f0
            if t >= 0.25:
                return f1
            return f0 + (f1 - f0) * (t - 0.15) / 0.10
        xs = pluck(bend, 0.8)
        self.assertLessEqual(abs(cents_off(xs[int(.02*SR):int(.14*SR)], f0)), 10)
        self.assertLessEqual(abs(cents_off(xs[int(.35*SR):int(.60*SR)], f1)), 10)

    def test_is_deterministic(self):
        self.assertEqual(pluck(220.0, 0.1), pluck(220.0, 0.1))

    def test_zero_duration_is_empty_not_an_error(self):
        self.assertEqual(pluck(220.0, 0.0), [])


class TestFM(unittest.TestCase):
    def test_integer_ratio_gives_a_harmonic_series(self):
        xs = fm(200.0, 0.4, ratio=1.0, index=3.0)
        for h in (1, 2, 3):
            self.assertGreater(goertzel(xs, 200.0 * h), 0.01)

    def test_index_zero_is_a_plain_sine(self):
        a = fm(300.0, 0.2, ratio=1.0, index=0.0)
        b = sine(300.0, 0.2)
        self.assertLess(max(abs(x - y) for x, y in zip(a, b)), 1e-9)

    def test_a_non_integer_ratio_puts_energy_off_the_harmonic_grid(self):
        xs = fm(200.0, 0.4, ratio=1.41, index=4.0)
        self.assertGreater(goertzel(xs, 200.0 * 1.41), 0.0)

    def test_a_decaying_mod_env_makes_the_attack_brighter_than_the_body(self):
        xs = fm(200.0, 0.6, ratio=1.0, index=6.0, mod_env=perc(25.0))
        head = goertzel(xs[:4000], 1000.0)
        tail = goertzel(xs[18000:22000], 1000.0)
        self.assertGreater(head, 3 * tail)


class TestVibrato(unittest.TestCase):
    def test_swings_symmetrically_about_the_centre(self):
        v = vibrato(440.0, rate=5.0, depth=0.01)
        vals = [v(i / 1000.0) for i in range(1000)]
        self.assertAlmostEqual(sum(vals) / len(vals), 440.0, delta=0.5)
        self.assertAlmostEqual(max(vals), 440.0 * 1.01, delta=0.05)
        self.assertAlmostEqual(min(vals), 440.0 * 0.99, delta=0.05)

    def test_onset_delays_the_wobble(self):
        peak = 1 / (4 * 5.0)                       # first crest of the LFO
        full = vibrato(440.0, rate=5.0, depth=0.01)(peak)
        ramp = vibrato(440.0, rate=5.0, depth=0.01, onset=0.5)(peak)
        self.assertLess(ramp - 440.0, (full - 440.0) * 0.25)

    def test_accepts_a_note_name(self):
        self.assertAlmostEqual(vibrato("A4", depth=0.0)(0.0), 440.0, places=6)


class TestFiltersAndShaping(unittest.TestCase):
    def test_lowpass_keeps_lows_and_removes_highs(self):
        lo, hi = sine(100.0, 0.3), sine(8000.0, 0.3)
        self.assertGreater(goertzel(lowpass(lo, 500), 100.0), 0.4)
        self.assertLess(goertzel(lowpass(hi, 500), 8000.0), 0.1)

    def test_highpass_does_the_opposite(self):
        lo, hi = sine(100.0, 0.3), sine(8000.0, 0.3)
        self.assertLess(goertzel(highpass(lo, 2000), 100.0), 0.15)
        self.assertGreater(goertzel(highpass(hi, 2000), 8000.0), 0.4)

    def test_drive_is_bounded_and_compresses_peaks(self):
        xs = drive([1.0, -1.0, 0.5], 2.0)
        self.assertTrue(all(abs(x) < 1.0 for x in xs))
        self.assertLess(xs[0], 1.0)

    def test_reverse_mirrors_without_mutating_the_input(self):
        src = [1.0, 2.0, 3.0]
        self.assertEqual(reverse(src), [3.0, 2.0, 1.0])
        self.assertEqual(src, [1.0, 2.0, 3.0])

    def test_ring_mod_creates_sum_and_difference_tones(self):
        xs = ring_mod(sine(1000.0, 0.4), 200.0, depth=1.0)
        self.assertGreater(goertzel(xs, 1200.0), 0.05)
        self.assertGreater(goertzel(xs, 800.0), 0.05)

    def test_noise_burst_colour_removes_the_top(self):
        white = noise_burst(0.3, None, 0.0, Noise(5))
        warm = noise_burst(0.3, None, 0.95, Noise(5))
        self.assertLess(goertzel(warm, 9000.0), goertzel(white, 9000.0))


class TestMixing(unittest.TestCase):
    def test_mix_grows_the_target_and_offsets_in_time(self):
        target = []
        mix(target, [1.0, 1.0], at=1.0 / SR)
        self.assertEqual(target, [0.0, 1.0, 1.0])

    def test_mix_adds_rather_than_replaces(self):
        self.assertEqual(mix([1.0, 1.0], [2.0, 2.0], gain=0.5), [2.0, 2.0])

    def test_silence_is_the_right_length_and_empty(self):
        s = silence(0.01)
        self.assertEqual(len(s), int(0.01 * SR))
        self.assertEqual(set(s), {0.0})

    def test_normalize_hits_the_requested_peak(self):
        self.assertAlmostEqual(max(abs(x) for x in normalize([0.1, -0.2], 0.9)), 0.9)

    def test_fades_start_and_end_at_zero(self):
        self.assertEqual(fade_in([1.0] * 1000, ms=10)[0], 0.0)
        self.assertEqual(fade_out([1.0] * 1000, ms=10)[-1], 0.0)


class TestPitch(unittest.TestCase):
    def test_concert_a(self):
        self.assertAlmostEqual(note("A4"), 440.0)

    def test_octaves_double(self):
        self.assertAlmostEqual(note("C5"), note("C4") * 2, places=6)

    def test_accidentals(self):
        self.assertAlmostEqual(note("C#4"), note("Db4"), places=6)
        self.assertAlmostEqual(note("Bb3"), note("A#3"), places=6)

    def test_rejects_nonsense(self):
        with self.assertRaises(ValueError):
            note("H4")

    def test_chord_returns_the_requested_intervals(self):
        c = chord("C4", (0, 4, 7))
        self.assertAlmostEqual(c[0], note("C4"), places=6)
        self.assertAlmostEqual(c[1], note("E4"), places=6)
        self.assertAlmostEqual(c[2], note("G4"), places=6)


class TestWriteWav(unittest.TestCase):
    def _write(self, samples, **kw):
        path = os.path.join(self.tmp.name, "t.wav")
        write_wav(path, samples, **kw)
        with wave.open(path) as w:
            params = (w.getnchannels(), w.getsampwidth(), w.getframerate())
            raw = w.readframes(w.getnframes())
        return params, [v / 32768.0 for v in struct.unpack("<%dh" % (len(raw)//2), raw)]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_writes_mono_16_bit_44100(self):
        params, _ = self._write(sine(440.0, 0.05))
        self.assertEqual(params, (1, 2, SR))

    def test_normalizes_to_the_requested_peak(self):
        _, xs = self._write([0.05, -0.05] * 1000, fade=0)
        self.assertAlmostEqual(max(abs(x) for x in xs), 0.9, places=2)

    def test_never_clips(self):
        _, xs = self._write([5.0, -5.0] * 1000)
        self.assertTrue(all(abs(x) <= 1.0 for x in xs))

    def test_returns_the_duration_in_seconds(self):
        path = os.path.join(self.tmp.name, "d.wav")
        self.assertAlmostEqual(write_wav(path, sine(440.0, 0.25)), 0.25, places=3)


if __name__ == "__main__":
    unittest.main()
