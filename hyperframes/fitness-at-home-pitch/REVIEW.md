# REVIEW — "Your coaching. Their living room."

Final file: `fitness-at-home-pitch.mp4` (copy of `renders/fitness-at-home-pitch.mp4`, which is gitignored).
1920x1080, 30 fps, H.264 + AAC 48 kHz stereo, 45.0 s, `--quality delivery`. Captions as SRT: `../../TectSoft_Fitness_Pitch_Captions.srt`.

## Creative calls
- Problem → solution, as asked: two problems (driving to the gym; getting to physio with arthritis or back pain), then the turn ("what if the gym, the studio and the clinic could come to them?"), then the offer (your expertise → your own app with AI-made video sessions, step-by-step guidance, progress).
- People are drawn as gym-signage pictograms, animated rep by rep from joint angles. No stock people, no fake clients, no invented results. The app screens are a concept of what a client's app could look like ("YOUR LOGO"), not a real product.
- Red marks only the problems and volt marks only the solution, so the before/after reads without words.
- The map at the start comes back near the end: the same city, but now one gym reaches every home.
- The physio line stays careful: "getting to physio can be the hardest part". No claims about treatment results.
- Storylines not built: (a) a day in one coach's life, from a packed class to clients training at home; (b) a split screen of gym vs. living room that merges into one phone.

## Audio
- Narration: Kokoro-82M `af_heart` (female, a change from the first trailer's male voice), one file per line in `assets/voice/`, with word timings in `*.words.json`.
- Music and effects: original, synthesised by `scripts/score.py` (seeded, deterministic). Tense ticking over the problems, an impact on the title, then a 120 bpm workout groove. Ducking under the voice is baked in.
- Measured, not heard: −15.9 LUFS integrated, true peak −1.1 dBTP, no clipping.

## Checks
- `hyperframes check`: 0 errors. Kept warnings: `line_unread` on the handwritten plan (it is carried from the roles shot into the phone, so it is on screen about 2 s in total across the two scenes) and on the app splash subline (it is timed to the voice).
- Frames pulled from the MP4 match the Studio snapshots.

## Weakest parts / next steps
- The synthesised score is clean and on cue, but simpler than a produced track. Swap in a licensed track if wanted (`npx hyperframes auth login`, then `/media-use` bgm).
- The end card uses the name "TectSoft" as text. Drop in the real logo file and add your handle or website.
- The pictogram poses are stylised. The yoga and stretch poses read well, but the physio role pose (one arm raised) is the least specific.
