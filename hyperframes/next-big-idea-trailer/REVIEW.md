# REVIEW — "Start with a conversation" (2:05 film)

Final file: `next-big-idea-film.mp4` (copy of `renders/next-big-idea-film.mp4`; `renders/` is gitignored).
1920x1080, 30 fps, H.264 + AAC 48 kHz stereo, 125.4 s, `--quality delivery`.
The earlier 30 s cut is kept in `versions/30s/` (MP4, HTML, score).

## What changed from the 30 s cut (feedback: show where to start, with real ideas)
- Five ideas trending in 2026, each as problem → fix → "Start here" with a concrete first step:
  1. AI support assistant (small businesses) → list the 20 questions customers ask most.
  2. Booking & reminders (salons, clinics) → a mobile-friendly booking page, not an app yet.
  3. Job app for trade crews → spend a day on site, then build mobile-first.
  4. One stock dashboard (online sellers) → map one seller's week, then build for the web.
  5. Wellness check-ins → a clickable prototype tested with 20 real people.
  Picked from 2026 market roundups (AI agents for small businesses, service-business booking, field-service software, ecommerce ops, wellness apps).
- A decision path, "Where do you start?": research / website / mobile app / design & brand / launch plan, each tied to the question that decides it.
- Expertise is shown, not claimed: specific first steps, the order of work, offline-first for crews, deposits + reminders, privacy by design, a plan to reach people. The copy never says "experts".
- Close: "Still unsure which path is yours? Start with a conversation." → impact → "We'll bring clarity to your idea, plan the first version, and help you bring it to life." → end card (unchanged copy).

## How it is built
- `scripts/narration.tsv` — the script, one line per Kokoro clip (`assets/voice2/`, voice `am_michael`, speed 0.95, `npx hyperframes tts`), word timings from `npx hyperframes transcribe`.
- `scripts/layout.py` → `timeline.json`, `index.html`, `compositions/captions.html` (line starts, scene windows, caption groups; keeps normalize-audio volumes).
- `scripts/build_ideas.py` → `compositions/idea-{a..e}.html` and `compositions/path.html` from the templates in `scripts/`.
- `scripts/score.py` → `assets/music/score.wav`, `assets/sfx/sfx.wav` (original, seeded numpy synthesis, cued from timeline.json).
- Order after a script change: tts → transcribe → layout.py → build_ideas.py → score.py → normalize-audio → check → render.
- Captions: the rail carries the lines not written on screen; idea cards, the path, the title and the end card show their narration verbatim as it is spoken.

## Measured (not heard)
- `check`: 0 errors. Craft, motion, layout and runtime clean after raising illustration type to ≥28 px and staggering the problem/fix pieces (removed five dead stretches).
- Mix: −18.4 LUFS integrated, peak −1.1 dBFS; impact at 107.7 s; music-only passage −24 dB mean vs voice passages −21 dB.
- Frames from the MP4 at 11, 26.7, 49, 54.7, 68.7, 79.3, 90.7, 100, 110, 118, 120, 124.7 s match the snapshots.
- Nobody has listened to it.

## Weakest parts / next steps
- 2:05 is long for paid social; a 30–45 s cutdown with two ideas is a straightforward edit.
- Synthesised score; a licensed catalog track needs `npx hyperframes auth login`.
- Illustrations are flat line art; real product UI would be stronger if there are client screens to show.

## Warnings kept
- `timeline_track_too_dense` (index.html): film-wide grain/vignette/letterbox overlays.
- `contrast_aa_failure #cl-l2` at 118.4 s: a struck-through decorative notebook line passing under the letterbox bar during the camera pull-back.
