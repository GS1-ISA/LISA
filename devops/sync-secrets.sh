
#!/bin/bash
# sync-secrets.sh: Sync secrets from Google Secret Manager into .env file

# Define secret names
SECRETS=("GOOGLE_API_KEY" "GCP_SA_KEY" "JIRA_WEBHOOK_SECRET" "GROUP_MAPPING")

# Define the environment (e.g., staging or production)
ENV=${1:-staging}

echo "# Loaded secrets for $ENV" > .env.$ENV

for SECRET in "${SECRETS[@]}"; do
  VALUE=$(gcloud secrets versions access latest --secret="${SECRET}_${ENV}")
  echo "${SECRET}=${VALUE}" >> .env.$ENV
done

echo ".env.$ENV successfully created from Secret Manager."
