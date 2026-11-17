"""More animated half-screen panels (same style as graphics.py): real-estate tax / tax reform script
(consórcio consultant, 2026-11-17). Times inside each panel are seconds from the panel start, taken
from words.json. Usage: graphics3.py <outdir> <name> <duration>   |   graphics3.py <outdir> preview"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graphics as g
from graphics import (Image, ImageDraw, W, H, S, NAVY0, GOLD, WHITE, MUTED, RED, GREEN,
                      text, rrect, finish, prog, ease_io, clamp, house, label, font)

def layer():
    L = Image.new('RGBA', (W*S, H*S)); return L, ImageDraw.Draw(L)

def check(d, cx, cy, s, col, a):
    if a <= 0: return
    c = col + (int(255*clamp(a)),); s *= S; cx *= S; cy *= S
    d.line([(cx-s*0.5, cy), (cx-s*0.12, cy+s*0.4), (cx+s*0.6, cy-s*0.45)], fill=c, width=int(9*S), joint='curve')

def strike(d, x0, x1, y, k, col=RED, w=8):
    if k > 0: d.line([(x0*S, y*S), ((x0+(x1-x0)*k)*S, y*S)], fill=col+(255,), width=w*S)

def pill(d, cx, cy, s, size, a, fill=GOLD, fg=NAVY0, w='xb', pad=46):
    if a <= 0: return
    tw = font(w, size).getlength(s)/S
    rrect(d, [cx-tw/2-pad, cy-size*0.85, cx+tw/2+pad, cy+size*0.85], int(size*0.85), fill=fill, alpha=a)
    text(d, (cx, cy), s, w, size, fg, a)

def eye(d, cx, cy, r, a, open_=1.0, col=WHITE):
    if a <= 0: return
    c = col + (int(255*clamp(a)),); k = max(0.05, open_)
    up = [(cx + r*math.cos(t), cy - r*0.55*k*math.sin(t)) for t in [math.pi*i/24 for i in range(25)]]
    lo = [(cx + r*math.cos(t), cy + r*0.55*k*math.sin(t)) for t in [math.pi*i/24 for i in range(25)]]
    d.line([(x*S, y*S) for x, y in up], fill=c, width=7*S, joint='curve')
    d.line([(x*S, y*S) for x, y in lo], fill=c, width=7*S, joint='curve')
    pr = r*0.3*k
    if pr > 2: d.ellipse([(cx-pr)*S, (cy-pr)*S, (cx+pr)*S, (cy+pr)*S], fill=GOLD+(int(255*clamp(a)),))

def shield(d, cx, cy, s, a):
    if a <= 0: return
    c = GOLD + (int(255*clamp(a)),); s *= S; cx *= S; cy *= S
    pts = [(cx, cy-s), (cx+s*0.8, cy-s*0.65), (cx+s*0.72, cy+s*0.15), (cx, cy+s), (cx-s*0.72, cy+s*0.15), (cx-s*0.8, cy-s*0.65)]
    d.polygon(pts, outline=c, width=int(7*S))
    check(d, cx/S, cy/S, s/S*0.55, GOLD, a)

# ---------------- panels ----------------
def g_2027(t):
    L, d = layer()
    a = prog(t, 0.1, 0.6); house(d, 540, 175, 70, GOLD, a)
    b = prog(t, 0.9); label(d, 300, 'COMPRAR IMÓVEL EM', b)
    k = clamp((t-1.55)/0.55); yr = 2024 + int(round(3*ease_io(k)))
    c = prog(t, 1.55, 0.35)
    text(d, (540, 410-18*c), str(yr), 'xb', 150, WHITE, c)
    e = prog(t, 3.25, 0.4); pill(d, 540, 560-14*e, 'O QUE NINGUÉM TE CONTA', 44, e)
    return finish(L)

def g_itbi(t):
    L, d = layer()
    a = prog(t, 0.1); label(d, 110, 'O QUE VOCÊ ACHA QUE PAGA', a)
    b = prog(t, 0.3); rrect(d, [140, 175, 940, 335], 26, fill=WHITE, alpha=0.06*b, outline=MUTED, width=2)
    text(d, (190, 255), 'VALOR DO IMÓVEL', 'xb', 54, WHITE, b, anchor='lm')
    c = prog(t, 1.35, 0.35); sc = 0.8 + 0.2*c
    text(d, (330, 450), '+', 'xb', 80, GOLD, c)
    rrect(d, [540-150*sc, 450-55*sc, 540+150*sc, 450+55*sc], 30, fill=GOLD, alpha=c)
    text(d, (540, 450), 'ITBI', 'xb', int(72*sc), NAVY0, c)
    e = prog(t, 1.8); text(d, (540, 580-12*e), 'SÓ ISSO?', 'xb', 54, RED, e)
    return finish(L)

def g_embutidos(t):
    L, d = layer()
    a = prog(t, 0.05); label(d, 105, 'PREÇO DO IMÓVEL', a)
    x0, x1, y0, y1 = 140, 940, 170, 300
    g1 = ease_io((t-0.15)/0.7); rrect(d, [x0, y0, x0+(x1-x0)*g1, y1], 22, fill=WHITE, alpha=prog(t, 0.15, 0.3))
    # taxes hidden inside the bar are revealed one by one
    tx = [(1.45, 0.62, 'IMPOSTO'), (1.75, 0.76, 'IMPOSTO'), (2.05, 0.88, 'IMPOSTO')]
    for st, fx, s in tx:
        r = prog(t, st, 0.35)
        if r > 0:
            xa = x0 + (x1-x0)*(fx-0.12); xb = x0 + (x1-x0)*fx
            rrect(d, [xa+4, y0+8, xb-4, y1-8], 14, fill=RED, alpha=r)
    k = prog(t, 1.5); text(d, (540, 395-12*k), 'IMPOSTOS EMBUTIDOS', 'xb', 60, RED, k)
    e = prog(t, 2.95); eye(d, 380, 520, 70, e, open_=1-ease_io((t-3.2)/0.4))
    if t > 3.35: d.line([(318*S, 585*S), (442*S, 455*S)], fill=RED+(int(255*prog(t, 3.35, 0.2)),), width=8*S)
    text(d, (480, 520), 'VOCÊ NÃO VÊ', 'xb', 56, WHITE, prog(t, 3.1), anchor='lm')
    return finish(L)

def g_reforma(t):
    L, d = layer()
    a = prog(t, 0.15); label(d, 100, 'REFORMA TRIBUTÁRIA', a)
    old = ['PIS', 'COFINS', 'ICMS', 'ISS', 'IPI']; xs = [190, 360, 540, 715, 890]
    out = ease_io((t-3.0)/0.6)
    for i, (s, x) in enumerate(zip(old, xs)):
        r = prog(t, 1.2+0.14*i, 0.35)*(1-0.7*out)
        y = 215 - 25*(1-prog(t, 1.2+0.14*i, 0.35))
        tw = font('b', 34).getlength(s)/S
        rrect(d, [x-tw/2-22, y-34, x+tw/2+22, y+34], 20, fill=WHITE, alpha=0.08*r, outline=MUTED, width=2)
        text(d, (x, y), s, 'b', 34, WHITE, r)
        strike(d, x-tw/2-14, x+tw/2+14, y, ease_io((t-2.9-0.08*i)/0.3), w=5)
    ar = prog(t, 3.3); text(d, (540, 320), '↓', 'xb', 64, GOLD, ar)
    for st, cx, s in [(3.75, 360, 'IBS'), (4.6, 720, 'CBS')]:
        c = prog(t, st, 0.4); sc = 0.85 + 0.15*c
        rrect(d, [cx-150*sc, 465-75*sc, cx+150*sc, 465+75*sc], 30, fill=GOLD, alpha=c)
        text(d, (cx, 465), s, 'xb', int(88*sc), NAVY0, c)
    return finish(L)

def g_visivel(t):
    L, d = layer()
    a = prog(t, 0.1, 0.4); eye(d, 540, 200, 120, a, open_=ease_io((t-0.15)/0.5))
    b = prog(t, 0.6); text(d, (540, 390-14*b), 'MAIS VISÍVEL', 'xb', 84, WHITE, b)
    c = prog(t, 1.4); pill(d, 540, 530-12*c, 'NA HORA DA COMPRA', 44, c)
    return finish(L)

def g_estrategia(t):
    L, d = layer()
    a = prog(t, 0.15); label(d, 100, 'COMO SE COMPRA UM IMÓVEL', a)
    b = prog(t, 1.25); text(d, (540, 245), 'IMPULSO', 'xb', 96, WHITE, b*(1-0.55*prog(t, 1.75)))
    tw = font('xb', 96).getlength('IMPULSO')/S
    strike(d, 540-tw/2-20, 540+tw/2+20, 245, ease_io((t-1.6)/0.3), w=10)
    xa = prog(t, 1.75); xc, r = 540-tw/2-70, 26
    if xa > 0:
        for q in (1, -1): d.line([((xc-r)*S, (245-r*q)*S), ((xc+r)*S, (245+r*q)*S)], fill=RED+(int(255*xa),), width=9*S)
    c = prog(t, 2.45, 0.4)
    rrect(d, [170, 410, 910, 560], 75, fill=GOLD, alpha=c)
    check(d, 260, 485, 40, NAVY0, c)
    text(d, (575, 485), 'ESTRATÉGIA', 'xb', 82, NAVY0, c)
    return finish(L)

def g_consorcio2(t):
    L, d = layer()
    a = prog(t, 0.05); shield(d, 540, 115, 62, a)
    text(d, (540, 225), 'CONSÓRCIO', 'xb', 46, GOLD, a, spacing=4)
    rows = [(0.2, 'CARTA REAJUSTADA'), (1.65, 'SEM JUROS'), (3.4, 'CRÉDITO ATUALIZADO')]
    for i, (st, s) in enumerate(rows):
        r = prog(t, st); y = 330 + 100*i; x = 200 + 30*(1-r)
        d.ellipse([(x-28)*S, (y-28)*S, (x+28)*S, (y+28)*S], fill=GREEN+(int(255*r),))
        check(d, x, y, 17, NAVY0, r)
        text(d, (x+58, y), s, 'xb', 52, WHITE, r, anchor='lm')
    return finish(L)

def g_cta2(t):
    L, d = layer()
    a = prog(t, 0.0, 0.3); text(d, (540, 120), 'COMENTE', 'sb', 36, GOLD, a, spacing=8)
    b = prog(t, 0.1, 0.4); sc = 0.9 + 0.1*b; w2, h2 = 400*sc, 90*sc; cx, cy = 540, 275
    rrect(d, [cx-w2, cy-h2, cx+w2, cy+h2], 40, fill=WHITE, alpha=b)
    if b > 0: d.polygon([((cx-170)*S, (cy+h2-2)*S), ((cx-110)*S, (cy+h2-2)*S), ((cx-195)*S, (cy+h2+60)*S)], fill=WHITE+(int(255*b),))
    word = 'PLANEJAMENTO'; k = int(clamp((t-0.3)/0.55)*len(word)+0.999) if t > 0.3 else 0
    text(d, (cx, cy), word[:k], 'xb', 76, NAVY0, 1.0)
    if 0 < k < len(word):
        tw = font('xb', 76).getlength(word[:k])/S; d.line([((cx+tw/2+8)*S, (cy-38)*S), ((cx+tw/2+8)*S, (cy+38)*S)], fill=GOLD+(255,), width=5*S)
    c = prog(t, 1.8); text(d, (540, 470-12*c), 'TE CHAMO NO DIRECT', 'xb', 54, WHITE, c)
    e = prog(t, 2.95); text(d, (540, 560-10*e), 'SÓ PARA QUEM ME SEGUE', 'b', 36, GOLD, e, spacing=3)
    return finish(L)

g.PANELS.update({'2027': g_2027, 'itbi': g_itbi, 'embutidos': g_embutidos, 'reforma': g_reforma, 'visivel': g_visivel,
                 'estrategia': g_estrategia, 'consorcio2': g_consorcio2, 'cta2': g_cta2})
NEW = ['2027', 'itbi', 'embutidos', 'reforma', 'visivel', 'estrategia', 'consorcio2', 'cta2']
if __name__ == '__main__':
    out = sys.argv[1]
    if sys.argv[2] == 'preview':   # static sheet: every new panel at its final state
        ims = [g.PANELS[n](float(sys.argv[3]) if len(sys.argv) > 3 else 5.0).resize((540, 480)) for n in NEW]
        sheet = Image.new('RGB', (540*4, 480*2))
        for i, im in enumerate(ims): sheet.paste(im, (540*(i % 4), 480*(i//4)))
        sheet.save(f'{out}/gfx_preview.png')
    else:
        g.render(sys.argv[2], float(sys.argv[3]), f'{out}/g_{sys.argv[2]}.mp4')
