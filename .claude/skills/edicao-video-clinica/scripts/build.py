"""Build the clinic Reels edit. Usage: python3 -I build.py <workdir> [all|none|i,j]
workdir needs: main.mov, br/*.mp4, mask built here, faces.json, words.json, project.json.
Standard + rationale: ../SKILL.md"""
import json, subprocess, os, sys, re, statistics as st
SFXPY=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sfx.py'); W=sys.argv[1]; os.chdir(W); ONLY=sys.argv[2] if len(sys.argv)>2 else 'all'
FPS=30; BH=960; FEATH=300; CLEAN=BH-FEATH
P0=json.load(open('project.json')); END=P0['end']; SH=P0.get('presenter_shift',470)  # SH: see SKILL.md
fr=lambda t: round(t*FPS)
faces=json.load(open('faces.json'))   # from faces.py on every B-roll clip
# start, end, mode, clip, src_start   (each B-roll range = one single shot, chosen from face analysis)
P=json.load(open('project.json'))
plan=[tuple(x) for x in P['plan']]   # [start,end,mode(talk|split|full),clip,src_start]
def face_stats(clip,a,b):
    d=faces[clip]; fs=[x for x in d['faces'] if a-0.01<=x[0]<=b and x[1] is not None]
    if not fs: return None
    return dict(cx=st.median([x[1] for x in fs]),cy=st.median([x[2] for x in fs]),h=st.median([x[3] for x in fs]),W=d['W'],H=d['H'])
def split_crop(clip,a,b):
    f=face_stats(clip,a,b); d=faces[clip]; Wsrc,Hsrc=d['W'],d['H']
    s=max(1080/Wsrc, BH/Hsrc); Hs=round(Hsrc*s); Ws=round(Wsrc*s)
    if f is None: return s,Ws,Hs,(Ws-1080)//2,max(0,(Hs-BH)//2),None
    eye=(f['cy']-0.12*f['h'])*s; top=(f['cy']-0.95*f['h'])*s; chin=(f['cy']+0.62*f['h'])*s
    y=eye-0.36*CLEAN                     # eyes on the upper third of the clean area
    y=max(y, chin-(CLEAN+60))            # chin no deeper than 60px into the fade
    y=min(y, top-40)                     # headroom wins: never cut the top of the head
    y=int(max(0,min(Hs-BH,y)))
    x=int(max(0,min(Ws-1080, f['cx']*s-540)))
    return s,Ws,Hs,x,y,dict(eye=eye-y,top=top-y,chin=chin-y,h=f['h'])

os.makedirs('seg',exist_ok=True)
enc=['-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r',str(FPS),'-an']
TI=0.38; TO=0.32
def panel(idx,clip,a,d,tag):
    s,Ws,Hs,x,y,_=split_crop(clip,a,a+d)
    return f"[{idx}:v]fps=30,setpts=PTS-STARTPTS,scale={Ws}:{Hs}:flags=lanczos,crop=1080:{BH}:{x}:{y},setsar=1,format=yuv420p[{tag}]"
lst=[]; sfx=[{'t':0.0,'kind':'thump','gain':-13},{'t':0.05,'kind':'shimmer','gain':-16,'seed':3},{'t':P0['name_card']['start']-0.05,'kind':'shimmer','gain':-17,'seed':11}]
for i,(s0,e0,mode,clip,cs) in enumerate(plan):
    n=fr(e0)-fr(s0); ss=fr(s0)/FPS; D=n/FPS; out=f'seg/{i:02d}.mp4'; lst.append(out)
    prev=plan[i-1] if i>0 else None; nxt=plan[i+1] if i+1<len(plan) else None
    if mode=='talk':
        cmd=['ffmpeg','-v','error','-y','-ss',str(ss),'-i','main.mov','-frames:v',str(n),'-vf','scale=1080:1920,setsar=1,fps=30']+enc+[out]
    elif mode=='full':
        sfx.append({'t':s0-0.33,'kind':'whoosh','gain':-13,'seed':i})
        f=face_stats(clip,cs,cs+D); Wsrc,Hsrc=faces[clip]['W'],faces[clip]['H']
        ax=(f['cx']/Wsrc) if f else 0.5; ay=((f['cy']-0.1*f['h'])/Hsrc) if f else 0.45
        K=f"min(clip(T/0.42,0,1),clip(({D:.3f}-T)/0.34,0,1))"
        fc=(f"[0:v]scale=1080:1920,setsar=1,fps=30,setpts=PTS-STARTPTS[m];"
            f"[1:v]fps=30,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,scale=2160:3840,"
            f"zoompan=z='1+0.03*on/{n}':x='({ax:.3f}*iw)-({ax:.3f}*iw/zoom)':y='({ay:.3f}*ih)-({ay:.3f}*ih/zoom)':d=1:s=1080x1920:fps=30,setsar=1,format=yuv420p,split[s][s2];"
            f"[s2]gblur=sigma=30[bl];[s][bl]blend=all_expr='A*{K}+B*(1-{K})',format=yuva420p,"
            f"fade=t=in:st=0:d=0.30:alpha=1,fade=t=out:st={D-0.28:.3f}:d=0.28:alpha=1[top];[m][top]overlay=0:0,format=yuv420p[v]")
        cmd=['ffmpeg','-v','error','-y','-ss',str(ss),'-i','main.mov','-ss',str(cs),'-i',clip,'-filter_complex',fc,'-map','[v]','-frames:v',str(n)]+enc+[out]
    else:
        ein_talk = not (prev and prev[2]=='split'); eout_talk = not (nxt and nxt[2]=='split')
        if ein_talk: sfx.append({'t':s0-0.30,'kind':'whoosh','gain':-14,'seed':i+40})
        else: sfx.append({'t':s0-0.22,'kind':'whoosh_soft','gain':-17,'seed':i+80})
        if eout_talk: sfx.append({'t':e0-0.22,'kind':'whoosh_down','gain':-22,'seed':i+120})
        ein=f"(1-pow(1-clip(t/{TI},0,1),3))" if ein_talk else "1"
        sx=f"clip((t-{D-TO:.3f})/{TO},0,1)"
        eout=f"(1-{sx}*{sx}*(3-2*{sx}))" if eout_talk else "1"
        Kin=f"clip(T/{TI},0,1)"; Kout=f"clip(({D:.3f}-T)/{TO},0,1)" if eout_talk else "1"
        K=f"min({Kin},{Kout})"
        fades=f"fade=t=in:st=0:d={TI*0.8:.3f}:alpha=1"+(f",fade=t=out:st={D-TO:.3f}:d={TO}:alpha=1" if eout_talk else "")
        inputs=['-ss',str(ss),'-i','main.mov','-ss',str(cs),'-i',clip,'-loop','1','-i','mask2.png']
        fc=(f"[0:v]scale=1080:1920,setsar=1,fps=30,setpts=PTS-STARTPTS,split[p][pb];"
            f"[pb]scale=270:480,gblur=sigma=10,scale=1080:1920,eq=brightness=-0.06[bgv];"
            f"[bgv][p]overlay=x=0:y='{SH}*{ein}*{eout}':eval=frame[base];"
            f"[2:v]format=gray,split[m1][m2];"+panel(1,clip,cs,D,'pn')+";"
            f"[pn]split[ps][pq];[pq]gblur=sigma=28[pbl];[ps][pbl]blend=all_expr='A*{K}+B*(1-{K})',format=rgba[pk];"
            f"[pk][m1]alphamerge,{fades}[top];")
        if not ein_talk:
            pcs=prev[4]+(fr(prev[1])-fr(prev[0]))/FPS
            inputs+=['-ss',str(pcs),'-i',prev[3]]
            fc+=panel(3,prev[3],prev[4],(fr(prev[1])-fr(prev[0]))/FPS,'pp')+";[pp]format=rgba[pp2];[pp2][m2]alphamerge[ptop];[base][ptop]overlay=0:0[base2];[base2][top]overlay=0:0,format=yuv420p[v]"
        else:
            fc+="[m2]nullsink;[base][top]overlay=0:0,format=yuv420p[v]"
        cmd=['ffmpeg','-v','error','-y']+inputs+['-filter_complex',fc,'-map','[v]','-frames:v',str(n)]+enc+[out]
    if ONLY=='all' or str(i) in ONLY.split(','): subprocess.run(cmd,check=True); print(out,mode,round(D,2),flush=True)
json.dump(sfx,open('sfx_events.json','w'))
subprocess.run(['python3','-I',SFXPY,'sfx_events.json',str(fr(END)/FPS),'sfx.wav'],check=True)
open('list.txt','w').write(''.join(f"file '{x}'\n" for x in lst))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','list.txt','-c','copy','video_only.mp4'],check=True)

words=json.load(open('words.json'))
def ts(t): t=max(0,t); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ev=[]
for k,w in enumerate(words):
    txt=re.sub(r"[.,!?;:]","",w['w']).strip()
    if not txt or w['s']>=END: continue
    if txt not in P0.get('keep_case',[]): txt=txt.lower()
    s_=w['s']; nx=words[k+1]['s'] if k+1<len(words) else w['e']+0.4
    en=min(nx,w['e']+0.35) if nx-w['e']>0.35 else nx
    md=next((m for (a,b,m,_,_) in plan if a<=s_+0.05<b),'talk')
    y={'split':1580,'full':1640,'talk':1250}[md]
    ev.append(f"Dialogue: 1,{ts(s_)},{ts(min(en,END))},Cap,,0,0,0,,{{\\pos(540,{y})}}{txt}")
title="\\N".join(P0["title_lines"]); TE=P0.get("title_end",6.25); NC=P0["name_card"]
ev.append(f"Dialogue: 2,{ts(0)},{ts(TE)},Title,,0,0,0,,{{\\pos(540,735)\\fad(150,200)}}{title}")
ev.append(f"Dialogue: 2,{ts(NC['start'])},{ts(NC['end'])},Name,,0,0,0,,{{\\pos(540,1640)\\fad(300,300)}}{NC['name']}")
ev.append(f"Dialogue: 2,{ts(NC['start'])},{ts(NC['end'])},Role,,0,0,0,,{{\\pos(540,1724)\\fad(300,300)}}{NC['role']}")
HDR="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,4,2,5,40,40,0,1
Style: Title,Inter ExtraBold,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,3,5,60,60,0,1
Style: Name,Inter ExtraBold,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,2,5,40,40,0,1
Style: Role,Inter SemiBold,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,4,0,1,2,2,5,40,40,0,1

"""
hdr=HDR
open('subs.ass','w').write(hdr+"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"+"\n".join(ev)+"\n")
E=fr(END)/FPS
subprocess.run(['ffmpeg','-v','error','-y','-i','video_only.mp4','-i','main.mov','-i','sfx.wav','-filter_complex',
 f"[0:v]ass=subs.ass:fontsdir=/usr/share/fonts/opentype/inter[v];"
 f"[1:a]atrim=0:{E},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-2:LRA=11,aresample=48000,aformat=channel_layouts=stereo[voice];"
 f"[2:a]aresample=48000,aformat=channel_layouts=stereo[fx];"
 f"[voice][fx]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.92:level=false,afade=t=out:st={E-0.4}:d=0.4[a]",
 '-map','[v]','-map','[a]','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest','final.mp4'],check=True)
print('OK')
