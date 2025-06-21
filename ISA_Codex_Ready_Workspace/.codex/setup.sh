#!/usr/bin/env bash
set -euo pipefail

echo "🔧 ISA Codex Bootstrap: Installing dependencies..."

# Verify key environment variables
: "${GOOGLE_API_KEY:?GOOGLE_API_KEY is not set}"
: "${FIREBASE_PROJECT:?FIREBASE_PROJECT is not set}"

npm install -g firebase-tools @genkit-ai/cli

echo "Installing frontend dependencies..."
cd web && npm install && cd ..

echo "Installing backend dependencies..."
cd functions && npm install && cd ..

echo "Installing Python validation dependencies..."
pip install -r requirements.txt || echo "No requirements.txt found."

echo "✅ ISA environment is ready. You may now run Firebase deploy or Genkit workflows."
