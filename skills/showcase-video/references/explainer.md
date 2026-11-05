# Explainer mode: a narrated film

For a film whose job is to **explain**: a demo for a client meeting, an audit or a report
walked through, a "how it works" for people who will watch it with sound. The voice carries
the message. The screen shows what proves it. Launch films and social reels stay silent
(music, SFX and on-screen text): they autoplay muted.

## Contents
1. Why it exists (the failure it prevents)
2. The script
3. Takes first, then the cut (`vo.py`, `voice.js`)
4. What the screen does while the voice talks
5. Sound: the bed under the voice
6. Review and delivery
7. Voices, consent and cost

## 1. Why it exists

A past explainer (an audit walked through for the client, 132 s) followed the slide deck
scene by scene. The client's verdict: "it is literally the presentation". The version they
kept was 79 s. A voice carried the message, there was far less text, visual metaphors
appeared only for what has no picture, and the real demo was used: cursor, clicks, states
changing. That version was built by hand, with clips placed by timestamp and manual ducking.
This mode makes it the normal path.

The two rules that came out of it:
- **Never a scene per slide.** A slide lists; a film shows one thing happening. Five points on
  a slide become one scene that proves the most important one, and a line of voice for the rest.
- **The voice and the screen never say the same thing.** On-screen text is figures and 1–3
  keywords ("47", "3 críticos"), never the sentence being spoken. Reading and listening to the
  same words at once is slower than either.

## 2. The script

- **Length.** Spanish narration runs ~2.5 words/s (English ~2.7). 60–90 s ≈ 150–220 words,
  minus the silent stretches (logo, a demo moment that needs no words, the end card). The
  real take durations decide, not this estimate.
- **One idea per take.** A take is one sentence or two short ones: the unit the cut follows.
  Ids `l1`, `l2`… in order. A take that needs a longer breath before it (a new chapter):
  `l5 (gap 0.9): …`.
- **Every claim is checkable.** Figures, names and dates come from the source (the audit, the
  product, the client's data), listed in `src/SOURCES.md` with where each was read. A claim
  you can't source is cut, not softened. (`research.md` §6.)
- **Spoken, not written.** Short sentences, the subject first, no parentheses or lists, figures
  written as digits when the screen shows them ("47 avisos": the timeline finds `47`).
- **The storyboard is the script.** In explainer mode its rows are takes: each row has the line,
  and the **mechanism** that proves it on screen (SKILL.md §3). A line with no mechanism is
  either cut or given one before approval.

## 3. Takes first, then the cut

The voice is the clock. Generate the takes, then derive every time from them. Never write a
time that a take decides: re-recording one line then moves every later cut, cue and sound
with it, and nothing needs re-timing by hand.

```bash
scripts/new_project.sh ~/Videos/acme-explainer --explainer   # voice-driven timeline.js + audio.ts, voice.js, VO.md
# write src/VO.md (the script), then:
python3 scripts/vo.py build src --provider say               # free scratch voice: time the cut
python3 scripts/vo.py voices                                 # pick the voice with the user (Round 2)
python3 scripts/vo.py build src                              # the final voice (ElevenLabs)
```

- **`vo.py build`** writes `assets/vo/<id>-<hash>.wav` (48 kHz mono, each take at −20 LUFS:
  takes from separate calls vary by ±2 dB) and `vo.js`: per take, the file, its duration, the
  silence before the first word and after the last, and every word with its start and end.
  - **ElevenLabs** (`/with-timestamps`): the time of every character, so word times are exact.
    `previous_text`/`next_text` keep the intonation continuous across takes. The key comes from
    `$ELEVENLABS_API_KEY` and is never printed. The voice is `@voice <id>` in VO.md or
    `$ELEVENLABS_VOICE_ID`.
  - **Cost control.** A take is regenerated only when its text, voice, model or settings
    change. Every generated take is recorded in `assets/vo/takes.json` the moment it exists,
    so a failure halfway (quota, network) loses nothing, and going back to an earlier wording
    reuses its take. `--dry-run` shows what would be generated and how many characters;
    `--only l3,l4` limits a run; `--force` pays again.
  - **Scratch voice** (`--provider say`, macOS) and **a human recording** (`--provider file`,
    `src/vo/<id>.wav|m4a|mp3`): word times from whisper-cli, mapped onto the script's words.
    The scratch voice is for timing only: qa.py blocks delivering it.
- **`voice.js` `layVoice(VO, start)`** lays the takes end to end, with `gap` s between them
  (0.35 by default; VO.md's `(gap …)` or `gapBefore` override it). Each file is placed at its
  first word minus its lead silence, so takes are spaced by what is heard, not by file length.
  It gives the timeline:
  - `V.at(id)`, `V.end(id)`: first and last word of a take;
  - `V.word(id, '47')`, `V.wordEnd(…)`: one word, for a pop, a highlight or a camera move on it.
    Matching ignores case, punctuation and accents (`'criticos'` finds "críticos."). A word
    the take doesn't contain throws, so a changed script fails loudly instead of drifting;
  - `V.gapMid(a, b)`: the middle of the breath between two takes, where cuts go (never mid-word);
  - `V.duration`.
- **`timeline.js`** (explainer version): `DURATION = V.duration + tail`, scenes cut in the
  breaths, and every cue written from `V`. The music keeps its bars, but the cuts follow the
  voice: don't snap them to bar lines.

## 4. What the screen does while the voice talks

- **Show the mechanism, at its word.** When the voice says "47 avisos", the figure lands on
  `V.word('l2', '47')`, in the real report. When it says "lo arreglamos en un clic", the cursor
  clicks and the state changes on screen. The camera move or the highlight sits on the word
  that matters, not on a bar line.
- **The real artifact before a metaphor.** The client's real document, the real dashboard, the
  real row highlighted. In an earlier film the client rejected an abstract "rules" panel and
  asked for the real contract with their row marked. A metaphor only for what has no picture
  (an index being built, a model reading). See `devices.md` § Metaphors.
- **Real interaction.** Cursor, clicks, typing, a state that changes (`lib.js` cursor, `tapAt`,
  captures from `capture.mjs`). A meeting audience trusts what they see work.
- **Less text.** Figures and keywords only, declared with `data-read` as always: the reading
  lint still applies, and the time to read a figure competes with listening.
- **Breathe.** A take every 2–4 s is relentless. Leave 1–2 moments where the demo plays with no
  voice (a gap of 1–2 s before a chapter), so the image lands.

## 5. Sound: the bed under the voice

- `audio.ts` (explainer version) places the takes with `placeVoice(V.lines)` and calls
  `mixdown({ …, voice: V.lines, voiceOverBed: 10 })`.
- **Ducking from the word times.** Not from a level follower: the bed dips 80 ms before each
  phrase, holds through pauses shorter than 0.4 s, and recovers over 300 ms after it. Default
  depths: music, pad and bass −10/−11 dB, drums −6, SFX −6 (`duckDb` to change them).
- **Each take is ridden** to `voiceOverBed` dB (10) over the ducked bed on its voiced spans,
  never more than 4 dB above the median take. `REPORT=1 bun audio.ts` prints the result per
  take: 8–12 dB reads clearly. A take flagged "buried" has a hit or busy SFX under it: move them
  into a breath. Pushing the take up would only feed finalize.sh's limiter. In a test, a
  voice ridden +17 dB over the end-card impact cost 7.5 dB of limiting.
- **The voice chain**, before and after the ride, as any voice-over has:
  - a compressor with an RMS detector (3:1 above −26 dBFS, 5/80 ms, +5 dB) evens out the
    stressed words: an ElevenLabs voice stresses some words ~8 dB over its sentence;
  - a look-ahead peak limiter caps each take at 15 dB over its level, for plosives and onsets.

  `REPORT=1` prints each take's crest and how much the limiter took. More than 5 % of the
  spoken time limited by over 1 dB means the takes are too dynamic: raise the compression.
- **Narrated films master to −16 LUFS** (`LOUDNESS` in the explainer `timeline.js`; finalize.sh
  and qa.py read it). −14 with true peak ≤ −2 dBTP leaves 12 dB from peak to loudness. A real
  voice has about 20, so every stressed word would lose 6–8 dB to the limiter. −16 is the
  spoken-word standard (podcasts, AES's recommendation for speech streaming).
- The voice is summed **after** the bed's compressor, soft clip and fades: no fade eats a word,
  and consonants don't saturate. finalize.sh masters the whole mix to −14 LUFS as usual.
- **The bed is quieter and sparser** than in a silent film: 8ths, not 16ths; light pulse; no
  drops under speech. The big hits go on the cuts, in the breaths.

## 6. Review and delivery

- `render.mjs review` also writes **`narration.md`**: every take with its absolute times, by
  scene. The reviewer reads it with the sheets and checks each line against what is on screen
  during its words (quality-loop.md rubric: Narration).
- **Exit criteria** add: final voice (not scratch); `REPORT=1` gives every take 8–12 dB over the
  bed; no on-screen sentence repeats the voice.
- Re-render after a new voice: `render-segs.sh` sees `vo.js` changed and renders every segment
  again (a re-timed voice must never be joined to frames of the old timing).
- **Subtitles** are not generated. If the film will also play muted, make a second, silent cut
  from the same project (the takes' text as captions is a different film: one thing to read at
  a time).

## 7. Voices, consent and cost

- **Choosing the voice** is the user's call (Round 2): list the account's voices with
  `vo.py voices` and offer 2–3 that match the language, accent and tone (e.g. peninsular
  Spanish, informative). Use the same voice across a client's films.
- **Never clone a person's voice** without their written consent, and never imitate a real
  person.
- **Commercial use.** Check that the ElevenLabs plan allows commercial use of the output before
  delivering a client film.
- **Cost.** One character ≈ one credit with multilingual v2. A 200-word script is ~1,200
  characters per full pass; iterate on the scratch voice and regenerate only changed takes.
  If the account is out of credits, the API answers 401 `quota_exceeded` and vo.py stops
  without touching vo.js.
