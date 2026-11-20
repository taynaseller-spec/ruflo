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
        # never cross a take cut / plan boundary: keep the chunk where most of it is spoken (SKILL 4i)
        for cut in sorted(set(P0.get('takes', [])) | {x[0] for x in plan}):
            cut = round(cut * 30) / 30
            if s < cut < e:
                if cut - s >= e_last - cut: e = cut - 0.006
                else: s = cut + 0.004
        seg = next((k for k, x in enumerate(plan) if x[0] <= s + 0.02 < x[1]), None)
        md = plan[seg][2] if seg is not None else 'talk'
        y = yseg.get(seg, ymode[md])
        TY = P0.get('caption_y_take')   # per-take y below the chin (talk), + presenter_shift in split
        if TY and md != 'full' and seg not in yseg:
            ti = max(0, sum(1 for cut in P0['takes'] if cut <= s + 0.02) - 1)
            y = TY[ti] + (P0.get('presenter_shift', 0) if md == 'split' else 0)
        # soft black blur behind the text, no outline (SKILL 4i)
        sh = "{\\1c&H000000&\\1a&H60&\\bord10\\3c&H000000&\\3a&HA0&\\blur16}"
        if c['kind'] == 'imp':
            txt = ' '.join(disp(x) for x in c['words'])
            mv = f"\\move(540,{y+70},540,{y},0,200)\\clip(0,{y-75},1080,{y+52})"
            ev.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},RImp,,0,0,0,,{{{mv}\\fad(80,0)}}{sh}{txt}")
            ev.append(f"Dialogue: 2,{_ts(s)},{_ts(e)},RImp,,0,0,0,,{{{mv}\\fad(80,0)}}{txt}")
            continue
        ent = "\\alpha&HFF&\\blur12\\fsp22\\t(0,260,0.6,\\alpha&H00&\\blur0\\fsp0)"
        if c['words']:
            txt = ' '.join(disp(x) for x in c['words'])
            ev.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},RBase,,0,0,0,,{{\\pos(540,{y})}}{sh}{txt}")
            ev.append(f"Dialogue: 2,{_ts(s)},{_ts(e)},RBase,,0,0,0,,{{\\pos(540,{y})}}{txt}")
        if c['key']:
            k = c['key']; ks = max(k['s'], s); txt = disp(k)
            ky = y + 78 if c['words'] else y
            ev.append(f"Dialogue: 1,{_ts(ks)},{_ts(e)},RSer,,0,0,0,,{{\\pos(540,{ky})\\bord10\\3c&H000000&\\1c&H000000&\\blur16{ent.replace('alpha&H00&', 'alpha&H70&')}}}{txt}")
            ev.append(f"Dialogue: 2,{_ts(ks)},{_ts(e)},RSer,,0,0,0,,{{\\pos(540,{ky}){ent}}}{txt}")
    return STYLES, ev
