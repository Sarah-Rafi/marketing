# REVIEW — "Help, right in your pocket." (two-friends version)

The earlier therapists version is kept as `mental-health-pitch-v1-therapists.mp4` (its captions: `../../TectSoft_MentalHealth_Pitch_v1_Captions.srt`).

Final file: `mental-health-pitch.mp4` (copy of `renders/mental-health-pitch.mp4`, which is gitignored).
1920x1080, 30 fps, H.264 + AAC, 62.0 s, `--quality delivery`. Captions as SRT (speakers labelled): `../../TectSoft_MentalHealth_Pitch_Captions.srt`.

## Research behind the story
- WHO, World Mental Health Report (June 2022): about 1 in 8 people lived with a mental disorder (2019 data). This is the only number on screen.
- Therapy outcomes are linked to exercises done between sessions, but completion is low (JMIR 2025; observational NHS study of between-session app use). Hence the angle "the six days in between".
- Young adults increasingly turn to AI chatbots and social media for mental health support (2025 surveys reported by eMarketer and YPulse; small or non-random samples, so none of these numbers is used). Hence the 2 a.m. chatbot scene.

## Creative calls
- The conversation is between two exhausted friends, not therapists: no time, no idea where to start, and a wish for "something on my phone that checks in on me and helps me find the right therapist when I'm ready". "And I bet we're not the only ones." → narrator: "They're not."
- The app answers each thing they asked for, in order: check-ins and a mood journal, breathing and AI audio for 2 a.m., booking a real therapist, and a community so no one struggles alone.
- The skyline from the opening comes back at the end, and its dark windows light up one by one ("make this world a better place for everyone").
- The CTA is aimed at anyone with a mental health app idea: "Reach out to us. Let's create it together."
- Responsible details: a crisis line on the breathing screen, real (licensed) therapists for care, the app as support, and no clinical claims. All screens are a concept, not a real product.

## Measured, not heard
- `hyperframes check`: 0 errors. Kept `line_unread` warnings on app screens that change with the narration (notification, crisis line, journal prompt, check-in thank-you, the Tuesday card). Each is a glance timed to the voice. Pause on them to read.
- Mix: −15.4 LUFS integrated, true peak −1.0 dBTP, no clipping. The score is original and synthesised by `scripts/score.py`; nobody has listened to it.
- Frames pulled from the MP4 match the Studio snapshots.

## Weakest parts / next steps
- The person lying in bed is the least polished drawing.
- The TTS voices are good but not human; a real therapist's voice for the dialogue would raise trust a lot.
- Swap in the real TectSoft logo and handle on the end card.
