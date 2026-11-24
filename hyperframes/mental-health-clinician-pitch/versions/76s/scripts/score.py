"""Original calm score + sound effects for the mental-health pitch (therapist version), synthesised from scratch.

Deterministic (seeded). No samples, no third-party music. Writes:
  assets/music/score.wav  (music bed, voice ducking baked in)
  assets/sfx/sfx.wav      (soft whooshes, pen, typing, taps, a phone buzz)

Run:  ~/.venvs/kokoro/bin/python scripts/score.py
"""

import os
import re
import wave

import numpy as np

SR = 48000
DUR = 76.2
N = int(SR * DUR)
rng = np.random.default_rng(20261114)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Speech windows (absolute seconds) — must match index.html <audio> starts + durations.
VOICE = [(0.5, 3.2), (4.0, 3.95), (8.6, 4.54), (13.4, 2.05), (16.2, 3.41), (20.2, 6.85), (27.4, 4.59), (32.5, 1.17), (36.0, 4.5), (41.2, 4.22), (46.0, 4.89), (51.2, 4.54), (56.4, 2.92), (59.6, 4.07), (64.4, 7.08)]
_html = open(os.path.join(ROOT, "index.html")).read()
_placed = [(float(s), float(d)) for s, d in re.findall(r'id="vo-\w+"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', _html)]
assert _placed == VOICE, f"VOICE {VOICE} != index.html speech {_placed}"

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




def pluck(f, dur=2.5, amp=0.08):
    """Soft felt-piano note: harmonics that die away faster the higher they are."""
    n = int(dur * SR)
    t = t_arr(n)
    x = np.zeros(n)
    for k in range(1, 9):
        if f * k > 8000:
            break
        x += np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) / k ** 1.6 * np.exp(-t * (1.6 + 1.1 * k))
    return amp * x * np.minimum(t / 0.008, 1)


def tap(amp=0.08):
    n = int(0.06 * SR)
    t = t_arr(n)
    return amp * fft_filter(rng.standard_normal(n), lo=1500, hi=6000) * np.exp(-t * 90)


def buzz(dur=0.5, amp=0.12):
    n = int(dur * SR)
    t = t_arr(n)
    x = np.sin(2 * np.pi * 160 * t) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t)))
    return amp * fft_filter(x, hi=900) * env_adsr(n, 0.02, 0.08, 1)


BEAT = 60 / 76
music = np.zeros((2, N))
F = lambda *ms: [midi(m) for m in ms]

# --- Night: 0–32.2. A low, patient pad under the therapist's words; a few lonely piano notes between lines.
place(music, strings(F(38, 45, 53, 64), 11.2, amp=0.14, a=2.0, r=1.5, bright=6), 0.0)
place(music, strings(F(34, 46, 53, 62), 11.0, amp=0.12, a=1.5, r=1.6, bright=6), 10.4)
place(music, strings(F(36, 43, 52, 60), 11.2, amp=0.12, a=1.5, r=1.6, bright=6), 20.6)
for at, m in [(0.2, 69), (3.8, 72), (8.2, 69), (13.2, 67), (15.8, 65), (19.8, 64), (27.1, 62), (31.0, 60)]:
    place(music, pluck(midi(m), 3.0, 0.07), at, 0.2)
# 4 a.m.: the pad thins, one high note.
place(music, strings(F(81), 4.0, amp=0.03, a=0.5, r=1.2, bright=3), 20.9, 0.3)
# --- Dawn: 32.2. The harmony opens to F major as the sun comes up ("Now there is.").
place(music, noise_riser(1.0, 0.08, lo0=200, hi1=5000), 31.25)
place(music, strings(F(41, 53, 57, 60, 65, 69), 4.0, amp=0.22, a=0.4, r=1.4, bright=8), 32.25)
place(music, boom(2.4, 50, 30, 0.25), 32.25)
place(music, pluck(midi(77), 3.0, 0.08), 32.7, 0.3)
place(music, pluck(midi(81), 3.0, 0.06), 32.95, -0.3)

# --- The app: 35.8–71.8. Gentle 76 bpm piano arpeggios, F – C – Dm – Bb, a pad per bar.
prog = [(41, [53, 57, 60, 65]), (36, [52, 55, 60, 64]), (38, [53, 57, 62, 65]), (34, [50, 53, 58, 62])]
END = 71.8
at = 35.8
bar = 0
while at < END - 1e-6:
    root, notes = prog[bar % 4]
    place(music, strings(F(root, root + 12) + F(*notes[:3]), 4 * BEAT + 0.3, amp=0.12, a=0.5, r=0.6, bright=6), at)
    pattern = [0, 1, 2, 3, 2, 1, 2, 3]
    for e, ix in enumerate(pattern):
        t0 = at + e * BEAT / 2
        if t0 >= END:
            break
        place(music, pluck(midi(notes[ix] + 12), 1.6, 0.055 if e % 2 else 0.07), t0, -0.25 if e % 2 else 0.25)
    if at >= 38.0:
        for b in range(4):
            place(music, tick(0.025), at + b * BEAT + BEAT / 2, 0.4)
    bar += 1
    at += 4 * BEAT
# The city warms up (66.8–71.8): a slow swell into the end card.
place(music, strings(F(53, 57, 60, 65, 72), 5.0, amp=0.1, a=3.2, r=0.4, bright=6), 66.8)
# --- End: 71.8. Resolve on F major and let it ring.
place(music, strings(F(29, 41, 53, 57, 60, 65, 69), 4.4, amp=0.24, a=0.3, r=2.2, bright=8), END)
for k, m in enumerate([65, 69, 72, 77]):
    place(music, pluck(midi(m), 3.5, 0.07), END + 0.05 + k * 0.18, (-0.3, 0.3)[k % 2])

music = np.stack([reverb(music[0], 3.0, 0.38), reverb(music[1], 3.0, 0.38)])
duck = np.ones(N)
t = t_arr(N)
for s, d in VOICE:
    a0, a1 = s - 0.15, s + d + 0.05
    g = np.clip(np.minimum((t - a0) / 0.12, (a1 + 0.35 - t) / 0.35), 0, 1)
    duck = np.minimum(duck, 1 - 0.55 * g)
music *= duck
music *= np.clip((DUR - t) / 2.5, 0, 1)

sfx = np.zeros((2, N))
for c in [8.4, 16.0, 20.0, 27.2, 32.2, 35.8, 41.0, 45.8, 51.0, 56.2, 59.4, 64.2, 71.8]:
    place(sfx, whoosh(rng.uniform(0.7, 0.9), 0.16), c - 0.42, rng.uniform(-0.5, 0.5))
place(sfx, buzz(0.5, 0.12), 20.9, 0.1)  # 4 a.m.: the phone goes off
for at in [22.45, 24.3, 24.9, 25.5]:  # messages keep coming
    place(sfx, tap(0.06), at, 0.1)
for at in [38.75, 39.15, 39.75]:  # check-in sliders set
    place(sfx, tap(0.07), at, 0.2)
for at in [51.75, 52.55]:  # alerts land
    place(sfx, tap(0.07), at, -0.2)
place(sfx, tap(0.09), 55.15, 0.2)  # crisis support tapped
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
