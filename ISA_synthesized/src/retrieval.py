import os, math, json, logging, re
from typing import List, Dict, Tuple, Optional
from collections import Counter
log = logging.getLogger("retrieval")
def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())
class EmbeddingClient:
    def __init__(self):
        self.backend = os.getenv("ISA_EMBEDDING_BACKEND","lexical").lower()
        self.model = os.getenv("ISA_EMBEDDING_MODEL","all-MiniLM-L6-v2")
        self._sentence_model = None
        if self.backend == "sentence":
            try:
                from sentence_transformers import SentenceTransformer
                self._sentence_model = SentenceTransformer(self.model)
            except Exception as e:
                log.warning("sentence-transformers not available: %s; falling back to lexical", e)
                self.backend = "lexical"
    def embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        if self.backend == "sentence" and self._sentence_model:
            try:
                vecs = self._sentence_model.encode(texts, normalize_embeddings=True)
                return [v.tolist() for v in vecs]
            except Exception as e:
                log.warning("Sentence embeddings error: %s", e)
                return None
        return None  # lexical only
def _cosine(a: List[float], b: List[float]) -> float:
    num = sum(x*y for x,y in zip(a,b))
    da = math.sqrt(sum(x*x for x in a)) or 1e-9
    db = math.sqrt(sum(y*y for y in b)) or 1e-9
    return num/(da*db)
class VectorIndex:
    def __init__(self, storage_path: str = "storage/index.json", embedding_client: Optional[EmbeddingClient]=None):
        self.storage_path = storage_path
        self.embedding_client = embedding_client or EmbeddingClient()
        self.docs: List[Dict] = []
        self.vecs: Optional[List[List[float]]] = None
        self.lex_df = Counter()
        self.lex_vocab_docs = 0
        self._load()
    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.docs = data.get("docs",[])
                self.vecs = data.get("vecs")
                self.lex_df = Counter(data.get("lex_df",{}))
                self.lex_vocab_docs = data.get("lex_vocab_docs", 0)
            except Exception:
                pass
    def _save(self):
        dirp = os.path.dirname(self.storage_path)
        if dirp: os.makedirs(dirp, exist_ok=True)
        data = {"docs": self.docs, "vecs": self.vecs, "lex_df": dict(self.lex_df), "lex_vocab_docs": self.lex_vocab_docs}
        with open(self.storage_path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
    def rebuild(self, docs: List[Tuple[str, str, Dict]]):
        self.docs = [{"id": d, "text": t, "meta": m} for d,t,m in docs]
        texts = [d["text"] for d in self.docs]
        vecs = self.embedding_client.embed(texts)
        self.vecs = vecs
        self.lex_df = Counter()
        self.lex_vocab_docs = len(texts)
        for t in texts:
            toks = set(_tokenize(t))
            for tok in toks: self.lex_df[tok]+=1
        self._save()
    def _lex_score(self, query: str, text: str) -> float:
        q = _tokenize(query); d = _tokenize(text)
        if not q or not d: return 0.0
        tf_q=Counter(q); tf_d=Counter(d)
        vocab = list(set(tf_q)|set(tf_d))
        def tfidf(tf, tok):
            tfv=tf.get(tok,0); df=self.lex_df.get(tok,1); import math
            idf=math.log((self.lex_vocab_docs+1)/(df+0.5)); return tfv*idf
        vq=[tfidf(tf_q,t) for t in vocab]; vd=[tfidf(tf_d,t) for t in vocab]
        num=sum(a*b for a,b in zip(vq,vd)); import math
        dq=math.sqrt(sum(a*a for a in vq)) or 1e-9; dd=math.sqrt(sum(b*b for b in vd)) or 1e-9
        return num/(dq*dd)
    def search(self, query: str, k: int = 5) -> List[Dict]:
        scores=[]
        if self.vecs:
            qv = self.embedding_client.embed([query])
            if qv and qv[0]:
                qvec = qv[0]
                for i,doc in enumerate(self.docs):
                    s = _cosine(qvec, self.vecs[i]); scores.append((s, doc))
        if not scores:
            for doc in self.docs:
                s = self._lex_score(query, doc["text"]); scores.append((s, doc))
        scores.sort(key=lambda x:x[0], reverse=True)
        return [{"score": float(s), **d} for s,d in scores[:k]]
