"""Production FX — risers, downlifters, impacts, sweeps and transitions.

The glue between sections of a track: build tension into a drop, slam an
impact on the downbeat, whoosh between scenes.
"""
import math
from synth import (sine, saw, noise_burst, mix, silence, perc, ad, bell,
                   lowpass, highpass, ring_mod, drive, reverse, Noise)

CATEGORY = "fx"
GROUP = "music"
DESCRIPTION = "Risers, downlifters, impacts, sweeps and transition effects."


def riser():
    """Uplifter — noise + tone sweeping up over ~1.5s to build tension."""
    dur = 1.5
    n = noise_burst(dur, lambda t: (t / dur) ** 2, 0.0, Noise(11))
    n = highpass(n, lambda t: 400 + 6000 * (t / dur))
    s = sine(lambda t: 200 + 1800 * (t / dur) ** 1.5, dur,
             lambda t: 0.3 + 0.7 * (t / dur))
    mix(n, s, 0.0, 0.5)
    return n


def downlifter():
    """Downlifter — pitch + filter falling away, a soft landing after a drop."""
    dur = 1.2
    s = saw(lambda t: 1600 * math.exp(-3 * t) + 120, dur, lambda t: math.exp(-1.6 * t))
    s = lowpass(s, lambda t: 5000 * math.exp(-2.5 * t) + 300)
    n = highpass(noise_burst(dur, lambda t: math.exp(-2.5 * t), 0.0, Noise(3)),
                 lambda t: 5000 * math.exp(-2.5 * t) + 300)
    mix(s, n, 0.0, 0.4)
    return s


def impact():
    """Impact — cinematic boom: sub drop + noise slam for the downbeat."""
    s = silence(1.0)
    mix(s, sine(lambda t: 110 * math.exp(-5 * t) + 35, 0.9, perc(3)), 0.0, 1.0)
    mix(s, noise_burst(0.5, perc(7), 0.35, Noise(909)), 0.0, 0.5)
    mix(s, highpass(noise_burst(0.06, perc(50), 0.0), 3000), 0.0, 0.4)
    return drive(s, 1.8)


def sub_drop():
    """Sub drop — sine sliding from 120 Hz down into the floor."""
    return sine(lambda t: 120 * math.exp(-4 * t) + 28, 1.0, perc(2.5))


def sweep_up():
    """White-noise sweep up — quick filtered whoosh into a hit."""
    dur = 0.7
    n = noise_burst(dur, bell(dur), 0.0, Noise(21))
    return highpass(n, lambda t: 300 + 7000 * (t / dur))


def sweep_down():
    """White-noise sweep down — whoosh out / transition away."""
    dur = 0.7
    n = noise_burst(dur, bell(dur), 0.0, Noise(22))
    return highpass(n, lambda t: 7000 - 6500 * (t / dur))


def reverse_cymbal():
    """Reverse cymbal — bright noise swell that sucks into the next bar."""
    dur = 1.3
    n = highpass(noise_burst(dur, perc(4), 0.0, Noise(97)), 4500)
    n = ring_mod(n, 5200, depth=0.2)
    return reverse(n)


def white_riser():
    """Pure noise riser — rising filtered hiss, no tonal content."""
    dur = 1.4
    n = noise_burst(dur, lambda t: (t / dur) ** 1.5, 0.0, Noise(44))
    return lowpass(highpass(n, lambda t: 200 + 8000 * (t / dur)), 16000)


def vinyl_crackle():
    """Vinyl crackle — low hiss with random pops, lo-fi texture bed."""
    dur = 1.5
    n = lowpass(noise_burst(dur, lambda t: 1.0, 0.0, Noise(7)), 4000)
    out = [v * 0.15 for v in n]
    pop = Noise(123)
    for i in range(len(out)):
        if abs(pop()) > 0.985:                              # sparse crackle
            out[i] += pop() * 0.8
    return out


def laser_zap():
    """Laser zap FX — fast descending ring-modulated sweep."""
    s = saw(lambda t: 2400 * math.exp(-12 * t) + 180, 0.3, perc(9))
    return ring_mod(s, 140, depth=0.4)


SOUNDS = [
    ("riser",          "Tension-building uplifter",      riser),
    ("downlifter",     "Falling post-drop downlifter",   downlifter),
    ("impact",         "Cinematic sub + noise impact",   impact),
    ("sub_drop",       "Sine sub drop into the floor",   sub_drop),
    ("sweep_up",       "Filtered noise sweep up",        sweep_up),
    ("sweep_down",     "Filtered noise sweep down",      sweep_down),
    ("reverse_cymbal", "Reverse cymbal swell",           reverse_cymbal),
    ("white_riser",    "Pure rising noise riser",        white_riser),
    ("vinyl_crackle",  "Lo-fi vinyl crackle bed",        vinyl_crackle),
    ("laser_zap",      "Descending ring-mod zap",        laser_zap),
]
