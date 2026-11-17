"""Original dramatic score + sound effects for the film, synthesised from scratch and cued from timeline.json.

Deterministic (seeded). No samples, no third-party music. Writes:
  assets/music/score.wav  (music bed, voice ducking baked in)
  assets/sfx/sfx.wav      (whooshes, pen scratch, paper slaps)

Run:  ~/.venvs/kokoro/bin/python scripts/score.py
"""

import os
import wave

import numpy as np

import json  # noqa: E402
import re  # noqa: E402

SR = 48000
rng = np.random.default_rng(20261112)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Everything is cued from timeline.json (written by scripts/layout.py).
TL = json.load(open(os.path.join(ROOT, "timeline.json")))
DUR = TL["total"]
N = int(SR * DUR)
ST, DR = TL["starts"], TL["durs"]
SC = {s["id"]: s for s in TL["scenes"]}
VOICE = [(ST[i], DR[i]) for i in ST]
IMPACT = TL["impact"]
END_HIT = SC["endcard"]["start"]

# Self-check: the ducking map must match the narration placed in index.html.
_html = open(os.path.join(ROOT, "index.html")).read()
_placed = [(float(s), float(d)) for s, d in re.findall(r'id="vo-\w+"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', _html)]
assert sorted(_placed) == sorted(VOICE), "index.html narration differs from timeline.json — rerun scripts/layout.py"


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
PROG = ["Dm", "Bb", "F", "C"]
BEAT = 0.5  # 120 bpm
music = np.zeros((2, N))
cuts = [s["start"] for s in TL["scenes"][1:]]

# --- Opening 0–8.9: the long thought. Drone, heartbeat; options pile up; a short silence.
place(music, strings([midi(D2), midi(A2)], 9.2, amp=0.22, a=2.5, r=1.0, bright=8), 0.0)
place(music, strings([midi(62), midi(65)], 6.0, amp=0.07, a=3.0, r=1.5), 0.4, -0.3)
for k, at in enumerate(np.arange(0.5, 6.0, 1.2)):
    place(music, tom(0.5, 90, 50, 0.18 + 0.03 * k), at)
    place(music, tom(0.5, 85, 48, (0.18 + 0.03 * k) * 0.6), at + 0.24)
opt = SC["options"]["start"]
place(music, strings([midi(Bb1 + 12), midi(D2 + 12), midi(51)], 2.2, amp=0.16, a=0.3, r=0.25, bright=10), opt)
tt, step = opt, 0.25
while tt < opt + 2.05:
    place(music, tick(0.1), tt, rng.uniform(-0.6, 0.6))
    tt += step
    step = max(0.09, step * 0.9)
place(music, noise_riser(1.95, 0.2), opt + 0.05)

# --- Ideas + path (city start → just before the impact): a steady 120 bpm pulse under the voice.
body0 = SC["city"]["start"]
place(music, boom(2.6, 55, 30, 0.45), body0)
place(music, strings([midi(81), midi(86)], 3.4, amp=0.05, a=0.8, r=1.0, bright=4), body0, 0.3)
body1 = IMPACT - 0.9
path0 = SC["path"]["start"]
bar, at = 0, body0 + 1.0
while at < body1 - 0.1:
    name = PROG[bar % 4]
    seg = min(2.0, body1 - at)
    place(music, strings([midi(m) for m in CHORDS[name]], seg + 0.25, amp=0.15, a=0.4, r=0.4, bright=8), at)
    for b8 in range(8):
        tb = at + b8 * BEAT / 2
        if tb >= body1 - 0.1:
            break
        note = CHORDS[name][0] + (12 if b8 % 2 else 0) + (7 if b8 in (3, 7) else 0)
        place(music, stab([midi(note)], 0.07), tb, 0.25 if b8 % 2 else -0.25)
    for b in range(4):  # kick on 1 and 3; every beat once we reach the path
        tb = at + b * BEAT
        if tb >= body1 - 0.1:
            break
        if b % 2 == 0 or tb >= path0:
            place(music, tom(0.5, 120, 60, 0.3 if b == 0 else 0.2), tb)
    bar += 1
    at += 2.0
# riser out of the path into the silence
place(music, noise_riser(2.6, 0.22), body1 - 2.6)
# silence, then a reverse swell into the hit
place(music, noise_riser(0.45, 0.25, lo0=150, hi1=6000), IMPACT - 0.45)

# --- Impact: "Start with a conversation."
place(music, braam(D2, 3.4, 0.5), IMPACT)
place(music, boom(3.0, 60, 28, 0.9), IMPACT)
crash = fft_filter(rng.standard_normal(int(2.5 * SR)), lo=3000, hi=12000) * np.exp(-t_arr(int(2.5 * SR)) * 2.2) * 0.12
place(music, crash, IMPACT, -0.2)
place(music, crash * 0.9, IMPACT + 0.01, 0.2)

# --- Build (impact → close): full ostinato + drums.
lift0 = SC["close"]["start"]
at, bar = IMPACT, 0
while at < lift0 - 0.05:
    name = PROG[bar % 4]
    seg = min(2.0, lift0 - at)
    place(music, strings([midi(m) for m in CHORDS[name]], seg + 0.25, amp=0.2, a=0.25, r=0.4, bright=9), at)
    for b8 in range(8):
        tb = at + b8 * BEAT / 2
        if tb >= lift0:
            break
        note = CHORDS[name][0] + (12 if b8 % 2 else 0) + (7 if b8 in (3, 7) else 0)
        place(music, stab([midi(note)], 0.09), tb, 0.25 if b8 % 2 else -0.25)
        if b8 % 2 == 0 and at >= SC["process"]["start"]:
            strong = b8 == 0
            place(music, tom(0.6, 130 if strong else 110, 62, 0.42 if strong else 0.25), tb)
            place(music, tom(0.4, 180, 95, 0.16), tb + BEAT / 2, 0.3)
            place(music, tick(0.06), tb + BEAT / 4, -0.4)
    bar += 1
    at += 2.0

# --- Lift (close): drums out, strings climb, riser into the end card.
ln = END_HIT - lift0
place(music, strings([midi(m) for m in [53, 57, 60, 65]], ln / 2 + 0.2, amp=0.2, a=0.6, r=0.3), lift0)
place(music, strings([midi(m) for m in [55, 60, 64, 67]], ln / 2 + 0.2, amp=0.22, a=0.3, r=0.4), lift0 + ln / 2)
place(music, strings([midi(74), midi(77)], ln, amp=0.06, a=1.5, r=0.3, bright=5), lift0, 0.3)
for b in range(int(ln / BEAT)):
    place(music, tom(0.5, 95, 52, 0.2), lift0 + 0.1 + b * BEAT)
place(music, noise_riser(1.5, 0.2), END_HIT - 1.5)

# --- End card: final hit, warm F major that rings out.
place(music, boom(3.2, 60, 30, 0.8), END_HIT)
place(music, braam(F2, 3.2, 0.32), END_HIT)
place(music, strings([midi(m) for m in [41, 53, 57, 60, 65, 69]], DUR - END_HIT, amp=0.26, a=0.05, r=1.6, bright=10), END_HIT)

music = np.stack([reverb(music[0]), reverb(music[1])])

# Duck the bed under each narration line (90 ms attack, 250 ms release).
duck = np.ones(N)
t = t_arr(N)
for s, d in VOICE:
    a0, a1 = s - 0.12, s + d + 0.05
    g = np.clip(np.minimum((t - a0) / 0.09, (a1 + 0.25 - t) / 0.25), 0, 1)
    duck = np.minimum(duck, 1 - 0.55 * g)
music *= duck
music *= np.clip((DUR - t) / 1.4, 0, 1)

sfx = np.zeros((2, N))
for c in cuts:
    if abs(c - IMPACT) < 0.05:
        continue  # the impact carries its own hit
    place(sfx, whoosh(0.75, 0.3), c - 0.42, rng.uniform(-0.5, 0.5))  # peak lands on the cut
# pen on paper: notebook write-ons, every "Start here" in red pen, "start here" in the close
pen = [(0.7, 0.9), (1.75, 0.8), (2.75, 0.5), (3.3, 0.55), (4.35, 0.9), (SC["close"]["start"] + 0.9, 0.5)]
for x in "abcde":
    pen.append((ST[x + "3"] + 0.0, 0.45))
for at, d in pen:
    place(sfx, scratch(d, 0.06), at, -0.2)
for k in range(9):  # sticky notes slapping on (process.html T.slap0/T.slapGap)
    place(sfx, slap(0.11), SC["process"]["start"] + 0.05 + k * 0.09, rng.uniform(-0.6, 0.6))
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
