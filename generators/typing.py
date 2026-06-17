"""Keyboard — keystrokes, backspace, space, enter, error key."""
import math
from synth import sine, noise_burst, mix, silence, perc, ad, Noise

CATEGORY = "typing"
GROUP = "interface"
DESCRIPTION = "Keystrokes, backspace, space, enter and key feedback."

# Each keystroke uses an independent noise seed so a typed sequence varies.
_seedctr = 7000


def _key(freq, body_decay=55, seed=None):
    global _seedctr
    if seed is None:
        _seedctr += 137
        seed = _seedctr
    n = Noise(seed)
    s = silence(0.12)
    mix(s, noise_burst(0.006, perc(380), 0.15, n), 0.0, 0.4)        # contact click
    mix(s, sine(freq, 0.05, perc(body_decay)), 0.002, 0.6)          # key body
    return s


def key_1():
    return _key(420, seed=7011)


def key_2():
    return _key(380, seed=7029)


def key_3():
    return _key(460, seed=7043)


def space_bar():
    """Spacebar — deeper, softer thock."""
    n = Noise(7100)
    s = silence(0.14)
    mix(s, noise_burst(0.008, perc(300), 0.25, n), 0.0, 0.35)
    mix(s, sine(lambda t: 240 * math.exp(-18 * t), 0.08, perc(35)), 0.002, 0.7)
    return s


def backspace():
    """Backspace — short downward delete tick."""
    s = silence(0.1)
    mix(s, sine(lambda t: 700 * math.exp(-8 * t) + 200, 0.07, perc(40)), 0.0, 0.6)
    mix(s, noise_burst(0.005, perc(360), 0.1, Noise(7200)), 0.0, 0.2)
    return s


def enter_key():
    """Enter/return — confirming click with a tiny upward lift."""
    s = silence(0.16)
    mix(s, noise_burst(0.006, perc(360), 0.15, Noise(7300)), 0.0, 0.3)
    mix(s, sine(lambda t: 380 + 220 * (1 - math.exp(-50 * t)), 0.1, perc(28)), 0.002, 0.65)
    return s


def key_error():
    """Invalid key — short flat low buzz."""
    s = silence(0.12)
    mix(s, sine(160, 0.09, perc(22)), 0.0, 0.5)
    mix(s, sine(151, 0.09, perc(22)), 0.0, 0.4)
    return s


SOUNDS = [
    ("key_1",      "Keystroke variation 1",          key_1),
    ("key_2",      "Keystroke variation 2",          key_2),
    ("key_3",      "Keystroke variation 3",          key_3),
    ("space",      "Deeper softer spacebar thock",   space_bar),
    ("backspace",  "Downward delete tick",           backspace),
    ("enter",      "Confirming return click",        enter_key),
    ("key_error",  "Invalid-key low buzz",           key_error),
]
