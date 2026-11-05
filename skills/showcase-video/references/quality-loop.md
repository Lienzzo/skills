# Quality loop: rubric, reviewer, exit criteria

After the plan is approved, quality comes from this loop, not from asking the user. Every
defect it catches is one the user won't have to find. In past productions, the user
found these in delivered cuts:

- a jump at a scene handoff;
- a hover card that never appeared;
- badge numbers off-centre;
- a speech bubble cut by the frame;
- a stray yellow artifact;
- a UI element the product doesn't have;
- store badges at different sizes.

All of them are visible in a contact sheet or a filmstrip. The loop exists to look.

## Contents
1. The iteration
2. Rubric (severity definitions)
3. Reviewer prompt
4. LOOP.md
5. Exit criteria and when to stop

---

## 1. The iteration

```
build / fix ─► node render.mjs review [--scene id] ─► read the pack yourself ─► fix the obvious
      ▲                                                                              │
      └──────── fix blockers + majors, log them ◄── fresh reviewer (subagent) ◄──────┘
```

- **Per scene (fast).** `review --scene id`, then your own check against the storyboard
  and the rubric. Repeat until clean. Then the next scene.
- **Whole film.** `review` (all scenes and all planned cuts), then a fresh reviewer.
  Repeat until the exit criteria are met.
- **Final file.** `qa.py` on the finalized mp4. Resolve every flagged moment (fix it, or
  add it to `INTENDED`), and give the reviewer the 1 fps sheet of the file. Repeat until
  qa.py exits 0.

The review pack in `out/review/<tag>/` contains:
- `scene-<id>.png`: the whole scene at ≤ 0.25 s steps;
- `cut-<t>.png`: ±0.3 s around each planned cut at 0.05 s;
- `phone-<n>.png`: one frame per bar at 390 px wide, the size a phone shows it;
- `lint.md`, with four checks:
  - text partly outside the frame (not text inside `data-read="0"`: a code wall cropped on purpose);
  - frames that change with seek order (the element and property that kept the state);
  - page errors;
  - **the reading lint.** Every `data-read` text is measured against 0.4 s per word + 0.5 s,
    a second text arriving while the first still needs its time is flagged, and so is its size
    on a 390 px phone. Big text nothing declared is listed, and a scene with none declared is
    NOT CHECKED.

  Clear the reading lint yourself before a reviewer sees the pack. In a past film, most of 6
  review rounds went on reading time a machine can measure.

Add full-size `preview` stills for detail-heavy moments: hovers, modals, badges, the end
card.

## 2. Rubric

For each item, the reviewer assigns **blocker** (can't ship), **major** (a viewer would
notice) or **minor** (polish).

| Area | Blocker | Major | Minor |
|---|---|---|---|
| Continuity | A jump or pop at a cut or mid-scene. A flash of the wrong scene. An element teleporting. | A mismatch between the last frame of A and the first of B (position, scale). A transition that stalls. | Easing that feels abrupt. |
| Framing | Important text or UI cut by the frame or its container. Empty stage visible outside the app. | Crowded or unbalanced composition. Key element too small to read at 1080p. | Uneven margins. |
| Fidelity | Wrong logo, brand name or theme. A feature or element the product doesn't have. | UI details off (spacing, radii, icon set, strings not the product's). | Tiny token mismatch. |
| Truth | A false or unverified claim, number or law on screen. | A misleading example. | |
| Readability | Text on screen for less than ~0.4 s per word + 0.5 s. Two things to read at once. Key text unreadable in the phone sheets when the film will be watched on phones. (The reading lint measures the first two: the reviewer checks what it can't, such as text baked into captures.) | Low contrast. Text over busy motion. Secondary text unreadable at phone size. | Awkward line breaks. |
| Story | A scene that doesn't match the approved storyboard. The magic moment missing or buried. | A scene with no clear point. Pacing monotony (same framing more than ~6 s, same layout repeated). | |
| Mechanism | | A claim made only in text (or voice) with nothing on screen proving it, where the storyboard has a real artifact. A metaphor where the real thing could be shown. | |
| Narration (narrated films) | The voice says something the screen contradicts. Scratch voice in a delivery. | On-screen text repeating the sentence being spoken. The mechanism shown well before or after the words that claim it (> ~1 s). A cut mid-word. A scene that reads as a slide being read aloud. | A take buried under the bed (REPORT < 8 dB). |
| Craft | Rendering artifacts (stray shapes, broken glyphs, missing fonts). A frame that changes with seek order (lint). | Off-centre badge text, misaligned icons, jittery motion, blurry text in a camera push. | |
| Generic look | | A centered title on a gradient, everything fading in, labels in corners or frame borders, glow on UI chrome, generic particle bursts, a logo as the only hook. A beat with nothing new for more than ~4 s. | |
| Sameness | Reads like a past video with another logo (compare with the profile). | A signature device reused from a past video. | |

**Taste is not a defect.** A preference that breaks no row of this rubric is at most *minor*.
Something the storyboard's **Locked decisions** or a WONTFIX in LOOP.md already settled is
not reported again, unless it is now unreadable, false, or a regression (it broke since). In
a past film, fresh reviewers reversed each other's taste calls for 10 rounds (which side a
card opens on, when it moves away) until the decisions were locked.

Audio is checked by numbers, not by ear. Check the stem report per scene: SFX audible in
UI scenes, no stem clipping. qa.py checks loudness and silences.

## 3. Reviewer prompt

Spawn a **fresh** subagent: general-purpose, or whatever is available. It must not
inherit your context: fresh eyes judge what is on screen, not what you intended. If
subagents aren't available, do the review yourself, strictly by the rubric, as if you
were seeing the film for the first time.

```
You are reviewing frames of a product video in production. You have not seen it before.
Judge only what is visible.

Storyboard (approved by the client):
<paste the storyboard table>

Product facts (what is real): <theme, brand name, key UI, what features exist>

Locked decisions (settled with the client or in earlier rounds; do NOT reopen them unless the
result is unreadable, false, or a regression):
<paste STORYBOARD.md § Locked decisions and LOOP.md's WONTFIX lines, each with its reason>
Past videos of this brand/user (must not be repeated): <from the profile, or "none">

Review pack — read every image:
<list the absolute paths: scene-*.png, cut-*.png, phone-*.png, lint.md, any previews>
<narrated films: narration.md, what the voice says and when. For each take, look at the
tiles inside its time range and check that what is on screen then proves what is said,
and that no on-screen sentence repeats it.>
Each tile is labelled with its time in seconds. Filmstrips show 0.05 s steps across a cut.
phone-*.png show frames at the size a phone displays them<, and this film WILL / will NOT
be watched on phones>: judge text size there, not in the full-size tiles.

Use this rubric: <paste section 2 of quality-loop.md>

Report ONLY defects, most severe first, one per line:
<severity> · <time or range> · <area> · WHERE <element> · PROBLEM <what is wrong> · CHANGE <the fix> · KEEP <what must not change>
A taste preference that breaks no rubric row is at most minor.
Then one line: "Verdict: ship" if there are no blockers or majors, otherwise "Verdict: fix".
Do not praise. Do not restate the storyboard. If a tile is ambiguous, say what you'd need
to see (e.g. "full-size preview at 18.4").
```

Feed back any preview it asks for and let it re-judge that point.

## 4. LOOP.md

Keep it in `src/`, newest entry last:

```
## Iteration 4 · whole-film review · 2026-10-02 14:10
Reviewer: 1 blocker, 3 majors, 5 minors
- FIXED blocker 10.02 s continuity: input box drops 20 px when the thread appears → thread pre-laid-out at rest
- FIXED major 18.4 s craft: citation digits off-centre → line-height 1 on the badge
- FIXED major 44.9 s readability: caption on screen 0.8 s for 9 words → held to 4.2 s (needs 4.1), cue shifted
- WONTFIX minor 30.1 s: margin 4 px uneven (hidden by the camera push)
- LOCKED 24–26 s: the two phones are a passing shot, not a hold (rounds 5 and 7 asked for
  opposite things) → added to STORYBOARD.md § Locked decisions
Next: re-review scenes cloud + hero; then render.
```

## 5. Exit criteria and when to stop

**The video is ready to deliver when:**
- the last whole-film review says "Verdict: ship" (no blockers or majors);
- the reading lint is clean (or each entry is explained in LOOP.md), and it says it CHECKED
  every scene;
- narrated films: the final voice (qa.py blocks the scratch one), and `REPORT=1` gives every
  take 8–12 dB over the bed;
- `lint.md` has no unexplained entries (a seek-order entry is never "explained": fix it);
- qa.py on the delivered mp4 exits 0;
- every fact on screen has a noted source.

**Don't ship on:**
- your own impression of a scene you haven't reviewed as images;
- a review of an earlier iteration (changes can break other scenes: re-review what you
  touched and every cut next to it).

**If it isn't converging:**
- the same defect across three rounds means changing the approach (re-layout, a
  different transition), not nudging numbers;
- more than ~8 whole-film rounds means stopping and reporting what's unresolved, with
  frames, rather than looping forever.

**Interrupt the user only for** an asset or fact only they can provide, or a brand or
legal risk. Everything else is your call, made from the plan, the rubric and the
profile.
