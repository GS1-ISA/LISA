# Secrets Management for ISA DevOps

## Overview
All secrets are managed through Google Cloud Secret Manager and injected into `.env` files via the provided sync script.

## Recommended Practices
- Rotate keys regularly
- Use `sync-secrets.sh` to generate `.env` files locally
- Never commit `.env` files or credentials

## Required Secrets
- `GOOGLE_API_KEY_<ENV>`
- `GCP_SA_KEY_<ENV>`
- `JIRA_WEBHOOK_SECRET_<ENV>`
- `GROUP_MAPPING_<ENV>`

## Syncing
Run:
```bash
bash sync-secrets.sh staging
```
