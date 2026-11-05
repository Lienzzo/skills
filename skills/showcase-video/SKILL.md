---
name: showcase-video
description: Make polished motion-design product videos (launch, promo, showcase, teaser, demo reel, social reel in 16:9, 9:16, 1:1 or 4:5) entirely in code. Scenes are frame-exact HTML rendered with headless Chromium and ffmpeg, with an original synthesized soundtrack and SFX synced to one timeline, and an optional narrated mode (ElevenLabs voice whose takes time the cut) for explainers and client meetings. It asks a few multiple-choice questions to pin down the film, researches reference launch videos and the real product's UI and brand, then proposes distinct concepts rooted in that product. The user approves one plan (storyboard and assets). After that it produces autonomously in a build → review → fix loop, with an independent reviewer and automated QA, until the video passes. Use it whenever someone asks for a promo, launch, showcase, explainer or motion-design video, an animated demo of their app or SaaS, a narrated walkthrough of a report or audit for a client, "un vídeo promocional / de lanzamiento", "un vídeo explicativo con voz", or to fix or iterate on one of these videos, even if they never say "motion design".
---

# Showcase video

This skill makes a 30–90 s product film in code. Every frame is a pure function of time
(`window.__seek(t)`), and the music and SFX are synthesized from the same timeline. So
sound lands on the exact frame, renders are repeatable, and any feedback at a timestamp
can be reproduced at that timestamp.

The work has two halves:

- **Plan, with the user.** A short interactive brief, research, then three distinct
  directions, a storyboard and an asset sheet. The user gives **one approval**.
- **Produce, autonomously.** Build → review → fix, repeated until an independent review
  and automated QA both pass. Then deliver. Don't come back with questions in between.
  Interrupt only for a true blocker: an asset only the user has, a claim you can't
  verify, or a brand or legal risk.

**Requirements:**
- Node ≥ 20 and bun;
- ffmpeg;
- ImageMagick 7;
- Playwright with `chromium-headless-shell` (and full `chromium` for `capture.mjs login`);
- uv, for logo tracing;
- yt-dlp, for references;
- poppler, for documents.

It runs on Linux and macOS (Windows through WSL). `scripts/new_project.sh` reports
anything missing.

## 0 · Profile

Read `${SHOWCASE_PROFILE:-~/.config/showcase-video/profile.md}` if it exists. It holds:

- **Preferences:** this user's standing taste, learned from their feedback on earlier
  videos. It overrides the defaults at the end of this file.
- **Past videos:** each one's concept, structure, devices and music. The new video must
  not repeat them.

Create or update the file at delivery (step 5).

## 1 · Brief (interactive)

Take what you can from context (the request, the repo, the site, the profile), then ask the
rest as **multiple-choice questions**, never as an open questionnaire:

- In Claude Code use the `AskUserQuestion` tool: up to 4 questions per call, 2–4 options
  each, your recommended option first with "(Recommended)" in its label, and a one-line
  description of what each option changes in the film. Elsewhere, one message with
  numbered options and your recommendation.
- **Two rounds at most.** Never ask what the context already answers; drop a question
  whose answer wouldn't change the film. Ask in the user's language.

**Round 1 · what the film is for** (before research):

| Question | Options (adapt them) | It sets |
|---|---|---|
| What is it for? | launch · new feature · sales showcase for clients · explainer/demo | structure, how much UI vs idea |
| Where will it play? (multi-select) | web hero (16:9, 30–45 s, may loop) · social (9:16 or 4:5, 15–30 s, readable muted) · chat apps and email (16:9, ≤ 60 s, share copy) · event screen (16:9, 60–90 s) | `FORMAT`(s), length, text size |
| Who watches? | people who don't know it · its users · the client's own team · investors | how much to explain |
| What tone? | calm and exact · energetic · warm and human · premium and restrained | tempo, key, world, easing |
| Voice? | silent: music, SFX and on-screen text · narrated: a voice carries the message | explainer mode (`references/explainer.md`) |

On "Voice?": recommend **narrated** when the film is an explainer or demo watched with sound
(a client meeting, a report walked through); recommend **silent** for launch, web hero and
social (they autoplay muted). Ask only if the purpose leaves it open.

Every extra format is reframed, reviewed and QA'd on its own: say so when they pick several.

**Round 2 · content and sound** (after a first look at the product, so the options are real):

| Question | Options | It sets |
|---|---|---|
| Which moment should the film build to? | 2–4 candidate "magic moments" from the product's real flows | the drop, the longest shot |
| Music? | an original synthesized score (nothing to license) · a track they supply or license (measured with `scripts/beats.py`) · only UI sound | `audio.ts` |
| Real data or demo data? | real, anonymized (needs their OK and a login: `capture.mjs`) · invented but plausible | fidelity, captures |
| Which voice? (narrated only) | 2–3 voices from the account (`scripts/vo.py voices`) that fit the language, accent and tone | the takes |

Also needed, asked plainly only if unknown: the product (repo, URL, app) and the on-screen
language (default: the product's own).

## 2 · Research (parallel tracks)

- **Reference films.** How good launches are made. Pick 4–6. Use
  `scripts/analyze_refs.py search …`, then `analyze <project>/refs name=<url|id|file> …`.
  That writes measured cuts, shot lengths, light/dark share and a loudness curve, plus
  timestamped contact sheets. **Look at every sheet.** Distil techniques, not scenes to
  copy.
- **The real product.** Send parallel Explore agents to its source:
  - theme tokens (the dark theme if it has one);
  - real strings;
  - the components of the flows you'll show;
  - logo files, icon set, fonts, easing constants;
  - existing animations worth rebuilding;
  - store presence;
  - realistic data.

  Read from the default branch without touching the user's working tree (`git show
  main:path`). Never check out, stash or reset their branch.
- **Capture or rebuild.** Screens shown as they are (the real window wide, dense pages, a
  burst of features) are captured from the running app with `template/capture.mjs`: the
  agent's own headless browser, never the user's; the human logs in themselves; personal
  data replaced before each shot; element boxes saved for the cursor. Screens that animate
  inside (typing, streaming, morphs) are rebuilt in HTML from the real tokens and strings.
  See `references/research.md` §4.
- **The user's own reference,** if they give one (a frame, a video, a folder of past work):
  take its grammar (palette, type, pacing, transitions, texture), never its content.
- **The product's visual DNA.** This is where originality comes from. From the research,
  list:
  - the shapes in its logo;
  - its signature UI moments;
  - the verb at its core (search, cite, fill, draft, predict…);
  - its "magic moment": the instant a user thinks "oh";
  - its domain's imagery;
  - a metaphor for the invisible work it does.

  Different products yield different films because this list differs.

Details and checklists are in `references/research.md`.

## 3 · The plan ✋ (the one approval)

Present everything in one message:

1. **Three directions,** genuinely different in structure, not just in colour. Examples:
   one continuous camera through a single world; a cut-driven film alternating
   typography with isolated UI; a metaphor-led story built from the logo's shapes. For
   each, give:
   - a one-line logline;
   - the core metaphor;
   - the structure;
   - which reference techniques and which DNA items it uses;
   - why it fits this product.

   Recommend one.
2. **Storyboard for the recommended direction,** on a 120 BPM grid (bar = 2 s, cuts on
   bar lines), with the musical arc (intro, drop, breakdown, build, drop 2, resolve):

   | Bars / time | Scene | Claim (what it says) | Mechanism: what proves it on screen | Shot | Into next | Sound |
   |---|---|---|---|---|---|---|

   **Every row has a mechanism:** the real thing on screen that makes the claim true. That
   can be a real document with the row marked, a click and the state it changes, or a real
   figure landing. A row whose claim is only stated in text isn't approved. **The real artifact
   comes before a metaphor**, which is only for work with no picture (indexing, a model
   reading). In a past film the client rejected an abstract "rules" panel and asked for their
   real contract with their row highlighted.

   **Narrated films** (explainer mode): the rows are the script's takes. *Claim* is the line
   the voice says, the time column is an estimate (≈ 2.5 words/s) until the takes exist, and
   cuts fall in the breaths between takes, not on bar lines. See `references/explainer.md`.

   With a supplied track, the grid is the track's: measure it first (`scripts/beats.py`)
   and put cuts on its bar lines and the drop on its biggest energy jump.
3. **Asset sheet.** `scripts/asset_sheet.sh <project>/refs/assets.png "file|label · source" …`
   shows every visual asset with its origin:
   - the logo file;
   - official store badges (`scripts/store_badges.sh`);
   - generated vs real imagery;
   - fonts and colour swatches;
   - screens you'll rebuild.

   Look at it yourself first.
4. **Open questions,** only if their answer changes the film.

**Before sending, run a sameness check.** Compare the recommended direction's opening,
structure and signature devices against the profile's past videos and the case studies
in `references/research.md`. If it would read as the same film with another logo,
change it. The demo template (logo draw → app window → end card) is an engine test, not
a structure: don't propose it. Check it against the generic look too (see *Making it
great*).

**Ask for the approval as a choice,** not as "ok?": in Claude Code, one `AskUserQuestion`
with one option per direction (the recommended one first), each with a `preview` holding
its logline and its beat list with times (6–10 lines, each with its claim → mechanism), so
the three structures sit side by side. The user can still answer "Other" with changes. If they pick a direction other
than the recommended one, write its storyboard and confirm that once.

Say explicitly that after approval you'll produce the whole video autonomously and come
back when it passes review.

## 4 · Produce: the autonomous loop

Keep a log at `src/LOOP.md`: one entry per iteration with what was built, what the
review found, what was fixed, and what's next. It makes the loop auditable, and it lets
you resume after a context reset.

1. **Set up.**
   - `scripts/new_project.sh ~/Videos/<product>-showcase` copies `template/`, a working
     14 s demo, into `src/` with git, and checks the tools (Playwright included). For a
     narrated film add `--explainer`, write `src/VO.md`, and generate the takes before the
     first scene (`references/explainer.md` §3): the takes set the timeline.
   - Run the smoke test it prints.
   - Save the approved plan as `src/STORYBOARD.md`. It holds:
     - the chosen direction;
     - the storyboard table;
     - the product facts;
     - the formats;
     - a **Locked decisions** section: what the client approved or asked for, each with
       its reason.

     The reviewer prompt and a resumed session read it from there. When a review round
     reverses an earlier call that was a matter of taste, add the call to Locked decisions:
     reviewers get them as "do not reopen".
   - Set `DEFAULT_FORMAT` in `timeline.js` to the main format (`16x9`, `9x16`, `1x1`,
     `4x5`); others render with `FORMAT=…` from the same timeline.
   - Put in the real brand:
     - `uv run trace_logo.py <logo> assets/logo.json`;
     - `node gen-icons.mjs <repo> icon…`;
     - the product's fonts as woff2;
     - its tokens into `:root`.
   - Captured screens: write `src/capture-shots.mjs` with `capture.mjs` (login first if
     the app needs one: `node capture.mjs login <url>`, the human types the password).
   - Real video (the app's splash animation, a screen recording): `scripts/frames.sh <video>
     src <name>` and `clipAt()` in the scene (`references/engine.md` § Cookbook). Never laid
     over the render afterwards with ffmpeg: the review loop wouldn't see it.
   - Write `timeline.js`: `T` cues, the `SCENES` windows, and `INTENDED` (planned
     instant changes). A supplied track: its BPM and first downbeat from `beats.py`.
   - Delete the `demo-*.js` scenes once the first real scene renders.
2. **Scene by scene.** Build it, with `data-read` on every text the viewer must read
   (`references/engine.md` § Pitfalls). Then run `node render.mjs review --scene <id>`. That
   writes a sheet of the scene, filmstrips across its cuts, phone-size sheets (what a
   viewer reads on a phone), and `lint.md`, with three lints:
   - text cut off by the frame;
   - frames that change with seek order (state left behind, which breaks parallel renders);
   - **reading time**: every `data-read` text measured against 0.4 s per word + 0.5 s, and
     one thing to read at a time.

   Clear the reading lint first: it is the defect reviewers used to spend most rounds on.
   Then read the images against the storyboard and `references/quality-loop.md`'s rubric.
   Fix and repeat until the scene is clean, then move on. The engine rules and pitfalls are in `references/engine.md`. **Read its
   pitfalls section before the first scene.**
3. **Whole-film review round.** Run `node render.mjs review`. Then have a **fresh
   subagent** review the pack against the storyboard and the rubric, using the prompt in
   `references/quality-loop.md`. A fresh reviewer judges what is on screen, not what you
   meant. It returns defects with timestamps and severities. Fix every blocker and major,
   log them, and repeat.
   - **Exit** when the reviewer reports no blocker or major and both lints are clean.
   - **Stuck?** If one issue survives three rounds, change the approach instead of
     nudging values.
4. **Audio,** once the timing is stable. Run `bun audio.ts` and
   `REPORT=1 bun audio.ts` (stem levels per scene). See `references/audio.md`.
5. **Render and QA.**
   - `./render-segs.sh <name> 2 2` is resumable and watchdog-guarded. Run it in the
     background.
   - `SRC=out/<name>.mkv NAME=… DEST=../vN ./finalize.sh` produces the master, web and
     share files. It takes minutes: run it in the background too. If it is interrupted,
     `RESUME=1` finishes the same version without redoing the files already written.
   - Other formats: the same steps with `FORMAT=9x16` (etc.) in front of each command,
     their own `NAME`, and their own review round first.
   - `python3 <skill>/scripts/qa.py ../vN/<name>.mp4 .` checks:
     - frames, resolution, colour, loudness;
     - every **unplanned** discontinuity (jumps, pops) and near-black stretch, each with
       a filmstrip cut from the file.

     For each flagged moment, fix it (re-render only the affected segments: delete their
     `.ok`) or add it to `INTENDED`.
   - Give the reviewer the final 1 fps sheet too.
   - Repeat until qa.py exits 0.

   Commands, memory and timings are in `references/render-deliver.md`.

## 5 · Deliver

- Commit and tag the version (`git tag vN`). Deliverables live in `<project>/vN/`.
  finalize.sh refuses to overwrite: earlier versions stay side by side.
- Report:
  - paths, sizes and duration;
  - the concept in one line;
  - what the loop caught and fixed (summarised from LOOP.md);
  - what a human should still judge. You can't watch motion in real time or hear the
    music. Give them `node render.mjs serve`: a live preview with sound, a timecode and
    seeking. Name the timestamps worth a look and a listen.
- Update the profile: add this video to *Past videos* (concept, structure, devices, key
  and tempo) and add any durable preference the user expressed.

## 6 · Feedback rounds

Feedback arrives as screenshots plus timestamps. For each point:

1. Reproduce it (`preview` or `sheet` at that time).
2. Fix the cause.
3. Run the loop again, scoped to the affected scenes, then the render and QA.

A new version goes to a new `vN/` folder unless the user says otherwise. Add durable
preferences to the profile, not one-off fixes.

## Making it great, and different every time

- **Start from the product, never from a previous film.** The DNA list and the
  references are the raw material. `references/devices.md` has a wider vocabulary of
  openings, transitions, metaphors and UI presentations than any one film should use.
  Pick few, and pick fresh.
- **Hook in the first 2–3 s.** A tension, a question or a striking image. A logo alone
  is not a hook.
- **Frame 0 is the thumbnail.** Chat apps, X and Threads show it before playback. Open on
  a finished image (the hook's key frame), never on black or an empty background. qa.py
  fails both.
- **Build the film around the magic moment.** Give it the drop in the music, the
  longest shot and the clearest framing.
- **Outcomes over features.** One idea per scene.
- **Vary camera distance and device.** Use transformations more than cuts. Show the real
  UI wide at least once, for credibility.
- **Keep text readable** (the review's reading lint measures it). Allow about 0.4 s per
  word plus 0.5 s, one thing to read at a time, and copy in the product's own words. No
  slogans.
- **Rhythm.** Shots of 3–5 s, one faster burst, and a breath in the music before each
  new section. Something new on screen every 2–4 s.
- **Not the generic AI video.** These read as made-by-default, so don't ship them unless
  the brief asks: a centered title on a gradient; everything fading in; labels in the
  corners and frame borders; glow on UI chrome; generic particle bursts; a logo as the
  only hook.
- **Readable on a phone** if it will be watched on one (social, chat apps): judge the
  phone-size sheets, not the full-size frames.

## Defaults (the profile overrides them)

- **Faithful to the real product:** real logo (traced, never redrawn), real theme, real
  strings, real flows. Never show features the product lacks.
- **The brand name, not a feature's name.**
- **Voice:** none in launch, web and social films; narrated in explainers watched with sound
  (recommended in Round 1, `references/explainer.md`).
- **Minimal copy** in the product's language.
- **Official store badges,** unmodified, at equal visual height.
- **Every delivered version kept.**
- **Honest reporting** of what was and wasn't verified.

## Files

- `template/` is the working project `new_project.sh` copies:
  - `timeline.js` (formats, cues, scenes), `lib.js` (maths, springs and multi-target
    `track`, camera, cursor, text streaming, comet links, touch taps), `logo.js`,
    `main.js` (with the live player), `index.html`;
  - the `demo-*.js` scenes;
  - `synth.ts` (the engine) and `audio.ts` (the arrangement and SFX);
  - `render.mjs` (serve, preview, sheet, review, render with optional motion blur),
    `render-segs.sh`, `watchdog.sh`, `finalize.sh`;
  - `capture.mjs` (real screens of the app), `montage.mjs` (labelled sheets drawn by
    Chromium), `pw.mjs` (finds Playwright and its browsers);
  - `trace_logo.py` and `gen-icons.mjs`;
  - `explainer/` (copied by `new_project.sh --explainer`): the voice-driven `timeline.js` and
    `audio.ts`, a sample `VO.md`; `voice.js` lays the takes on the clock.
- `scripts/`:
  - `new_project.sh`, `analyze_refs.py`, `asset_sheet.sh`, `store_badges.sh`;
  - `pdf_passage.py`: a real document page plus the boxes of a quoted passage;
  - `beats.py`: tempo, bar lines and sections of a supplied track;
  - `vo.py`: the narration's takes (ElevenLabs, scratch or recorded) and their word times;
  - `frames.sh`: a real video (alpha kept) as the frame sequence `clipAt()` shows;
  - `qa.py`: automated checks on the rendered file.
- `references/`:
  - `research.md`: references, product fidelity, fact-checking, case studies;
  - `devices.md`: the creative vocabulary;
  - `engine.md`: rules, API, cookbook, pitfalls;
  - `quality-loop.md`: rubric, reviewer prompt, exit criteria;
  - `audio.md`;
  - `explainer.md`: the narrated mode (script, takes, cut, ducking, review);
  - `render-deliver.md`.
