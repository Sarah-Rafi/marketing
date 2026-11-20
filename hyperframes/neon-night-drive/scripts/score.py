"""Original synthwave score + sound effects for the neon night drive, synthesised from scratch.

Deterministic (seeded); no samples. Writes assets/audio/mix.wav (15 s, 48 kHz stereo).
Event times are absolute seconds and must match the scene timings in index.html/compositions.
Run: ~/.venvs/kokoro/bin/python scripts/score.py
"""

import os
import wave

import numpy as np

SR = 48000
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(20261120)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

L = np.zeros(N)
R = np.zeros(N)


def t_arr(n):
    return np.arange(n) / SR


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i : i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i : i + len(sig)] += sig * gain * (1 + min(pan, 0))


def env(n, a, d):
    e = np.exp(-t_arr(n) / d)
    na = max(int(a * SR), 1)
    e[:na] *= np.linspace(0, 1, na)
    return e


def saw(f, n):
    ph = np.cumsum(np.full(n, f) if np.isscalar(f) else f) / SR
    return 2 * (ph % 1) - 1


# ---------- music: 120 bpm, A minor, Am F C G ----------
BEAT = 0.5
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
ROOTS = [33, 29, 36, 31]
intensity = lambda t: 0.35 if t < 4.2 else (0.8 if t < 10.4 else 1.0)

for bar in range(8):
    t0 = bar * 2.0
    ch = CHORDS[bar % 4]
    n = int(2.0 * SR)
    pad = sum(saw(midi(m) * d, n) for m in ch for d in (0.997, 1.003))
    pad = lowpass(pad, 900) * env(n, 0.3, 3.0) * 0.05
    add(pad, t0, intensity(t0), pan=0.0)
    for k in range(16):  # eighth-note bass
        t = t0 + k * BEAT / 2
        nb = int(0.22 * SR)
        b = lowpass(saw(midi(ROOTS[bar % 4]), nb), 500) * env(nb, 0.005, 0.12)
        add(b, t, 0.32 * intensity(t))

for k in range(int(DUR / BEAT)):
    t = k * BEAT
    if t >= 4.2:
        nk = int(0.3 * SR)
        f = 50 + 90 * np.exp(-t_arr(nk) / 0.03)
        add(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(nk, 0.001, 0.12), t, 0.6)
        if k % 2:
            ns = int(0.2 * SR)
            add(lowpass(rng.standard_normal(ns), 5000) * env(ns, 0.001, 0.06), t, 0.22)
    for h in (0, 0.25):
        nh = int(0.05 * SR)
        hat = rng.standard_normal(nh) - lowpass(rng.standard_normal(nh), 3000)
        add(hat * env(nh, 0.001, 0.015), t + h, 0.05 * intensity(t))

ARP = [69, 72, 76, 72, 69, 72, 76, 79]
t = 7.2
i = 0
while t < 14.4:  # sixteenth-note lead arp once the chase is on
    na = int(0.12 * SR)
    root_shift = [0, -4, -9, -2][int(t // 2.0) % 4]
    a = lowpass(saw(midi(ARP[i % 8] + root_shift), na), 2500) * env(na, 0.003, 0.07)
    add(a, t, 0.06, pan=0.3 if i % 2 else -0.3)
    t += 0.125
    i += 1

# ---------- foley ----------
def click(gain, cutoff=3000, dur=0.04):
    n = int(dur * SR)
    return lowpass(rng.standard_normal(n), cutoff) * env(n, 0.001, dur / 4) * gain


for k, t in enumerate(np.arange(0.1, 2.4, 0.26)):  # footsteps
    add(click(0.5, 1800), t + (0.11 if k % 2 else 0), 1.0, pan=-0.2 if k % 2 else 0.2)
for t in np.arange(2.45, 3.0, 0.15):
    add(click(0.5, 1800), t)

add(click(0.6, 6000, 0.03), 2.85)  # door latch
nd = int(0.4 * SR)
slam = lowpass(rng.standard_normal(nd), 400) * env(nd, 0.002, 0.08) + np.sin(2 * np.pi * 70 * t_arr(nd)) * env(nd, 0.002, 0.12)
add(slam, 3.73, 0.9)

# engine: start + rev at 3.9, then a sustained growl that follows the driving
ne = N - int(3.9 * SR)
te = t_arr(ne)
rpm = 34 + 30 * (1 - np.exp(-te / 0.25)) * (te < 0.7) + (te >= 0.7) * (46 + 6 * np.sin(2 * np.pi * 0.7 * te))
rpm = rpm + 14 * np.exp(-((te - 0.4) ** 2) / 0.02)
eng = lowpass(saw(rpm, ne) + 0.5 * saw(rpm * 2.01, ne), 380)
eng *= np.clip(te / 0.05, 0, 1) * 0.22
add(eng, 3.9)

# sirens: two cruisers, offset wails, panned apart
for k, (pan, ph) in enumerate([(-0.5, 0.0), (0.5, 0.45)]):
    ns = N - int(5.6 * SR)
    ts = t_arr(ns)
    f = 1000 + 320 * np.sin(2 * np.pi * (ts / 1.1 + ph))
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
    s = lowpass(s, 2500)
    amp = np.clip(ts / 0.9, 0, 1) * 0.06
    amp *= np.clip((DUR - 5.6 - ts) / 0.6, 0, 1)
    add(s * amp, 5.6, 1.0, pan)

# whoosh of oncoming traffic on the coast road
nw = int(0.5 * SR)
add(lowpass(rng.standard_normal(nw), 1200) * np.hanning(nw) * 0.25, 5.75, pan=-0.4)
add(lowpass(rng.standard_normal(nw), 1200) * np.hanning(nw) * 0.25, 6.35, pan=-0.4)

# gun handling
for t in (8.0, 9.7):
    add(click(0.7, 7000, 0.025), t)
    add(click(0.7, 5000, 0.03), t + 0.09)


def gunshot(gain, cutoff):
    n = int(0.5 * SR)
    crack = lowpass(rng.standard_normal(n), cutoff) * env(n, 0.0005, 0.035)
    boom = np.sin(2 * np.pi * 90 * t_arr(n) * np.exp(-t_arr(n) / 0.2)) * env(n, 0.001, 0.09)
    tail = lowpass(rng.standard_normal(n), 900) * env(n, 0.01, 0.18) * 0.3
    return (crack + boom + tail) * gain


for t in (10.7, 11.0, 11.4, 11.9, 13.3):  # passenger
    add(gunshot(0.95, 7000), t)
    add(click(0.35, 9000, 0.02), t + 0.05, pan=0.5)  # ricochet ping on the cruiser
    for j in range(3):
        add(click(0.12, 9000, 0.015), t + 0.32 + j * 0.07, pan=0.3)  # shell tinkle
for t, pan in ((11.2, -0.5), (11.65, 0.5)):  # police return fire
    add(gunshot(0.6, 4000), t, pan=pan)

# tyre screech through the turn
nq = int(0.95 * SR)
tq = t_arr(nq)
sq = np.sin(2 * np.pi * np.cumsum(1400 + 120 * np.sin(2 * np.pi * 9 * tq)) / SR)
sq = (sq * 0.5 + lowpass(rng.standard_normal(nq), 3000) * 0.5) * np.hanning(nq) * 0.3
add(sq, 12.65)

# ---------- master ----------
mix = np.stack([L, R], axis=1)
fade = int(0.4 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix *= 0.9 / np.max(np.abs(mix))
out = os.path.join(ROOT, "assets", "audio", "mix.wav")
os.makedirs(os.path.dirname(out), exist_ok=True)
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", out, f"{N / SR:.1f}s")
