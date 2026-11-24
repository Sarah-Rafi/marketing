"""Original electronic score + sound effects for the TECTSOFT fitness-coach ad, synthesised from scratch.

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
DUR = 43.5
N = int(SR * DUR)
rng = np.random.default_rng(20261113)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Narration windows (absolute seconds) — must match index.html <audio> starts + durations.
VOICE = [(0.2, 7.21), (7.6, 5.85), (13.8, 3.22), (18.1, 6.29), (24.6, 6.76), (32.4, 2.26), (36.7, 4.5)]
_html = open(os.path.join(ROOT, "index.html")).read()
_placed = [(float(s), float(d)) for s, d in re.findall(r'id="vo-\d+"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', _html)]
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


def glass_sweep(dur=0.7, amp=0.09, up=True):
    """Airy glass: high band-passed air whose brightness sweeps across the cut, plus a faint glassy shimmer."""
    n = int(dur * SR)
    t = t_arr(n)
    p = t / dur if up else 1 - t / dur
    x = rng.standard_normal(n)
    bands = [fft_filter(x, lo=lo, hi=hi, slope=8) for lo, hi in ((1800, 3500), (3500, 6500), (6500, 11000))]
    w = [np.clip(1 - abs(p * 2 - k), 0, 1) for k in range(3)]  # crossfade low -> mid -> high band
    air = sum(wk * bk for wk, bk in zip(w, bands))
    f = 2600 + 2200 * p  # shimmer glides with the sweep
    ph = 2 * np.pi * np.cumsum(f) / SR
    shimmer = 0.06 * (np.sin(ph) + 0.5 * np.sin(1.5 * ph + 1.3))
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return amp * (air / (np.std(air) + 1e-9) * 0.25 + shimmer) * env


def key_click(amp=0.15):
    """A keyboard key: bright tick plus a short low thock."""
    n = int(0.06 * SR)
    t = t_arr(n)
    tick_ = fft_filter(rng.standard_normal(n), lo=1500, hi=7000) * np.exp(-t * 350)
    thock = np.sin(2 * np.pi * rng.uniform(170, 210) * t) * np.exp(-t * 90) * 0.6
    return amp * (tick_ + thock)


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


BEAT = 0.5  # 120 bpm, downbeats on 22.4 + k*0.5 (the features groove)
CH = {"Am": [57, 60, 64], "F": [53, 57, 60], "C": [55, 60, 64], "G": [55, 59, 62]}
ROOTS = {"Am": 45, "F": 41, "C": 48, "G": 43}
music = np.zeros((2, N))


def groove(t0, t1, prog, claps_from=1e9, hats16_from=1e9, stabs_from=1e9, kick_amp=0.55):
    """Kick on every beat, offbeat hats, 8th-note bass, a chord per bar."""
    bar, at = 0, t0
    while at < t1 - 1e-6:
        name = prog[bar % len(prog)]
        place(music, strings([midi(m) for m in CH[name]], 2.1, amp=0.13, a=0.08, r=0.4, bright=8), at)
        for b in range(4):
            tb = at + b * BEAT
            if tb >= t1:
                break
            place(music, kick(kick_amp), tb)
            place(music, tick(0.07), tb + BEAT / 2, 0.35)
            if tb >= hats16_from:
                place(music, tick(0.04), tb + BEAT / 4, -0.35)
            if tb >= claps_from and b % 2 == 1:
                place(music, clap(0.16), tb)
            for e in range(2):
                place(music, bass(midi(ROOTS[name] - 12 + (12 if e else 0)), 0.24, 0.17), tb + e * BEAT / 2)
            if tb >= stabs_from:
                place(music, stab([midi(CH[name][2] + 12)], 0.05), tb + 0.75 * BEAT, 0.25)
        bar += 1
        at += 4 * BEAT


# --- Hook: 0–7.4. A moving pulse; a soft hit on each audience cut.
place(music, strings([midi(45), midi(52), midi(57)], 7.6, amp=0.16, a=0.6, r=0.6, bright=8), 0.0)
for k in range(29):
    at = k * 0.25
    place(music, tick(0.05 if k % 2 else 0.08), at, -0.3 if k % 2 else 0.3)
    if k % 2 == 0:
        place(music, kick(0.32), at)
for at in (1.85, 2.78, 3.4, 4.97):
    place(music, tom(0.6, 140, 70, 0.3), at)
place(music, noise_riser(1.4, 0.12), 6.1)
# --- Problem: 7.4–13.7. Tension: ticking over a drone, frantic once the dozen apps join; a thud when it all drops.
place(music, strings([midi(m) for m in [41, 57, 60]], 6.4, amp=0.15, a=0.8, r=0.6, bright=7), 7.4)
for k in range(21):
    at = 7.4 + k * 0.25
    place(music, tick(0.06 + 0.03 * (at > 11.6)), at, -0.3 if k % 2 else 0.3)
    if at > 11.6:
        place(music, tick(0.05), at + 0.125, 0.3 if k % 2 else -0.3)
place(music, tom(0.8, 110, 50, 0.4), 12.7)
place(music, noise_riser(1.0, 0.15), 12.7)
# --- Reveal: 13.7. Impact, then a lifted bed under the app.
place(music, boom(2.8, 60, 30, 0.8), 13.7)
place(music, braam(48, 2.8, 0.26), 13.7)
place(music, strings([midi(m) for m in [36, 48, 55, 60, 64, 67]], 3.2, amp=0.22, a=0.03, r=1.2, bright=10), 13.7)
crash = fft_filter(rng.standard_normal(int(2.2 * SR)), lo=3000, hi=12000) * np.exp(-t_arr(int(2.2 * SR)) * 2.4) * 0.08
place(music, crash, 13.7, -0.2)
for k in range(4):
    place(music, kick(0.3), 15.6 + k * 0.5)
place(music, noise_riser(1.1, 0.15), 16.8)
# --- Features: 17.9–32.1. The groove builds as the features stack up.
groove(17.9, 32.1, ["Am", "F", "C", "G"], claps_from=24.5, hats16_from=27.3, stabs_from=19.9)
for at in (19.9, 22.2, 24.5):
    place(music, boom(1.4, 58, 34, 0.26), at)
place(music, boom(1.8, 58, 34, 0.33), 27.3)
# --- Transformation: 32.1–36.3. Brighter progression, riser into the end card.
groove(32.1, 35.7, ["F", "G"], claps_from=32.1, hats16_from=32.1, stabs_from=32.1, kick_amp=0.6)
place(music, strings([midi(m) for m in [55, 59, 62, 67]], 0.9, amp=0.22, a=0.2, r=0.4), 35.5)
place(music, noise_riser(1.5, 0.17), 34.8)
# --- End: 36.3. Final hit; C major rings out under the logo.
place(music, boom(3.4, 60, 30, 0.75), 36.3)
place(music, braam(48, 3.0, 0.2), 36.3)
place(music, strings([midi(m) for m in [36, 48, 55, 60, 64, 67, 72]], 6.6, amp=0.24, a=0.04, r=3.0, bright=10), 36.3)
place(music, kick(0.5), 36.3)

music = np.stack([reverb(music[0]), reverb(music[1])])
duck = np.ones(N)
t = t_arr(N)
for s, d in VOICE:
    a0, a1 = s - 0.12, s + d + 0.05
    g = np.clip(np.minimum((t - a0) / 0.09, (a1 + 0.25 - t) / 0.25), 0, 1)
    duck = np.minimum(duck, 1 - 0.6 * g)
music *= duck
music *= np.clip((DUR - t) / 2.0, 0, 1)

sfx = np.zeros((2, N))
# Scene changes: an airy glass sweep, like a glass panel sliding past (peaks on the cut).
for i, c in enumerate([1.85, 2.78, 3.4, 4.97, 7.4, 13.7, 17.9, 19.9, 22.2, 24.5, 25.85, 27.3, 32.1, 36.3]):
    place(sfx, glass_sweep(0.7, 0.09, up=i % 2 == 0), c - 0.42, -0.35 if i % 2 else 0.35)
# Keyboard: one click per character of the typed website. Must match TYPE_AT / GAPS in compositions/endcard.html.
TYPE_AT = 36.3 + 4.1
TYPE_GAPS = [0.09, 0.07, 0.1, 0.08, 0.11, 0.07, 0.09, 0.13, 0.08, 0.07, 0.1, 0.08]
k = TYPE_AT
for g in TYPE_GAPS:
    place(sfx, key_click(rng.uniform(0.13, 0.17)), k, rng.uniform(-0.15, 0.15))
    k += g
for at in (8.38, 9.12, 9.92, 10.66):  # juggled icons: clients, schedules, workouts, progress
    place(sfx, pop(0.1), at, rng.uniform(-0.5, 0.5))
for k in range(8):  # a dozen different apps
    place(sfx, pop(0.05), 11.6 + k * 0.06, rng.uniform(-0.7, 0.7))
for k in range(6):  # icons hit the floor
    place(sfx, tom(0.25, 160, 80, 0.12), 12.95 + k * 0.07, rng.uniform(-0.6, 0.6))
place(sfx, pop(0.09), 16.7, 0.2)  # brand mark
for at in (19.35, 20.75, 28.9):  # milestone, plan shared, payment received
    place(sfx, pop(0.12), at, 0.2)
place(sfx, glass_sweep(0.6, 0.05, up=True), 19.9, 0.3)  # plan flies to the phone
for k in range(3):  # food lands on the plate
    place(sfx, pop(0.07), 22.4 + k * 0.22, -0.3)
for k in range(3):  # AI sparkles
    place(sfx, tick(0.05), 23.85 + k * 0.1, 0.3)
for k in range(8):  # members join
    place(sfx, pop(0.05), 24.85 + k * 0.06, rng.uniform(-0.5, 0.5))
place(sfx, pop(0.1), 25.85, -0.3)  # price tag
place(sfx, pop(0.1), 28.5, 0.3)  # class booked
for at in (33.0, 33.5, 34.35):  # coach's tablet updates clients
    place(sfx, pop(0.08), at, rng.uniform(-0.4, 0.4))
place(sfx, pop(0.07), 41.45, 0.0)  # email
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
