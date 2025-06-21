
# 🔁 Simulated GitHub Deployment Pipeline: ISA + Firebase + Genkit

## ✅ Trigger: Push to `main` Branch
- GitHub Action `.github/workflows/ci.yml` starts
- Secrets loaded: `GOOGLE_API_KEY`, `GCP_SA_KEY`, `JIRA_WEBHOOK_SECRET`

## 🧪 Stage 1: Setup
- ✅ Node 18.x installed
- ✅ `npm ci` run
- ✅ All dependencies restored

## 📦 Stage 2: Lint & Type Check
- ✅ ESLint passes (`src/` + `ai/flows/`)
- ✅ TypeScript strict mode: OK

## 🧠 Stage 3: Genkit Flow Check
- ✅ Genkit CLI used to validate flow config
- ✅ All `.genkit.ts` tools pass compilation
- ✅ `genkit build --check` complete

## 🧬 Stage 4: Firebase Emulators (Staging)
- ✅ `firebase emulators:start --only functions,firestore`
- Logs show correct binding of functions to local endpoints
- Function `vectorSearchFlow` returns valid result from mock input

## 🔐 Stage 5: Secret Sync
- ✅ `sync-secrets.sh` invoked
- ✅ `.env.staging` → GitHub Actions secrets → Firebase CLI `functions:secrets:set`

## 🚀 Stage 6: Deploy to Firebase Hosting & Functions
- ✅ `firebase deploy --only hosting,functions`
- Hosting URL: https://isa-staging.web.app
- Functions:
  - `vectorSearchFlow`
  - `logStructuredTrace`
  - `updateKnowledgeGraph`

## 📊 Stage 7: Post-deploy Check & Monitoring
- ✅ Structured logging via Pino to Firestore
- ✅ Genkit flows tested via CI ping
- ✅ Alerting set up via Firebase Alerts

🎉 Final Status: **Successful**
