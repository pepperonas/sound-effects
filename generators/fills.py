"""Fills — drum figures that lead into the next bar.

The `drums` category is a kit: one hit per file, for building a beat. This is
the other half — the four beats before the drop, where the drummer stops
keeping time and starts announcing something. Every one of these is a *figure*
you drop on top of a running mix, so they are all under a bar and all end
pointing forwards.

Two things make a fill sound played rather than sequenced. Hits are never at
one velocity — a fill is loud on the accents and almost inaudible on the ghost
notes in between — and a drum struck twice in quick succession does not sound
the same both times, so the noise seed moves with the hit.
"""
import math
from synth import (sine, triangle, noise_burst, mix, silence, perc, reverse,
                   ring_mod, lowpass, highpass, drive, normalize, Noise)

CATEGORY = "fills"
GROUP = "dj"
DESCRIPTION = "Drum fills and rolls: toms, snares, hats, claps, into the drop."

STEP = 60.0 / 128.0 / 4.0          # a 1/16 at 128 BPM


def _tom(f, seed=1, dur=0.30, snap=0.30):
    s = sine(lambda t: f * (1 + 1.1 * math.exp(-26.0 * t)), dur, perc(9.0))
    mix(s, triangle(f * 1.6, 0.05, perc(40.0)), 0.0, 0.22)
    mix(s, lowpass(noise_burst(0.02, perc(90.0), 0.0, Noise(seed)), 3000), 0.0, snap)
    return drive(s, 1.4)


def _snare(seed=7, dur=0.24, body=1.0, tone=180.0):
    s = silence(dur)
    mix(s, sine(tone, 0.13, perc(22.0)), 0.0, 0.45 * body)
    mix(s, triangle(tone * 1.85, 0.10, perc(28.0)), 0.0, 0.26 * body)
    mix(s, highpass(noise_burst(dur * 0.85, perc(19.0), 0.0, Noise(seed)), 1400),
        0.0, 0.85)
    return s


def _hat(seed=53, dur=0.05, dec=120.0):
    n = highpass(noise_burst(dur, perc(dec), 0.0, Noise(seed)), 7000)
    return ring_mod(n, 8200.0, depth=0.25)


def _clap(seed=31, spread=0.011):
    s = silence(0.30)
    n = Noise(seed)
    for k, off in enumerate((0.0, spread, spread * 2, spread * 3)):
        mix(s, highpass(noise_burst(0.05, perc(45.0), 0.0, n), 1100), off, 0.5)
    mix(s, highpass(noise_burst(0.19, perc(12.0), 0.0, n), 1100), spread * 3.2, 0.42)
    return s


def _kick(dur=0.34):
    s = sine(lambda t: 48.0 + 118.0 * math.exp(-32.0 * t), dur, perc(8.0))
    mix(s, noise_burst(0.004, perc(280.0), 0.0, Noise(3)), 0.0, 0.32)
    return drive(s, 1.6)


def _crash(dur=0.85):
    n = highpass(noise_burst(dur, perc(4.6), 0.0, Noise(909)), 4200)
    return ring_mod(n, 5300.0, depth=0.18)


def _play(events, tail=0.05):
    """events: (start_in_16ths, buffer, gain)."""
    out = []
    for at, buf, g in events:
        mix(out, buf, at * STEP, g)
    out.extend([0.0] * int(tail * 44100))
    lead = next((i for i, x in enumerate(out) if abs(x) > 0.002), 0)
    return normalize(out[lead:] if lead else out, 0.88)


# --------------------------------------------------------------------------- #
# Tom fills.
# --------------------------------------------------------------------------- #
def fill_toms_down():
    """Four toms descending — the fill everybody hums when they say "drum fill"."""
    return _play([(i * 2, _tom(f, seed=11 + i), 0.85 + 0.05 * i)
                  for i, f in enumerate((210.0, 168.0, 130.0, 98.0))])


def fill_toms_up():
    """Four toms climbing instead, so the fill lifts into the bar."""
    return _play([(i * 2, _tom(f, seed=17 + i), 0.8 + 0.06 * i)
                  for i, f in enumerate((98.0, 130.0, 168.0, 210.0))])


def fill_toms_fast():
    """Six toms in sixteenths — the same descent, twice the hurry."""
    return _play([(i, _tom(f, seed=23 + i, dur=0.22), 0.78 + 0.04 * i)
                  for i, f in enumerate((230.0, 195.0, 168.0, 145.0, 122.0, 98.0))])


def fill_tom_snare():
    """Snare, tom, snare, tom — the alternation that fills a half bar."""
    return _play([(0, _snare(seed=41), 1.0), (2, _tom(150.0, 29), 0.9),
                  (4, _snare(seed=43), 0.95), (6, _tom(105.0, 31), 1.0)])


def fill_floor_tom():
    """Two floor toms and a kick — heavy, low, unhurried."""
    return _play([(0, _tom(88.0, 37, dur=0.42), 1.0), (3, _tom(88.0, 39, dur=0.42), 0.9),
                  (6, _kick(0.40), 1.0)])


# --------------------------------------------------------------------------- #
# Snare work.
# --------------------------------------------------------------------------- #
def fill_snare_roll():
    """Snare roll — eight even sixteenths growing into the bar line."""
    return _play([(i, _snare(seed=61 + i, dur=0.16), 0.45 + 0.07 * i)
                  for i in range(8)])


def fill_snare_accel():
    """Accelerating roll — the hits crowd together as the bar runs out."""
    ev, t, gap = [], 0.0, 1.5
    while t < 8.0:
        ev.append((t, _snare(seed=71 + int(t * 4), dur=0.14), 0.5 + 0.055 * t))
        t += gap
        gap = max(0.42, gap * 0.86)          # a floor, or the series converges
    return _play(ev)


def fill_snare_flam():
    """Flam — two sticks a hair apart, so the hit is thick rather than doubled."""
    return _play([(0, _snare(seed=81, dur=0.20), 0.45),
                  (0.16, _snare(seed=83), 1.0)])


def fill_snare_drag():
    """Drag — two ghost notes crushed onto the front of the accent."""
    return _play([(0, _snare(seed=91, dur=0.12, body=0.5), 0.30),
                  (0.30, _snare(seed=93, dur=0.12, body=0.5), 0.32),
                  (0.75, _snare(seed=95), 1.0)])


def fill_snare_ghost():
    """Accents with ghost notes between them — the fill a drummer plays quietly."""
    g = [0.28, 1.0, 0.24, 0.30, 0.9, 0.26, 0.32, 1.0]
    return _play([(i, _snare(seed=101 + i, dur=0.18 if v > 0.5 else 0.11,
                             body=1.0 if v > 0.5 else 0.4), v)
                  for i, v in enumerate(g)])


def fill_snare_triplet():
    """Triplets — three hits per beat, so the fill fights the grid."""
    return _play([(i * 4 / 3.0, _snare(seed=111 + i, dur=0.16), 0.7 + 0.05 * (i % 3))
                  for i in range(6)])


# --------------------------------------------------------------------------- #
# Hats, claps and combinations.
# --------------------------------------------------------------------------- #
def fill_hat_roll():
    """Hat roll — sixteen closed hats, opening out at the end."""
    return _play([(i * 0.5, _hat(seed=53 + i, dur=0.05 + 0.004 * i,
                                 dec=120.0 - 5.0 * i), 0.55 + 0.03 * i)
                  for i in range(16)])


def fill_hat_open():
    """Three closed hats into one open — the oldest lead-in in dance music."""
    return _play([(0, _hat(53), 0.8), (2, _hat(55), 0.8), (4, _hat(57), 0.85),
                  (6, _hat(59, dur=0.34, dec=11.0), 1.0)])


def fill_clap_build():
    """Claps doubling in speed across the bar."""
    ev, t, gap = [], 0.0, 1.7
    while t < 6.4:
        ev.append((t, _clap(seed=131 + int(t * 3)), 0.6 + 0.05 * t))
        t += gap
        gap = max(0.5, gap * 0.72)
    return _play(ev)


def fill_kick_snare():
    """Kick and snare trading sixteenths — busy, front-heavy."""
    ev = []
    for i, which in enumerate((0, 1, 0, 1, 1, 0, 1, 1)):
        ev.append((i, _kick(0.26) if which == 0 else _snare(seed=151 + i, dur=0.18),
                   0.8 + 0.02 * i))
    return _play(ev)


def fill_kick_roll():
    """Double-kick roll — eight kicks, the metal and DnB lead-in."""
    return _play([(i, _kick(0.22), 0.75 + 0.03 * i) for i in range(8)])


def fill_half_bar():
    """Half-bar fill — ghost snares under two toms and a crash."""
    return _play([(0, _snare(seed=161, dur=0.12, body=0.45), 0.3),
                  (1, _tom(180.0, 163), 0.85),
                  (2, _snare(seed=165, dur=0.12, body=0.45), 0.32),
                  (3, _tom(120.0, 167), 0.9),
                  (4, _crash(0.58), 1.0), (4, _kick(0.32), 0.95)])


def fill_one_beat():
    """One-beat fill — four sixteenths, for a gap you barely have."""
    return _play([(0, _snare(seed=171, dur=0.14), 0.8),
                  (1, _snare(seed=173, dur=0.14), 0.7),
                  (2, _tom(150.0, 175, dur=0.22), 0.9),
                  (3, _tom(110.0, 177, dur=0.22), 1.0)])


def fill_crash_out():
    """The landing — crash and kick together, everything else stopped."""
    return _play([(0, _crash(0.95), 1.0), (0, _kick(0.40), 1.0)])


def fill_reverse():
    """Reverse fill — a swell sucking backwards into the downbeat."""
    ev = reverse(_play([(i, _snare(seed=181 + i, dur=0.16), 0.5 + 0.06 * i)
                        for i in range(8)]))
    lead = next((i for i, x in enumerate(ev) if abs(x) > 0.002), 0)
    return normalize(ev[lead:] if lead else ev, 0.88)


SOUNDS = [
    ("fill_toms_down",    "Four toms descending",         fill_toms_down),
    ("fill_toms_up",      "Four toms climbing",           fill_toms_up),
    ("fill_toms_fast",    "Six toms in sixteenths",       fill_toms_fast),
    ("fill_tom_snare",    "Snare and tom alternating",    fill_tom_snare),
    ("fill_floor_tom",    "Heavy floor toms and kick",    fill_floor_tom),
    ("fill_snare_roll",   "Even eight-hit snare roll",    fill_snare_roll),
    ("fill_snare_accel",  "Accelerating snare roll",      fill_snare_accel),
    ("fill_snare_flam",   "Two-stick flam",               fill_snare_flam),
    ("fill_snare_drag",   "Ghost-note drag into accent",  fill_snare_drag),
    ("fill_snare_ghost",  "Accents with ghost notes",     fill_snare_ghost),
    ("fill_snare_triplet", "Six triplet snares",          fill_snare_triplet),
    ("fill_hat_roll",     "Sixteen hats opening out",     fill_hat_roll),
    ("fill_hat_open",     "Three closed into one open",   fill_hat_open),
    ("fill_clap_build",   "Claps doubling in speed",      fill_clap_build),
    ("fill_reverse",      "Backwards swell into the beat", fill_reverse),
    ("fill_kick_snare",   "Kick and snare trading",       fill_kick_snare),
    ("fill_kick_roll",    "Eight-kick double roll",       fill_kick_roll),
    ("fill_half_bar",     "Half-bar fill into a crash",   fill_half_bar),
    ("fill_one_beat",     "Four-hit one-beat fill",       fill_one_beat),
    ("fill_crash_out",    "Crash and kick landing",       fill_crash_out),
]
