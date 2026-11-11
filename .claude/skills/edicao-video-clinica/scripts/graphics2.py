"""Animated half-screen scenes (1080x960) for the milk / A2 video. Data-driven: each scene is a
list of elements with cue times (seconds from scene start). Ambient motion: floating milk bubbles.
Usage: graphics2.py <outdir> <scene_name> <duration>"""
import sys, math, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS=30; W,H=1080,960; S=2
FD='/usr/share/fonts/opentype/inter/'
BG0=(9,26,52); BG1=(18,48,88); MILK=(250,248,240); BLUE=(142,197,255); GOLD=(226,186,110)
WHITE=(246,246,244); MUTED=(160,180,205); RED=(236,98,92); GREEN=(92,206,150)
_fc={}
def F(w,s):
    k=(w,s)
    if k not in _fc: _fc[k]=ImageFont.truetype(FD+{'xb':'Inter-ExtraBold.otf','b':'Inter-Bold.otf','sb':'Inter-SemiBold.otf'}[w],s*S)
    return _fc[k]
def cl(x,a=0.0,b=1.0): return max(a,min(b,x))
def eo(x): x=cl(x); return 1-(1-x)**3
def sm(x): x=cl(x); return x*x*(3-2*x)
def pr(t,c,d=0.4): return eo((t-c)/d)
def A(c,a): return tuple(c)+(int(255*cl(a)),)
# ---------- background with ambient bubbles ----------
_bg=None
def bg_base():
    global _bg
    if _bg is None:
        im=Image.new('RGB',(W*S,H*S)); d=ImageDraw.Draw(im)
        for y in range(H*S):
            f=y/(H*S); d.line([(0,y),(W*S,y)],fill=tuple(int(BG1[i]*(1-f)+BG0[i]*f) for i in range(3)))
        g=Image.new('L',im.size,0); ImageDraw.Draw(g).ellipse([W*S*0.1,-H*S*0.4,W*S*0.9,H*S*0.5],fill=70)
        g=g.filter(ImageFilter.GaussianBlur(170*S)); _bg=Image.composite(Image.new('RGB',im.size,(48,92,150)),im,g)
    return _bg.copy()
rng=random.Random(5); BUB=[(rng.uniform(0,W),rng.uniform(0,H),rng.uniform(6,26),rng.uniform(18,45),rng.uniform(0,6.28)) for _ in range(26)]
def bubbles(d,t):
    for x,y0,r,sp,ph in BUB:
        y=(y0-sp*t)%(H+60)-30; xx=x+10*math.sin(t*0.8+ph)
        d.ellipse([(xx-r)*S,(y-r)*S,(xx+r)*S,(y+r)*S],outline=A(MILK,0.10),width=2*S)
# ---------- primitives ----------
def text(d,x,y,s,w,size,col,a,anchor='mm',sp=0):
    if a<=0: return
    if sp:
        f=F(w,size); ws=[f.getlength(c)+sp*S for c in s]; tot=sum(ws)-sp*S; cx=x*S-tot/2
        for c,wd in zip(s,ws): d.text((cx,y*S),c,font=f,fill=A(col,a),anchor='l'+anchor[1]); cx+=wd
    else: d.text((x*S,y*S),s,font=F(w,size),fill=A(col,a),anchor=anchor)
def rr(d,b,r,fill=None,ol=None,w=1,a=1.0):
    d.rounded_rectangle([v*S for v in b],r*S,fill=A(fill,a) if fill else None,outline=A(ol,a) if ol else None,width=w*S)
def glass(d,cx,cy,h,level,t,a,strike=0.0):
    if a<=0: return
    wt,wb=h*0.62,h*0.48; top,bot=cy-h/2,cy+h/2
    lv=bot-(h*0.9)*level
    pts=[]
    for i in range(41):
        u=i/40; x=cx-wt/2+(wt)*u; pts.append((x,lv+6*math.sin(u*9+t*4)))
    # milk body (clip to trapezoid approx)
    poly=[(x*S,y*S) for x,y in pts]+[((cx+wb/2)*S,bot*S),((cx-wb/2)*S,bot*S)]
    if level>0.02: d.polygon(poly,fill=A(MILK,a*0.95))
    d.line([((cx-wt/2)*S,top*S),((cx-wb/2)*S,bot*S),((cx+wb/2)*S,bot*S),((cx+wt/2)*S,top*S)],fill=A(BLUE,a),width=6*S,joint='curve')
    if strike>0:
        L=h*0.75; k=sm(strike)
        d.line([((cx-L/2)*S,(cy-L/2)*S),((cx-L/2+L*k)*S,(cy-L/2+L*k)*S)],fill=A(RED,a),width=12*S)
def carton(d,cx,cy,h,a,label='LEITE',badge=None,ba=0.0):
    if a<=0: return
    w=h*0.55; top=cy-h/2
    d.polygon([((cx-w/2)*S,(top+h*0.22)*S),(cx*S,(top)*S),((cx+w/2)*S,(top+h*0.22)*S)],fill=A(BLUE,a))
    rr(d,[cx-w/2,top+h*0.22,cx+w/2,cy+h/2],10,fill=MILK,a=a)
    d.rectangle([(cx-w/2)*S,(cy-h*0.05)*S,(cx+w/2)*S,(cy+h*0.12)*S],fill=A(BLUE,a))
    text(d,cx,cy+h*0.035,label,'xb',int(h*0.09),BG0,a)
    if badge and ba>0:
        r=h*0.2*(0.6+0.4*eo(ba)); bx,by=cx-w/2,cy-h*0.2
        d.ellipse([(bx-r)*S,(by-r)*S,(bx+r)*S,(by+r)*S],fill=A(GREEN,ba))
        for i,ln in enumerate(badge.split('\n')): text(d,bx,by+(i-(badge.count('\n'))/2)*r*0.42,ln,'xb',int(r*0.38),WHITE,ba)
def check(d,cx,cy,s,col,a):
    if a<=0: return
    d.line([((cx-s*0.5)*S,cy*S),((cx-s*0.15)*S,(cy+s*0.35)*S),((cx+s*0.55)*S,(cy-s*0.4)*S)],fill=A(col,a),width=int(s*0.18)*S,joint='curve')
def cross(d,cx,cy,s,col,a):
    if a<=0: return
    for k in (1,-1): d.line([((cx-s/2)*S,(cy-k*s/2)*S),((cx+s/2)*S,(cy+k*s/2)*S)],fill=A(col,a),width=int(s*0.16)*S)
def warn(d,cx,cy,s,a):
    if a<=0: return
    d.polygon([(cx*S,(cy-s*0.55)*S),((cx+s*0.6)*S,(cy+s*0.45)*S),((cx-s*0.6)*S,(cy+s*0.45)*S)],fill=A(GOLD,a))
    text(d,cx,cy+s*0.08,'!','xb',int(s*0.62),BG0,a)
def magnifier(d,cx,cy,r,a):
    if a<=0: return
    d.ellipse([(cx-r)*S,(cy-r)*S,(cx+r)*S,(cy+r)*S],outline=A(WHITE,a),width=10*S)
    d.line([((cx+r*0.72)*S,(cy+r*0.72)*S),((cx+r*1.5)*S,(cy+r*1.5)*S)],fill=A(WHITE,a),width=18*S)
def plane(d,cx,cy,s,a):
    if a<=0: return
    d.polygon([((cx-s)*S,(cy)*S),((cx+s)*S,(cy-s*0.8)*S),((cx+s*0.2)*S,(cy+s*0.8)*S)],fill=A(WHITE,a))
    d.polygon([((cx-s*0.1)*S,(cy+s*0.05)*S),((cx+s)*S,(cy-s*0.8)*S),((cx+s*0.05)*S,(cy+s*0.45)*S)],fill=A(BLUE,a))
def circle_badge(d,cx,cy,r,txt,col,a,glow=0.0):
    if a<=0: return
    if glow>0:
        for k in range(4): rg=r+10+k*12; d.ellipse([(cx-rg)*S,(cy-rg)*S,(cx+rg)*S,(cy+rg)*S],outline=A(col,glow*(0.35-k*0.08)),width=4*S)
    d.ellipse([(cx-r)*S,(cy-r)*S,(cx+r)*S,(cy+r)*S],fill=A(col,a))
    text(d,cx,cy,txt,'xb',int(r*0.75),BG0,a)
def line_in(d,t,c,y,s,w='xb',size=58,col=WHITE,dy=18,x=540):
    a=pr(t,c); text(d,x,y+dy*(1-a),s,w,size,col,a)
def kicker(d,t,c,y,s): text(d,540,y,s,'sb',30,GOLD,pr(t,c),sp=6)
# ---------- scenes ----------
def s_cortar(d,t):
    glass(d,540,250,300,0.15+0.6*sm(t/1.6),t,pr(t,0.0))
    line_in(d,t,0.5,470,'CORTAR O LEITE?'); line_in(d,t,2.9,560,'BARRIGA RECLAMOU?','b',46,BLUE)
    a=pr(t,3.55,0.25);
    if a>0: rr(d,[680,190,960,280],45,fill=GOLD,a=a); text(d,820,235,'CALMA!','xb',56,BG0,a)
def s_tirar(d,t):
    glass(d,540,260,320,0.75,t,pr(t,0.0),strike=(t-4.9)/0.4)
    line_in(d,t,1.2,480,'TIRAR O LEITE DA VIDA?','xb',54)
    line_in(d,t,4.9,565,'ACABOU PRO LEITE?','b',46,RED)
def s_erro(d,t):
    warn(d,540,230,190,pr(t,0.15)); line_in(d,t,1.2,440,'PODE SER','b',50,MUTED); line_in(d,t,1.35,520,'UM ERRO','xb',86,GOLD)
def s_culpado(d,t):
    glass(d,470,270,280,0.7,t,pr(t,0.0)); mx=470+150*math.sin(min(t,3)*1.6)
    magnifier(d,mx,250,95,pr(t,0.3))
    line_in(d,t,1.2,480,'O CULPADO É O LEITE?','xb',54); line_in(d,t,2.85,565,'NEM SEMPRE','xb',58,GOLD)
def s_50(d,t):
    n=int(50*sm((t-0.4)/1.0)); a=pr(t,0.3)
    text(d,540,250,f'{n}+','xb',190,GOLD,a)
    line_in(d,t,2.0,470,'DIGESTÃO','xb',62); line_in(d,t,2.2,550,'MAIS SENSÍVEL','b',50,BLUE)
def s_causas(d,t):
    kicker(d,t,0.1,90,'PODE VIR DE')
    items=[(1.05,'INTESTINO'),(2.15,'GASES'),(3.1,'CARBOIDRATOS QUE FERMENTAM'),(4.65,'ADOÇANTE'),(5.7,'OUTRO PROBLEMA DE SAÚDE')]
    for i,(c,s) in enumerate(items):
        a=pr(t,c); y=165+90*i; x=150+30*(1-a)
        d.ellipse([(x-12)*S,(y-12)*S,(x+12)*S,(y+12)*S],fill=A(BLUE,a))
        text(d,x+40,y,s,'b',46,WHITE,a,anchor='lm')
def s_lactose(d,t):
    carton(d,330,300,330,pr(t,0.1),badge='ZERO\nLACTOSE',ba=pr(t,4.0,0.35))
    line_in(d,t,2.35,230,'INTOLERÂNCIA','xb',56,WHITE,x=750); line_in(d,t,2.5,300,'À LACTOSE?','xb',56,GOLD,x=750)
    check(d,750,420,90,GREEN,pr(t,5.2,0.3)); text(d,750,520,'COSTUMA RESOLVER','b',36,GREEN,pr(t,5.25))
def s_ninguem(d,t):
    r=120+380*sm((t-0.1)/0.8)
    d.ellipse([(540-r)*S,(300-r*0.6)*S,(540+r)*S,(300+r*0.6)*S],fill=A((60,110,175),0.35*pr(t,0.1)))
    line_in(d,t,0.6,260,'QUASE NINGUÉM','xb',72); line_in(d,t,0.8,350,'SABE DISSO','xb',72,GOLD)
def s_proteina(d,t):
    line_in(d,t,0.9,120,'SEM INTOLERÂNCIA','b',46,MUTED); line_in(d,t,3.3,195,'MAS PASSA MAL','xb',58,RED)
    carton(d,330,420,280,pr(t,4.1),label='COMUM')
    line_in(d,t,6.3,390,'PROTEÍNA','xb',66,GOLD,x=720); line_in(d,t,6.45,465,'DO LEITE','xb',50,WHITE,x=720)
def s_a1a2(d,t):
    kicker(d,t,0.1,90,'2 TIPOS DE PROTEÍNA')
    circle_badge(d,340,280,110,'A1',MUTED,pr(t,1.85,0.35))
    circle_badge(d,740,280,125,'A2',GOLD,pr(t,2.65,0.35),glow=pr(t,3.4)*(0.75+0.25*math.sin(t*4)))
    line_in(d,t,4.2,480,'VACA QUE PRODUZ A2','xb',50); line_in(d,t,5.3,555,'NATURALMENTE','b',44,GOLD)
def s_digerir(d,t):
    kicker(d,t,0.1,90,'DIGESTÃO')
    a1=pr(t,1.4); text(d,170,200,'LEITE COMUM','b',36,MUTED,a1,anchor='ls'); rr(d,[170,220,170+700*sm((t-1.5)/0.8),280],14,fill=RED,a=a1)
    a2=pr(t,2.4); text(d,170,350,'A2','b',36,GOLD,a2,anchor='ls'); rr(d,[170,370,170+300*sm((t-2.5)/0.8),430],14,fill=GREEN,a=a2)
    text(d,170+300*sm((t-2.5)/0.8)+30,400,'MAIS LEVE','xb',40,GREEN,pr(t,3.4),anchor='lm')
    line_in(d,t,4.9,540,'MAIS FÁCIL DE DIGERIR','xb',52)
def s_junta(d,t):
    k=sm((t-3.5)/0.6); x1=360+80*k; x2=720-80*k
    circle_badge(d,x1,280,120,'A2',GOLD,pr(t,2.35,0.35))
    a=pr(t,3.35,0.35); r=120
    if a>0:
        d.ellipse([(x2-r)*S,(280-r)*S,(x2+r)*S,(280+r)*S],fill=A(GREEN,a))
        text(d,x2,255,'ZERO','xb',46,WHITE,a); text(d,x2,310,'LACTOSE','xb',40,WHITE,a)
    text(d,540,280,'+','xb',90,WHITE,pr(t,3.0)*(1-k))
    line_in(d,t,1.4,520,'AS DUAS COISAS JUNTAS','xb',50)
def s_naocorte(d,t):
    a=pr(t,0.2); rr(d,[440,100,640,300],40,ol=RED,w=10,a=a); cross(d,540,200,110,RED,a)
    line_in(d,t,0.5,400,'NÃO CORTE POR','xb',56); line_in(d,t,0.65,470,'CONTA PRÓPRIA','xb',56,RED)
    line_in(d,t,2.1,560,'DESCUBRA A CAUSA','b',46,GOLD)
def s_bom(d,t):
    glass(d,240,330,330,0.8,t,pr(t,0.1))
    kicker(d,t,1.2,110,'O QUE O LEITE TEM DE BOM')
    for i,(c,s) in enumerate([(2.6,'PROTEÍNA'),(3.65,'CÁLCIO'),(4.3,'NUTRIENTES')]):
        a=pr(t,c); y=230+110*i; check(d,470,y,50,GREEN,a); text(d,520,y,s,'xb',58,WHITE,a,anchor='lm')
def s_responde(d,t):
    text(d,540,110,'RESPONDE AQUI','sb',32,GOLD,pr(t,0.1),sp=6)
    b=pr(t,0.2,0.45); rr(d,[150,170,930,420],50,fill=WHITE,a=b)
    if b>0: d.polygon([(260*S,418*S),(330*S,418*S),(230*S,490*S)],fill=A(WHITE,b))
    s='A2 × ZERO LACTOSE'; k=int(cl((t-0.5)/0.9)*len(s)+0.999) if t>0.5 else 0
    text(d,540,265,s[:k],'xb',64,BG0,1.0); text(d,540,350,'VOCÊ JÁ SABIA?','b',44,BG1,pr(t,1.6))
def s_envia(d,t):
    k=sm((t-0.2)/1.2); plane(d,300+480*k,260-90*k,70,pr(t,0.15)*(1-sm((t-1.6)/0.4)))
    line_in(d,t,0.35,430,'ENVIE PARA QUEM','xb',54); line_in(d,t,0.5,505,'CORTOU O LEITE','xb',54,GOLD)
def s_segue(d,t):
    a=pr(t,0.2); text(d,540,170,'NUTRI','sb',36,GOLD,a,sp=8); line_in(d,t,0.3,250,'ALEXANDRE SILVA','xb',70)
    b=pr(t,1.55,0.35); sc=1+0.06*math.sin(max(0,t-1.9)*6)*(t>1.9)
    rr(d,[540-170*sc,370-50*sc,540+170*sc,370+50*sc],50,fill=BLUE if t<1.95 else GOLD,a=b)
    text(d,540-(18 if t>=1.95 else 0),370,'SEGUIR' if t<1.95 else 'SEGUINDO','xb',46,BG0,b)
    if t>=1.95: check(d,540+125,370,30,BG0,b)
SCENES={k[2:]:v for k,v in globals().items() if k.startswith('s_')}
def frame(name,t):
    L=Image.new('RGBA',(W*S,H*S)); d=ImageDraw.Draw(L); bubbles(d,t); SCENES[name](d,t)
    im=bg_base().convert('RGBA'); im.alpha_composite(L); return im.convert('RGB').resize((W,H),Image.LANCZOS)
def render(name,dur,out):
    n=round((dur+0.7)*FPS)
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(name,i/FPS).tobytes())
    p.stdin.close(); p.wait()
if __name__=='__main__': render(sys.argv[2],float(sys.argv[3]),f'{sys.argv[1]}/g_{sys.argv[2]}.mp4')
