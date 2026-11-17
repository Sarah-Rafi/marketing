"""Lay out the film from the narration: line starts, scene windows, caption groups.

Reads scripts/narration.tsv + assets/voice2/<id>.wav (+ .words.json).
Writes timeline.json, index.html and compositions/captions.html.
Run: python3 scripts/layout.py   (then scripts/score.py for the audio bed)
"""

import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)  # noqa: E731

lines = [l.rstrip("\n").split("\t") for l in open(P("scripts/narration.tsv")) if l.strip()]
text = {i: t for i, t in lines}
order = [i for i, _ in lines]


def dur(i):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", P(f"assets/voice2/{i}.wav")])
    return round(float(out), 3)


def words(i):
    return json.load(open(P(f"assets/voice2/{i}.words.json")))


D = {i: dur(i) for i in order}
S = {}

# Gap (s) before each line; the first line of each section gets a longer breath.
GAP = {"o1": 1.0, "o2": None, "o3": None, "o4": None, "a1": 1.0, "b1": 1.1, "c1": 1.1, "d1": 1.1, "e1": 1.1, "p1": 1.2, "z1": 1.3, "z2": None, "z3": None, "z4": 0.7}
FIXED = {"o2": 4.0, "o3": 6.4, "o4": 9.2}  # opening keeps the 30 s cut's notebook/options timing
t = 0.0
for i in order:
    if i in FIXED:
        t = FIXED[i]
    elif i in ("z2", "z3"):
        pass  # placed below from the impact / z2
    else:
        g = GAP.get(i)
        if g is None:
            g = 0.5 if i[0] == "p" else 0.4
        t = t + g
    if i == "z2":
        impact = S["z1"] + [w for w in words("z1") if w["text"].lower().startswith("start")][0]["start"] - 0.03
        t = impact + 2.3
    if i == "z3":
        t = S["z2"] + D["z2"] + 2.6
    S[i] = round(t, 3)
    t = S[i] + D[i]

impact = round(S["z1"] + [w for w in words("z1") if w["text"].lower().startswith("start")][0]["start"] - 0.03, 3)


def sec(prefix):
    ids = [i for i in order if i.startswith(prefix)]
    return S[ids[0]], S[ids[-1]] + D[ids[-1]]


scenes = []
add = lambda sid, start, end, kind="graphics": scenes.append({"id": sid, "start": round(start, 3), "dur": round(end - start, 3), "kind": kind})  # noqa: E731
add("notebook", 0, 6.1)
add("options", 6.1, 8.9)
idea_ids = "abcde"
first_idea = S["a1"] - 0.6
add("city", 8.9, first_idea)
for k, x in enumerate(idea_ids):
    s0, s1 = sec(x)
    nxt = S[idea_ids[k + 1] + "1"] - 0.6 if k < 4 else S["p1"] - 0.5
    add("idea-" + x, s0 - 0.6, nxt)
add("path", S["p1"] - 0.5, impact)
proc0 = S["z2"] - 0.1
add("title", impact, proc0)
add("process", proc0, S["z3"] - 0.5)
add("close", S["z3"] - 0.5, S["z3"] + 3.2)
end0 = S["z3"] + 3.2
S["z4"] = round(end0 + 0.7, 3)
add("endcard", end0, end0 + 4.0)
TOTAL = round(end0 + 4.0, 3)

# Caption rail: only lines that are not already written on screen as they are spoken.
RAIL = ["o1", "o2", "o3", "o4", "z1", "z2", "z3"]
BREAK_AFTER = {"o1": [4], "o4": [5], "z3": [3]}  # word index (0-based) to break after; replaces punctuation breaks for that line
groups = []
for i in RAIL:
    w = words(i)
    script_words = text[i].replace("—", " ").split()
    # map script words onto transcript words by position (counts can differ by a split/merge)
    ratio = len(w) / len(script_words)
    tw = lambda k: w[min(len(w) - 1, int(k * ratio))]  # noqa: E731
    phrase, k0 = [], 0
    for k, sw in enumerate(script_words):
        phrase.append(sw)
        last = k == len(script_words) - 1
        end_phrase = last or (k in BREAK_AFTER[i] if i in BREAK_AFTER else bool(re.search(r"[,.?!:]$", sw)))
        if end_phrase:
            g0 = S[i] + tw(k0)["start"] - 0.05
            g1 = S[i] + (tw(k)["end"] if k < len(script_words) - 1 else D[i]) + 0.05
            groups.append([round(g0, 2), round(g1, 2), " ".join(phrase)])
            phrase, k0 = [], k + 1
# drop the embedded "Start with a conversation." (it is the title card)
groups = [g for g in groups if not (g[0] >= impact - 0.1 and g[2].startswith("Start with"))]
# merge one-word stragglers into the previous group of the same line, close gaps, keep one group visible
merged = []
for g in groups:
    if merged and len(g[2].split()) == 1 and g[0] - merged[-1][1] < 0.3:
        merged[-1][1], merged[-1][2] = g[1], merged[-1][2] + " " + g[2]
    else:
        merged.append(g)
for a, b in zip(merged, merged[1:]):
    if b[0] - a[1] < 0.25:
        a[1] = b[0]
for g in merged:
    g[0] = max(g[0], 0.1)

timeline = {"total": TOTAL, "impact": impact, "starts": S, "durs": D, "scenes": scenes, "captions": merged}
json.dump(timeline, open(P("timeline.json"), "w"), indent=1)

# ---------- index.html ----------
hosts = "\n".join(
    f'      <div id="{s["id"]}" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html" '
    f'data-start="{s["start"]}" data-duration="{s["dur"]}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>'
    for s in scenes
)
# keep levels set by `npx hyperframes normalize-audio --write` across re-layouts
old = open(P("index.html")).read() if os.path.exists(P("index.html")) else ""
vol = dict(re.findall(r'<audio id="(vo-\w+|music|sfx)"[^>]*?data-volume="([\d.]+)"', old))
vattr = lambda k: f' data-volume="{vol[k]}"' if k in vol else ""  # noqa: E731
audios = "\n".join(
    f'      <audio id="vo-{i}" src="assets/voice2/{i}.wav" data-start="{S[i]}" data-duration="{D[i]}"{vattr("vo-" + i)} data-track-index="10"></audio>' for i in order
)
tpl = open(P("scripts/index.template.html")).read()
html = tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{HOSTS}}", hosts).replace("{{AUDIOS}}", audios)
html = html.replace("{{GRAIN_STEPS}}", str(int(TOTAL * 12)))
for k in ("music", "sfx"):
    if k in vol:
        html = re.sub(rf'(<audio id="{k}"[^>]*?data-volume=")[\d.]+"', rf'\g<1>{vol[k]}"', html)
open(P("index.html"), "w").write(html)

# ---------- captions.html ----------
divs = "\n".join(f'    <div id="cap-{n + 1}" class="cap"><span>{g[2].replace(chr(39), "&rsquo;")}</span></div>' for n, g in enumerate(merged))
gl = ",\n      ".join(f"[{g[0]}, {g[1]}]" for g in merged)
cap = open(P("scripts/captions.template.html")).read().replace("{{DIVS}}", divs).replace("{{GROUPS}}", gl)
open(P("compositions/captions.html"), "w").write(cap)

# self-check: one caption group visible at a time, scenes tile the film without gaps
assert all(b[0] >= a[1] - 1e-6 for a, b in zip(merged, merged[1:])), "overlapping caption groups"
assert all(abs(a["start"] + a["dur"] - b["start"]) < 1e-3 for a, b in zip(scenes, scenes[1:])), "scene gap/overlap"
print(f"total {TOTAL}s · impact {impact}s · {len(merged)} caption groups")
for s in scenes:
    print(f'  {s["id"]:9s} {s["start"]:7.2f} +{s["dur"]:.2f}')
