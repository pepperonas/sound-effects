#!/usr/bin/env python3
"""Synthesize a short ~0.5s 'paste from clipboard' UI sound -> paste.wav"""
import wave, struct, math

SR = 44100
DUR = 0.5
N = int(SR * DUR)

def env_ad(i, attack, decay, total):
    """Attack-decay envelope, times in samples."""
    if i < attack:
        return i / attack
    j = i - attack
    if j < decay:
        return math.exp(-3.0 * j / decay)
    return 0.0

samples = [0.0] * N

# Layer 1: soft "tick" click at the very start (broadband short blip)
tick_len = int(0.012 * SR)
for i in range(tick_len):
    t = i / SR
    # high-ish ping that decays fast
    s = math.sin(2 * math.pi * 2200 * t) * math.exp(-180 * t)
    s += 0.5 * math.sin(2 * math.pi * 3400 * t) * math.exp(-220 * t)
    samples[i] += 0.35 * s

# Layer 2: a short upward "swoosh"/drop-in body ~ paste landing (40ms in)
start2 = int(0.04 * SR)
body_len = int(0.12 * SR)
for k in range(body_len):
    i = start2 + k
    if i >= N:
        break
    t = k / SR
    # pitch glides up quickly then settles (paste "pop in")
    f = 320 + 520 * (1 - math.exp(-40 * t))
    e = env_ad(k, int(0.004 * SR), body_len, body_len)
    s = math.sin(2 * math.pi * f * t) * e
    s += 0.4 * math.sin(2 * math.pi * 2 * f * t) * e
    samples[i] += 0.5 * s

# Layer 3: subtle low "thump" to give it weight
start3 = int(0.045 * SR)
thump_len = int(0.10 * SR)
for k in range(thump_len):
    i = start3 + k
    if i >= N:
        break
    t = k / SR
    f = 150 * math.exp(-6 * t)
    s = math.sin(2 * math.pi * f * t) * math.exp(-22 * t)
    samples[i] += 0.45 * s

# Gentle global fade-out tail to avoid clicks at the end
fade = int(0.05 * SR)
for k in range(fade):
    i = N - fade + k
    samples[i] *= (1 - k / fade)

# Normalize
peak = max(1e-9, max(abs(s) for s in samples))
gain = 0.9 / peak

with wave.open("paste.wav", "w") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    frames = bytearray()
    for s in samples:
        v = int(max(-1.0, min(1.0, s * gain)) * 32767)
        frames += struct.pack("<h", v)
    w.writeframes(bytes(frames))

print("wrote paste.wav (%.2fs, %d Hz)" % (DUR, SR))
