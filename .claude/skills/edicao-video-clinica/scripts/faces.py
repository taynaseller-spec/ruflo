import cv2, sys, json
casc=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_alt2.xml')
prof=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_profileface.xml')
out={}
for p in sys.argv[2:]:
    cap=cv2.VideoCapture(p); fps=cap.get(5); n=int(cap.get(7)); W=int(cap.get(3)); H=int(cap.get(4))
    step=max(1,round(fps/3)); res=[]
    for i in range(0,n,step):
        cap.set(1,i); ok,fr=cap.read()
        if not ok: break
        g=cv2.equalizeHist(cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY))
        fs=list(casc.detectMultiScale(g,1.1,5,minSize=(W//12,W//12)))
        if not fs: fs=list(prof.detectMultiScale(g,1.1,5,minSize=(W//12,W//12)))
        if fs:
            x,y,w,h=max(fs,key=lambda r:r[2]*r[3]); res.append([round(i/fps,2),int(x+w/2),int(y+h/2),int(h)])
        else: res.append([round(i/fps,2),None,None,None])
    out[p]={'W':W,'H':H,'fps':fps,'faces':res}
json.dump(out,open(sys.argv[1],'w'))
for p,v in out.items():
    print(p,v['W'],v['H'])
    print(' '.join(f"{t}:{'-' if c is None else f'{c},{y},{h}'}" for t,c,y,h in v['faces']))
