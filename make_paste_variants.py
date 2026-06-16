#!/usr/bin/env python3
"""Generate 10 'paste from clipboard' sounds in different styles -> paste_01..10.wav"""
import wave, struct, math

SR = 44100

def write_wav(name, samples):
    peak = max(1e-9, max(abs(s) for s in samples))
    gain = 0.9 / peak
    with wave.open(name, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for s in samples:
            v = int(max(-1.0, min(1.0, s * gain)) * 32767)
            frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))
    print("wrote", name, "(%.2fs)" % (len(samples) / SR))

def buf(dur):
    return [0.0] * int(SR * dur)

def fade_tail(s, ms=40):
    f = int(ms / 1000 * SR)
    for k in range(min(f, len(s))):
        s[len(s) - 1 - k] *= k / f

# simple noise (deterministic LCG so it's reproducible)
_seed = 12345
def noise():
    global _seed
    _seed = (_seed * 1103515245 + 12345) & 0x7fffffff
    return (_seed / 0x3fffffff) - 1.0


# 1. Soft bubble pop — round, friendly, water-droplet-ish
def s1():
    s = buf(0.45)
    L = len(s)
    for i in range(L):
        t = i / SR
        f = 420 + 900 * (1 - math.exp(-60 * t))   # quick upward glide
        e = math.exp(-14 * t)
        s[i] = math.sin(2 * math.pi * f * t) * e
        s[i] += 0.3 * math.sin(2 * math.pi * 2 * f * t) * math.exp(-22 * t)
    fade_tail(s)
    return s

# 2. Mechanical keyboard click — sharp, snappy, two-stage clack
def s2():
    s = buf(0.4)
    # down-stroke click
    for i in range(int(0.01 * SR)):
        t = i / SR
        s[i] += (noise() * 0.6 + math.sin(2 * math.pi * 1800 * t)) * math.exp(-260 * t)
    # bottom-out thock
    st = int(0.018 * SR)
    for k in range(int(0.06 * SR)):
        i = st + k; t = k / SR
        s[i] += 0.7 * math.sin(2 * math.pi * 320 * math.exp(-30 * t) * t) * math.exp(-45 * t)
        s[i] += 0.2 * noise() * math.exp(-120 * t)
    fade_tail(s, 20)
    return s

# 3. Sci-fi / digital teleport-in — bright zappy materialize
def s3():
    s = buf(0.5)
    L = len(s)
    for i in range(L):
        t = i / SR
        f = 200 + 2600 * (t / (L / SR))           # rising sweep
        e = (1 - math.exp(-40 * t)) * math.exp(-6 * t)
        s[i] = math.sin(2 * math.pi * f * t) * e
        # ring modulation for digital shimmer
        s[i] *= 0.6 + 0.4 * math.sin(2 * math.pi * 90 * t)
        s[i] += 0.15 * math.sin(2 * math.pi * 3 * f * t) * e
    fade_tail(s)
    return s

# 4. Retro 8-bit blip — square-wave game coin/insert
def s4():
    s = buf(0.35)
    L = len(s)
    steps = [600, 900, 1320]                       # arpeggio up
    seg = L // len(steps)
    for n, f in enumerate(steps):
        for k in range(seg):
            i = n * seg + k; t = k / SR
            sq = 1.0 if (math.sin(2 * math.pi * f * t) >= 0) else -1.0
            s[i] = sq * 0.5 * math.exp(-8 * t)
    fade_tail(s, 15)
    return s

# 5. Deep UI thunk — soft, weighty, premium app "drop in"
def s5():
    s = buf(0.5)
    L = len(s)
    for i in range(L):
        t = i / SR
        f = 180 * math.exp(-5 * t) + 70
        s[i] = math.sin(2 * math.pi * f * t) * math.exp(-9 * t)
    # tiny top tick for definition
    for i in range(int(0.008 * SR)):
        t = i / SR
        s[i] += 0.25 * math.sin(2 * math.pi * 2600 * t) * math.exp(-200 * t)
    fade_tail(s)
    return s

# 6. Whoosh + snap — fast air swipe landing on a click
def s6():
    s = buf(0.45)
    L = len(s)
    # filtered noise whoosh (rising then falling amplitude)
    lp = 0.0
    for i in range(int(0.18 * SR)):
        t = i / SR
        a = math.sin(math.pi * t / 0.18)           # bell-shaped
        lp = lp * 0.75 + noise() * 0.25             # crude low-pass
        s[i] += lp * a * 0.8
    # snap at the end of the whoosh
    st = int(0.17 * SR)
    for k in range(int(0.04 * SR)):
        i = st + k; t = k / SR
        s[i] += 0.8 * math.sin(2 * math.pi * 1400 * t) * math.exp(-90 * t)
    fade_tail(s)
    return s

# 7. Glassy marimba ping — musical two-note "tonk"
def s7():
    s = buf(0.55)
    L = len(s)
    notes = [(659.25, 0.0), (987.77, 0.05)]        # E5 then B5
    for f, off in notes:
        st = int(off * SR)
        for k in range(L - st):
            i = st + k; t = k / SR
            e = math.exp(-7 * t)
            s[i] += math.sin(2 * math.pi * f * t) * e * 0.7
            s[i] += 0.25 * math.sin(2 * math.pi * 3 * f * t) * math.exp(-16 * t)
    fade_tail(s)
    return s

# 8. Modem / data-burst — glitchy digital paste, granular bursts
def s8():
    s = buf(0.5)
    L = len(s)
    freqs = [880, 1500, 660, 2000, 1100, 1760]
    g = L // len(freqs)
    for n, f in enumerate(freqs):
        for k in range(g):
            i = n * g + k; t = k / SR
            sq = 1.0 if (math.sin(2 * math.pi * f * t) >= 0) else -1.0
            gate = 1.0 if (int(t * 400) % 2 == 0) else 0.3
            s[i] = sq * 0.4 * gate
    fade_tail(s, 25)
    return s

# 9. Soft "tape" stick — analog paste, warm noise swell + thud
def s9():
    s = buf(0.5)
    L = len(s)
    lp = 0.0
    for i in range(L):
        t = i / SR
        env = math.sin(math.pi * min(1.0, t / 0.25)) * math.exp(-3 * t)
        lp = lp * 0.85 + noise() * 0.15
        s[i] = lp * env * 0.6
    # warm low thud underneath
    for i in range(int(0.12 * SR)):
        t = i / SR
        s[i] += 0.5 * math.sin(2 * math.pi * 120 * t) * math.exp(-18 * t)
    fade_tail(s)
    return s

# 10. Bright double-tick "confirm" — crisp, modern, two quick clicks
def s10():
    s = buf(0.4)
    for off in (0.0, 0.07):
        st = int(off * SR)
        for k in range(int(0.03 * SR)):
            i = st + k; t = k / SR
            s[i] += math.sin(2 * math.pi * 1900 * t) * math.exp(-110 * t)
            s[i] += 0.4 * math.sin(2 * math.pi * 2850 * t) * math.exp(-150 * t)
    fade_tail(s, 15)
    return s


variants = [
    ("paste_01_bubble.wav",   s1),
    ("paste_02_mechkey.wav",  s2),
    ("paste_03_scifi.wav",    s3),
    ("paste_04_8bit.wav",     s4),
    ("paste_05_thunk.wav",    s5),
    ("paste_06_whoosh.wav",   s6),
    ("paste_07_marimba.wav",  s7),
    ("paste_08_databurst.wav",s8),
    ("paste_09_tape.wav",     s9),
    ("paste_10_doubletick.wav", s10),
]

for name, fn in variants:
    write_wav(name, fn())
