import os, json, yaml, re, hashlib, pathlib
RAW='data/raw'; OUT='data/silver'
os.makedirs(OUT, exist_ok=True)
def read_txt(fp):
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f: return f.read()
    except: return ""
def chunks(txt, sz=1200, overlap=200):
    i=0; L=len(txt)
    while i<L:
        yield txt[i:i+sz]
        i+=sz-overlap
def meta_for(fp, text):
    h=hashlib.sha256(text.encode('utf-8','ignore')).hexdigest()[:16]
    return {"source_path":fp,"checksum":h}
def process_file(fp):
    text=read_txt(fp)
    if not text: return 0
    stem=os.path.splitext(os.path.basename(fp))[0]
    out_dir=os.path.join(OUT, stem); os.makedirs(out_dir, exist_ok=True)
    n=0
    for i,ch in enumerate(chunks(text)):
        p_txt=os.path.join(out_dir, f"chunk_{i:04d}.md")
        p_meta=os.path.join(out_dir, f"chunk_{i:04d}.meta.yaml")
        with open(p_txt,'w',encoding='utf-8') as f: f.write(ch)
        with open(p_meta,'w',encoding='utf-8') as f: yaml.safe_dump(meta_for(fp, ch), f)
        n+=1
    return n
total=0
for root,_,files in os.walk(RAW):
    for f in files:
        if f.lower().endswith(('.txt','.md','.csv','.json','.ttl','.xml','.rdf','.html','.htm')):
            total+=process_file(os.path.join(root,f))
print(json.dumps({"status":"ok","chunks":total}))
