"""Build compositions/captions.html and the .srt from the voice word timings. Run: python3 scripts/captions.py"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, "index.html")).read()
START = {v: float(s) for v, s in re.findall(r'id="vo-(\w+)"[^>]*data-start="([\d.]+)"', html)}
# (voice, word tokens, text, on-screen title so not in the rail)
G = [
    ("a1", 10, "Are you a psychiatrist, a therapist, or a clinic owner,", True), ("a1", 9, "here to make a real difference in mental health?", True),
    ("a2", 5, "But you keep getting stuck.", True),
    ("a3", 7, "And the problems keep coming your way."),
    ("d1", 5, "TECTSOFT is here to help.", True),
    ("d2", 4, "With one connected space,", True), ("d2", 7, "care doesn’t end when the session does.", True),
    ("v5", 5, "Imagine your own practice app."),
    ("v6a", 5, "Patients can complete daily check-ins,"),
    ("v6b", 7, "build healthy habits, and record their progress,"),
    ("v6c", 8, "and stay connected with the resources you provide."),
    ("v7", 6, "While you get a clearer view"), ("v7", 5, "of their journey between appointments."),
    ("v8", 5, "Less time managing scattered information."), ("v8", 5, "More time focusing on people."),
    ("v9", 5, "Technology that supports your practice,"), ("v9", 7, "while keeping professional care at the centre."),
    ("v10", 9, "At TECTSOFT, we turn your vision into digital solutions,"), ("v10", 7, "built around your practice and your patients."),
    ("v11", 8, "Let’s build a more connected care experience, together."),
]
PSY = set()  # one narrator throughout; no speaker mark
words, pos, out = {}, {}, []
for g in G:
    v, n, text = g[:3]
    w = words.setdefault(v, json.load(open(os.path.join(ROOT, f"assets/voice2/{v}.words.json"))))
    i = pos.get(v, 0)
    pos[v] = i + n
    out.append((v, round(START[v] + w[i]["start"], 2), round(START[v] + w[i + n - 1]["end"] + 0.1, 2), text, len(g) > 3))
for v, n in pos.items():
    assert n == len(words[v]), f"{v}: grouped {n} of {len(words[v])} words"
# no overlaps in the rail
for a, b in zip(out, out[1:]):
    assert a[2] <= b[1] + 0.11, (a, b)
rail = [o for o in out if not o[4]]
divs = "\n".join(f'    <div id="cap-{k + 1}" class="cap{" a" if o[0] in PSY else ""}"><span>{o[3]}</span></div>' for k, o in enumerate(rail))
groups = ",\n".join(f"      [{o[1]}, {min(o[2], (rail[k + 1][1] if k + 1 < len(rail) else 99))}]" for k, o in enumerate(rail))
cap = open(os.path.join(ROOT, "compositions/captions.html")).read()
cap = re.sub(r'(<div id="root"[^>]*>\n).*?(\n  </div>\n  <script>)', lambda m: m.group(1) + "    <!-- Verbatim speech. Lines that appear on screen as titles while spoken are not in the rail. -->\n" + divs + m.group(2), cap, flags=re.S)
cap = re.sub(r"const groups = \[\n.*?\n    \];", "const groups = [\n" + groups + ",\n    ];", cap, flags=re.S)
cap = cap.replace("/* Speaker marks: friend A wears sage, friend B wears sand; the narrator has none. */", "/* Speaker mark: the therapist wears sage; the narrator has none. */")
cap = re.sub(r"\n    \.cap\.b span \{\n.*?\n    \}", "", cap, flags=re.S)
open(os.path.join(ROOT, "compositions/captions.html"), "w").write(cap)
ts = lambda t: f"{int(t // 3600):02}:{int(t % 3600 // 60):02}:{int(t % 60):02},{int(round(t % 1 * 1000)):03}"
srt = "\n".join(f"{k + 1}\n{ts(o[1])} --> {ts(o[2])}\n{o[3]}\n" for k, o in enumerate(out))
open(os.path.join(ROOT, "..", "..", "TectSoft_MentalHealth_CareBeyondTheSession_Captions.srt"), "w").write(srt)
print(len(rail), "rail groups,", len(out), "srt cues")
