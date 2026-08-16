"""Media controls — play, pause, stop, skip, volume, record, screenshot."""
import math
from synth import sine, triangle, noise_burst, mix, silence, perc, ad, Noise
from synth.core import lowpass, highpass

CATEGORY = "media"
GROUP = "interface"
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


def screenshot_dslr():
    """Screenshot — rich DSLR shutter: mirror slap, double curtain, metal ring."""
    s = silence(0.30)
    n = Noise(4242)
    # Mirror slap: low bodied thump with a hard attack
    mix(s, lowpass(noise_burst(0.03, perc(90), 0.2, n), 900), 0.0, 0.9)
    mix(s, sine(180, 0.035, perc(120)), 0.0, 0.5)
    # First curtain: bright snick
    mix(s, highpass(noise_burst(0.014, perc(220), 0.05, n), 1800), 0.012, 0.8)
    # Second curtain, slightly later and duller (the classic double)
    mix(s, highpass(noise_burst(0.016, perc(180), 0.1, n), 1200), 0.075, 0.7)
    # Tiny metallic after-ring of the mechanism
    mix(s, sine(3100, 0.05, perc(140)), 0.075, 0.10)
    mix(s, sine(2200, 0.06, perc(110)), 0.078, 0.08)
    # Winder settle: faint low tick at the end
    mix(s, lowpass(noise_burst(0.02, perc(150), 0.3, n), 700), 0.15, 0.25)
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
    ("screenshot_dslr", "Rich DSLR shutter (mirror slap + double curtain)", screenshot_dslr),
]
