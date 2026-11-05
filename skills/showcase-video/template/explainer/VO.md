# Narration of the demo explainer. One take per line: `id: text`, or `id (gap 0.8): text` for a
# longer breath before it. The voice carries the message; the screen shows the mechanism that
# proves it. On-screen text never repeats the voice: figures and 1–3 keywords only.
# scripts/vo.py build . → assets/vo/*.wav + vo.js (ElevenLabs: $ELEVENLABS_API_KEY, @voice <id>).
# Scratch voice to time the cut for free (macOS): vo.py build . --provider say (qa.py blocks it).
@voice XrExE9yKIg1WjnnlVkGX
@say_voice Samantha
@model eleven_multilingual_v2
@lang en

l1: Every Monday, your team asks the same question.
l2 (gap 0.6): Now they just type it, in their own words.
l3 (gap 0.6): It answers from your documents, and cites every source.
l4 (gap 1.4): Ask it today.
