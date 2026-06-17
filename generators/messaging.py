"""Messaging — send, receive, sent-confirm, typing, call tones."""
import math
from synth import sine, triangle, mix, silence, perc, ad

CATEGORY = "messaging"
GROUP = "interface"
DESCRIPTION = "Send, receive, delivered, typing and call tones."


def send():
    """Send message — quick upward 'swoosh out'."""
    f = lambda t: 500 + 900 * t / 0.2
    s = sine(f, 0.2, ad(0.004, 0.1))
    mix(s, sine(lambda t: 2 * f(t), 0.2, ad(0.004, 0.09)), 0.0, 0.2)
    return s


def receive():
    """Receive message — gentle downward-then-settle pop."""
    s = silence(0.3)
    mix(s, sine(1046.5, 0.14, perc(11)), 0.0, 0.55)
    mix(s, sine(880.0, 0.18, perc(9)), 0.06, 0.55)
    return s


def delivered():
    """Delivered/sent confirm — tiny high double-pip."""
    s = silence(0.18)
    for off in (0.0, 0.06):
        mix(s, sine(2093.0, 0.05, perc(60)), off, 0.5)
    return s


def typing_indicator():
    """Typing — soft low triple-blip."""
    s = silence(0.4)
    for i in range(3):
        mix(s, sine(330, 0.05, perc(30)), i * 0.12, 0.45)
    return s


def call_ring():
    """Incoming call — warm two-tone ring burst."""
    s = silence(0.6)
    for off in (0.0, 0.3):
        mix(s, sine(440, 0.2, ad(0.01, 0.14)), off, 0.45)
        mix(s, sine(480, 0.2, ad(0.01, 0.14)), off, 0.45)
    return s


def call_end():
    """Call ended — short descending two-tone."""
    s = silence(0.32)
    mix(s, sine(660, 0.12, ad(0.005, 0.08)), 0.0, 0.5)
    mix(s, sine(440, 0.16, ad(0.005, 0.1)), 0.1, 0.5)
    return s


SOUNDS = [
    ("send",       "Upward swoosh-out",             send),
    ("receive",    "Gentle settle pop",             receive),
    ("delivered",  "High delivered double-pip",     delivered),
    ("typing",     "Soft triple typing blip",       typing_indicator),
    ("call_ring",  "Warm two-tone ring burst",      call_ring),
    ("call_end",   "Descending call-end two-tone",  call_end),
]
