#!/usr/bin/env python3
"""Voice takes for a narrated film: script → audio files + word timestamps → src/vo.js.

    python3 vo.py build <src> [--provider eleven|say|file] [--only l2,l3] [--force] [--dry-run]
    python3 vo.py voices               # the ElevenLabs voices this key can use (id · name · labels)

The script is <src>/VO.md: one take per line, `id: text`, optionally `id (gap 0.9): text` to
leave a longer breath before it. Settings are `@key value` lines; everything else is ignored.

    @voice  <ElevenLabs voice id>    (or $ELEVENLABS_VOICE_ID; with --provider say, a `say -v` name)
    @model  eleven_multilingual_v2   @format pcm_24000 (pcm_44100 needs a Pro plan)
    @stability 0.5  @similarity 0.75  @style 0  @speed 1     @rate 175 (say, words per minute)
    @lang   es                       (whisper's language, for say/file)

    l1: Cada semana, la misma pregunta.
    l2 (gap 0.8): Tu web tiene 47 avisos abiertos, y 3 son críticos.

Write figures as digits ("47", "1.250 €") when the screen shows them: `V.word('l2', '47')` in
timeline.js finds them. Out: <src>/assets/vo/<id>.wav (48 kHz mono, each take at −20 LUFS) and
<src>/vo.js, which timeline.js and audio.ts import (template/voice.js lays the takes on the clock).

Providers:
  eleven  The final voice. ElevenLabs /with-timestamps: audio plus the time of every character,
          so the word times are exact. Key in $ELEVENLABS_API_KEY (never printed). previous_text /
          next_text keep the intonation continuous across takes. A take is regenerated only when
          its text, voice, model or settings change (or with --force): that is the cost control.
  say     A free scratch voice (macOS) to time the cut before spending credits. Word times come
          from whisper-cli. qa.py blocks delivering a film with it.
  file    A human recording: put <src>/vo/<id>.wav|m4a|mp3 per take; aligned with whisper-cli.

whisper-cli (whisper.cpp) model: $WHISPER_MODEL or ~/.cache/whisper-cpp/ggml-small.bin.
"""
import array, base64, hashlib, json, os, re, subprocess, sys, tempfile, unicodedata, urllib.error, urllib.request
from difflib import SequenceMatcher

API = 'https://api.elevenlabs.io/v1'
SR = 48000
TARGET_LUFS = -20.0


def die(msg):
    sys.exit(f'vo.py: {msg}')


def run(cmd, **kw):
    kw.setdefault('text', True)
    r = subprocess.run(cmd, capture_output=True, **kw)
    if r.returncode:
        err = r.stderr if isinstance(r.stderr, str) else r.stderr.decode(errors='replace')
        die(f'{cmd[0]} failed: {err.strip()[-400:]}')
    return r


def norm(w):
    """Token used to match words: lower case, letters and digits only, no accents (as voice.js)."""
    return ''.join(ch for ch in unicodedata.normalize('NFD', w.lower()) if ch.isalnum() and not unicodedata.combining(ch))


# ── the script ────────────────────────────────────────────────────────────────
def read_script(src):
    p = os.path.join(src, 'VO.md')
    if not os.path.exists(p):
        die(f'{p} not found: write the script first (one take per line, `id: text`)')
    cfg, lines = {}, []
    for raw in open(p, encoding='utf-8'):
        s = raw.strip()
        m = re.match(r'^@(\w+)\s+(.+)$', s)
        if m:
            cfg[m[1]] = m[2].strip()
            continue
        m = re.match(r'^([A-Za-z][\w-]*)\s*(?:\(\s*gap\s*([\d.]+)\s*\))?\s*:\s*(.+)$', s)
        if m:
            lines.append({'id': m[1], 'gap': float(m[2]) if m[2] else None, 'text': m[3].strip()})
    if not lines:
        die(f'{p} has no takes (`id: text` lines)')
    ids = [l['id'] for l in lines]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        die(f'duplicate take ids in VO.md: {", ".join(sorted(dup))}')
    return cfg, lines


# ── audio helpers ─────────────────────────────────────────────────────────────
def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    i = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    pk = re.findall(r'Peak:\s+(-?[\d.]+|-inf) dBFS', r.stderr)
    return float(i[-1]) if i else None, float(pk[-1]) if pk and pk[-1] != '-inf' else None


def to_take(inp, out, raw=None):
    """Decode to 48 kHz mono 24-bit, then set the take to TARGET_LUFS (peaks kept ≤ −1 dBFS).
    Gain only: no trimming, so every timestamp stays valid."""
    tmp = out + '.tmp.wav'
    pre = ['-f', 's16le', '-ar', str(raw), '-ac', '1'] if raw else []
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *pre, '-i', inp, '-ac', '1', '-ar', str(SR), '-c:a', 'pcm_s24le', tmp])
    i, pk = loudness(tmp)
    if i is None:
        die(f'{out}: could not measure the take (silent?)')
    g = TARGET_LUFS - i
    if pk is not None and pk + g > -1.0:
        g = -1.0 - pk
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', tmp, '-af', f'volume={g:.2f}dB', '-c:a', 'pcm_s24le', out])
    os.remove(tmp)


def bounds(path, thr_db=-42.0, win=0.01):
    """Silence before the first and after the last sound (s), and the duration."""
    r = run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], text=False)
    a = array.array('h')
    a.frombytes(r.stdout)
    n = int(16000 * win)
    thr = 32768 * 10 ** (thr_db / 20)
    loud = [max(abs(x) for x in a[i:i + n]) > thr for i in range(0, max(1, len(a) - n), n)]
    dur = len(a) / 16000
    if not any(loud):
        return 0.0, 0.0, dur
    first = loud.index(True) * win
    last = (len(loud) - loud[::-1].index(True)) * win
    return round(first, 3), round(max(0.0, dur - last), 3), round(dur, 3)


# ── word times ────────────────────────────────────────────────────────────────
def words_from_chars(text, chars, starts, ends):
    """ElevenLabs alignment (one entry per character of the input text) → words."""
    out, cur = [], None
    for ch, a, b in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                out.append(cur)
            cur = None
            continue
        if cur is None:
            cur = {'w': '', 't0': a, 't1': b}
        cur['w'] += ch
        cur['t1'] = b
    if cur:
        out.append(cur)
    out = [w for w in out if norm(w['w'])]
    script = [w for w in text.split() if norm(w)]
    if [norm(w['w']) for w in out] != [norm(w) for w in script]:
        die(f'alignment does not match the text: {" ".join(w["w"] for w in out)!r} vs {text!r}')
    return [{'w': w['w'], 't0': round(w['t0'], 3), 't1': round(w['t1'], 3)} for w in out]


def whisper_words(path, lang):
    model = os.environ.get('WHISPER_MODEL', os.path.expanduser('~/.cache/whisper-cpp/ggml-small.bin'))
    if not os.path.exists(model):
        die(f'whisper model not found: {model} (set WHISPER_MODEL)')
    with tempfile.TemporaryDirectory() as d:
        w16 = os.path.join(d, 'a.wav')
        run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ar', '16000', '-ac', '1', w16])
        run(['whisper-cli', '-m', model, '-l', lang, '-ml', '1', '-sow', '-oj', '-of', os.path.join(d, 'a'), '-np', w16])
        segs = json.load(open(os.path.join(d, 'a.json'), encoding='utf-8'))['transcription']
    return [{'n': norm(s['text']), 't0': s['offsets']['from'] / 1000, 't1': s['offsets']['to'] / 1000} for s in segs if norm(s['text'])]


def align_script(text, heard, lead, voiced_end):
    """Map the script's words onto whisper's (which may mishear or spell numbers differently).
    Matched words take whisper's times; the rest are spread by length between their neighbours."""
    script = [w for w in text.split() if norm(w)]
    S = [norm(w) for w in script]
    times = [None] * len(S)
    for blk in SequenceMatcher(None, S, [h['n'] for h in heard], autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            h = heard[blk.b + k]
            times[blk.a + k] = [h['t0'], h['t1']]
    i = 0
    while i < len(S):
        if times[i]:
            i += 1
            continue
        j = i
        while j < len(S) and not times[j]:
            j += 1
        a = times[i - 1][1] if i else lead
        b = times[j][0] if j < len(S) else voiced_end
        span = max(0.0, b - a)
        tot = sum(len(S[k]) + 1 for k in range(i, j))
        t = a
        for k in range(i, j):
            d = span * (len(S[k]) + 1) / tot
            times[k] = [t, t + d]
            t += d
        i = j
    if times:  # whisper's first offset is coarse: the energy onset is better
        times[0][0] = max(times[0][0], lead) if times[0][0] < lead + 0.25 else times[0][0]
        times[-1][1] = min(times[-1][1], voiced_end) if times[-1][1] > voiced_end - 0.25 else times[-1][1]
    return [{'w': w, 't0': round(t[0], 3), 't1': round(t[1], 3)} for w, t in zip(script, times)]


# ── providers ─────────────────────────────────────────────────────────────────
def key():
    k = os.environ.get('ELEVENLABS_API_KEY')
    if not k:
        die('ELEVENLABS_API_KEY is not set (export it in this shell; it is never printed)')
    return k


def eleven_call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method='POST' if body is not None else 'GET',
                                 headers={'xi-api-key': key(), 'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        die(f'ElevenLabs {e.code}: {e.read().decode(errors="replace")[:400]}')


def gen_eleven(line, prev, nxt, cfg, out):
    voice = cfg.get('voice') or os.environ.get('ELEVENLABS_VOICE_ID') or die('no voice: @voice <id> in VO.md or $ELEVENLABS_VOICE_ID (vo.py voices lists them)')
    fmt = cfg.get('format', 'pcm_24000')
    m = re.match(r'pcm_(\d+)$', fmt) or die(f'@format must be pcm_<rate> (got {fmt})')
    body = {
        'text': line['text'],
        'model_id': cfg.get('model', 'eleven_multilingual_v2'),
        'voice_settings': {k: float(cfg[c]) for k, c in [('stability', 'stability'), ('similarity_boost', 'similarity'), ('style', 'style'), ('speed', 'speed')] if c in cfg},
    }
    if prev:
        body['previous_text'] = prev
    if nxt:
        body['next_text'] = nxt
    d = eleven_call(f'{API}/text-to-speech/{voice}/with-timestamps?output_format={fmt}', body)
    return parse_eleven(d, line['text'], out, int(m[1]))


def parse_eleven(d, text, out, rate):
    """Response of /with-timestamps → take file + words. Split out so it can be tested on a fixture."""
    al = d.get('alignment') or die('ElevenLabs response has no alignment')
    with tempfile.NamedTemporaryFile(suffix='.pcm', delete=False) as f:
        f.write(base64.b64decode(d['audio_base64']))
    try:
        to_take(f.name, out, raw=rate)
    finally:
        os.remove(f.name)
    return words_from_chars(text, al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds'])


def gen_say(line, cfg, out):
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, 'a.aiff')
        cmd = ['say', '-o', a, '-r', cfg.get('rate', '175')]
        if cfg.get('voice'):
            cmd += ['-v', cfg['voice']]
        run(cmd + [line['text']])
        to_take(a, out)
    return None  # words come from whisper


def gen_file(line, src, out):
    for ext in ('wav', 'm4a', 'mp3', 'aiff', 'flac'):
        p = os.path.join(src, 'vo', f"{line['id']}.{ext}")
        if os.path.exists(p):
            to_take(p, out)
            return None
    die(f"no recording for {line['id']}: put it at {src}/vo/{line['id']}.wav (or .m4a/.mp3)")


# ── build ─────────────────────────────────────────────────────────────────────
def take_hash(provider, line, cfg):
    keep = {k: v for k, v in cfg.items() if k in ('voice', 'model', 'format', 'stability', 'similarity', 'style', 'speed', 'rate')}
    if provider == 'eleven' and 'voice' not in keep:
        keep['voice'] = os.environ.get('ELEVENLABS_VOICE_ID', '')
    if provider == 'file':
        for ext in ('wav', 'm4a', 'mp3', 'aiff', 'flac'):
            p = os.path.join(SRC, 'vo', f"{line['id']}.{ext}")
            if os.path.exists(p):
                keep['mtime'] = os.path.getmtime(p)
    return hashlib.sha256(json.dumps([provider, line['text'], keep], sort_keys=True).encode()).hexdigest()[:16]


def build(src, provider, only, force, dry):
    cfg, lines = read_script(src)
    vodir = os.path.join(src, 'assets', 'vo')
    os.makedirs(vodir, exist_ok=True)
    # Every generated take is recorded here the moment it exists, keyed by its hash (text, voice,
    # settings, provider), so a failure halfway (quota, network) never loses a paid take, and
    # going back to an earlier wording reuses its take. File names carry the hash: a take's audio
    # and its word times can't get out of step.
    cpath = os.path.join(vodir, 'takes.json')
    cache = json.load(open(cpath, encoding='utf-8')) if os.path.exists(cpath) else {}
    out_lines, todo = [], []
    for i, line in enumerate(lines):
        h = take_hash(provider, line, cfg)
        f = f"assets/vo/{line['id']}-{h[:8]}.wav"  # a regeneration (--force) gets a new name below
        cached = cache.get(h)
        fresh = cached and os.path.exists(os.path.join(src, cached['file']))
        want = (force or not fresh) and (not only or line['id'] in only)
        if not want and not fresh:
            die(f"{line['id']} is out of date but not in --only")
        if force and fresh and want and provider == 'eleven':
            print(f"  (--force: {line['id']} is paid for again)")
        todo.append((i, line, h, f, want, cached))
    chars = sum(len(l['text']) for _, l, _, _, w, _ in todo if w)
    print(f"{sum(w for *_, w, _ in todo)} take(s) to generate with {provider} ({chars} characters), {sum(not w for *_, w, _ in todo)} cached")
    if dry:
        for _, l, _, _, w, _ in todo:
            print(f"  {'gen ' if w else 'keep'} {l['id']}: {l['text']}")
        return
    for i, line, h, f, want, cached in todo:
        if want:
            k = 2
            while os.path.exists(os.path.join(src, f)):  # never overwrite a take vo.js may still point to
                f = f"assets/vo/{line['id']}-{h[:8]}-{k}.wav"
                k += 1
        path = os.path.join(src, f)
        if want:
            print(f"  {line['id']} …", flush=True)
            if provider == 'eleven':
                words = gen_eleven(line, lines[i - 1]['text'] if i else None, lines[i + 1]['text'] if i + 1 < len(lines) else None, cfg, path)
            elif provider == 'say':
                words = gen_say(line, cfg, path)
            else:
                words = gen_file(line, src, path)
            lead, tail, dur = bounds(path)
            if words is None:
                words = align_script(line['text'], whisper_words(path, cfg.get('lang', 'es')), lead, dur - tail)
            # The voiced span is the words' span: the energy bounds only tighten coarse edges.
            lead = round(min(max(lead, 0.0), words[0]['t0'] + 0.05), 3)
            tail = round(max(0.0, dur - max(words[-1]['t1'], dur - tail)), 3)
            entry = {'id': line['id'], 'text': line['text'], 'file': f, 'dur': dur, 'lead': lead, 'tail': tail, 'hash': h, 'words': words}
            cache[h] = entry
            with open(cpath, 'w', encoding='utf-8') as fh:
                json.dump(cache, fh, ensure_ascii=False)
        else:
            entry = cached
        out_lines.append({**entry, 'id': line['id'], 'gap': line['gap']})
    vo = {'provider': provider, 'voice': cfg.get('voice') or (os.environ.get('ELEVENLABS_VOICE_ID') if provider == 'eleven' else None), 'model': cfg.get('model') if provider == 'eleven' else None, 'lines': out_lines}
    tmpjs = os.path.join(src, 'vo.js.tmp')  # written whole, then renamed: never half a vo.js
    with open(tmpjs, 'w', encoding='utf-8') as f:
        f.write('// Generated by scripts/vo.py from VO.md: do not edit by hand (re-run vo.py build).\n')
        f.write('export default {\n')
        f.write(''.join(f' {json.dumps(k)}: {json.dumps(vo[k], ensure_ascii=False)},\n' for k in ('provider', 'voice', 'model')))
        f.write(' "lines": [\n' + ',\n'.join('  ' + json.dumps(l, ensure_ascii=False) for l in out_lines) + '\n ]\n}\n')
    os.replace(tmpjs, os.path.join(src, 'vo.js'))
    for l in out_lines:
        voiced = l['dur'] - l['lead'] - l['tail']
        n = len(l['words'])
        print(f"  {l['id']:<6} {voiced:5.2f} s voiced · {n} words · {n / max(voiced, 0.01):.1f} w/s")
    total = sum(l['dur'] - l['lead'] - l['tail'] for l in out_lines)
    print(f"vo.js written: {len(out_lines)} takes, {total:.1f} s of voice ({provider})" + ('  ← scratch voice: qa.py blocks delivery' if provider == 'say' else ''))


def voices():
    d = eleven_call(f'{API}/voices')
    for v in d.get('voices', []):
        labels = ', '.join(f'{k}: {x}' for k, x in (v.get('labels') or {}).items())
        print(f"{v['voice_id']}  {v.get('name', '')}  ({v.get('category', '')}{'; ' + labels if labels else ''})")


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in ('build', 'voices'):
        print(__doc__)
        sys.exit(1)
    if a[0] == 'voices':
        voices()
        sys.exit(0)
    if len(a) < 2:
        die('usage: vo.py build <src> [--provider eleven|say|file] [--only ids] [--force] [--dry-run]')
    SRC = os.path.abspath(a[1])
    prov = a[a.index('--provider') + 1] if '--provider' in a else 'eleven'
    if prov not in ('eleven', 'say', 'file'):
        die(f'unknown provider {prov}')
    only = set(a[a.index('--only') + 1].split(',')) if '--only' in a else None
    build(SRC, prov, only, '--force' in a, '--dry-run' in a)
