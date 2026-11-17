"""Original dramatic score + sound effects for the trailer, synthesised from scratch.

Deterministic (seeded). No samples, no third-party music. Writes:
  assets/music/score.wav  (music bed, voice ducking baked in)
  assets/sfx/sfx.wav      (whooshes, pen scratch, paper slaps)

Run:  ~/.venvs/kokoro/bin/python scripts/score.py
"""

import os
import wave

import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(20261112)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Narration windows (absolute seconds) — must match index.html <audio> starts + durations.
VOICE = [(1.0, 2.39), (4.0, 1.86), (6.3, 2.37), (9.4, 1.83), (12.25, 1.79), (14.5, 8.66), (23.7, 3.22), (27.6, 1.15)]
CUTS_WHOOSH = [6.1, 9.2, 14.5, 18.05, 23.2]

# Self-check: the ducking map must match the narration placed in index.html.
import re  # noqa: E402

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


D2, F2, A2, Bb1, C2 = 38, 41, 45, 34, 36
CHORDS = {  # midi triads, low voicing
    "Dm": [50, 53, 57, 62],
    "Bb": [46, 50, 53, 58],
    "F": [48, 53, 57, 60],
    "C": [48, 52, 55, 60],
}

music = np.zeros((2, N))

# --- A: 0–9.2  — the long thought. Low drone, slow swell, a heartbeat.
place(music, strings([midi(D2), midi(A2)], 9.6, amp=0.22, a=2.5, r=1.2, bright=8), 0.0)
place(music, strings([midi(62), midi(65)], 6.0, amp=0.07, a=3.0, r=1.5), 0.4, -0.3)
for k, at in enumerate(np.arange(0.5, 9.0, 1.2)):  # heartbeat pair, growing
    g = 0.18 + 0.03 * k
    place(music, tom(0.5, 90, 50, g), at)
    place(music, tom(0.5, 85, 48, g * 0.6), at + 0.24)
# 6.1 — the idea lands: soft boom + high shimmer
place(music, boom(2.6, 55, 30, 0.45), 6.1)
place(music, strings([midi(81), midi(86)], 3.4, amp=0.05, a=0.8, r=1.0, bright=4), 6.1, 0.3)

# --- Tension: 9.2–11.3 — options pile up. Ticks accelerate, riser, then silence.
place(music, strings([midi(Bb1 + 12), midi(D2 + 12), midi(51)], 2.3, amp=0.16, a=0.3, r=0.25, bright=10), 9.2)
tt = 9.2
step = 0.25
while tt < 11.25:
    place(music, tick(0.1), tt, rng.uniform(-0.6, 0.6))
    tt += step
    step = max(0.09, step * 0.9)
place(music, noise_riser(2.05, 0.22), 9.25)
# silence 11.3–11.55, then a reverse swell into the hit
rev = noise_riser(0.45, 0.25, lo0=150, hi1=6000)
place(music, rev, 11.55)

# --- Impact: 12.0
place(music, braam(D2, 3.4, 0.5), 12.0)
place(music, boom(3.0, 60, 28, 0.9), 12.0)
crash = fft_filter(rng.standard_normal(int(2.5 * SR)), lo=3000, hi=12000) * np.exp(-t_arr(int(2.5 * SR)) * 2.2) * 0.12
place(music, crash, 12.0, -0.2)
place(music, crash[::-1][::-1] * 0.9, 12.01, 0.2)

# --- B: 12–23.2 — the build. 120 bpm string ostinato, chords per bar, toms.
BEAT = 0.5
prog = [("Dm", 12.0), ("Bb", 14.0), ("F", 16.0), ("C", 18.0), ("Dm", 20.0), ("Bb", 22.0)]
for name, at in prog:
    place(music, strings([midi(m) for m in CHORDS[name]], 2.25, amp=0.2, a=0.25, r=0.4, bright=9), at)
    root = CHORDS[name][0]
    for b8 in range(8):  # eighth-note ostinato, octave figure
        note = root + (12 if b8 % 2 else 0) + (7 if b8 in (3, 7) else 0)
        place(music, stab([midi(note)], 0.09), at + b8 * BEAT / 2 + 0.0, 0.25 if b8 % 2 else -0.25)
for b in range(int((23.2 - 14.5) / BEAT)):
    at = 14.5 + b * BEAT
    if at >= 23.2:
        break
    strong = b % 4 == 0
    place(music, tom(0.6, 130 if strong else 110, 62, 0.42 if strong else 0.25), at)
    if at >= 18.0:  # full drums from the MVP beat
        place(music, tom(0.4, 180, 95, 0.18), at + BEAT / 2, 0.3)
        place(music, tick(0.06), at + BEAT / 4, -0.4)
place(music, boom(1.8, 58, 34, 0.35), 18.05)

# --- Lift: 23.2–26.8 — drums out, strings climb, riser into the end card.
place(music, strings([midi(m) for m in [53, 57, 60, 65]], 1.9, amp=0.2, a=0.6, r=0.3), 23.2)
place(music, strings([midi(m) for m in [55, 60, 64, 67]], 1.9, amp=0.22, a=0.3, r=0.4), 25.0)
place(music, strings([midi(74), midi(77)], 3.6, amp=0.06, a=1.5, r=0.3, bright=5), 23.2, 0.3)
for b in range(7):
    place(music, tom(0.5, 95, 52, 0.2), 23.3 + b * BEAT)
place(music, noise_riser(1.5, 0.2), 25.3)

# --- End: 26.9 — final hit, warm F major that rings out.
place(music, boom(3.2, 60, 30, 0.8), 26.9)
place(music, braam(F2, 3.2, 0.32), 26.9)
place(music, strings([midi(m) for m in [41, 53, 57, 60, 65, 69]], 3.2, amp=0.26, a=0.05, r=1.6, bright=10), 26.9)

music = np.stack([reverb(music[0]), reverb(music[1])])

# Duck the bed ~7 dB under each narration line (90 ms attack, 250 ms release).
duck = np.ones(N)
t = t_arr(N)
for s, d in VOICE:
    a0, a1 = s - 0.12, s + d + 0.05
    g = np.clip(np.minimum((t - a0) / 0.09, (a1 + 0.25 - t) / 0.25), 0, 1)
    duck = np.minimum(duck, 1 - 0.55 * g)
music *= duck
# final fade 28.6–30
fade = np.clip((30.0 - t) / 1.4, 0, 1)
music *= fade

sfx = np.zeros((2, N))
for c in CUTS_WHOOSH:
    w = whoosh(0.75, 0.32)
    place(sfx, w, c - 0.42, rng.uniform(-0.5, 0.5))  # peak lands on the cut
# pen scratches in the notebook (match the handwriting write-ons in compositions/notebook.html)
for at, d in [(0.7, 0.9), (1.75, 0.8), (2.75, 0.5), (3.3, 0.55), (4.35, 0.9), (24.1, 0.5)]:
    place(sfx, scratch(d, 0.06), at, -0.2)
# sticky notes slapping on (compositions/process.html)
for k in range(9):
    place(sfx, slap(0.11), 14.62 + k * 0.13, rng.uniform(-0.6, 0.6))
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
