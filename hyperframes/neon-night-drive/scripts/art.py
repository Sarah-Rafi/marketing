"""Cartoon cel-shaded art for the neon night drive, drawn as plain SVG.

Writes assets/art/*.svg. Run: python3 scripts/art.py
Characters are stylized from the two reference photos (outfits, hair, beard), not traced.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "art")
os.makedirs(OUT, exist_ok=True)

INK = "#0b0b12"
G = f'stroke="{INK}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"'


def _dedupe(tag):
    # a later stroke-width overrides the shared style G; XML forbids repeating it
    m = tag.group(0)
    while m.count(" stroke-width=") > 1:
        i = m.index(" stroke-width=")
        j = m.index('"', m.index('"', i) + 1)
        m = m[:i] + m[j + 1 :]
    return m


def svg(name, vb, body, defs=""):
    body = re.sub(r"<[^>]+>", _dedupe, body)
    defs = re.sub(r"<[^>]+>", _dedupe, defs)
    w, h = vb
    doc = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f"<defs>{defs}</defs>{body}</svg>"
    )
    with open(os.path.join(OUT, name), "w") as f:
        f.write(doc)


# ---------- characters ----------

C1 = dict(skin="#c98a63", shade="#a86e4c", hair="#141016", suit="#8cc4ee", suit_dk="#6fa9d8")
C2 = dict(skin="#b97a55", shade="#9a6243", hair="#24160f", suit="#1c1c24", suit_dk="#34343f")


def c1_torso():
    stripes = "".join(
        f'<line x1="{x}" y1="300" x2="{x}" y2="760" stroke="#e8f4ff" stroke-width="2" opacity=".6"/>'
        for x in range(30, 380, 20)
    )
    return f"""
<g {G}>
 <path id="c1s" d="M14,470 Q20,355 120,325 L200,372 L280,325 Q380,355 386,470 Z" fill="{C1['suit']}"/>
 <g clip-path="url(#c1clip)" stroke="none">{stripes}
  <path d="M280,325 Q380,355 386,470 L330,470 Q330,380 280,340 Z" fill="{C1['suit_dk']}"/></g>
 <path d="M150,318 L200,372 L250,318 L240,300 L160,300 Z" fill="#fff"/>
 <path d="M175,300 L225,300 L232,345 L200,372 L168,345 Z" fill="#15151c"/>
 <g fill="none" stroke="#fff" stroke-width="3"><circle cx="190" cy="318" r="6"/><circle cx="212" cy="334" r="6"/><circle cx="197" cy="352" r="5"/></g>
 <path d="M120,325 L168,345 L200,372 L170,425 L148,362 Z" fill="{C1['suit_dk']}"/>
 <path d="M280,325 L232,345 L200,372 L230,425 L252,362 Z" fill="{C1['suit_dk']}"/>
 <path d="M282,402 L322,396 L318,414 L286,416 Z" fill="#fff"/><path d="M290,404 L306,398 L314,410 Z" fill="#15151c" stroke-width="3"/>
 <circle cx="180" cy="440" r="7" fill="#e6e9ef" stroke-width="3"/><circle cx="220" cy="440" r="7" fill="#e6e9ef" stroke-width="3"/>
</g>"""


def c1_head():
    s = C1
    return f"""
<g {G}>
 <path d="M168,250 L168,305 Q200,320 232,305 L232,250 Z" fill="{s['shade']}"/>
 <ellipse cx="126" cy="185" rx="16" ry="24" fill="{s['skin']}"/>
 <ellipse cx="274" cy="185" rx="16" ry="24" fill="{s['skin']}"/>
 <path d="M126,150 Q126,70 200,68 Q274,70 274,150 L272,215 Q265,285 200,298 Q135,285 128,215 Z" fill="{s['skin']}"/>
 <path d="M244,92 Q274,104 274,150 L272,215 Q265,285 200,298 Q248,262 252,200 Z" fill="{s['shade']}" stroke="none"/>
 <path d="M128,188 Q130,282 200,304 Q270,282 272,188 Q262,232 246,236 Q226,226 200,228 Q174,226 154,236 Q138,232 128,188 Z" fill="#1d130e"/>
 <path d="M166,242 Q200,224 234,242 Q214,238 200,243 Q186,238 166,242 Z" fill="#1d130e"/>
 <path d="M184,256 Q200,266 216,256 Q200,260 184,256 Z" fill="#8a4b3a" stroke-width="3"/>
 <path d="M200,166 L190,212 Q200,220 212,212" fill="none" stroke-width="4"/>
 <ellipse cx="168" cy="170" rx="15" ry="9" fill="#fff" stroke-width="4"/><ellipse cx="232" cy="170" rx="15" ry="9" fill="#fff" stroke-width="4"/>
 <circle cx="174" cy="171" r="6" fill="#2a1a10" stroke="none"/><circle cx="238" cy="171" r="6" fill="#2a1a10" stroke="none"/>
 <path d="M146,150 Q166,136 190,146" fill="none" stroke-width="10"/><path d="M210,146 Q234,136 254,150" fill="none" stroke-width="10"/>
 <path d="M122,172 Q110,92 150,60 Q190,26 250,40 Q298,56 290,112 Q288,142 278,174 Q272,128 250,112 Q210,96 168,106 Q140,116 132,162 Z" fill="{s['hair']}"/>
 <path d="M160,62 Q205,40 252,54" fill="none" stroke="#4d5070" stroke-width="5"/>
</g>"""


def c2_torso():
    return f"""
<g {G}>
 <path d="M24,470 Q30,360 125,330 L200,380 L275,330 Q370,360 376,470 Z" fill="{C2['suit']}"/>
 <path d="M160,318 L168,470 L232,470 L240,318 Z" fill="#fff"/>
 <circle cx="200" cy="412" r="5" fill="#111" stroke="none"/><circle cx="200" cy="446" r="5" fill="#111" stroke="none"/>
 <path d="M125,330 L165,340 L192,398 L168,470 L146,402 Z" fill="{C2['suit_dk']}"/>
 <path d="M275,330 L235,340 L208,398 L232,470 L254,402 Z" fill="{C2['suit_dk']}"/>
 <path d="M200,332 L162,314 L162,352 Z" fill="#0d0d12"/><path d="M200,332 L238,314 L238,352 Z" fill="#0d0d12"/>
 <rect x="190" y="322" width="20" height="20" rx="4" fill="#26262e"/>
</g>"""


def c2_head():
    s = C2
    return f"""
<g {G}>
 <path d="M172,262 L172,318 Q200,332 228,318 L228,262 Z" fill="{s['shade']}"/>
 <ellipse cx="132" cy="190" rx="15" ry="26" fill="{s['skin']}"/>
 <ellipse cx="268" cy="190" rx="15" ry="26" fill="{s['skin']}"/>
 <path d="M134,150 Q134,75 200,72 Q266,75 266,150 L262,225 Q252,290 200,302 Q148,290 138,225 Z" fill="{s['skin']}"/>
 <path d="M238,96 Q266,108 266,150 L262,225 Q252,290 200,302 Q244,260 246,200 Z" fill="{s['shade']}" stroke="none"/>
 <ellipse cx="172" cy="176" rx="13" ry="8" fill="#fff" stroke-width="4"/><ellipse cx="228" cy="176" rx="13" ry="8" fill="#fff" stroke-width="4"/>
 <circle cx="175" cy="177" r="5.5" fill="#2a1a10" stroke="none"/><circle cx="231" cy="177" r="5.5" fill="#2a1a10" stroke="none"/>
 <path d="M152,157 Q170,149 188,155" fill="none" stroke-width="6"/><path d="M212,155 Q230,149 248,157" fill="none" stroke-width="6"/>
 <path d="M200,170 L192,220 Q200,226 210,220" fill="none" stroke-width="4"/>
 <path d="M183,243 Q200,237 217,243" fill="none" stroke="#3a2418" stroke-width="4"/>
 <path d="M184,256 Q202,266 220,252" fill="none" stroke-width="4"/>
 <path d="M130,168 Q120,95 165,70 Q205,50 252,66 Q282,84 272,152 Q266,118 245,104 Q200,88 165,112 Q148,126 140,170 Z" fill="{s['hair']}"/>
 <path d="M146,116 Q196,64 266,96 Q222,90 176,124 Z" fill="{s['hair']}"/>
 <path d="M168,84 Q210,66 248,78" fill="none" stroke="#5a4030" stroke-width="4"/>
</g>"""


c1_defs = '<clipPath id="c1clip"><path d="M14,470 Q20,355 120,325 L200,372 L280,325 Q380,355 386,470 Z"/></clipPath>'

svg("char1-bust.svg", (400, 470), c1_torso() + c1_head(), c1_defs)
svg("char2-bust.svg", (400, 470), c2_torso() + c2_head())


# full bodies for walking: torso + lower jacket + sleeves; legs are separate files
def body(torso, head, suit, suit_dk, skin, extra_defs="", stripes=False):
    lines = ""
    if stripes:
        lines = "".join(
            f'<line x1="{x}" y1="440" x2="{x}" y2="720" stroke="#e8f4ff" stroke-width="2" opacity=".6"/>'
            for x in range(70, 340, 20)
        )
        lines = f'<g clip-path="url(#lowclip)" stroke="none">{lines}</g>'
    low = f"""
<g {G}>
 <path d="M18,450 Q6,580 34,700 L84,700 Q78,580 90,470 Z" fill="{suit_dk}"/>
 <path d="M382,450 Q394,580 366,700 L316,700 Q322,580 310,470 Z" fill="{suit_dk}"/>
 <circle cx="58" cy="716" r="24" fill="{skin}"/><circle cx="342" cy="716" r="24" fill="{skin}"/>
 <path id="low" d="M74,440 L326,440 L316,700 Q200,722 84,700 Z" fill="{suit}"/>
 {lines}
 <line x1="200" y1="470" x2="200" y2="712" stroke-width="4"/>
</g>"""
    d = extra_defs + '<clipPath id="lowclip"><path d="M74,440 L326,440 L316,700 Q200,722 84,700 Z"/></clipPath>'
    return low + torso + head, d


b1, d1 = body(c1_torso(), c1_head(), C1["suit"], C1["suit_dk"], C1["skin"], c1_defs, stripes=True)
svg("char1-body.svg", (400, 760), b1, d1)
b2, d2 = body(c2_torso(), c2_head(), C2["suit"], C2["suit_dk"], C2["skin"])
svg("char2-body.svg", (400, 760), b2, d2)


def leg(name, cloth, shoe):
    svg(
        name,
        (130, 350),
        f"""<g {G}><path d="M18,0 L112,0 L100,300 L30,300 Z" fill="{cloth}"/>
<path d="M14,290 L104,290 Q128,300 122,342 L14,342 Z" fill="{shoe}"/>
<path d="M30,300 L40,330" stroke="#fff" stroke-width="3" opacity=".5"/></g>""",
    )


leg("char1-leg.svg", "#f4f2ec", "#5a3420")
leg("char2-leg.svg", "#16161c", "#0a0a0e")

# passenger leaning out, gun pointed back at the camera (foreshortened)
lean_arm = f"""
<g {G} transform="translate(10,40)">
 <path d="M96,348 Q60,330 70,282 L150,268 Q170,320 150,356 Z" fill="{C2['suit']}"/>
 <path d="M70,282 L150,268 L156,290 L76,304 Z" fill="#fff"/>
 <rect x="62" y="210" width="96" height="70" rx="10" fill="#2b2d33"/>
 <circle cx="110" cy="240" r="16" fill="#050507"/>
 <circle cx="110" cy="240" r="7" fill="#000" stroke="none"/>
 <path d="M66,276 Q60,250 92,246 L128,246 Q160,250 154,278 Q110,296 66,276 Z" fill="{C2['skin']}"/>
</g>"""
svg("char2-lean.svg", (400, 470), c2_torso() + c2_head() + lean_arm)

svg(
    "gun.svg",
    (220, 140),
    f"""<g {G}>
 <path d="M44,58 L96,58 L86,132 L38,132 Z" fill="#1a1b1f"/>
 <path d="M96,58 Q120,90 104,96 Q92,96 92,76" fill="none" stroke-width="5"/>
 <rect x="18" y="20" width="186" height="40" rx="5" fill="#2b2d33"/>
 <g stroke-width="3">{''.join(f'<line x1="{x}" y1="26" x2="{x}" y2="54"/>' for x in range(30, 70, 8))}</g>
 <rect x="196" y="28" width="16" height="22" fill="#111"/>
</g>""",
)

# ---------- vehicles ----------

ARCHES = "L975,250 L860,250 A80,80 0 0 0 700,250 L310,250 A80,80 0 0 0 150,250 L40,250 Z"
MUSCLE = "M40,250 L36,192 Q40,166 90,160 L300,150 Q338,70 410,62 L585,62 Q640,68 690,150 L920,164 Q968,170 972,206 " + ARCHES
WIN_M = "M330,146 Q356,82 412,76 L470,76 L470,146 Z M488,146 L488,76 L576,76 Q618,82 650,146 Z"

svg(
    "wheel.svg",
    (160, 160),
    f"""<g {G}><circle cx="80" cy="80" r="74" fill="#111116"/>
<circle cx="80" cy="80" r="46" fill="#9aa3b5"/>
<g stroke-width="7">{''.join(f'<line x1="80" y1="80" x2="{80 + 40 * __import__("math").cos(a * 1.2566)}" y2="{80 + 40 * __import__("math").sin(a * 1.2566)}"/>' for a in range(5))}</g>
<circle cx="80" cy="80" r="12" fill="#d8dce6"/><circle cx="80" cy="80" r="46" fill="none" stroke="#e8ecf4" stroke-width="3" opacity=".6"/></g>""",
)

svg(
    "car-side.svg",
    (1000, 340),
    f"""
<path d="M330,150 L690,150 L690,252 L310,252 Z" fill="#2a0f1c"/>
<path d="M360,150 Q380,120 420,130 L440,250 L370,250 Z" fill="#5a1630" stroke="{INK}" stroke-width="4"/>
<path d="{MUSCLE} {WIN_M}" fill="#17171f" fill-rule="evenodd" {G}/>
<path d="{WIN_M}" fill="#59c8ff" opacity=".16"/>
<path d="M300,152 Q338,72 410,64 L585,64 Q640,70 690,152 L920,166" fill="none" stroke="#19e3ff" stroke-width="5" opacity=".9"/>
<path d="M60,200 L960,200" stroke="#ff2e88" stroke-width="5" opacity=".75"/>
<path d="M60,236 L300,236 M700,236 L960,236" stroke="#3b3f58" stroke-width="6"/>
<rect x="944" y="182" width="26" height="16" rx="4" fill="#ffe9a8" {G} stroke-width="4"/>
<rect x="36" y="172" width="16" height="22" rx="3" fill="#ff2244" {G} stroke-width="4"/>
<path d="M30,246 L120,246 M880,246 L980,246" stroke="#cfd5e2" stroke-width="7"/>
<path d="M412,76 L470,76 L470,146 M488,146 L488,76" fill="none" {G}/>
""",
)

# the near (passenger) door, drawn to sit exactly on car-side at x=310..690, y=146..252
svg(
    "car-door.svg",
    (380, 108),
    f"""<path d="M3,4 L377,4 L377,104 L3,104 Z" fill="#17171f" {G}/>
<path d="M10,54 L372,54" stroke="#ff2e88" stroke-width="5" opacity=".75"/>
<rect x="300" y="20" width="44" height="10" rx="4" fill="#cfd5e2" stroke="{INK}" stroke-width="3"/>""",
)

POLICE = "M40,250 L38,178 Q44,160 80,158 L262,150 Q300,100 362,92 L620,92 Q660,96 700,150 L930,160 Q966,166 970,200 " + ARCHES
svg(
    "police-side.svg",
    (1000, 340),
    f"""
<defs><clipPath id="pb"><path d="{POLICE}"/></clipPath></defs>
<g clip-path="url(#pb)"><rect width="1000" height="340" fill="#f1f2f6"/>
<rect x="0" y="0" width="262" height="340" fill="#15151c"/><rect x="700" y="0" width="300" height="340" fill="#15151c"/>
<rect x="0" y="232" width="1000" height="30" fill="#15151c"/></g>
<path d="{POLICE}" fill="none" {G}/>
<path d="M300,148 Q330,108 368,104 L470,104 L470,148 Z M488,148 L488,104 L612,104 Q650,110 676,148 Z" fill="#0e1830" {G}/>
<path d="M330,140 L380,108" stroke="#7fb6ff" stroke-width="6" opacity=".5"/>
<rect x="430" y="70" width="140" height="22" rx="6" fill="#222" {G} stroke-width="4"/>
<rect x="436" y="73" width="62" height="16" rx="3" fill="#ff2a3d"/><rect x="502" y="73" width="62" height="16" rx="3" fill="#2a6bff"/>
<text x="490" y="210" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="38" fill="#15151c">POLICE</text>
<rect x="944" y="176" width="24" height="16" rx="4" fill="#ffe9a8" {G} stroke-width="4"/>
<rect x="970" y="196" width="22" height="52" rx="4" fill="#2b2d33" {G} stroke-width="4"/>
""",
)


def rear(name, passenger=True, police=False):
    heads = f'<path d="M222,150 Q216,104 252,100 Q286,104 280,150 Z" fill="{INK}"/><path d="M228,104 Q250,80 286,96 Q262,96 244,108 Z" fill="{INK}"/>'
    if passenger:
        heads += f'<path d="M322,150 Q318,108 350,104 Q382,108 378,150 Z" fill="{INK}"/>'
    if police:
        heads = f'<path d="M222,150 Q216,108 252,104 Q286,108 280,150 Z" fill="{INK}"/><rect x="226" y="96" width="54" height="14" rx="4" fill="{INK}"/>'
        heads += f'<path d="M322,150 Q318,108 350,104 Q382,108 378,150 Z" fill="{INK}"/><rect x="324" y="96" width="54" height="14" rx="4" fill="{INK}"/>'
    body_fill = "#15151c"
    cabin_fill = "#f1f2f6" if police else "#17171f"
    bar = ""
    if police:
        bar = f'<rect x="220" y="34" width="160" height="26" rx="6" fill="#222" {G} stroke-width="4"/><rect x="226" y="38" width="72" height="18" rx="3" fill="#ff2a3d"/><rect x="302" y="38" width="72" height="18" rx="3" fill="#2a6bff"/>'
    plate = "POLICE" if police else "NEON 1"
    svg(
        name,
        (600, 380),
        f"""
<rect x="56" y="270" width="96" height="92" rx="14" fill="#0d0d10" {G}/>
<rect x="448" y="270" width="96" height="92" rx="14" fill="#0d0d10" {G}/>
<path d="M150,168 L192,72 Q200,58 222,58 L378,58 Q400,58 408,72 L450,168 Z" fill="{cabin_fill}" {G}/>
<path d="M186,152 L214,84 L386,84 L414,152 Z" fill="#0f1a2e" {G} stroke-width="5"/>
{heads}
<path d="M200,148 L224,92" stroke="#7fd8ff" stroke-width="6" opacity=".45"/>
{bar}
<path d="M40,300 L40,206 Q48,170 110,160 L490,160 Q552,170 560,206 L560,300 Q300,316 40,300 Z" fill="{body_fill}" {G}/>
<path d="M70,180 Q300,168 530,180" stroke="#19e3ff" stroke-width="4" opacity=".8" fill="none"/>
<rect x="70" y="196" width="460" height="30" rx="8" fill="#ff2244" {G} stroke-width="5"/>
<rect x="250" y="236" width="100" height="34" rx="4" fill="#f4f1e6" {G} stroke-width="4"/>
<text x="300" y="262" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="20" fill="#15151c">{plate}</text>
<rect x="50" y="280" width="500" height="14" rx="6" fill="#cfd5e2" {G} stroke-width="4"/>
<circle cx="150" cy="306" r="14" fill="#2a2a30" {G} stroke-width="4"/><circle cx="150" cy="306" r="6" fill="#ff8a3d"/>
<circle cx="450" cy="306" r="14" fill="#2a2a30" {G} stroke-width="4"/><circle cx="450" cy="306" r="6" fill="#ff8a3d"/>
""",
    )


rear("car-rear.svg")
rear("car-rear-lean.svg", passenger=False)
rear("police-rear.svg", police=True)


def top(name, base, hood, bar=False, stripe="#19e3ff"):
    lb = ""
    if bar:
        lb = f'<rect x="40" y="214" width="140" height="22" rx="5" fill="#222" {G} stroke-width="4"/><rect x="44" y="217" width="64" height="16" fill="#ff2a3d"/><rect x="112" y="217" width="64" height="16" fill="#2a6bff"/>'
    svg(
        name,
        (220, 440),
        f"""<g {G}>
<rect x="12" y="10" width="196" height="420" rx="56" fill="{base}"/>
<path d="M12,140 L208,140 L208,66 Q208,10 152,10 L68,10 Q12,10 12,66 Z" fill="{hood}"/>
<path d="M12,360 L208,360 L208,374 Q208,430 152,430 L68,430 Q12,430 12,374 Z" fill="{hood}"/>
<path d="M36,150 L184,150 L170,196 L50,196 Z" fill="#1d3b5c"/>
<rect x="48" y="196" width="124" height="110" rx="10" fill="{base}"/>
<path d="M50,306 L170,306 L182,346 L38,346 Z" fill="#1d3b5c"/>
<rect x="34" y="16" width="34" height="14" rx="4" fill="#ffe9a8" stroke-width="3"/><rect x="152" y="16" width="34" height="14" rx="4" fill="#ffe9a8" stroke-width="3"/>
<rect x="30" y="414" width="44" height="10" rx="3" fill="#ff2244" stroke-width="3"/><rect x="146" y="414" width="44" height="10" rx="3" fill="#ff2244" stroke-width="3"/>
</g>
<path d="M90,24 L90,134 M130,24 L130,134" stroke="{stripe}" stroke-width="5" opacity=".8"/>
{lb}""",
    )


top("car-top.svg", "#1d1d27", "#17171f")
top("police-top.svg", "#f1f2f6", "#15151c", bar=True, stripe="none")
top("traffic-teal.svg", "#2fb7a8", "#25968a", stripe="none")
top("traffic-orange.svg", "#ff9a3d", "#e07a20", stripe="none")

# ---------- scenery ----------

fronds = "".join(
    f'<path d="M165,150 Q{165 + dx * 0.55},{150 + dy * 0.55 - 40} {165 + dx},{150 + dy} Q{165 + dx * 0.5},{150 + dy * 0.5 - 6} 165,158 Z"/>'
    for dx, dy in [(-150, 40), (-120, 110), (-60, 150), (140, 50), (120, 120), (60, 150), (-30, -60), (70, -40)]
)
svg(
    "palm.svg",
    (330, 640),
    f'<g fill="#1a0b2e"><path d="M150,640 Q138,420 158,150 L174,150 Q160,420 176,640 Z"/>{fronds}<circle cx="165" cy="152" r="16"/></g>',
)

leaves = "".join(
    f'<path d="M80,80 Q{80 + 34 * dx - 14 * dy},{80 + 34 * dy + 14 * dx} {80 + 72 * dx},{80 + 72 * dy} Q{80 + 34 * dx + 14 * dy},{80 + 34 * dy - 14 * dx} 80,80 Z"/>'
    for dx, dy in [(1, 0), (0.62, 0.78), (-0.22, 0.97), (-0.9, 0.43), (-0.9, -0.43), (-0.22, -0.97), (0.62, -0.78)]
)
svg(
    "palm-top.svg",
    (160, 160),
    f'<g fill="#1f6a45" stroke="{INK}" stroke-width="4">{leaves}</g><circle cx="80" cy="80" r="12" fill="#5a3a20" stroke="{INK}" stroke-width="4"/>',
)

print("wrote", sorted(os.listdir(OUT)))
