import json, sys, urllib.request, urllib.parse, time
UA={'User-Agent':'video-editing-script/1.0 (personal project)'}
def q(term, ftype='video', n=12):
    p={'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrlimit':n,
       'gsrsearch':f'{term} filetype:{ftype}','prop':'imageinfo','iiprop':'url|size|mime|extmetadata','iiurlwidth':320}
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)
    for k in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except Exception as e: time.sleep(3*(k+1))
    return {}
out=[]
for term in sys.argv[2:]:
    r=q(term, sys.argv[1])
    for pg in (r.get('query',{}).get('pages',{}) or {}).values():
        ii=pg['imageinfo'][0]; md=ii.get('extmetadata',{})
        lic=md.get('LicenseShortName',{}).get('value','?')
        out.append(dict(term=term,title=pg['title'],url=ii['url'],thumb=ii.get('thumburl'),w=ii.get('width'),h=ii.get('height'),dur=ii.get('duration'),mime=ii['mime'],lic=lic,size=ii.get('size')))
    time.sleep(1)
json.dump(out,open('commons_'+sys.argv[1]+'.json','w'),indent=0)
for o in out: print(o['term'][:18].ljust(18),o['w'],o['h'],str(o['dur'])[:5],o['lic'][:12].ljust(12),round((o['size'] or 0)/1e6,1),'MB',o['title'][5:80])
