import subprocess, sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WD = sys.argv[1]
W, H, FPS = 1080, 1920, 30
DUR = 36.5
F = lambda n, s: ImageFont.truetype(f"{WD}/fonts/{n}", s)
SERIF = f"DMSerifDisplay-Regular.ttf"; XB = "Montserrat-ExtraBold.ttf"; SB = "Montserrat-SemiBold.ttf"

# ---------- items: (start, image, focal(fx,fy), verdict 'ok'/'no', verdict_time)
ITEMS = [
    (0.00, "4996", (0.55, 0.45), "no", 1.48),
    (2.23, "4986", (0.45, 0.55), "no", 3.78),
    (5.87, "4987", (0.55, 0.55), "no", 7.92),
    (8.83, "4988", (0.40, 0.40), "ok", 11.02),
    (11.73, "4992", (0.50, 0.32), "ok", 12.72),
    (13.33, "4991", (0.50, 0.35), "no", 15.00),
    (17.07, "4989", (0.50, 0.50), "ok", 18.64),
    (19.17, "4993", (0.50, 0.60), "no", 20.92),
    (22.63, "4994", (0.45, 0.40), "ok", 23.70),
    (24.30, "4995", (0.55, 0.40), "no", 26.54),
]
CARD_END = 28.50
# label captions above card (start, text)
LABELS = [(0.0, "Usar tônico"), (2.30, "Óleos essenciais"), (6.08, "Comprar um creme"), (6.84, "de mil reais"),
          (9.04, "Protetor solar"), (9.70, "todos os dias"), (11.96, "Vitamina C"), (13.48, "Máscaras caseiras"),
          (18.16, "Retinol"), (19.28, "Esfoliar a pele"), (20.08, "todos os dias"), (22.74, "Dormir bem"),
          (24.34, "Seguir tendências"), (25.50, "do TikTok")]
# final captions: (start, end, line1(sans small), line2(serif), t_line2, big)
FINAL = [(28.50, 29.40, "E o que", "mais importa", 28.84, False),
         (29.40, 30.30, "para a", "sua pele?", 29.76, False),
         (30.30, 30.88, "", "Constância", 30.34, False),
         (30.88, 32.70, "nas poucas coisas", "que funcionam", 31.54, False),
         (32.75, 33.50, "E já", "COMPARTILHA", 33.12, True),
         (33.50, 34.40, "com quem precisa", "ver isso", 34.02, False),
         (34.40, 35.30, "e me segue aqui", "que eu trago", 35.06, False),
         (35.30, 36.50, "umas dicas", "como essa", 35.74, False)]
def zoom_at(t):
    return 1.12 if 30.13 <= t < 32.75 else 1.0
ANCHOR = (540, 700)

ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
def smooth(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

def rrect_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); return m

def grad(w, h, c1, c2, diag=True):
    x = np.linspace(0, 1, w)[None, :]; y = np.linspace(0, 1, h)[:, None]
    k = (x * 0.6 + y * 0.4) if diag else (y + 0 * x)
    a = np.array(c1, float)[None, None, :]; b = np.array(c2, float)[None, None, :]
    return Image.fromarray((a + (b - a) * k[..., None]).astype(np.uint8))

def shadowed(img, blur=14, off=(0, 8), alpha=110, pad=40):
    w, h = img.size
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    sh.paste((0, 0, 0, 255), (pad + off[0], pad + off[1]), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sh); out.alpha_composite(img, (pad, pad)); return out, pad

# ---------- buttons
BW, BH = 390, 328
def button(label, kind, active):
    base = grad(BW, BH, (255, 214, 77), (255, 132, 58)) if active else grad(BW, BH, (252, 252, 252), (196, 196, 198))
    im = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); im.paste(base, (0, 0), rrect_mask(BW, BH, 26))
    d = ImageDraw.Draw(im)
    f = F(XB, 33 if len(label) < 12 else 29)
    d.text((BW / 2, 58), label, font=f, fill=(20, 20, 20), anchor="mm")
    cx, cy, r = BW / 2, 196, 92
    col = (76, 217, 100) if kind == "ok" else (240, 52, 64)
    hi = (130, 235, 140) if kind == "ok" else (255, 110, 110)
    circ = grad(2 * r, 2 * r, hi, col, diag=False)
    im.paste(circ, (int(cx - r), int(cy - r)), _circle(2 * r))
    if kind == "ok":
        d.line([(cx - 44, cy + 2), (cx - 12, cy + 34), (cx + 46, cy - 30)], fill="white", width=24, joint="curve")
        for p in [(cx - 44, cy + 2), (cx + 46, cy - 30)]: d.ellipse([p[0] - 12, p[1] - 12, p[0] + 12, p[1] + 12], fill="white")
    else:
        for a, b in [((cx - 38, cy - 38), (cx + 38, cy + 38)), ((cx + 38, cy - 38), (cx - 38, cy + 38))]:
            d.line([a, b], fill="white", width=24)
            for p in (a, b): d.ellipse([p[0] - 12, p[1] - 12, p[0] + 12, p[1] + 12], fill="white")
    return shadowed(im, 16, (0, 10), 90)

def _circle(s):
    m = Image.new("L", (s * 4, s * 4), 0); ImageDraw.Draw(m).ellipse([0, 0, s * 4 - 1, s * 4 - 1], fill=255)
    return m.resize((s, s), Image.LANCZOS)

BTN = {(k, a): button(l, k, a) for k, l in [("ok", "IMPORTANTE"), ("no", "NÃO IMPORTANTE")] for a in (False, True)}
BX = {"ok": 125, "no": 565}; BY = 1335

# ---------- card
CX, CY, CW, CH, BORD = 200, 985, 680, 324, 6
frame_gold = grad(CW, CH, (176, 128, 44), (246, 216, 128))
fg2 = grad(CW, CH, (246, 216, 128), (168, 118, 38), diag=False)
gold = Image.blend(frame_gold, fg2, 0.4)
CARD_MASK = rrect_mask(CW, CH, 20); IN_MASK = rrect_mask(CW - 2 * BORD, CH - 2 * BORD, 15)
SRC = {}
def load(name):
    if name not in SRC: SRC[name] = Image.open(f"{WD}/imgc/{name}.png").convert("RGB")
    return SRC[name]

def card(item, t_local):
    _, name, (fx, fy), _, _ = item
    src = load(name); iw, ih = CW - 2 * BORD, CH - 2 * BORD
    z = 1.0 + 0.05 * min(t_local / 4.0, 1)  # slow push
    s = max(iw / src.width, ih / src.height) * z
    sw, sh = src.width * s, src.height * s
    x0 = min(max(fx * sw - iw / 2, 0), sw - iw); y0 = min(max(fy * sh - ih / 2, 0), sh - ih)
    crop = src.resize((math.ceil(sw), math.ceil(sh)), Image.BICUBIC).crop((int(x0), int(y0), int(x0) + iw, int(y0) + ih))
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); im.paste(gold, (0, 0), CARD_MASK); im.paste(crop, (BORD, BORD), IN_MASK)
    return shadowed(im, 18, (0, 10), 100)

def place(canvas, img_pad, x, y, scale=1.0, alpha=1.0):
    img, pad = img_pad
    if alpha <= 0: return
    if scale != 1.0:
        w, h = img.size; nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        cx, cy = x - pad + w / 2, y - pad + h / 2
        img = img.resize((nw, nh), Image.BICUBIC); px, py = cx - nw / 2, cy - nh / 2
    else: px, py = x - pad, y - pad
    if alpha < 1: img = img.copy(); img.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    canvas.alpha_composite(img, (int(round(px)), int(round(py))))

# ---------- text
def text_img(txt, font, fill=(255, 255, 255)):
    bb = font.getbbox(txt, anchor="ls"); w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 60
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ox, oy = 30 - bb[0], 30 - bb[1]
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((ox, oy + 3), txt, font=font, fill=(0, 0, 0, 170), anchor="ls")
    sh = sh.filter(ImageFilter.GaussianBlur(7)); im.alpha_composite(sh)
    d.text((ox, oy), txt, font=font, fill=fill, anchor="ls", stroke_width=1, stroke_fill=(0, 0, 0, 60))
    return im, oy  # oy = baseline y inside img
TC = {}
def draw_text(canvas, txt, font_key, size, cx, baseline, alpha=1.0, rise=0):
    k = (txt, font_key, size)
    if k not in TC: TC[k] = text_img(txt, F(font_key, size))
    im, by = TC[k]
    if alpha < 1: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(baseline - by + rise)))

def fit_size(txt, key, size, maxw=960):
    while F(key, size).getlength(txt) > maxw: size -= 2
    return size

# ---------- frame loop
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"{WD}/main.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{WD}/main.mov", "-map", "0:v", "-map", "1:a",
                        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,volume=1.5dB,alimiter=limit=0.92:level=false,afade=t=out:st=36.1:d=0.4",
                        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", f"{WD}/final.mp4"], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS
    base = Image.frombuffer("RGB", (W, H), raw)
    z = zoom_at(t)
    if z != 1.0:
        ax, ay = ANCHOR; nw, nh = round(W * z), round(H * z)
        x0 = min(max(ax * z - ax, 0), nw - W); y0 = min(max(ay * z - ay, 0), nh - H)
        base = base.resize((nw, nh), Image.BICUBIC).crop((int(x0), int(y0), int(x0) + W, int(y0) + H))
    cv = base.convert("RGBA")
    if t < CARD_END:
        out = smooth((CARD_END - t) / 0.22)  # exit
        ex_scale = 0.9 + 0.1 * out
        idx = max(i for i, it in enumerate(ITEMS) if it[0] <= t + 1e-6)
        it = ITEMS[idx]; tl = t - it[0]
        # card pop on change (first item: entrance)
        p = ease(tl / 0.28)
        sc = (0.9 + 0.1 * p) * ex_scale
        place(cv, card(it, tl), CX, CY, sc, min(1, 0.35 + 0.65 * p) * out if idx else p * out)
        for k in ("ok", "no"):
            active = it[3] == k and t >= it[4]
            bs = 1.0
            if active:
                q = (t - it[4]) / 0.30
                bs = 1 + 0.07 * math.sin(math.pi * min(q, 1)) if q < 1 else 1.0
            ent = ease(t / 0.3)
            place(cv, BTN[(k, active)], BX[k], BY, bs * ex_scale * (0.9 + 0.1 * ent), out * ent)
        lab = [l for l in LABELS if l[0] <= t + 1e-6][-1]
        la = smooth((t - lab[0]) / 0.12) * out
        sz = fit_size(lab[1], SERIF, 84)
        draw_text(cv, lab[1], SERIF, sz, 540, 955, la, rise=int(10 * (1 - smooth((t - lab[0]) / 0.15))))
    for s, e, l1, l2, t2, big in FINAL:
        if s <= t < e:
            a = smooth((t - s) / 0.1) * smooth((e - t) / 0.06 if e < 36.4 else 1)
            if l1: draw_text(cv, l1, SB, 46, 540, 935, a)
            if t >= t2:
                a2 = smooth((t - t2) / 0.1) * a / max(smooth((t - s) / 0.1), 1e-3) if False else smooth((t - t2) / 0.1)
                a2 *= smooth((e - t) / 0.06) if e < 36.4 else 1
                if big:
                    sc_ = 1 + 0.25 * (1 - ease((t - t2) / 0.25))
                    size = fit_size(l2, SERIF, int(150 * sc_), 1000)
                    draw_text(cv, l2, SERIF, size, 540, 1080, a2)
                else:
                    draw_text(cv, l2, SERIF, fit_size(l2, SERIF, 92), 540, 1025, a2, rise=int(8 * (1 - smooth((t - t2) / 0.15))))
    enc.stdin.write(cv.convert("RGB").tobytes())
    n += 1
    if n % 150 == 0: print(n, flush=True)
enc.stdin.close(); enc.wait(); dec.wait(); print("frames", n)
