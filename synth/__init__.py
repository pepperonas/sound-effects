"""synth — dependency-free audio synthesis toolkit for UI sound effects."""
from .core import (
    SR, Noise,
    perc, ad, adsr, bell,
    osc, sine, square, saw, triangle, noise_burst, pluck, fm,
    mix, silence, ring_mod, lowpass, highpass, drive, reverse,
    note, chord, vibrato, fade_in, fade_out, normalize, write_wav,
)

__all__ = [
    "SR", "Noise",
    "perc", "ad", "adsr", "bell",
    "osc", "sine", "square", "saw", "triangle", "noise_burst", "pluck", "fm",
    "mix", "silence", "ring_mod", "lowpass", "highpass", "drive", "reverse",
    "note", "chord", "vibrato", "fade_in", "fade_out", "normalize", "write_wav",
]
