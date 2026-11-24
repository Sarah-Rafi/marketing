"""Build compositions/captions.html and the .srt from the voice word timings. Run: python3 scripts/captions.py"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, "index.html")).read()
START = {v: float(s) for v, s in re.findall(r'id="vo-(\w+)"[^>]*data-start="([\d.]+)"', html)}
# (voice, word tokens, text, on-screen title so not in the rail)
G = [
    ("h1", 3, "I’m a psychiatrist.", True), ("h1", 10, "I want to help as many people as I can.", True),
    ("h2", 7, "But there are barriers in my way.", True),
    ("h3", 5, "TECTSOFT is here to help.", True),
    ("t1", 6, "I see each of my patients"), ("t1", 5, "for one hour a week."),
    ("t2", 4, "The other one hundred and sixty-seven hours,"), ("t2", 4, "I’m in the dark."),
    ("t5", 4, "My calendar is full."), ("t5", 5, "New patients wait for weeks."),
    ("t6", 8, "And at 4 a.m., a patient messages me, panicking."), ("t6", 4, "I want to help."), ("t6", 7, "I just can’t be awake for everyone."),
    ("p4", 9, "It’s all too much for one person to manage."),
    ("d1", 3, "With TECTSOFT,"), ("d1", 7, "your care doesn’t stop at the session.", True),
    ("n2", 4, "Your own practice app."), ("n2", 5, "Patients check in every day:"), ("n2", 4, "mood, sleep, and anxiety."),
    ("hb", 5, "Daily nudges build healthy habits:"), ("hb", 6, "journaling, walks, exercise, and better meals."),
    ("n3", 6, "Every exercise you assign is tracked,"), ("n3", 9, "so you see their progress before they walk in."),
    ("n4", 8, "At 4 a.m., AI guides them through the moment,"), ("n4", 6, "with the coping steps you’ve approved."),
    ("n5", 6, "Warning signs reach you right away,"), ("n5", 8, "and crisis support is always one tap away."),
    ("n6", 5, "Even people on your waitlist"), ("n6", 5, "get support while they wait."),
    ("s1", 6, "Now I can help more people,"), ("s1", 8, "and I know how their week really went."),
    ("n7", 4, "Therapist, psychiatrist, or clinic?", True), ("n7", 4, "Reach out to us."), ("n7", 5, "Let’s build your app together,", True), ("n7", 7, "and help more people, every single day."),
]
PSY = {"h1", "h2", "t1", "t2", "t5", "t6", "p4", "s1"}  # the psychiatrist; everything else is the narrator
words, pos, out = {}, {}, []
for g in G:
    v, n, text = g[:3]
    w = words.setdefault(v, json.load(open(os.path.join(ROOT, f"assets/voice/{v}.words.json"))))
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
srt = "\n".join(f"{k + 1}\n{ts(o[1])} --> {ts(o[2])}\n{'Psychiatrist: ' if o[0] in PSY else ''}{o[3]}\n" for k, o in enumerate(out))
open(os.path.join(ROOT, "..", "..", "TectSoft_MentalHealth_Therapist_Pitch_Captions.srt"), "w").write(srt)
print(len(rail), "rail groups,", len(out), "srt cues")
