"""System events — startup, shutdown, connect, login, unlock, battery."""
import math
from synth import sine, triangle, noise_burst, mix, silence, perc, ad, bell, Noise

CATEGORY = "system"
GROUP = "interface"
DESCRIPTION = "Startup, shutdown, connect/disconnect, login and power events."


def startup():
    """Power-on — rising swell into a bright resolving chord."""
    s = silence(0.9)
    mix(s, sine(lambda t: 110 + 220 * t / 0.4, 0.4, ad(0.1, 0.3)), 0.0, 0.35)
    for i, f in enumerate((261.63, 329.63, 392.0, 523.25)):  # C major
        mix(s, sine(f, 0.55, perc(4)), 0.3 + i * 0.04, 0.32)
    return s


def shutdown():
    """Power-off — descending sweep that fades out."""
    s = silence(0.85)
    mix(s, sine(lambda t: 523.25 - 380 * t / 0.6, 0.6, ad(0.02, 0.45)), 0.0, 0.45)
    mix(s, sine(lambda t: 261.63 - 150 * t / 0.6, 0.6, ad(0.02, 0.45)), 0.0, 0.25)
    mix(s, sine(lambda t: 110 * math.exp(-2 * t), 0.25, perc(8)), 0.55, 0.3)
    return s


def connect():
    """Device/network connect — rising two-note 'plugged in'."""
    s = silence(0.4)
    mix(s, sine(659.25, 0.18, ad(0.004, 0.12)), 0.0, 0.6)
    mix(s, sine(987.77, 0.22, ad(0.004, 0.14)), 0.11, 0.6)
    return s


def disconnect():
    """Device/network disconnect — falling two-note 'unplugged'."""
    s = silence(0.4)
    mix(s, sine(987.77, 0.18, ad(0.004, 0.12)), 0.0, 0.6)
    mix(s, sine(659.25, 0.22, ad(0.004, 0.14)), 0.11, 0.6)
    return s


def login():
    """Login/unlock — warm welcoming upward arpeggio."""
    s = silence(0.6)
    for i, f in enumerate((440.0, 554.37, 659.25, 880.0)):  # A major
        mix(s, sine(f, 0.35, perc(6)), i * 0.05, 0.5)
    return s


def logout():
    """Logout/lock — short descending settle."""
    s = silence(0.4)
    for i, f in enumerate((880.0, 659.25, 440.0)):
        mix(s, sine(f, 0.2, perc(9)), i * 0.05, 0.5)
    return s


def battery_low():
    """Battery low — two soft warning dips."""
    s = silence(0.5)
    for off in (0.0, 0.22):
        mix(s, triangle(lambda t: 500 - 180 * t / 0.14, 0.14, ad(0.006, 0.09)), off, 0.6)
    return s


def usb_plug():
    """USB plug-in — short bright detected blip."""
    s = sine(lambda t: 700 + 500 * (1 - math.exp(-60 * t)), 0.12, perc(20))
    n = Noise()
    mix(s, noise_burst(0.01, perc(300), 0.2, n), 0.0, 0.1)
    return s


SOUNDS = [
    ("startup",      "Rising swell into a major chord",   startup),
    ("shutdown",     "Descending fade-out sweep",         shutdown),
    ("connect",      "Rising 'plugged in' two-note",      connect),
    ("disconnect",   "Falling 'unplugged' two-note",      disconnect),
    ("login",        "Warm welcoming arpeggio",           login),
    ("logout",       "Short descending settle",           logout),
    ("battery_low",  "Two soft warning dips",             battery_low),
    ("usb_plug",     "Bright USB-detected blip",          usb_plug),
]
