# Quickstart
Last updated: 2025-09-02

```bash
# 1) Clone and enter repo
git clone <repo>
cd <repo>

# 2) (Optional) Create virtualenv
python3 -m venv .venv && source .venv/bin/activate

# 3) Install deps
pip install -r ISA_SuperApp/requirements-dev.txt -r ISA_SuperApp/requirements.txt

# 4) Copy env template (edit as needed)
cp .env.example .env

# 5) Run tests (quick)
cd ISA_SuperApp && python3 -m pytest -q && cd ..

# 6) Start API
make api
# then open http://127.0.0.1:8787/ui/users
```
