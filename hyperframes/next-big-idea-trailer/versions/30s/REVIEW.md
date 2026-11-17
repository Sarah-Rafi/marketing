# REVIEW — "Start with a conversation" trailer

Final file: `next-big-idea-trailer.mp4` (copy of `renders/next-big-idea-trailer.mp4`, which is gitignored).
1920x1080, 30 fps, H.264 + AAC 48 kHz stereo, 30.000 s, `--quality delivery`.

## Creative calls
- Story told through objects, not abstract glow: notebook (the idea) → skyline lighting up (the difference) → pile of wireframes (what to build?) → title impact → sticky notes → columns → phone + browser → people → back to the notebook → end card.
- The red pen is the one accent and the carrier across seams: circle → ring over the city → title underline → check marks → "Let's talk.".
- Captions are verbatim narration in a bottom rail on a scrim. Two lines are not in the rail because they are the on-screen text at that moment: "Start with a conversation." (title card) and "Let's talk." (end card, written as it is spoken).
- End card reads exactly "Your next big idea starts with a conversation. Let's talk." as requested; the narration says "one conversation" (also as requested), so the card and the voice differ by that one word on purpose.
- Not built: a storyboard with alternative storylines (the request asked for the file).

## Audio sources
- Narration: Kokoro-82M (via `npx hyperframes tts`, kokoro-onnx, voice `am_michael`, speed 0.95), one file per line in `assets/voice/`. Word timings from `npx hyperframes transcribe` (whisper small.en) in `assets/voice/*.words.json`.
- Music and effects: original, synthesised from scratch by `scripts/score.py` (seeded numpy; re-running gives byte-identical files). No samples, no third-party or Marvel material. Voice ducking is baked into the score.
- Font: Caveat (SIL OFL 1.1, licence in `assets/fonts/Caveat-OFL.txt`); League Gothic and Inter are HyperFrames bundled fonts.

## Measured (not heard)
- `hyperframes check`: lint 0 errors / 1 warning, runtime, layout, motion, contrast, craft, audio all clean.
- Rendered mix: −17.6 LUFS integrated, true peak −1.0 dBTP, no clipping. Silence dip before the impact (−37 dB mean at 11.35 s), impact at 12.1 s, voice passages ~6–7 dB over the bed between lines.
- Frames pulled from the MP4 at 2, 5.5, 7.5, 10.8, 13, 16, 20, 22.5, 25, 28, 29.8 s match the Studio snapshots.
- Nobody has listened to it. The synthesised score is the weakest element by nature: it is clean and cued, but simpler than a produced orchestral track.

## Weakest shot / next steps
- Score: swap in a licensed catalog track (`npx hyperframes auth login`, then `/media-use` bgm) if a richer orchestral sound is wanted; keep `sfx.wav`.
- Options shot (9.2–12.0): wireframes are line art; could carry more depth.
- Circle in the notebook runs a little past "hand." on the right; reads as hand-drawn.

## Warnings kept
- `timeline_track_too_dense` (index.html track 3): grain, vignette and the two letterbox bars are film-wide overlays; splitting them into a scene adds nothing.
