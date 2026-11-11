"""Half-screen edit with PHOTO B-roll (no captions/title). Usage: build_photo.py <workdir> [all|none|i,j]
project.json: end, presenter_shift, plan=[[start,end,'talk'|'split',photo,fx,fy],...] (fx,fy = focal point 0..1; optional 7th = extra zoom for a better composition)"""
import json, subprocess, os, sys
SFXPY=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sfx.py')
W=sys.argv[1]; os.chdir(W); ONLY=sys.argv[2] if len(sys.argv)>2 else 'all'
P=json.load(open('project.json')); END=P['end']; SH=P['presenter_shift']
FPS=30; BH=960; FEATH=300; CLEAN=BH-FEATH; TI=0.38; TO=0.18; DRIFT=0.03
fr=lambda t: round(t*FPS)
plan=[tuple(x) for x in P['plan']]
os.makedirs('seg',exist_ok=True); os.makedirs('pan',exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=white:s=1080x{BH}:d=1','-vf',
 f"format=gray,geq=lum='255*if(lt(Y,{CLEAN}),1,pow(1-(Y-{CLEAN})/{FEATH},2)*(3-2*(1-(Y-{CLEAN})/{FEATH})))'",'-frames:v','1','mask.png'],check=True)
enc=['-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r',str(FPS),'-an']
def panel_clip(i,photo,fx,fy,D,zoom=1.0):
    """Photo -> 1080x960 clip: cover-scale, focal point placed in the clean (unfaded) zone, slow 3% push-in on it."""
    out=f'pan/{i:02d}.mp4'; n=fr(D+0.7)
    w,h=map(int,subprocess.run(['ffprobe','-v','error','-show_entries','stream=width,height','-of','csv=p=0',photo],capture_output=True,text=True).stdout.strip().split(','))
    K=2  # render at 2x for smooth sub-pixel motion
    s=max(1080*K/w, BH*K/h)*zoom; Ws,Hs=round(w*s),round(h*s)
    cx=fx*Ws; cy=fy*Hs
    x0=min(max(cx-540*K,0),Ws-1080*K); y0=min(max(cy-(CLEAN*0.5)*K,0),Hs-BH*K)   # focal point at middle of clean zone
    # zoompan on the cropped 2x canvas; zoom anchored at the focal point inside it
    ax=(cx-x0)/(1080*K); ay=(cy-y0)/(BH*K)
    vf=(f"scale={Ws}:{Hs}:flags=lanczos,crop={1080*K}:{BH*K}:{int(x0)}:{int(y0)},"
        f"zoompan=z='1+{DRIFT}*on/{n}':x='{ax:.4f}*iw-{ax:.4f}*iw/zoom':y='{ay:.4f}*ih-{ay:.4f}*ih/zoom':d={n}:s=1080x{BH}:fps={FPS},setsar=1,format=yuv420p")
    subprocess.run(['ffmpeg','-v','error','-y','-i',photo,'-vf',vf,'-frames:v',str(n)]+enc+[out],check=True)
    return out
lst=[]; sfx=[{'t':0.0,'kind':'thump','gain':-11}]+P.get('extra_sfx',[])
panels={}
for i,it in enumerate(plan):
    if it[2]=='split':
        D=(fr(it[1])-fr(it[0]))/FPS
        if it[3].endswith('.mp4'): panels[i]=it[3]; continue          # pre-rendered animated graphic
        panels[i]=f'pan/{i:02d}.mp4' if (ONLY not in('all',) and os.path.exists(f'pan/{i:02d}.mp4') and str(i) not in ONLY.split(',')) else panel_clip(i,it[3],it[4],it[5],D,*(it[6:7]))
for i,it in enumerate(plan):
    s0,e0,mode=it[:3]; n=fr(e0)-fr(s0); ss=fr(s0)/FPS; D=n/FPS; out=f'seg/{i:02d}.mp4'; lst.append(out)
    prev=plan[i-1] if i>0 else None; nxt=plan[i+1] if i+1<len(plan) else None
    if mode=='talk':
        cmd=['ffmpeg','-v','error','-y','-ss',str(ss),'-i','main.mov','-frames:v',str(n),'-vf','scale=1080:1920,setsar=1,fps=30']+enc+[out]
    else:
        ein_talk=not(prev and prev[2]=='split'); eout_talk=not(nxt and nxt[2]=='split')
        if ein_talk: sfx.append({'t':s0-0.30,'kind':'whoosh','gain':-10,'seed':i+40})
        else: sfx.append({'t':s0-0.22,'kind':'whoosh_soft','gain':-13,'seed':i+80})
        if eout_talk: sfx.append({'t':e0-0.22,'kind':'whoosh_down','gain':-18,'seed':i+120})
        ein=f"(1-pow(1-clip(t/{TI},0,1),3))" if ein_talk else "1"
        sx=f"clip((t-{D-TO:.3f})/{TO},0,1)"; eout=f"(1-{sx}*{sx}*(3-2*{sx}))" if eout_talk else "1"
        K=f"min(clip(T/{TI},0,1),{f'clip(({D:.3f}-T)/{TO},0,1)' if eout_talk else '1'})"
        fades=f"fade=t=in:st=0:d={TI*0.8:.3f}:alpha=1"+(f",fade=t=out:st={D-TO:.3f}:d={TO}:alpha=1" if eout_talk else "")
        inputs=['-ss',str(ss),'-i','main.mov','-i',panels[i],'-loop','1','-i','mask.png']
        fc=(f"[0:v]scale=1080:1920,setsar=1,fps=30,setpts=PTS-STARTPTS,split[p][pb];"
            f"[pb]scale=270:480,gblur=sigma=10,scale=1080:1920,eq=brightness=-0.06[bgv];"
            f"[bgv][p]overlay=x=0:y='{SH}*{ein}*{eout}':eval=frame[base];"
            f"[2:v]format=gray,split[m1][m2];[1:v]setpts=PTS-STARTPTS,format=yuv420p,split[ps][pq];[pq]gblur=sigma=28[pbl];"
            f"[ps][pbl]blend=all_expr='A*{K}+B*(1-{K})',format=rgba[pk];[pk][m1]alphamerge,{fades}[top];")
        if not ein_talk:
            pD=(fr(prev[1])-fr(prev[0]))/FPS
            inputs+=['-ss',f'{pD:.3f}','-i',panels[i-1]]
            fc+="[3:v]setpts=PTS-STARTPTS,format=rgba[pp];[pp][m2]alphamerge[ptop];[base][ptop]overlay=0:0[base2];[base2][top]overlay=0:0,format=yuv420p[v]"
        else: fc+="[m2]nullsink;[base][top]overlay=0:0,format=yuv420p[v]"
        cmd=['ffmpeg','-v','error','-y']+inputs+['-filter_complex',fc,'-map','[v]','-frames:v',str(n)]+enc+[out]
    if ONLY=='all' or str(i) in ONLY.split(','): subprocess.run(cmd,check=True); print(out,mode,round(D,2),flush=True)
json.dump(sfx,open('sfx_events.json','w'))
E=fr(END)/FPS
subprocess.run(['python3','-I',SFXPY,'sfx_events.json',str(E),'sfx.wav'],check=True)
open('list.txt','w').write(''.join(f"file '{x}'\n" for x in lst))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','list.txt','-c','copy','video_only.mp4'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i','video_only.mp4','-i','main.mov','-i','sfx.wav','-filter_complex',
 f"[1:a]atrim=0:{E},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-2:LRA=11,volume=1.5dB,aresample=48000,aformat=channel_layouts=stereo[voice];"
 f"[2:a]aresample=48000,aformat=channel_layouts=stereo[fx];"
 f"[voice][fx]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:level=false,afade=t=out:st={E-0.4}:d=0.4[a]",
 '-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest','final.mp4'],check=True)
print('OK')
