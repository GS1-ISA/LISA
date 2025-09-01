from __future__ import annotations
from datetime import datetime
import os, pandas as pd
from pathlib import Path
from isa_c.adapters.base import BaseAdapter

class EfragAdapter(BaseAdapter):
    def fetch(self, since: datetime) -> pd.DataFrame:
        offline = os.getenv("ISA_OFFLINE","1") == "1"
        outdir = Path("data/raw/efrag")
        outdir.mkdir(parents=True, exist_ok=True)
        sample = outdir / "sample.csv"
        if offline:
            # Write a fresh sample each run (timestamped row)
            sample.write_text("id,title,date\n1,Offline Sample,{datetime.utcnow().date()}\n", encoding="utf-8")
            return pd.read_csv(sample)
        # TODO: implement real API call here
        sample.write_text("id,title,date\n1,Online Placeholder,{datetime.utcnow().date()}\n", encoding="utf-8")
        return pd.read_csv(sample)

def run(since: datetime) -> pd.DataFrame:
    return EfragAdapter().run(since)
