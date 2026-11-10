import sys, json
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[2], device="cpu", compute_type="int8")
import numpy as np, wave; wf=wave.open(sys.argv[1]); a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(np.float32)/32768
segs, info = m.transcribe(a, language="pt", word_timestamps=True, vad_filter=False)
words=[]
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words: words.append({"w":w.word.strip(),"s":round(w.start,2),"e":round(w.end,2)})
json.dump(words, open(sys.argv[3],"w"), ensure_ascii=False)
