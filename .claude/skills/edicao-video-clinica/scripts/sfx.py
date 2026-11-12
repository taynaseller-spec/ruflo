# Synthesised, original sound design (no samples): airy whooshes, shimmer, soft impact, mixed into one stereo track.
import numpy as np, sys, json
from scipy.signal import stft, istft, fftconvolve, butter, sosfilt
from scipy.io import wavfile
SR=48000; rng=np.random.default_rng(7)
def reverb(x, t60=0.9, mix=0.25):
    n=int(SR*t60); ir=rng.standard_normal(n)*np.exp(-6.9*np.arange(n)/n)
    ir=sosfilt(butter(2,[300,7000],'bandpass',fs=SR,output='sos'),ir); ir/=np.sqrt((ir**2).sum())
    wet=fftconvolve(x,ir)[:len(x)+n]; out=np.zeros(len(x)+n); out[:len(x)]+=x*(1-mix); out[:len(wet)]+=wet*mix; return out
def whoosh(dur=0.55, f0=350, f1=3200, rise=0.62, seed=0, up=True):
    r=np.random.default_rng(seed); n=int(SR*dur); x=r.standard_normal(n)
    f,t,Z=stft(x,SR,nperseg=1024,noverlap=896)
    tt=t/dur; prog=np.clip(tt,0,1)
    fc=f0*(f1/f0)**(prog if up else 1-prog)
    bw=0.55
    G=np.exp(-0.5*(np.log2((f[:,None]+1)/fc[None,:])/bw)**2)
    _,y=istft(Z*G,SR,nperseg=1024,noverlap=896); y=y[:n]
    tn=np.arange(n)/n
    env=np.where(tn<rise,(tn/rise)**2.2,np.exp(-(tn-rise)/(1-rise)*4.5))
    y*=env; y=reverb(y,0.7,0.3); y/=np.abs(y).max()
    m=len(y); pan=np.clip(np.arange(m)/(n),0,1)            # glides left -> right
    L=y*np.cos(pan*np.pi/2*0.8+0.15); R=y*np.sin(pan*np.pi/2*0.8+0.15)
    return np.stack([L,R],1)
def shimmer(seed=3, n_part=14, spread=0.28):
    r=np.random.default_rng(seed); dur=1.6; n=int(SR*dur); t=np.arange(n)/SR; y=np.zeros(n)
    base=[2093,2637,3136,3951,4186,5274,6272]                 # C-major-ish airy partials
    for k in range(n_part):
        fr=base[k%len(base)]*(1+r.uniform(-0.004,0.004))*(2 if k>=len(base) and r.random()<0.4 else 1)
        st=r.uniform(0,spread); env=np.where(t>=st,np.exp(-(t-st)/r.uniform(0.18,0.45))*(1-np.exp(-(t-st)/0.004)),0)
        y+=np.sin(2*np.pi*fr*t+r.uniform(0,6.28))*env*r.uniform(0.4,1)
    y=reverb(y,1.4,0.45); y/=np.abs(y).max()
    d=int(0.011*SR); L=y; R=np.concatenate([np.zeros(d),y[:-d]])       # slight stereo width
    return np.stack([L,R],1)
def thump():
    dur=0.9; n=int(SR*dur); t=np.arange(n)/SR
    f=45+55*np.exp(-t/0.07); ph=2*np.pi*np.cumsum(f)/SR
    y=np.sin(ph)*np.exp(-t/0.28)*(1-np.exp(-t/0.003))
    nz=sosfilt(butter(2,1800,'lowpass',fs=SR,output='sos'),rng.standard_normal(n))*np.exp(-t/0.02)*0.25
    y=reverb(y+nz,0.8,0.15); y/=np.abs(y).max(); return np.stack([y,y],1)
def pop(seed=0):
    r=np.random.default_rng(seed); dur=0.35; n=int(SR*dur); t=np.arange(n)/SR
    f0=r.uniform(700,950); f=f0*(1+0.5*np.exp(-t/0.02))
    y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.045)*(1-np.exp(-t/0.0015))
    y+=0.35*np.sin(2*np.pi*2*np.cumsum(f)/SR)*np.exp(-t/0.025)
    y=reverb(y,0.5,0.18); y/=np.abs(y).max(); return np.stack([y*0.92,y],1)
def ding(seed=0):                      # soft bell for key info (original synthesis)
    dur=1.4; n=int(SR*dur); t=np.arange(n)/SR; f0=1318.5
    y=sum(a*np.sin(2*np.pi*f0*m*t)*np.exp(-t/d) for m,a,d in [(1,1,0.55),(2.01,0.35,0.3),(2.76,0.22,0.18),(4.07,0.1,0.1)])
    y*=(1-np.exp(-t/0.002)); y=reverb(y,1.0,0.3); y/=np.abs(y).max(); return np.stack([y,y*0.95],1)
def click(seed=0):                     # short UI click
    n=int(SR*0.12); t=np.arange(n)/SR; r=np.random.default_rng(seed)
    y=sosfilt(butter(2,[1800,6500],'bandpass',fs=SR,output='sos'),r.standard_normal(n))*np.exp(-t/0.006)
    y+=0.6*np.sin(2*np.pi*2400*t)*np.exp(-t/0.01); y/=np.abs(y).max(); return np.stack([y,y],1)
# ---- v2 (2026-11-12): softer, "prettier" design: pink-noise doppler air, FM chime, sub boom, marimba pluck
def _lp(x,fc,o=2): return sosfilt(butter(o,fc,'lowpass',fs=SR,output='sos'),x)
def _rev(x,t60,mix,bright=6000):
    n=int(SR*t60); ir=rng.standard_normal(n)*np.exp(-6.9*np.arange(n)/n); ir=sosfilt(butter(2,[200,bright],'bandpass',fs=SR,output='sos'),ir); ir/=np.sqrt((ir**2).sum())
    w=fftconvolve(x,ir); o=np.zeros(len(w)); o[:len(x)]+=x*(1-mix); o+=w*mix; return _tail(o,0.25)
def _tail(y,sec=0.35):
    k=min(len(y),int(sec*SR)); y=y.copy(); y[-k:]*=np.cos(np.linspace(0,np.pi/2,k))**2; return y
def _pan(y,p0,p1,haas=0.0):
    m=len(y); p=np.linspace(p0,p1,m); th=(p+1)*np.pi/4; L=y*np.cos(th); R=y*np.sin(th)
    if haas: d=int(haas*SR); R=np.concatenate([np.zeros(d),R[:-d]])
    return np.stack([L,R],1)
def air(dur=0.75, f_lo=220, f_hi=2600, peak=0.58, seed=0, p0=-0.6, p1=0.6, tone=0.12):
    r=np.random.default_rng(seed); n=int(SR*dur); x=r.standard_normal(n)
    f,t,Z=stft(x,SR,nperseg=2048,noverlap=1792); Z=Z/np.sqrt(np.maximum(f[:,None],40)/40)   # pink
    u=np.clip(t/dur,0,1); up=np.clip(u/peak,0,1); dn=np.clip((u-peak)/(1-peak),0,1)
    fc=np.where(u<peak, f_lo*(f_hi/f_lo)**(up**1.6), f_hi*(0.45)**dn)                       # doppler: rise then fall
    G=np.exp(-0.5*(np.log2((f[:,None]+1)/fc[None,:])/0.75)**2)
    _,y=istft(Z*G,SR,nperseg=2048,noverlap=1792); y=y[:n]
    tn=np.arange(n)/n; env=np.where(tn<peak,np.sin(np.pi/2*tn/peak)**3,np.exp(-(tn-peak)/(1-peak)*3.2))
    y=_lp(y*env,9000)
    fi=np.interp(np.arange(n)/SR,t,fc)*1.0; wh=np.sin(2*np.pi*np.cumsum(fi)/SR)*env**2*tone      # faint tonal sheen
    y=y/np.abs(y).max()+wh; y=_rev(y,0.9,0.28,7000); y/=np.abs(y).max()
    return _pan(y,p0,p1,0.004)
def chime(seed=0, notes=(1318.5,1975.5), gap=0.075):
    dur=2.2; n=int(SR*dur); t=np.arange(n)/SR; y=np.zeros(n)
    for k,f0 in enumerate(notes):
        st=int(k*gap*SR); tt=t[:n-st]; idx=1.6*np.exp(-tt/0.12)
        bell=np.sin(2*np.pi*f0*tt+idx*np.sin(2*np.pi*f0*3.5*tt))*np.exp(-tt/0.9)*(1-np.exp(-tt/0.004))
        bell+=0.25*np.sin(2*np.pi*f0*2*tt)*np.exp(-tt/0.35)
        y[st:]+=bell*(1 if k==0 else 0.75)
    y=_rev(_tail(_lp(y,9000),0.6),1.8,0.38,9000); y/=np.abs(y).max(); return _pan(y,-0.15,0.15,0.008)
def boom(seed=0):
    dur=1.6; n=int(SR*dur); t=np.arange(n)/SR; f=36+30*np.exp(-t/0.12)
    y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.55)*(1-np.exp(-t/0.006))
    nz=_lp(np.random.default_rng(seed).standard_normal(n),350)*np.exp(-t/0.08)*0.5
    y=_rev(_tail(y+nz,0.5),1.4,0.22,3000); y/=np.abs(y).max(); return np.stack([y,y],1)
def pluck(seed=0, f0=784.0):
    dur=0.9; n=int(SR*dur); t=np.arange(n)/SR
    y=np.sin(2*np.pi*f0*t)*np.exp(-t/0.22)+0.3*np.sin(2*np.pi*f0*4*t)*np.exp(-t/0.03)+0.15*np.sin(2*np.pi*f0*2*t)*np.exp(-t/0.1)
    y*=(1-np.exp(-t/0.002)); y=_rev(_tail(y,0.3),1.0,0.3,8000); y/=np.abs(y).max(); return _pan(y,0.1,0.1,0.006)
# ---- "common" (2026-11-12): the familiar stock-style CapCut sounds, short and crisp, little reverb
def whoosh_c(seed=0, dur=0.42):
    r=np.random.default_rng(seed); n=int(SR*dur); x=r.standard_normal(n)
    f,t,Z=stft(x,SR,nperseg=1024,noverlap=896); u=np.clip(t/dur,0,1)
    fc=700*(5200/700)**np.sin(np.pi/2*np.clip(u/0.55,0,1))*np.where(u>0.55,0.6**((u-0.55)/0.45),1)
    G=np.exp(-0.5*(np.log2((f[:,None]+1)/fc[None,:])/0.9)**2); _,y=istft(Z*G,SR,nperseg=1024,noverlap=896); y=y[:n]
    tn=np.arange(n)/n; env=np.where(tn<0.5,(tn/0.5)**2,np.exp(-(tn-0.5)/0.5*5)); y=_rev(y*env,0.35,0.15,9000); y/=np.abs(y).max()
    return _pan(y,-0.8,0.8)
def swipe_c(seed=0):
    r=np.random.default_rng(seed); n=int(SR*0.22); t=np.arange(n)/n
    y=sosfilt(butter(2,[2500,9000],'bandpass',fs=SR,output='sos'),r.standard_normal(n))*np.sin(np.pi*t)**1.5
    y=_tail(y,0.03); y/=np.abs(y).max(); return _pan(y,0.6,-0.6)
def pop_c(seed=0):
    n=int(SR*0.16); t=np.arange(n)/SR; f=380+900*(1-np.exp(-t/0.018))
    y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.035)*(1-np.exp(-t/0.0008))
    y=_tail(y,0.03); y/=np.abs(y).max(); return np.stack([y,y],1)
def ding_c(seed=0):
    n=int(SR*1.1); t=np.arange(n)/SR; f0=1760.0
    y=sum(a*np.sin(2*np.pi*f0*m*t)*np.exp(-t/d) for m,a,d in [(1,1,0.42),(2,0.28,0.2),(3,0.12,0.1),(0.5,0.18,0.3)])
    y*=(1-np.exp(-t/0.001)); y=_rev(_tail(y,0.3),0.6,0.15,9000); y/=np.abs(y).max(); return np.stack([y,y],1)
def db(g): return 10**(g/20)
events=json.load(open(sys.argv[1])); total=float(sys.argv[2]); out=np.zeros((int(SR*(total+2)),2))
for ev in events:
    k=ev['kind']; s=ev.get('seed',0)
    if k=='whoosh': x=whoosh(ev.get('dur',0.55),seed=s,up=True)
    elif k=='whoosh_soft': x=whoosh(0.42,500,2400,0.55,seed=s,up=True)
    elif k=='whoosh_down': x=whoosh(0.38,2600,600,0.35,seed=s,up=True)
    elif k=='shimmer': x=shimmer(s)
    elif k=='thump': x=thump()
    elif k=='pop': x=pop(s)
    elif k=='ding': x=ding(s)
    elif k=='click': x=click(s)
    elif k=='air': x=air(ev.get('dur',0.75),seed=s,p0=ev.get('p0',-0.6),p1=ev.get('p1',0.6))
    elif k=='air_soft': x=air(0.5,320,1800,0.55,seed=s,p0=-0.3,p1=0.3,tone=0.06)
    elif k=='air_down': x=air(0.55,1600,500,0.3,seed=s,p0=0.5,p1=-0.5,tone=0.05)
    elif k=='chime': x=chime(s)
    elif k=='boom': x=boom(s)
    elif k=='whoosh_c': x=whoosh_c(s)
    elif k=='swipe_c': x=swipe_c(s)
    elif k=='pop_c': x=pop_c(s)
    elif k=='ding_c': x=ding_c(s)
    elif k=='pluck': x=pluck(s,ev.get('f0',784.0))
    if ev['t']<0: continue
    i=int(ev['t']*SR); x=x*db(ev['gain']); out[i:i+len(x)]+=x[:len(out)-i]
out=out[:int(SR*total)]
fade=int(0.3*SR); out[-fade:]*=np.linspace(1,0,fade)[:,None]
wavfile.write(sys.argv[3],SR,(np.clip(out,-1,1)*32767).astype(np.int16)); print('peak dBFS',20*np.log10(np.abs(out).max()+1e-9))
