"""Original animated B-roll panels (1080x960) for the half-screen layout.
Content stays inside the clean zone (y<640); the bottom fades into the presenter.
Usage: graphics.py <outdir> <name> <duration>   (or 'all' with a json spec)"""
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS=30; W,H=1080,960; S=2                      # supersampling factor
FD='/usr/share/fonts/opentype/inter/'
NAVY0=(11,22,38); NAVY1=(20,38,62); GOLD=(214,178,108); WHITE=(245,245,242); MUTED=(150,165,185)
RED=(232,94,88); GREEN=(88,201,145)
_fc={}
def font(w,size):
    k=(w,size)
    if k not in _fc: _fc[k]=ImageFont.truetype(FD+{'xb':'Inter-ExtraBold.otf','b':'Inter-Bold.otf','sb':'Inter-SemiBold.otf','m':'Inter-Medium.otf'}[w],size*S)
    return _fc[k]
def clamp(x,a=0.0,b=1.0): return max(a,min(b,x))
def ease(x): x=clamp(x); return 1-(1-x)**3                       # easeOutCubic
def ease_io(x): x=clamp(x); return x*x*(3-2*x)
def prog(t,start,dur=0.45): return ease((t-start)/dur)
_bg=None
def background():
    global _bg
    if _bg is None:
        im=Image.new('RGB',(W*S,H*S)); d=ImageDraw.Draw(im)
        for y in range(H*S):
            f=y/(H*S); c=tuple(int(NAVY1[i]*(1-f)+NAVY0[i]*f) for i in range(3)); d.line([(0,y),(W*S,y)],fill=c)
        glow=Image.new('L',(W*S,H*S),0); ImageDraw.Draw(glow).ellipse([W*S*0.15,-H*S*0.35,W*S*0.85,H*S*0.55],fill=60)
        glow=glow.filter(ImageFilter.GaussianBlur(160*S))
        im=Image.composite(Image.new('RGB',im.size,(40,62,95)),im,glow); _bg=im
    return _bg.copy()
def text(d,xy,s,w,size,fill,alpha=1.0,anchor='mm',spacing=0):
    if alpha<=0: return
    col=tuple(int(c) for c in fill)+(int(255*clamp(alpha)),)
    x,y=xy[0]*S,xy[1]*S
    if spacing:
        f=font(w,size); widths=[f.getlength(ch)+spacing*S for ch in s]; tot=sum(widths)-spacing*S
        cx=x-tot/2 if anchor[0]=='m' else (x if anchor[0]=='l' else x-tot)
        for ch,wd in zip(s,widths): d.text((cx,y),ch,font=f,fill=col,anchor='l'+anchor[1]); cx+=wd
    else: d.text((x,y),s,font=font(w,size),fill=col,anchor=anchor)
def rrect(d,box,r,fill=None,outline=None,width=1,alpha=1.0):
    a=int(255*clamp(alpha)); box=[v*S for v in box]
    d.rounded_rectangle(box,r*S,fill=(fill+(a,)) if fill else None,outline=(outline+(a,)) if outline else None,width=width*S)
def finish(layer):
    im=background().convert('RGBA'); im.alpha_composite(layer)
    return im.convert('RGB').resize((W,H),Image.LANCZOS)
def arrow_up(d,cx,cy,size,fill,alpha):
    a=int(255*clamp(alpha)); s=size*S; cx*=S; cy*=S
    d.polygon([(cx,cy-s),(cx+s*0.8,cy),(cx+s*0.28,cy),(cx+s*0.28,cy+s),(cx-s*0.28,cy+s),(cx-s*0.28,cy),(cx-s*0.8,cy)],fill=fill+(a,))
def label(d,y,s,alpha):  # small gold kicker
    text(d,(540,y),s,'sb',30,GOLD,alpha,spacing=6)

# ---------------- panels ----------------
def g_juros(t):
    L=Image.new('RGBA',(W*S,H*S)); d=ImageDraw.Draw(L)
    label(d,95,'TAXA DE JUROS',prog(t,0.05))
    x0,x1,y0,y1=150,930,190,560
    for i in range(5):
        y=y0+(y1-y0)*i/4; d.line([(x0*S,y*S),(x1*S,y*S)],fill=(255,255,255,int(28*prog(t,0.1))),width=S)
    pts=[(0,0.18),(0.12,0.22),(0.24,0.2),(0.36,0.33),(0.48,0.3),(0.6,0.47),(0.72,0.55),(0.84,0.72),(1.0,0.9)]
    p=ease_io((t-0.25)/1.5); n=len(pts)-1; seg=[]
    for i in range(n+1):
        fx=i/n
        if fx<=p: seg.append(pts[i])
        else:
            if i>0:
                a,b=pts[i-1],pts[i]; k=(p-(i-1)/n)*n; seg.append((a[0]+(b[0]-a[0])*k,a[1]+(b[1]-a[1])*k))
            break
    xy=[((x0+(x1-x0)*u)*S,(y1-(y1-y0)*v)*S) for u,v in seg]
    if len(xy)>1:
        area=xy+[(xy[-1][0],y1*S),(xy[0][0],y1*S)]; d.polygon(area,fill=GOLD+(38,))
        d.line(xy,fill=GOLD+(255,),width=7*S,joint='curve')
        ex,ey=xy[-1]; r=(13+3*math.sin(t*6))*S; d.ellipse([ex-r,ey-r,ex+r,ey+r],fill=WHITE+(255,))
    a=prog(t,1.45)
    text(d,(160,250-20*a),'EM ALTA','xb',74,WHITE,a,anchor='lm'); arrow_up(d,505,250-20*a,36,RED,a)
    return finish(L)

def g_parcela(t):
    L=Image.new('RGBA',(W*S,H*S)); d=ImageDraw.Draw(L)
    label(d,95,'FINANCIAMENTO',prog(t,0.05))
    bx=150; lim=bx+560
    a=prog(t,0.15); text(d,(bx,200),'SUA RENDA','b',34,MUTED,a,anchor='ls')
    rrect(d,[bx,220,bx+560*a,290],14,fill=WHITE,alpha=a)
    a2=prog(t,0.7); text(d,(bx,370),'PARCELA','b',34,MUTED,a2,anchor='ls')
    g=ease_io((t-1.0)/1.3); wbar=40+760*g
    col=tuple(int(WHITE[i]*(1-clamp((bx+wbar-lim)/120))+RED[i]*clamp((bx+wbar-lim)/120)) for i in range(3))
    if a2>0: rrect(d,[bx,390,bx+wbar,460],14,fill=col,alpha=a2)
    la=prog(t,0.5)
    for y in range(180,500,22): d.line([(lim*S,y*S),(lim*S,(y+12)*S)],fill=GOLD+(int(255*la),),width=3*S)
    text(d,(lim,165),'LIMITE','sb',24,GOLD,la,spacing=4)
    a3=prog(t,2.0); text(d,(540,560-15*a3),'NÃO CABE NO BOLSO','xb',58,RED,a3)
    return finish(L)

def house(d,cx,cy,s,col,alpha,width=6):
    a=int(255*clamp(alpha)); c=col+(a,); s*=S; cx*=S; cy*=S
    pts=[(cx-s,cy-s*0.1),(cx,cy-s*0.95),(cx+s,cy-s*0.1)]
    d.line(pts,fill=c,width=width*S,joint='curve')
    d.line([(cx-s*0.75,cy-s*0.3),(cx-s*0.75,cy+s*0.8),(cx+s*0.75,cy+s*0.8),(cx+s*0.75,cy-s*0.3)],fill=c,width=width*S,joint='curve')
    d.rectangle([cx-s*0.2,cy+s*0.25,cx+s*0.2,cy+s*0.8],fill=c)

def g_morar(t):
    L=Image.new('RGBA',(W*S,H*S)); d=ImageDraw.Draw(L)
    a=prog(t,0.2,0.6); house(d,540,230,105,GOLD,a)
    a1=prog(t,0.7); text(d,(540,420-15*a1),'PRECISAM MORAR','xb',64,WHITE,a1)
    a2=prog(t,1.9); text(d,(540,525-15*a2),'DE ALUGUEL','xb',64,GOLD,a2)
    return finish(L)

def g_motivos(t):
    L=Image.new('RGBA',(W*S,H*S)); d=ImageDraw.Draw(L)
    rows=[(0.35,'MUDOU DE EMPREGO'),(1.35,'MUDOU DE CIDADE'),(2.05,'FILHO ESTUDANDO FORA')]
    dim=1-0.55*prog(t,3.3)
    for i,(st,s) in enumerate(rows):
        a=prog(t,st); y=150+105*i; x=170+30*(1-a)
        d.ellipse([(x-22)*S,(y-22)*S,(x+22)*S,(y+22)*S],outline=GOLD+(int(255*a*dim),),width=4*S)
        text(d,(x,y),str(i+1),'b',26,GOLD,a*dim)
        text(d,(x+50,y),s,'b',46,WHITE,a*dim,anchor='lm')
    a=prog(t,3.35); rrect(d,[200,470,880,570],50,fill=GOLD,alpha=a)
    text(d,(540,520),'TODOS NO ALUGUEL','xb',48,NAVY0,a)
    return finish(L)

def g_demanda(t):
    L=Image.new('RGBA',(W*S,H*S)); d=ImageDraw.Draw(L)
    base=520; cols=[(250,'PROCURA',0.4,330,GOLD),(540,'OFERTA',3.5,90,MUTED),(830,'ALUGUEL',2.9,290,RED)]
    d.line([(120*S,base*S),(960*S,base*S)],fill=(255,255,255,int(60*prog(t,0.05))),width=2*S)
    for cx,lab,st,hgt,col in cols:
        a=prog(t,st,0.3); g=ease_io((t-st)/0.9); h=hgt*g
        rrect(d,[cx-75,base-h,cx+75,base],12,fill=col,alpha=a)
        text(d,(cx,base+48),lab,'b',32,WHITE,a,spacing=3)
        if lab!='OFERTA' and g>0.6: arrow_up(d,cx,base-h-60,30,col,prog(t,st+0.6))
    return finish(L)

def g_consorcio(t):
    L=Image.new('RGBA',(W*S,H*S)); d=ImageDraw.Draw(L)
    a=prog(t,0.1); b=prog(t,0.35)
    rrect(d,[70,110,520,600],28,fill=(255,255,255),alpha=0.05*a,outline=MUTED,width=2)
    rrect(d,[560,110,1010,600],28,fill=GOLD,alpha=0.08*b,outline=GOLD,width=3)
    text(d,(295,175),'FINANCIAMENTO','b',36,MUTED,a,spacing=2)
    text(d,(785,175),'CONSÓRCIO','xb',40,GOLD,b,spacing=2)
    a1=prog(t,0.5); text(d,(295,300),'JUROS','xb',62,RED,a1); text(d,(295,360),'ALTOS','b',34,RED,a1,spacing=4)
    a2=prog(t,0.65); text(d,(785,300),'JUROS','xb',62,WHITE,a2*(1-0.6*prog(t,2.9)))
    sk=ease_io((t-2.9)/0.35)
    if sk>0: d.line([(660*S,300*S),((660+250*sk)*S,300*S)],fill=RED+(255,),width=8*S)
    a3=prog(t,3.25); text(d,(785,370),'SEM JUROS','xb',46,GREEN,a3)
    a4=prog(t,6.0); text(d,(785,470),'TAXA DE ADM.','b',34,WHITE,a4)
    a5=prog(t,7.35); text(d,(785,530),'+ CORREÇÕES','b',34,WHITE,a5)
    return finish(L)

def g_cta(t):
    L=Image.new('RGBA',(W*S,H*S)); d=ImageDraw.Draw(L)
    a=prog(t,0.05); text(d,(540,140),'COMENTE','sb',36,GOLD,a,spacing=8)
    b=prog(t,0.25,0.5); sc=0.9+0.1*b
    w2,h2=330*sc,95*sc; cx,cy=540,300
    rrect(d,[cx-w2,cy-h2,cx+w2,cy+h2],40,fill=WHITE,alpha=b)
    if b>0: d.polygon([((cx-150)*S,(cy+h2-2)*S),((cx-90)*S,(cy+h2-2)*S),((cx-175)*S,(cy+h2+60)*S)],fill=WHITE+(int(255*b),))
    word='INVESTIR'; k=int(clamp((t-0.9)/0.5)*len(word)+0.999) if t>0.9 else 0
    text(d,(cx,cy),word[:k],'xb',96,NAVY0,1.0)
    if 0<k<len(word) or (t>0.9 and int(t*3)%2==0 and k==len(word) and t<1.8):
        tw=font('xb',96).getlength(word[:k])/S; d.line([((cx+tw/2+8)*S,(cy-45)*S),((cx+tw/2+8)*S,(cy+45)*S)],fill=GOLD+(255,),width=5*S)
    c=prog(t,1.85); text(d,(540,525-12*c),'TE CHAMO NO DIRECT','xb',50,WHITE,c)
    return finish(L)

PANELS=dict(juros=g_juros,parcela=g_parcela,morar=g_morar,motivos=g_motivos,demanda=g_demanda,consorcio=g_consorcio,cta=g_cta)
def render(name,dur,out,shift=0.0):
    n=round((dur+0.7)*FPS)
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(PANELS[name](i/FPS-shift).tobytes())
    p.stdin.close(); p.wait()
if __name__=='__main__':
    render(sys.argv[2],float(sys.argv[3]),f'{sys.argv[1]}/g_{sys.argv[2]}.mp4',float(sys.argv[4]) if len(sys.argv)>4 else 0.0)
