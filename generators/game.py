"""Game & gamified UI — coin, powerup, jump, level-up, achievement, game over."""
import math
from synth import square, sine, triangle, noise_burst, mix, silence, perc, ad, Noise

CATEGORY = "game"
GROUP = "interface"
DESCRIPTION = "Retro-flavored coin, powerup, jump, level-up and game-over cues."


def coin():
    """Coin pickup — classic two-step square blip."""
    s = silence(0.3)
    mix(s, square(987.77, 0.07, perc(12)), 0.0, 0.5)     # B5
    mix(s, square(1318.5, 0.22, perc(7)), 0.06, 0.5)     # E6
    return s


def powerup():
    """Power-up — rising stepped arpeggio sweep."""
    s = silence(0.4)
    steps = [392, 523, 659, 784, 1047]
    for i, f in enumerate(steps):
        mix(s, square(f, 0.07, perc(16)), i * 0.05, 0.4)
    return s


def jump():
    """Jump — quick upward square swoop."""
    return square(lambda t: 300 + 700 * t / 0.18, 0.18, perc(9))


def hurt():
    """Hurt/damage — short downward dissonant blip."""
    s = square(lambda t: 440 - 240 * t / 0.16, 0.16, perc(14))
    mix(s, noise_burst(0.02, perc(80), 0.1), 0.0, 0.2)
    return s


def level_up():
    """Level up — triumphant ascending major run."""
    s = silence(0.6)
    notes = [523.25, 659.25, 783.99, 1046.5]
    for i, f in enumerate(notes):
        mix(s, square(f, 0.12, perc(10)), i * 0.08, 0.4)
        mix(s, square(f * 1.5, 0.12, perc(14)), i * 0.08, 0.12)
    return s


def achievement():
    """Achievement unlocked — bright fanfare with shimmer tail."""
    s = silence(0.8)
    for i, f in enumerate((659.25, 880.0, 1318.5)):
        mix(s, sine(f, 0.5, perc(5)), i * 0.06, 0.45)
        mix(s, square(f, 0.18, perc(12)), i * 0.06, 0.12)
    mix(s, sine(1760.0, 0.4, perc(7)), 0.2, 0.2)
    return s


def game_over():
    """Game over — descending minor 'fail' run."""
    s = silence(0.8)
    notes = [659.25, 587.33, 466.16, 349.23]
    for i, f in enumerate(notes):
        mix(s, square(f, 0.2, perc(7)), i * 0.14, 0.4)
    return s


def select():
    """Menu select — short retro confirm blip."""
    return square(lambda t: 880 + 220 * (1 - math.exp(-60 * t)), 0.08, perc(20))


def laser():
    """Laser/shoot — fast descending zap."""
    s = square(lambda t: 1800 * math.exp(-14 * t) + 200, 0.16, perc(14))
    return s


def explosion():
    """Explosion — noisy boom with low rumble."""
    s = silence(0.4)
    n = Noise(909)
    mix(s, noise_burst(0.3, perc(9), 0.4, n), 0.0, 0.7)
    mix(s, sine(lambda t: 90 * math.exp(-4 * t), 0.3, perc(8)), 0.0, 0.5)
    return s


SOUNDS = [
    ("coin",         "Classic two-step coin blip",     coin),
    ("powerup",      "Rising stepped power-up",        powerup),
    ("jump",         "Upward square jump swoop",       jump),
    ("hurt",         "Downward damage blip",           hurt),
    ("level_up",     "Triumphant ascending run",       level_up),
    ("achievement",  "Bright unlock fanfare",          achievement),
    ("game_over",    "Descending minor fail run",      game_over),
    ("select",       "Retro menu select blip",         select),
    ("laser",        "Fast descending zap",            laser),
    ("explosion",    "Noisy boom with rumble",         explosion),
]
