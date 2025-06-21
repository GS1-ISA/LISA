#!/bin/bash
# ISA v2.1 Strategy Archive Auto-Push Script

echo "🔄 Adding all files..."
git add .

echo "🧠 Committing with strategy integration message..."
git commit -m "📌 Integrated ISA Strategy Archive v2.1: roadmap, routing logic, prompt strategy, mitigation, visuals"

echo "🚀 Pushing to origin main..."
git push origin main

echo "✅ Push complete. Please review GitHub Actions workflow for autonomous agent output."
