"""Write compositions/idea-{a..e}.html from timeline.json.

Each idea card: the title, the problem and the fix (narration, verbatim, revealed as spoken),
"Start here" handwritten in red pen, and an illustration that shows the problem, then the fix.
Run after scripts/layout.py.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)  # noqa: E731
T = json.load(open(P("timeline.json")))
S = T["starts"]
text = dict(l.rstrip("\n").split("\t") for l in open(P("scripts/narration.tsv")) if l.strip())
scene = {s["id"]: s for s in T["scenes"]}

CHAT = """
  <rect class="s f" x="40" y="40" width="620" height="600" rx="22"/>
  <line class="s" x1="40" y1="112" x2="660" y2="112"/>
  <text class="t" x="76" y="88">Messages</text>
  <path class="s" d="M596 64 a22 22 0 1 0 22 34 a17 17 0 1 1 -22 -34 z"/>
  <text class="tm" x="430" y="90">11:48 pm</text>
  <g id="{p}-q"><g><rect class="bub" x="76" y="146" width="400" height="66" rx="18"/><text class="t" x="98" y="189">Are you open Sunday?</text></g>
  <g><rect class="bub" x="76" y="228" width="320" height="66" rx="18"/><text class="t" x="98" y="271">Do you deliver?</text></g>
  <g><rect class="bub" x="76" y="310" width="400" height="66" rx="18"/><text class="t" x="98" y="353">Are you open Sunday?</text></g></g>
  <g id="{p}-prob"><g><circle cx="652" cy="48" r="34" fill="#c8372d"/><text class="tb" x="652" y="58" text-anchor="middle">12</text></g></g>
  <g id="{p}-fix"><g><circle cx="652" cy="48" r="34" fill="#f2b35a"/><path d="M636 48 l11 12 l21 -24" fill="none" stroke="#22201c" stroke-width="7" stroke-linecap="round"/></g>
  <g><text class="tm" x="250" y="420">Assistant · instant</text>
  <rect x="236" y="432" width="400" height="124" rx="18" fill="#f2b35a"/><text class="td" x="260" y="482">Yes, 10am to 4pm.</text><text class="td" x="260" y="526">Want me to book you in?</text></g></g>
"""

BOOK = """
  <rect class="s f" x="40" y="40" width="620" height="560" rx="22"/>
  <text class="t" x="76" y="96">Thursday</text><line class="s" x1="40" y1="122" x2="660" y2="122"/>
  <g class="tm"><text x="70" y="186">10:00</text><text x="70" y="276">11:00</text><text x="70" y="366">12:00</text><text x="70" y="456">2:00</text><text x="70" y="546">3:00</text></g>
  <rect class="slot" x="170" y="150" width="460" height="64" rx="10"/><rect class="slot" x="170" y="420" width="460" height="64" rx="10"/>
  <rect x="170" y="240" width="460" height="64" rx="10" fill="rgba(234,226,207,0.3)"/><text class="t" x="194" y="281">Booked</text>
  <g id="{p}-prob"><g><rect x="170" y="330" width="460" height="64" rx="10" fill="none" stroke="#c8372d" stroke-width="4" stroke-dasharray="12 8"/><text class="tr" x="194" y="372">No-show</text></g>
  <g><rect x="170" y="510" width="460" height="64" rx="10" fill="none" stroke="#c8372d" stroke-width="4" stroke-dasharray="12 8"/><text class="tr" x="194" y="552">No-show</text></g></g>
  <g id="{p}-fix"><g><rect x="170" y="330" width="460" height="64" rx="10" fill="#f2b35a"/><text class="td" x="194" y="372">Booked · deposit paid</text></g>
  <g><rect x="170" y="510" width="460" height="64" rx="10" fill="#f2b35a"/><text class="td" x="194" y="552">Booked · deposit paid</text></g>
  <g><rect x="320" y="596" width="370" height="100" rx="18" fill="#1d1b19" stroke="#eae2cf" stroke-width="3"/><text class="t" x="342" y="636">Reminder: Thu 2pm.</text><text class="tm" x="342" y="674">Reply C to confirm</text></g></g>
"""

CREW = """
  <g id="{p}-prob"><g transform="rotate(-7 230 340)"><rect x="70" y="120" width="320" height="430" rx="6" fill="#e9e1cc"/>
  <path d="M100 190 h220 M100 240 h180 M100 290 h240 M100 340 h150 M100 390 h210" stroke="#1d2740" stroke-width="5" stroke-linecap="round"/>
  <path d="M110 450 q40 -30 80 0 t80 0" fill="none" stroke="#1d2740" stroke-width="4"/></g>
  <g><rect class="bub" x="360" y="110" width="320" height="66" rx="18"/><text class="t" x="380" y="153">where's the invoice??</text></g>
  <g><rect class="bub" x="430" y="200" width="150" height="66" rx="18"/><text class="t" x="452" y="243">pics?</text></g>
  <g><rect class="bub" x="390" y="290" width="270" height="66" rx="18"/><text class="t" x="410" y="333">which address?</text></g></g>
  <g id="{p}-fix"><g><rect x="160" y="30" width="380" height="630" rx="40" fill="#121316" stroke="#eae2cf" stroke-width="5"/>
  <line class="s" x1="320" y1="58" x2="380" y2="58"/>
  <text class="t" x="196" y="112">Job 214 · Kitchen</text></g><g>
  <path class="ck" d="M200 160 l9 10 l17 -20"/><text class="t" x="238" y="172">Old units out</text>
  <path class="ck" d="M200 210 l9 10 l17 -20"/><text class="t" x="238" y="222">Worktop fitted</text>
  <path class="ck" d="M200 260 l9 10 l17 -20"/><text class="t" x="238" y="272">Signed off</text></g><g>
  <rect class="s f" x="196" y="300" width="140" height="114" rx="10"/><path class="s" d="M206 396 l34 -36 l26 24 l16 -14 l40 28"/>
  <rect class="s f" x="360" y="300" width="140" height="114" rx="10"/><path class="s" d="M370 396 l30 -30 l30 26 l20 -16 l40 22"/>
  <text class="tm" x="196" y="450">2 photos · on site</text></g><g>
  <rect x="196" y="490" width="304" height="68" rx="12" fill="#f2b35a"/><text class="td" x="218" y="534">Invoice sent ✓</text>
  <text class="tm" x="196" y="612">Offline · syncs later</text></g></g>
"""

STOCK = """
  <rect class="s f" x="40" y="60" width="620" height="300" rx="16"/>
  <g class="grid"><path d="M40 120 h620 M40 180 h620 M40 240 h620 M40 300 h620 M250 60 v300 M460 60 v300"/></g>
  <text class="t" x="66" y="100">Product</text><text class="t" x="270" y="100">Channel</text><text class="t" x="480" y="100">Stock</text>
  <text class="t" x="66" y="160">Ceramic mug</text><text class="t" x="270" y="160">Web store</text>
  <text class="t" x="66" y="220">Ceramic mug</text><text class="t" x="270" y="220">Marketplace</text>
  <text class="t" x="66" y="280">Ceramic mug</text><text class="t" x="270" y="280">Social shop</text>
  <g id="{p}-prob"><text class="tr" x="480" y="160">12</text><text class="tr" x="480" y="220">9</text><text class="tr" x="480" y="280">15 ?</text></g>
  <g id="{p}-fix"><g><text class="ta" x="480" y="160">12</text><text class="ta" x="480" y="220">12</text><text class="ta" x="480" y="280">12</text></g>
  <g><path class="s" d="M350 372 v60" /><path class="s" d="M336 418 l14 16 l14 -16"/></g>
  <g><rect x="110" y="440" width="480" height="200" rx="18" fill="#f2b35a"/>
  <text class="td" x="140" y="494">All channels · in sync</text>
  <text class="td" x="140" y="544">Orders today: 38</text><text class="td" x="140" y="594">Stock left: 12</text></g></g>
"""

WELL = """
  <rect x="160" y="30" width="380" height="630" rx="40" fill="#121316" stroke="#eae2cf" stroke-width="5"/>
  <line class="s" x1="320" y1="58" x2="380" y2="58"/>
  <g class="tm"><text x="232" y="560">M</text><text x="270" y="560">T</text><text x="308" y="560">W</text><text x="346" y="560">T</text><text x="384" y="560">F</text><text x="422" y="560">S</text><text x="458" y="560">S</text></g>
  <g id="{p}-prob"><g><circle cx="238" cy="590" r="11" fill="#c8372d"/><circle cx="276" cy="590" r="11" fill="#c8372d"/></g>
  <g fill="none" stroke="#c8372d" stroke-width="3" stroke-dasharray="4 4"><circle cx="314" cy="590" r="11"/><circle cx="352" cy="590" r="11"/><circle cx="390" cy="590" r="11"/><circle cx="428" cy="590" r="11"/><circle cx="464" cy="590" r="11"/></g>
  <g><text class="tr" x="200" y="300">Last opened</text><text class="tr" x="200" y="340">6 days ago</text></g></g>
  <g id="{p}-fix"><g fill="#f2b35a"><circle cx="238" cy="590" r="11"/><circle cx="276" cy="590" r="11"/><circle cx="314" cy="590" r="11"/><circle cx="352" cy="590" r="11"/><circle cx="390" cy="590" r="11"/><circle cx="428" cy="590" r="11"/><circle cx="464" cy="590" r="11"/></g>
  <g><text class="t" x="200" y="130">Morning, Sam.</text><text class="t" x="200" y="170">How are you today?</text></g>
  <g><g class="s"><circle cx="248" cy="240" r="20"/><circle cx="298" cy="240" r="20"/><circle cx="398" cy="240" r="20"/><circle cx="448" cy="240" r="20"/></g>
  <circle cx="348" cy="240" r="24" fill="#f2b35a"/></g>
  <g><rect class="s f" x="196" y="300" width="304" height="120" rx="14"/><text class="t" x="220" y="348">One minute.</text><text class="t" x="220" y="388">That's it.</text></g>
  <g><rect class="s" x="204" y="458" width="22" height="18" rx="3"/><path class="s" d="M208 458 v-8 a7 7 0 0 1 14 0 v8"/><text class="tm" x="238" y="476">Private to you</text></g></g>
"""

IDEAS = {
    "a": ("AI support assistant", CHAT, ["list the twenty questions", "customers ask most."]),
    "b": ("Booking & reminders", BOOK, ["a mobile-friendly booking page.", "Not an app, yet."]),
    "c": ("A job app for trade crews", CREW, ["spend a day on site.", "Then build mobile-first."]),
    "d": ("One stock dashboard", STOCK, ["map one seller's week.", "Then build for the web."]),
    "e": ("Wellness check-ins", WELL, ["a clickable prototype, tested", "with twenty real people."]),
}

TEMPLATE = open(P("scripts/idea.template.html")).read()


def words(i):
    return json.load(open(P(f"assets/voice2/{i}.words.json")))


for x, (title, art, start_lines) in IDEAS.items():
    sid = "idea-" + x
    s0, sd = scene[sid]["start"], scene[sid]["dur"]
    loc = lambda i: round(S[i] - s0, 3)  # noqa: E731
    w3 = words(x + "3")
    ratio = len(w3) / len(text[x + "3"].split())
    first_word_of = lambda k: w3[min(len(w3) - 1, int(k * ratio))]["start"]  # noqa: E731
    n1 = len(start_lines[0].split())
    t_line1 = round(loc(x + "3") + first_word_of(2) - 0.05, 3)  # after "Start here:"
    t_line2 = round(loc(x + "3") + first_word_of(2 + n1) - 0.05, 3)
    html = (
        TEMPLATE.replace("{{ID}}", sid)
        .replace("{p}", "i" + x)
        .replace("{{P}}", "i" + x)
        .replace("{{TITLE}}", title)
        .replace("{{PROBLEM}}", text[x + "1"].replace("'", "&rsquo;"))
        .replace("{{FIX}}", text[x + "2"].replace("'", "&rsquo;"))
        .replace("{{START1}}", start_lines[0].replace("'", "&rsquo;"))
        .replace("{{START2}}", start_lines[1].replace("'", "&rsquo;"))
        .replace("{{ART}}", art.replace("{p}", "i" + x))
        .replace("{{T1}}", str(loc(x + "1")))
        .replace("{{T2}}", str(loc(x + "2")))
        .replace("{{T3}}", str(loc(x + "3")))
        .replace("{{TL1}}", str(t_line1))
        .replace("{{TL2}}", str(t_line2))
        .replace("{{TOUT}}", str(round(sd - 0.35, 3)))
        .replace("{{D1}}", str(T["durs"][x + "1"]))
        .replace("{{D2}}", str(T["durs"][x + "2"]))
    )
    assert "{{" not in html and "{p}" not in html, sid
    open(P(f"compositions/{sid}.html"), "w").write(html)
    print(sid, "t1", loc(x + "1"), "t2", loc(x + "2"), "t3", loc(x + "3"), "lines", t_line1, t_line2, "out", round(sd - 0.35, 3))

# ---------- path.html: "So, where do you start?" ----------
PATH = [
    ("p2", "Not sure people want it?", "Research first", "research"),
    ("p3", "Customers find you by searching?", "A website", "website"),
    ("p4", "Used every day, on the go?", "A mobile app", "mobile"),
    ("p5", "Trust decides the sale?", "Design & brand first", "design"),
    ("p6", "And every launch needs", "A plan to reach people", "plan"),
]
s0, sd = scene["path"]["start"], scene["path"]["dur"]
rows, beats = [], []
for k, (i, q, a, key) in enumerate(PATH):
    ta = S[i] + [w for w in words(i) if w["text"].lower().strip(",.?").startswith(key)][0]["start"] - s0
    beats.append(f"[{round(S[i] - s0, 3)}, {round(ta, 3)}]")
    rows.append(
        f'      <div id="pa-r{k + 1}" class="pa-row" style="top: {270 + k * 120}px">'
        f'<div class="pa-q">{q}</div>'
        f'<svg class="pa-arrow" viewBox="0 0 150 60"><path d="M6 30 C 50 22 96 34 132 30 M112 14 L136 30 L112 46" fill="none" stroke="#e0483b" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1.2" stroke-dashoffset="1.1"/></svg>'
        f'<div class="pa-a">{a.replace("&", "&amp;")}</div></div>'
    )
t_unsure = round(S["z1"] - s0, 3)
html = (
    open(P("scripts/path.template.html")).read()
    .replace("{{ROWS}}", "\n".join(rows))
    .replace("{{BEATS}}", ", ".join(beats))
    .replace("{{THEAD}}", str(round(S["p1"] - s0, 3)))
    .replace("{{TUNSURE}}", str(t_unsure))
    .replace("{{TPUSH}}", str(round(t_unsure - 1.5, 3)))
    .replace("{{PUSH}}", str(round(sd - t_unsure + 1.5, 3)))
)
assert "{{" not in html
open(P("compositions/path.html"), "w").write(html)
print("path beats", beats, "unsure", t_unsure)
