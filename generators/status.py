"""Status feedback — success, error, warning, completion."""
import math
from synth import sine, square, triangle, noise_burst, mix, silence, perc, ad

CATEGORY = "status"
GROUP = "interface"
DESCRIPTION = "Success, error, warning and completion feedback."


def success_arp():
    """Success — bright ascending major arpeggio (C-E-G)."""
    s = silence(0.5)
    for i, f in enumerate((523.25, 659.25, 783.99)):
        mix(s, sine(f, 0.3, perc(8)), i * 0.06, 0.6)
        mix(s, sine(2 * f, 0.3, perc(14)), i * 0.06, 0.12)
    return s


def success_short():
    """Success (short) — quick rising two-tone confirm."""
    s = silence(0.28)
    mix(s, sine(880, 0.12, ad(0.003, 0.08)), 0.0, 0.6)
    mix(s, sine(1318.5, 0.16, ad(0.003, 0.1)), 0.07, 0.6)
    return s


def error_buzz():
    """Error — low descending buzz, dissonant."""
    s = silence(0.4)
    mix(s, square(220, 0.18, perc(10)), 0.0, 0.35)
    mix(s, square(207, 0.18, perc(10)), 0.0, 0.35)  # slight beat = harsh
    mix(s, square(165, 0.22, perc(9)), 0.16, 0.35)
    return s


def error_descend():
    """Error — clean descending minor two-tone."""
    s = silence(0.4)
    mix(s, triangle(659.25, 0.16, ad(0.004, 0.1)), 0.0, 0.6)
    mix(s, triangle(440.0, 0.22, ad(0.004, 0.13)), 0.13, 0.6)
    return s


def warning_pulse():
    """Warning — two urgent mid pulses."""
    s = silence(0.42)
    for off in (0.0, 0.2):
        mix(s, square(587.33, 0.13, ad(0.004, 0.08)), off, 0.4)
    return s


def complete_done():
    """Task complete — warm resolving three-note (G-B-D up an octave)."""
    s = silence(0.6)
    for i, f in enumerate((392.0, 493.88, 587.33)):
        mix(s, sine(f, 0.45, perc(6)), i * 0.07, 0.55)
    mix(s, sine(783.99, 0.5, perc(6)), 0.21, 0.5)   # final octave sparkle
    return s


def denied_thud():
    """Denied/invalid — flat low thud, no resolution."""
    s = sine(lambda t: 180 * math.exp(-4 * t), 0.22, perc(16))
    mix(s, noise_burst(0.02, perc(120), 0.2), 0.0, 0.15)
    return s


SOUNDS = [
    ("success",         "Ascending major arpeggio",          success_arp),
    ("success_short",   "Quick rising confirm",              success_short),
    ("error_buzz",      "Low dissonant error buzz",          error_buzz),
    ("error_descend",   "Clean descending error two-tone",   error_descend),
    ("warning_pulse",   "Two urgent warning pulses",         warning_pulse),
    ("complete",        "Warm resolving completion",         complete_done),
    ("denied",          "Flat low denial thud",              denied_thud),
]
