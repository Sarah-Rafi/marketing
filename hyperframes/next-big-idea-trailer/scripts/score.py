"""Original soft corporate score + sound effects for TECTSOFT "From idea to impact", synthesised from scratch.

Deterministic (seeded). No samples, no third-party music. Writes:
  assets/music/score.wav  (music bed, voice ducking baked in)
  assets/sfx/sfx.wav      (glass sweeps, soft pops, check ticks, key clicks)

Run:  ~/.venvs/kokoro/bin/python scripts/score.py
"""

import os
import re
import wave

import numpy as np

SR = 48000
DUR = 43.0
N = int(SR * DUR)
rng = np.random.default_rng(20261123)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Narration windows (absolute seconds) — must match index.html <audio> starts + durations.
VOICE = [(0.2, 2.75), (3.1, 4.27), (7.9, 4.18), (14.2, 4.27), (20.6, 2.62), (25.2, 3.01), (30.0, 2.69), (36.4, 3.29)]
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



def pluck(f, dur=1.2, amp=0.06):
    """Soft felt-piano-like note: a few harmonics, quick attack, gentle decay."""
    n = int(dur * SR)
    t = t_arr(n)
    x = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.5 + 2.2 * k)) / k ** 1.6 for k in range(1, 7))
    return amp * x * np.minimum(t / 0.004, 1)


BEAT = 60 / 96  # 96 bpm
CH = {"F": [53, 57, 60, 64], "C": [48, 55, 60, 64], "Am": [45, 52, 57, 60], "G": [43, 50, 55, 59]}
ROOTS = {"F": 41, "C": 36, "Am": 45, "G": 43}
PROG = ["F", "C", "Am", "G"]
music = np.zeros((2, N))


def section(t0, t1, arp=False, drums=False, bass_on=False, pad_amp=0.1):
    bar, at = 0, t0
    while at < t1 - 1e-6:
        name = PROG[bar % 4]
        bl = min(4 * BEAT, t1 - at)
        place(music, strings([midi(m) for m in CH[name]], bl + 0.6, amp=pad_amp, a=0.5, r=0.6, bright=5, vib=0.002), at)
        for e in range(8):
            tb = at + e * BEAT / 2
            if tb >= t1:
                break
            if arp:
                notes = CH[name][1:] + [CH[name][1] + 12]
                place(music, pluck(midi(notes[(e * 3) % 4] + 12), 1.0, 0.05), tb, -0.25 + 0.5 * (e % 2))
            if drums:
                if e % 4 == 0:
                    place(music, kick(0.28), tb)
                if e % 2 == 1:
                    place(music, tick(0.035), tb, 0.3)
                if e == 4:
                    place(music, clap(0.05), tb)
            if bass_on and e % 2 == 0:
                place(music, bass(midi(ROOTS[name]), BEAT * 0.9, 0.1), tb)
        bar += 1
        at += 4 * BEAT


# Hook (0–3.1): a warm pad and two open piano notes — a question, not a beat.
section(0.0, 3.1, pad_amp=0.08)
for at, m in [(0.35, 72), (1.9, 76)]:
    place(music, pluck(midi(m), 1.6, 0.05), at, 0.2)
# TECTSOFT arrives (3.1): the arpeggio starts; the journey line draws.
section(3.1, 7.6, arp=True, pad_amp=0.08)
# How TECTSOFT works (7.6–34.0): a light pulse; fuller from Build on.
section(7.6, 20.3, arp=True, drums=True, bass_on=True, pad_amp=0.09)
section(20.3, 34.0, arp=True, drums=True, bass_on=True, pad_amp=0.1)
# "From idea to impact" (34.0) and the end card (36.0): resolve on C major and let it ring.
place(music, strings([midi(m) for m in [48, 55, 60, 64]], 2.2, amp=0.12, a=0.2, r=0.8, bright=6, vib=0.002), 34.0)
place(music, strings([midi(m) for m in [36, 48, 55, 60, 64, 67, 72]], 7.0, amp=0.14, a=0.15, r=3.5, bright=6, vib=0.002), 36.0)
for k, m in enumerate([72, 76, 79, 84]):
    place(music, pluck(midi(m), 2.4, 0.045), 36.0 + k * 0.12, -0.3 + 0.2 * k)
place(music, kick(0.25), 36.0)

music = np.stack([reverb(music[0], 2.6, 0.32), reverb(music[1], 2.6, 0.32)])
duck = np.ones(N)
t = t_arr(N)
for s, d in VOICE:
    a0, a1 = s - 0.12, s + d + 0.05
    g = np.clip(np.minimum((t - a0) / 0.09, (a1 + 0.25 - t) / 0.25), 0, 1)
    duck = np.minimum(duck, 1 - 0.5 * g)
music *= duck
music *= np.clip((DUR - t) / 2.0, 0, 1)

sfx = np.zeros((2, N))
# Beat changes: the quiet airy glass sweep (never a whoosh). Cues match compositions/story.html.
for i, c in enumerate([3.0, 7.5, 14.0, 20.4, 25.0, 29.8, 34.05, 36.0]):
    place(sfx, glass_sweep(0.7, 0.08, up=i % 2 == 0), c - 0.42, -0.3 if i % 2 else 0.3)
# Journey stops, stage cards, roadmap, launch checks, users, loop stops: soft pops.
for k in range(7):
    place(sfx, pop(0.045), 4.3 + k * 0.2, -0.6 + 0.2 * k)
for at in (8.2, 9.85, 11.4, 14.4):
    place(sfx, pop(0.07), at, 0.1)
for i in range(6):  # questions fly into the roadmap
    place(sfx, glass_sweep(0.35, 0.03, up=True), 15.8 + i * 0.1, 0.2)
for i in range(6):  # bars draw
    place(sfx, pop(0.05), 16.6 + i * 0.22, -0.2 + 0.08 * i)
for at in (25.4, 25.72, 26.04, 26.36, 26.68):  # launch checklist ticks
    place(sfx, stab([midi(84), midi(88)], 0.045), at + 0.2, 0.2)
for at in (27.4, 30.07, 31.0, 31.9):
    place(sfx, pop(0.08), at, 0.15)
# Keyboard: one click per character. Must match TYPE_AT / GAPS in compositions/endcard.html.
TYPE_AT = 36.0 + 3.1
TYPE_GAPS = [0.09, 0.07, 0.1, 0.08, 0.11, 0.07, 0.09, 0.13, 0.08, 0.07, 0.1, 0.08]
k = TYPE_AT
for g in TYPE_GAPS:
    place(sfx, key_click(rng.uniform(0.11, 0.14)), k, rng.uniform(-0.15, 0.15))
    k += g
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


write(os.path.join(ROOT, "assets/music/score.wav"), music, -4.0)
write(os.path.join(ROOT, "assets/sfx/sfx.wav"), sfx, -6.0)
