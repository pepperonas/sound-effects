"""Clicks, taps and toggles — the most frequent interaction sounds."""
import math
from synth import sine, square, noise_burst, mix, silence, perc, ad, Noise

CATEGORY = "clicks"
GROUP = "interface"
DESCRIPTION = "Buttons, taps, toggles and switches."


def click_soft():
    """Soft rounded button click."""
    s = sine(1100, 0.04, perc(120))
    mix(s, sine(1650, 0.04, perc(160)), 0.0, 0.3)
    return s


def click_crisp():
    """Crisp modern UI click — bright and short."""
    s = sine(1900, 0.03, perc(150))
    mix(s, sine(2850, 0.03, perc(190)), 0.0, 0.4)
    mix(s, noise_burst(0.006, perc(400), 0.2), 0.0, 0.15)
    return s


def tap_minimal():
    """Minimal flat tap — neutral, almost a tick."""
    return sine(900, 0.025, perc(180))


def toggle_on():
    """Toggle on — short upward two-tone."""
    s = silence(0.16)
    mix(s, sine(700, 0.05, ad(0.002, 0.04)), 0.0, 0.6)
    mix(s, sine(1050, 0.06, ad(0.002, 0.05)), 0.045, 0.6)
    return s


def toggle_off():
    """Toggle off — short downward two-tone."""
    s = silence(0.16)
    mix(s, sine(1050, 0.05, ad(0.002, 0.04)), 0.0, 0.6)
    mix(s, sine(700, 0.06, ad(0.002, 0.05)), 0.045, 0.6)
    return s


def switch_mech():
    """Physical toggle switch — clicky snap with a tail."""
    s = silence(0.18)
    n = Noise()
    mix(s, noise_burst(0.008, perc(300), 0.1, n), 0.0, 0.5)
    mix(s, sine(lambda t: 520 * math.exp(-25 * t), 0.08, perc(40)), 0.01, 0.7)
    return s


def radio_select():
    """Radio/checkbox select — single clean pip."""
    return sine(lambda t: 1300 + 200 * (1 - math.exp(-80 * t)), 0.06, ad(0.002, 0.045))


SOUNDS = [
    ("click_soft",    "Soft rounded button click",        click_soft),
    ("click_crisp",   "Crisp bright modern click",        click_crisp),
    ("tap_minimal",   "Minimal flat tap/tick",            tap_minimal),
    ("toggle_on",     "Upward two-tone toggle on",        toggle_on),
    ("toggle_off",    "Downward two-tone toggle off",     toggle_off),
    ("switch_mech",   "Physical clicky switch snap",      switch_mech),
    ("radio_select",  "Clean radio/checkbox pip",         radio_select),
]
