# Environment Configuration Guide

This document explains how to prepare environment variables and configure Firebase for local development.

## 1. Create your `.env`
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in the placeholders with your actual credentials. Keys include API tokens for OpenAI, Claude, Gemini, Firebase configuration and database settings.

## 2. Install required tooling
- [Node.js](https://nodejs.org/) 18+
- [Firebase CLI](https://firebase.google.com/docs/cli) (`npm install -g firebase-tools`)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) for Google Cloud operations

## 3. Run the setup script
Execute the project setup script which installs dependencies, creates `.env` if needed and builds the project:
```bash
./scripts/setup.sh
```

## 4. Configure Firebase and gcloud
Use the helper script to set the active Firebase project and gcloud project ID based on your `.env`:
```bash
./scripts/configure_firebase.sh
```
This script reads `GCP_PROJECT_ID` from `.env` and configures both the Firebase CLI and gcloud. Ensure you are logged in (`firebase login` and `gcloud auth login`) before running it.

### Primary Firebase Development Project
The primary Firebase development project for ISA is accessible via the Firebase Studio at:
`https://studio.firebase.google.com/main-6-juni-48577360`

This project ID (`main-6-juni-48577360`) is configured in your `.env` file under `GCP_PROJECT_ID` and in `firebase.json` as the default project.

## 5. Start the emulators
```bash
firebase emulators:start
```
The emulator ports are defined in `firebase.json` and mirrored in `.env`.

## 6. Start the development server
```bash
npm run dev
```
Open <http://localhost:9002> in your browser.

For Genkit flows, run:
```bash
npm run genkit:dev
```
which exposes the developer UI on <http://localhost:4000/dev>.

