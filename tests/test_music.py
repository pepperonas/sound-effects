"""Unit tests for the shared motif machinery (generators/_music.py)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synth import SR, note, sine
from generators._music import STEP, motif, glide, filter_env, stack, additive


def probe(pitch, dur, v=1.0, **kw):
    """A voice that records how it was called and returns a flat ramp."""
    probe.calls.append((pitch, dur, v, kw))
    return [1.0] * int(dur * SR)


class TestMotif(unittest.TestCase):
    def setUp(self):
        probe.calls = []

    def test_events_land_on_their_step(self):
        out = motif(probe, [(0, "C3", 1, 1.0), (4, "C3", 1, 1.0)])
        self.assertEqual(len(probe.calls), 2)
        # the second note must start four steps in
        first_gap = next(i for i, v in enumerate(out) if v == 0.0)
        self.assertAlmostEqual(first_gap / SR, STEP, places=3)

    def test_length_is_measured_in_steps(self):
        motif(probe, [(0, "C3", 3, 1.0)])
        self.assertAlmostEqual(probe.calls[0][1], 3 * STEP, places=6)

    def test_a_chord_calls_the_voice_once_per_note(self):
        motif(probe, [(0, ("C3", "E3", "G3"), 1, 1.0)])
        self.assertEqual([c[0] for c in probe.calls], ["C3", "E3", "G3"])

    def test_negative_spread_strums_from_the_top(self):
        motif(probe, [(0, ("C3", "E3", "G3"), 1, 1.0)], spread=-0.01)
        self.assertEqual([c[0] for c in probe.calls], ["G3", "E3", "C3"])

    def test_spread_staggers_the_notes_in_time(self):
        out = motif(probe, [(0, ("C3", "E3"), 1, 1.0)], spread=0.05)
        self.assertGreater(len(out), int((STEP + 0.05) * SR))

    def test_per_note_overrides_reach_the_voice(self):
        motif(probe, [(0, "C3", 1, 1.0, {"mute": 0.5})], damp=0.3)
        self.assertEqual(probe.calls[0][3], {"damp": 0.3, "mute": 0.5})

    def test_an_override_beats_the_motif_wide_setting(self):
        motif(probe, [(0, "C3", 1, 1.0, {"damp": 0.9})], damp=0.3)
        self.assertEqual(probe.calls[0][3]["damp"], 0.9)

    def test_velocity_scales_the_mixed_gain(self):
        loud = motif(probe, [(0, "C3", 1, 1.0)])
        soft = motif(probe, [(0, "C3", 1, 0.0)])
        self.assertGreater(max(loud), max(soft))

    def test_a_chord_is_bigger_than_one_note_but_not_n_times_bigger(self):
        one = max(motif(probe, [(0, "C3", 1, 1.0)]))
        three = max(motif(probe, [(0, ("C3", "E3", "G3"), 1, 1.0)]))
        self.assertGreater(three, one)
        self.assertLess(three, 3 * one)

    def test_starts_on_the_first_attack_with_no_leading_silence(self):
        out = motif(probe, [(0, "C3", 1, 1.0)])
        self.assertNotEqual(out[0], 0.0)

    def test_ends_with_a_short_silent_tail(self):
        out = motif(probe, [(0, "C3", 1, 1.0)], tail=0.025)
        self.assertEqual(out[-1], 0.0)
        self.assertEqual(len(out), int(STEP * SR) + int(0.025 * SR))


class TestGlide(unittest.TestCase):
    def test_holds_then_travels_then_holds(self):
        g = glide("C3", "D3", hold=0.1, rise=0.1)
        self.assertAlmostEqual(g(0.0), note("C3"))
        self.assertAlmostEqual(g(0.05), note("C3"))
        self.assertAlmostEqual(g(0.3), note("D3"))

    def test_the_midpoint_is_halfway(self):
        g = glide("C3", "C4", hold=0.0, rise=0.2)
        self.assertAlmostEqual(g(0.1), (note("C3") + note("C4")) / 2, places=3)

    def test_is_smooth_not_linear_at_the_edges(self):
        g = glide(100.0, 200.0, hold=0.0, rise=1.0)
        # smoothstep leaves and arrives slowly: a tenth in is well under a tenth up
        self.assertLess(g(0.1) - 100.0, 10.0)
        self.assertGreater(g(0.9) - 100.0, 90.0)

    def test_is_monotonic(self):
        g = glide(100.0, 200.0, hold=0.05, rise=0.2)
        vals = [g(t / 200.0) for t in range(80)]
        self.assertEqual(vals, sorted(vals))

    def test_accepts_raw_frequencies_too(self):
        self.assertAlmostEqual(glide(110.0, 220.0, 0.0, 0.1)(0.2), 220.0)


class TestFilterEnv(unittest.TestCase):
    def test_starts_closed_and_snaps_open(self):
        cut = filter_env(200.0, 3000.0)
        self.assertAlmostEqual(cut(0.0), 200.0, delta=1.0)
        self.assertGreater(cut(0.022), 3.0 * cut(0.0))

    def test_settles_below_its_peak_but_above_the_floor(self):
        cut = filter_env(200.0, 3000.0)
        peak = max(cut(t / 1000.0) for t in range(400))
        late = cut(0.4)
        self.assertLess(late, peak)
        self.assertGreater(late, 200.0)

    def test_span_is_honoured_because_the_bump_is_normalised(self):
        peak = max(filter_env(0.0, 1000.0)(t / 2000.0) for t in range(600))
        self.assertAlmostEqual(peak, 1000.0, delta=60.0)

    def test_never_exceeds_nyquist(self):
        cut = filter_env(1000.0, 500000.0)
        self.assertLessEqual(max(cut(t / 1000.0) for t in range(300)), 17000.0)


class TestStack(unittest.TestCase):
    """The detune spread must not grow with the ensemble: six voices at
    multiples of the step put the outer pair 31 cents out, which reads as out
    of tune rather than as a section."""

    def _spread_cents(self, voices, detune=0.006):
        rings = max(1, (voices - 1 + 1) // 2)
        offs = [0.0] + [detune * (((k + 1) // 2) / rings) * (1 if k % 2 else -1)
                        for k in range(1, voices)]
        return max(abs(1200 * math.log2(1 + o)) for o in offs)

    def test_spread_stays_bounded_as_voices_are_added(self):
        for v in (2, 3, 4, 6, 8, 12):
            with self.subTest(voices=v):
                self.assertLess(self._spread_cents(v), 11.0)

    def test_more_voices_do_not_widen_the_ensemble(self):
        self.assertAlmostEqual(self._spread_cents(3), self._spread_cents(9), delta=0.5)

    def test_produces_one_buffer_of_the_right_length(self):
        out = stack("saw", 220.0, 0.05, None, voices=4)
        self.assertEqual(len(out), int(0.05 * SR))

    def test_a_single_voice_is_just_the_oscillator(self):
        from synth import osc
        self.assertEqual(stack("saw", 220.0, 0.02, None, voices=1),
                         osc("saw", 220.0, 0.02, None))


class TestAdditive(unittest.TestCase):
    def _mag(self, xs, f):
        w = 2 * math.pi * f / SR
        c = 2 * math.cos(w)
        s1 = s2 = 0.0
        for x in xs:
            s0 = x + c * s1 - s2
            s2, s1 = s1, s0
        return math.sqrt(abs(s1 * s1 + s2 * s2 - c * s1 * s2)) / len(xs)

    def test_partials_appear_at_their_multipliers(self):
        xs = additive(200.0, 0.4, [(1.0, 1.0, 0.0), (3.0, 0.5, 0.0)])
        self.assertGreater(self._mag(xs, 600.0), 0.1)
        self.assertLess(self._mag(xs, 400.0), 0.02)      # nothing at the 2nd

    def test_inharmonic_multipliers_are_honoured(self):
        xs = additive(200.0, 0.4, [(1.0, 1.0, 0.0), (3.93, 1.0, 0.0)])
        self.assertGreater(self._mag(xs, 786.0), 0.1)

    def test_a_higher_decay_rate_dies_sooner(self):
        slow = additive(200.0, 0.5, [(1.0, 1.0, 1.0)])
        fast = additive(200.0, 0.5, [(1.0, 1.0, 20.0)])
        self.assertLess(abs(fast[-100]), abs(slow[-100]))

    def test_attack_ramp_removes_the_click(self):
        xs = additive(200.0, 0.2, [(1.0, 1.0, 0.0)], attack=0.01)
        self.assertLess(abs(xs[0]), 1e-3)

    def test_vibrato_spreads_energy_symmetrically_about_the_pitch(self):
        # exactly three LFO cycles, so the window is not biased by a part cycle
        xs = additive(440.0, 0.6, [(1.0, 1.0, 0.0)], vib=(5.0, 0.01))
        lo = self._mag(xs, 440 * 2 ** (-0.09 / 12))
        hi = self._mag(xs, 440 * 2 ** (0.09 / 12))
        self.assertLess(abs(lo - hi) / max(lo, hi), 0.12)

    def test_no_vibrato_is_bit_identical_to_omitting_it(self):
        self.assertEqual(additive(300.0, 0.1, [(1.0, 1.0, 2.0)]),
                         additive(300.0, 0.1, [(1.0, 1.0, 2.0)], vib=None))

    def test_zero_duration_is_empty(self):
        self.assertEqual(additive(200.0, 0.0, [(1.0, 1.0, 0.0)]), [])


if __name__ == "__main__":
    unittest.main()
