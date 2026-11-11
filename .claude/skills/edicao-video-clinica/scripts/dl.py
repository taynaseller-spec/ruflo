import subprocess, time, sys, json, re
def fetch(url, out, tries=8):
    for k in range(tries):
        r=subprocess.run(['curl','-s','-A','video-editing-script/1.0 (personal project)','-o',out,'-w','%{http_code}',url],capture_output=True,text=True)
        if r.stdout=='200':
            head=open(out,'rb').read(16)
            if not head.startswith(b'<!DOCTYPE') and not head.startswith(b'<html'): return True
        time.sleep(3+2*k)
    return False
def thumb(url,w):
    m=re.match(r'(https://upload\.wikimedia\.org/wikipedia/commons/)(\w/\w\w/)([^?]+)',url)
    base,h,name=m.groups(); ext='.jpg' if name.lower().endswith('.webp') else ''
    return f"{base}thumb/{h}{name}/{w}px-{name}{ext if name.lower().endswith('.webp') else ''}"
if __name__=='__main__':
    info=json.load(open(sys.argv[1])); w=int(sys.argv[2]); pre=sys.argv[3]
    for k,(n,v) in enumerate(info.items()):
        ok=fetch(thumb(v['url'],w) if v['w']>w else v['url'].split('?')[0], f'{pre}{k:02d}.jpg'); print(k,ok,n,flush=True); time.sleep(2)
