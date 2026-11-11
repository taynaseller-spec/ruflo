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
    if ev['t']<0: continue
    i=int(ev['t']*SR); x=x*db(ev['gain']); out[i:i+len(x)]+=x[:len(out)-i]
out=out[:int(SR*total)]
fade=int(0.3*SR); out[-fade:]*=np.linspace(1,0,fade)[:,None]
wavfile.write(sys.argv[3],SR,(np.clip(out,-1,1)*32767).astype(np.int16)); print('peak dBFS',20*np.log10(np.abs(out).max()+1e-9))
