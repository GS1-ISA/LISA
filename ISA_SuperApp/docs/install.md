# Installation (macOS)
Last updated: 2025-09-02

## Prereqs
- macOS 14+ (Apple Silicon)
- Xcode CLT: `xcode-select --install`
- Homebrew (optional)
- Python 3.11+
- Node 20+ and npm

## Steps
```bash
make setup      # creates .venv + installs Python deps
make test       # runs unit + smoke tests
make run        # starts API at http://127.0.0.1:8787
```

## Desktop App (DMG)
```bash
cd desktop/electron
npm install
npx electron-builder --mac dmg
open dist/*.dmg
```


## Universal (arm64+x64) build
```bash
cd desktop/electron
npm install
npx electron-builder --mac universal
open dist/*.dmg
```

## Configuration

### LLM Provider

By default, the application uses OpenRouter as the LLM provider. You can also configure it to use OpenAI's models.

To use OpenAI, you will need an OpenAI API key. You can get one from [platform.openai.com](https://platform.openai.com/).

Once you have your API key, you can use the `scripts/setup_openai.sh` script to configure the application to use it:

```bash
./scripts/setup_openai.sh
```

This will create a `.env` file in the project root with your API key and set the `ISA_LLM_PROVIDER` to `openai`.

If you want to switch back to OpenRouter, you can either delete the `.env` file or change the `ISA_LLM_PROVIDER` to `openrouter`.
