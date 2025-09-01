import os, json, shutil, yaml, pathlib
SILVER='data/silver'; OUT='exports/rag'
targets=['ollama','anythingllm','langchain','obsidian','freechat']
for t in targets:
    pathlib.Path(os.path.join(OUT,t)).mkdir(parents=True, exist_ok=True)

def pack_for_ollama(dirpath):
    # simple plaintext corpus
    dest=os.path.join(OUT,'ollama')
    for root,_,files in os.walk(dirpath):
        for f in files:
            if f.endswith('.md'):
                shutil.copy2(os.path.join(root,f), os.path.join(dest,f))
def pack_for_anythingllm(dirpath):
    dest=os.path.join(OUT,'anythingllm')
    for root,_,files in os.walk(dirpath):
        for f in files:
            if f.endswith('.md'):
                shutil.copy2(os.path.join(root,f), os.path.join(dest,f.replace('.md','.txt')))
def pack_for_langchain(dirpath):
    dest=os.path.join(OUT,'langchain'); idx=[]
    for root,_,files in os.walk(dirpath):
        for f in files:
            if f.endswith('.md'):
                p=os.path.join(dest, os.path.relpath(os.path.join(root,f), start=dirpath).replace(os.sep,'__'))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                shutil.copy2(os.path.join(root,f), p)
                idx.append({"path":p,"metadata":{}})
    with open(os.path.join(dest,'index.json'),'w') as jf: json.dump(idx, jf, indent=2)
def pack_for_obsidian(dirpath):
    dest=os.path.join(OUT,'obsidian','.obsidian'); os.makedirs(dest, exist_ok=True)
    vault=os.path.join(OUT,'obsidian'); 
    for root,_,files in os.walk(dirpath):
        for f in files:
            if f.endswith('.md'):
                shutil.copy2(os.path.join(root,f), os.path.join(vault,f))
def pack_for_freechat(dirpath):
    dest=os.path.join(OUT,'freechat')
    for root,_,files in os.walk(dirpath):
        for f in files:
            if f.endswith('.md'):
                shutil.copy2(os.path.join(root,f), os.path.join(dest,f))

for d in os.listdir(SILVER):
    dirpath=os.path.join(SILVER,d)
    if not os.path.isdir(dirpath): continue
    pack_for_ollama(dirpath)
    pack_for_anythingllm(dirpath)
    pack_for_langchain(dirpath)
    pack_for_obsidian(dirpath)
    pack_for_freechat(dirpath)

print(json.dumps({"status":"ok","exports":"done"}))
