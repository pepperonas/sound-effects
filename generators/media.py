"""Media controls — play, pause, stop, skip, volume, record, screenshot."""
import math
from synth import sine, triangle, noise_burst, mix, silence, perc, ad, Noise

CATEGORY = "media"
DESCRIPTION = "Play, pause, stop, skip, volume, record and capture controls."


def play():
    """Play — short bright upward 'go'."""
    s = sine(lambda t: 520 + 380 * (1 - math.exp(-50 * t)), 0.16, ad(0.004, 0.1))
    mix(s, sine(lambda t: 2 * (520 + 380 * (1 - math.exp(-50 * t))), 0.16, perc(20)), 0.0, 0.18)
    return s


def pause():
    """Pause — two soft equal taps (the two pause bars)."""
    s = silence(0.2)
    for off in (0.0, 0.08):
        mix(s, sine(560, 0.06, ad(0.003, 0.04)), off, 0.55)
    return s


def stop():
    """Stop — flat damped block, no resolution."""
    s = sine(lambda t: 300 * math.exp(-5 * t) + 160, 0.16, perc(20))
    mix(s, noise_burst(0.012, perc(160), 0.25), 0.0, 0.15)
    return s


def next_track():
    """Skip forward — quick rising double-blip."""
    s = silence(0.2)
    mix(s, sine(700, 0.05, perc(40)), 0.0, 0.5)
    mix(s, sine(1050, 0.06, perc(35)), 0.05, 0.5)
    return s


def prev_track():
    """Skip back — quick falling double-blip."""
    s = silence(0.2)
    mix(s, sine(1050, 0.05, perc(40)), 0.0, 0.5)
    mix(s, sine(700, 0.06, perc(35)), 0.05, 0.5)
    return s


def volume_up():
    """Volume up — short rising glide tick."""
    return sine(lambda t: 600 + 500 * t / 0.12, 0.12, ad(0.003, 0.08))


def volume_down():
    """Volume down — short falling glide tick."""
    return sine(lambda t: 1100 - 500 * t / 0.12, 0.12, ad(0.003, 0.08))


def mute():
    """Mute — soft downward thunk."""
    return sine(lambda t: 520 * math.exp(-6 * t) + 130, 0.18, perc(16))


def record():
    """Record start — firm low confirming tone."""
    s = sine(330, 0.22, ad(0.006, 0.16))
    mix(s, sine(660, 0.22, perc(10)), 0.0, 0.2)
    return s


def screenshot():
    """Screenshot — classic camera shutter snap."""
    s = silence(0.22)
    n = Noise(4242)
    mix(s, noise_burst(0.018, perc(130), 0.1, n), 0.0, 0.6)       # first curtain
    mix(s, noise_burst(0.02, perc(110), 0.1, n), 0.05, 0.55)      # second curtain
    mix(s, sine(1400, 0.01, perc(300)), 0.0, 0.2)
    return s


SOUNDS = [
    ("play",         "Bright upward play",            play),
    ("pause",        "Two soft pause taps",           pause),
    ("stop",         "Flat damped stop block",        stop),
    ("next_track",   "Rising skip-forward blip",      next_track),
    ("prev_track",   "Falling skip-back blip",        prev_track),
    ("volume_up",    "Rising volume tick",            volume_up),
    ("volume_down",  "Falling volume tick",           volume_down),
    ("mute",         "Soft downward mute thunk",      mute),
    ("record",       "Firm record-start tone",        record),
    ("screenshot",   "Camera shutter snap",           screenshot),
]
