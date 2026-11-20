"""Caption style "ref" (Referência nova, 2026-11-20) — see SKILL.md 4g.
Chunks of 1-3 lowercase words in Inter Medium with a soft blurred shadow; key words in large
Instrument Serif Italic that enter with blur + letter-spacing settle (attached under the current
chunk, like "em quantas / fotos"); impact phrases in Inter Bold, bigger, rising out of a mask.
build(words, plan, P0) -> (styles_text, [Dialogue lines]). Fonts in <workdir>/fonts:
Inter-Medium.otf, Inter-Bold.otf (rsms/inter v3.19), InstrumentSerif-Italic.ttf (OFL)."""
import re

STYLES = """Style: RBase,Inter Medium,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,40,40,0,1
Style: RSer,Instrument Serif,128,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00000000,0,1,0,0,100,100,0,0,1,1,0,5,40,40,0,1
Style: RImp,Inter Bold,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,-1,0,1,0,0,5,40,40,0,1
"""
PUNCT = r"[.,!?;:…]+$"


def _ts(t):
    t = max(0, t)
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


def _norm(w):
    return re.sub(r"[^\wà-ü]", "", w.lower())


def build(words, plan, P0, end):
    keys = {_norm(k) for k in P0.get('caption_keywords', [])}
    keep = set(P0.get('keep_case', []))
    impact = P0.get('caption_impact', [])          # [[start,end],...] phrases rendered big + rising
    caps_until = P0.get('caption_caps_until', 0)    # hook words before this time in CAPS (ref: "VOCÊ")
    ymode = P0.get('caption_y', {'talk': 1260, 'split': 1400, 'full': 1560})
    yseg = {int(k): v for k, v in P0.get('caption_y_seg', {}).items()}

    def disp(w):
        t = re.sub(r"\.\.\.$|[.,!;:…]+$", "", w['w']).strip()
        if w['s'] < caps_until: return t.upper()
        return t if t in keep else t.lower()

    def in_imp(w):
        return next((i for i, (a, b) in enumerate(impact) if a - 0.02 <= w['s'] < b), None)

    chunks = []  # dict(kind, words, key)
    cur = []

    def flush():
        nonlocal cur
        if cur: chunks.append(dict(kind='base', words=cur, key=None))
        cur = []
    i = 0
    while i < len(words):
        w = words[i]
        if w['s'] >= end: break
        im = in_imp(w)
        if im is not None:
            flush(); grp = []
            while i < len(words) and in_imp(words[i]) == im:
                grp.append(words[i]); i += 1
            # split long impact phrases into <=16-char pieces
            piece = []
            for g in grp:
                if piece and len(' '.join(disp(x) for x in piece + [g])) > 16:
                    chunks.append(dict(kind='imp', words=piece, key=None)); piece = []
                piece.append(g)
            if piece: chunks.append(dict(kind='imp', words=piece, key=None))
            continue
        if _norm(w['w']) in keys:
            if cur and len(cur) <= 2 and not re.search(PUNCT, cur[-1]['w']) and w['s'] - cur[-1]['e'] < 0.3:
                chunks.append(dict(kind='base', words=cur, key=w)); cur = []
            else:
                flush(); chunks.append(dict(kind='key', words=[], key=w))
            i += 1; continue
        if cur and (w['s'] - cur[-1]['e'] > 0.3 or len(cur) >= 3 or
                    len(' '.join(disp(x) for x in cur + [w])) > 15):
            flush()
        cur.append(w)
        if re.search(PUNCT, w['w']): flush()
        i += 1
    flush()

    ev = []
    for n, c in enumerate(chunks):
        ws = c['words'] + ([c['key']] if c['key'] else [])
        s = ws[0]['s']; e_last = ws[-1]['e']
        nxt = chunks[n + 1] if n + 1 < len(chunks) else None
        ns = (nxt['words'] + ([nxt['key']] if nxt['key'] else []))[0]['s'] if nxt else end
        e = ns if ns - e_last < 0.6 else e_last + 0.3
        e = min(e, end)
        seg = next((k for k, x in enumerate(plan) if x[0] <= s + 0.05 < x[1]), None)
        md = plan[seg][2] if seg is not None else 'talk'
        y = yseg.get(seg, ymode[md])
        sh = "{\\1c&H000000&\\1a&H38&\\bord7\\3c&H000000&\\3a&H90&\\blur12}"     # soft shadow layer (ref: no outline, diffuse shadow)
        if c['kind'] == 'imp':
            txt = ' '.join(disp(x) for x in c['words'])
            mv = f"\\move(540,{y+70},540,{y},0,200)\\clip(0,{y-75},1080,{y+52})"
            ev.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},RImp,,0,0,0,,{{{mv}\\fad(80,0)}}{sh}{txt}")
            ev.append(f"Dialogue: 2,{_ts(s)},{_ts(e)},RImp,,0,0,0,,{{{mv}\\fad(80,0)}}{txt}")
            continue
        ent = "\\alpha&HFF&\\blur12\\fsp22\\t(0,260,0.6,\\alpha&H00&\\blur0\\fsp0)"
        if c['words']:
            txt = ' '.join(disp(x) for x in c['words'])
            ev.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},RBase,,0,0,0,,{{\\pos(542,{y+3})}}{sh}{txt}")
            ev.append(f"Dialogue: 2,{_ts(s)},{_ts(e)},RBase,,0,0,0,,{{\\pos(540,{y})}}{txt}")
        if c['key']:
            k = c['key']; ks = k['s']; txt = disp(k)
            ky = y + 78 if c['words'] else y
            ev.append(f"Dialogue: 1,{_ts(ks)},{_ts(e)},RSer,,0,0,0,,{{\\pos(543,{ky+4})\\bord5\\3c&H000000&\\1c&H000000&\\blur12{ent.replace('alpha&H00&', 'alpha&H68&')}}}{txt}")
            ev.append(f"Dialogue: 2,{_ts(ks)},{_ts(e)},RSer,,0,0,0,,{{\\pos(540,{ky}){ent}}}{txt}")
    return STYLES, ev
