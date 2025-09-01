# Packaging (Desktop)

Electron Builder targets:
- macOS: DMG
- Windows: NSIS

Commands:
```bash
cd desktop/electron
npm install
npm run dev
npm run dist
```
Electron starts API via scripts: `scripts/mac/start_api.sh` or `scripts/win/start_api.bat` then loads `http://127.0.0.1:8787/ui/users`.
