"""Original workout-pop score + sound effects for the fitness pitch, synthesised from scratch.

Deterministic (seeded). No samples, no third-party music. Writes:
  assets/music/score.wav  (music bed, voice ducking baked in)
  assets/sfx/sfx.wav      (whooshes, pen strokes, pops)

Run:  ~/.venvs/kokoro/bin/python scripts/score.py
"""

import os
import re
import wave

import numpy as np

SR = 48000
DUR = 45.0
N = int(SR * DUR)
rng = np.random.default_rng(20261113)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Narration windows (absolute seconds) — must match index.html <audio> starts + durations.
VOICE = [(0.4, 3.2), (4.0, 2.41), (7.0, 5.12), (12.6, 3.48), (19.2, 4.84), (24.5, 7.0), (32.0, 5.33), (38.0, 2.07), (41.6, 0.94)]
_html = open(os.path.join(ROOT, "index.html")).read()
_placed = [(float(s), float(d)) for s, d in re.findall(r'id="vo-\d"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', _html)]
assert _placed == VOICE, f"VOICE {VOICE} != index.html narration {_placed}"

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def t_arr(n):
    return np.arange(n) / SR


def env_adsr(n, a, r, curve=2.0):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na) ** curve
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e


def fft_filter(x, lo=None, hi=None, slope=6.0):
    """Smooth band filter in the frequency domain (whole-buffer)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** slope)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** slope)
    return np.fft.irfft(X * g, len(x))


def strings(freqs, dur, amp=0.1, a=1.0, r=1.0, bright=10, vib=0.004):
    n = int(dur * SR)
    t = t_arr(n)
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.0025, 0.0, 0.0031):
            ph = rng.uniform(0, 2 * np.pi)
            vibr = 1 + vib * np.sin(2 * np.pi * (4.7 + det * 300) * t + ph)
            fv = f * (1 + det) * vibr
            phase = 2 * np.pi * np.cumsum(fv) / SR
            for k in range(1, bright + 1):
                if f * k > 9000:
                    break
                out += np.sin(k * phase + ph * k) / k ** 1.25
    out *= amp / (len(freqs) * 3)
    return out * env_adsr(n, a, r)


def boom(dur=2.4, f0=62, f1=31, amp=0.9):
    n = int(dur * SR)
    t = t_arr(n)
    f = f1 + (f0 - f1) * np.exp(-t * 3.0)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    click = fft_filter(rng.standard_normal(n), lo=200, hi=3000) * np.exp(-t * 60) * 0.25
    return amp * (s + click)


def braam(root_midi, dur=3.2, amp=0.55):
    n = int(dur * SR)
    t = t_arr(n)
    out = np.zeros(n)
    for m in (root_midi - 12, root_midi, root_midi + 7, root_midi + 12):
        for det in (-0.004, 0.0, 0.005):
            phase = 2 * np.pi * midi(m) * (1 + det) * t
            saw = sum(np.sin(k * phase) / k for k in range(1, 30) if midi(m) * k < 8000)
            out += saw
    out = np.tanh(out * 0.35)
    out = fft_filter(out, hi=1800, slope=4)
    e = np.minimum(t / 0.04, 1) * np.exp(-t * 0.9)
    return amp * out * e


def tom(dur=0.6, f0=120, f1=68, amp=0.5):
    n = int(dur * SR)
    t = t_arr(n)
    f = f1 + (f0 - f1) * np.exp(-t * 18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    nz = fft_filter(rng.standard_normal(n), lo=150, hi=1200) * np.exp(-t * 30) * 0.3
    return amp * (s + nz)


def tick(amp=0.08):
    n = int(0.05 * SR)
    t = t_arr(n)
    return amp * fft_filter(rng.standard_normal(n), lo=3000, hi=9000) * np.exp(-t * 120)


def stab(freqs, amp=0.07):
    n = int(0.32 * SR)
    t = t_arr(n)
    out = np.zeros(n)
    for f in freqs:
        phase = 2 * np.pi * f * t
        out += sum(np.sin(k * phase) / k ** 1.1 for k in range(1, 14) if f * k < 9000)
    return amp / len(freqs) * out * np.minimum(t / 0.006, 1) * np.exp(-t * 11)


def noise_riser(dur, amp=0.25, lo0=300, hi1=9000):
    n = int(dur * SR)
    t = t_arr(n)
    x = rng.standard_normal(n)
    # crossfade between a dark and a bright filtered copy as it rises
    dark = fft_filter(x, lo=lo0, hi=1200)
    bright = fft_filter(x, lo=2000, hi=hi1)
    p = (t / dur) ** 2
    gliss = np.sin(2 * np.pi * np.cumsum(220 + 660 * p ** 1.5) / SR) * 0.25
    return amp * ((1 - p) * dark + p * bright + gliss) * p


def whoosh(dur=0.7, amp=0.3):
    n = int(dur * SR)
    t = t_arr(n)
    x = fft_filter(rng.standard_normal(n), lo=250, hi=4500)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2.5
    return amp * x * e


def scratch(dur, amp=0.05):
    """Pen on paper: high-passed noise with stroke-rate amplitude modulation."""
    n = int(dur * SR)
    t = t_arr(n)
    x = fft_filter(rng.standard_normal(n), lo=2500, hi=8000)
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * 7.3 * t + 2 * np.sin(2 * np.pi * 1.9 * t))
    return amp * x * mod * env_adsr(n, 0.05, 0.08, 1)


def slap(amp=0.12):
    n = int(0.12 * SR)
    t = t_arr(n)
    return amp * fft_filter(rng.standard_normal(n), lo=600, hi=5000) * np.exp(-t * 45)


def reverb(x, secs=2.2, wet=0.28):
    n = int(secs * SR)
    t = t_arr(n)
    ir = rng.standard_normal(n) * np.exp(-t * 3.2 / secs * 2)
    ir = fft_filter(ir, hi=5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[: len(x)]
    return (1 - wet) * x + wet * y


def place(buf, sig, at, pan=0.0):
    i = int(at * SR)
    j = min(i + len(sig), N)
    if j <= i:
        return
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    buf[0, i:j] += sig[: j - i] * l
    buf[1, i:j] += sig[: j - i] * r



def kick(amp=0.6):
    n = int(0.35 * SR)
    t = t_arr(n)
    f = 48 + 110 * np.exp(-t * 35)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def clap(amp=0.14):
    n = int(0.2 * SR)
    t = t_arr(n)
    x = fft_filter(rng.standard_normal(n), lo=900, hi=4000)
    e = np.exp(-t * 28) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0) * (t < 0.03))
    return amp * x * e


def bass(f, dur, amp=0.16):
    n = int(dur * SR)
    t = t_arr(n)
    ph = 2 * np.pi * f * t
    x = sum(np.sin(k * ph) / k for k in range(1, 12))
    return amp * fft_filter(x, hi=500, slope=4) * np.minimum(t / 0.01, 1) * np.exp(-t * 5)


def pop(amp=0.1):
    n = int(0.09 * SR)
    t = t_arr(n)
    f = 900 + 500 * np.exp(-t * 60)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 55)


BEAT = 0.5  # 120 bpm, downbeats on 16.2 + k*0.5
CH = {"Am": [57, 60, 64], "F": [53, 57, 60], "C": [55, 60, 64], "G": [55, 59, 62]}
ROOTS = {"Am": 45, "F": 41, "C": 48, "G": 43}
music = np.zeros((2, N))

# --- Problem: 0–12.4. A ticking clock over a low drone; the crunch cuts hit; physio goes quiet and tender.
place(music, strings([midi(45), midi(52)], 7.2, amp=0.2, a=1.5, r=1.0, bright=8), 0.0)
for k in range(14):
    at = 0.2 + k * 0.5
    if at < 6.9:
        place(music, tick(0.07 if k % 2 else 0.1), at, -0.3 if k % 2 else 0.3)
for at in (4.0, 4.7, 5.87):
    place(music, tom(0.6, 140, 70, 0.4), at)
    place(music, stab([midi(57), midi(60)], 0.06), at)
place(music, strings([midi(41), midi(57), midi(60), midi(64)], 5.6, amp=0.15, a=1.2, r=1.2, bright=7), 7.0)
place(music, strings([midi(76)], 4.5, amp=0.04, a=1.5, r=1.2, bright=3), 7.6, 0.3)
# --- Turn: 12.4–16.2. Strings climb, riser into the title impact.
place(music, strings([midi(m) for m in [48, 55, 60, 64]], 1.9, amp=0.17, a=0.4, r=0.3), 12.4)
place(music, strings([midi(m) for m in [50, 55, 62, 67]], 1.9, amp=0.19, a=0.3, r=0.3), 14.3)
place(music, noise_riser(2.6, 0.2), 13.55)
# --- Impact: 16.2 (title). Bright C major hit that rings under the title.
place(music, boom(2.8, 60, 30, 0.85), 16.2)
place(music, braam(48, 2.8, 0.3), 16.2)
place(music, strings([midi(m) for m in [36, 48, 55, 60, 64, 67]], 3.0, amp=0.24, a=0.03, r=1.2, bright=10), 16.2)
crash = fft_filter(rng.standard_normal(int(2.2 * SR)), lo=3000, hi=12000) * np.exp(-t_arr(int(2.2 * SR)) * 2.4) * 0.1
place(music, crash, 16.2, -0.2)
for b in range(4):
    place(music, tick(0.06), 17.7 + b * 0.25, 0.4)
place(music, noise_riser(0.5, 0.18), 18.7)

# --- Groove: 19.2–37.7. Kick on every beat, offbeat hats, 8th-note bass, a chord per bar (Am F C G).
prog = ["Am", "F", "C", "G"]
bar = 0
at = 19.2
while at < 37.7 - 1e-6:
    name = prog[bar % 4]
    place(music, strings([midi(m) for m in CH[name]], 2.1, amp=0.13, a=0.08, r=0.4, bright=8), at)
    for b in range(4):
        t0 = at + b * BEAT
        if t0 >= 37.7:
            break
        place(music, kick(0.55), t0)
        place(music, tick(0.07), t0 + BEAT / 2, 0.35)
        if t0 >= 31.7:
            place(music, tick(0.04), t0 + BEAT / 4, -0.35)
            if b % 2 == 1:
                place(music, clap(0.16), t0)
        for e in range(2):
            place(music, bass(midi(ROOTS[name] - 12 + (12 if e else 0)), 0.24, 0.17), t0 + e * BEAT / 2)
        if t0 >= 24.3:
            place(music, stab([midi(CH[name][2] + 12)], 0.05), t0 + 0.75 * BEAT, 0.25)
    bar += 1
    at += 4 * BEAT
place(music, boom(1.5, 58, 34, 0.3), 24.3)
place(music, boom(1.8, 58, 34, 0.35), 31.7)
# --- Claim: 37.7–40.2. Drums out, held chord and a riser into the end card.
place(music, strings([midi(m) for m in [53, 57, 60, 65]], 1.3, amp=0.2, a=0.3, r=0.3), 37.7)
place(music, strings([midi(m) for m in [55, 59, 62, 67]], 1.3, amp=0.22, a=0.2, r=0.4), 38.95)
for b in range(5):
    place(music, kick(0.3), 37.7 + b * BEAT)
place(music, noise_riser(1.6, 0.18), 38.6)
# --- End: 40.2. Final hit, C major rings out.
place(music, boom(3.4, 60, 30, 0.8), 40.2)
place(music, braam(48, 3.0, 0.25), 40.2)
place(music, strings([midi(m) for m in [36, 48, 55, 60, 64, 67, 72]], 4.6, amp=0.26, a=0.04, r=2.2, bright=10), 40.2)
place(music, kick(0.5), 40.2)

music = np.stack([reverb(music[0]), reverb(music[1])])
duck = np.ones(N)
t = t_arr(N)
for s, d in VOICE:
    a0, a1 = s - 0.12, s + d + 0.05
    g = np.clip(np.minimum((t - a0) / 0.09, (a1 + 0.25 - t) / 0.25), 0, 1)
    duck = np.minimum(duck, 1 - 0.6 * g)
music *= duck
music *= np.clip((45.0 - t) / 2.0, 0, 1)

sfx = np.zeros((2, N))
for c in [4.0, 4.7, 5.87, 7.0, 12.4, 19.0, 24.3, 31.7, 37.7, 40.2]:
    place(sfx, whoosh(rng.uniform(0.6, 0.8), 0.3), c - 0.38, rng.uniform(-0.5, 0.5))
for k in range(4):  # red crosses on the calendar
    place(sfx, scratch(0.18, 0.07), 6.0 + k * 0.17, 0.2)
for at in (8.25, 9.15):  # rings drawn on knee and back
    place(sfx, scratch(0.45, 0.06), at, -0.2)
for k in range(5):  # the coach's plan writes itself
    place(sfx, scratch(0.28, 0.05), 19.0 + 4.15 + k * 0.2, -0.1)
for k in range(3):  # steps ticked off in the app
    place(sfx, pop(0.12), 24.3 + 4.17 + k * 0.38, 0.2)
for k in range(16):  # homes light up across the city
    place(sfx, pop(0.05), 37.7 + 0.43 + k * 0.07, rng.uniform(-0.6, 0.6))
sfx = np.stack([reverb(sfx[0], 0.8, 0.15), reverb(sfx[1], 0.8, 0.15)])


def write(path, x, peak_db=-1.5):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pcm = (np.clip(x.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", path)


write(os.path.join(ROOT, "assets/music/score.wav"), music)
write(os.path.join(ROOT, "assets/sfx/sfx.wav"), sfx, -3.0)
