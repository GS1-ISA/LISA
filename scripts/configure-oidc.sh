#!/bin/bash
# OIDC Configuration Script for GitHub Actions

set -euo pipefail

# Source helper functions
source "$(dirname "$0")/unified-cicd-helpers.sh"

# Configuration
OIDC_PROVIDER="token.actions.githubusercontent.com"
AUDIENCE="api://AzureADTokenExchange"
DEFAULT_ROLE_SESSION_NAME="github-actions-deployment"

# AWS OIDC Configuration
configure_aws_oidc() {
    local account_id=$1
    local role_name=$2
    local repository=$3
    local environment=${4:-"*"}
    
    log_info "Configuring AWS OIDC for repository: $repository"
    
    # Create IAM OIDC provider (if not exists)
    local provider_arn="arn:aws:iam::$account_id:oidc-provider/$OIDC_PROVIDER"
    
    if ! aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$provider_arn" 2>/dev/null; then
        log_info "Creating OIDC provider for AWS"
        
        # Get GitHub's OIDC thumbprint
        local thumbprint=$(echo | openssl s_client -servername "$OIDC_PROVIDER" -connect "$OIDC_PROVIDER":443 2>/dev/null | openssl x509 -fingerprint -sha1 -noout | sed 's/SHA1 Fingerprint=//' | tr -d ':')
        
        aws iam create-open-id-connect-provider \
            --url "https://$OIDC_PROVIDER" \
            --client-id-list "sts.amazonaws.com" \
            --thumbprint-list "$thumbprint"
        
        log_success "OIDC provider created successfully"
    else
        log_info "OIDC provider already exists"
    fi
    
    # Create IAM role with trust policy
    local trust_policy=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "$provider_arn"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "$OIDC_PROVIDER:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "$OIDC_PROVIDER:sub": "repo:$repository:ref:refs/heads/*"
                }
            }
        }
    ]
}
EOF
)
    
    # Create or update IAM role
    if ! aws iam get-role --role-name "$role_name" 2>/dev/null; then
        log_info "Creating IAM role: $role_name"
        aws iam create-role \
            --role-name "$role_name" \
            --assume-role-policy-document "$trust_policy" \
            --description "GitHub Actions deployment role for $repository"
    else
        log_info "Updating IAM role: $role_name"
        aws iam update-assume-role-policy \
            --role-name "$role_name" \
            --policy-document "$trust_policy"
    fi
    
    log_success "AWS OIDC configuration completed"
    log_info "Role ARN: arn:aws:iam::$account_id:role/$role_name"
}

# Azure OIDC Configuration
configure_azure_oidc() {
    local subscription_id=$1
    local resource_group=$2
    local app_name=$3
    local repository=$4
    
    log_info "Configuring Azure OIDC for repository: $repository"
    
    # Create Azure AD application (if not exists)
    local app_id=$(az ad app list --display-name "$app_name" --query "[0].appId" -o tsv 2>/dev/null || echo "")
    
    if [[ -z "$app_id" ]]; then
        log_info "Creating Azure AD application: $app_name"
        app_id=$(az ad app create --display-name "$app_name" --query "appId" -o tsv)
        log_success "Azure AD application created: $app_id"
    else
        log_info "Using existing Azure AD application: $app_id"
    fi
    
    # Create service principal (if not exists)
    local sp_id=$(az ad sp list --display-name "$app_name" --query "[0].id" -o tsv 2>/dev/null || echo "")
    
    if [[ -z "$sp_id" ]]; then
        log_info "Creating service principal for application: $app_id"
        sp_id=$(az ad sp create --id "$app_id" --query "id" -o tsv)
        log_success "Service principal created: $sp_id"
    else
        log_info "Using existing service principal: $sp_id"
    fi
    
    # Configure federated credentials
    local fed_credential_name="github-actions-federation"
    
    # Remove existing federated credential if it exists
    az ad app federated-credential delete \
        --id "$app_id" \
        --federated-credential-id "$fed_credential_name" 2>/dev/null || true
    
    # Create new federated credential
    local repository_name=$(echo "$repository" | cut -d'/' -f2)
    local subject="repo:$repository:environment:production"
    
    log_info "Creating federated credential with subject: $subject"
    
    az ad app federated-credential create \
        --id "$app_id" \
        --parameters "{
            \"name\": \"$fed_credential_name\",
            \"issuer\": \"https://$OIDC_PROVIDER\",
            \"subject\": \"$subject\",
            \"description\": \"GitHub Actions OIDC federation\",
            \"audiences\": [\"api://AzureADTokenExchange\"]
        }"
    
    # Assign role to service principal
    local role_definition="Contributor"
    local scope="/subscriptions/$subscription_id/resourceGroups/$resource_group"
    
    log_info "Assigning role $role_definition to service principal at scope: $scope"
    
    # Remove existing role assignment
    local existing_assignment=$(az role assignment list \
        --assignee "$sp_id" \
        --role "$role_definition" \
        --scope "$scope" \
        --query "[0].id" -o tsv 2>/dev/null || echo "")
    
    if [[ -n "$existing_assignment" ]]; then
        az role assignment delete --ids "$existing_assignment"
    fi
    
    # Create new role assignment
    az role assignment create \
        --assignee "$sp_id" \
        --role "$role_definition" \
        --scope "$scope"
    
    log_success "Azure OIDC configuration completed"
    log_info "Application ID: $app_id"
    log_info "Service Principal ID: $sp_id"
}

# GCP OIDC Configuration
configure_gcp_oidc() {
    local project_id=$1
    local service_account=$2
    local repository=$3
    local pool_name=${4:-"github-actions-pool"}
    local provider_name=${5:-"github-actions-provider"}
    
    log_info "Configuring GCP OIDC for repository: $repository"
    
    # Create workload identity pool (if not exists)
    if ! gcloud iam workload-identity-pools describe "$pool_name" \
        --project="$project_id" \
        --location="global" 2>/dev/null; then
        
        log_info "Creating workload identity pool: $pool_name"
        gcloud iam workload-identity-pools create "$pool_name" \
            --project="$project_id" \
            --location="global" \
            --display-name="GitHub Actions Pool"
        
        log_success "Workload identity pool created"
    else
        log_info "Using existing workload identity pool: $pool_name"
    fi
    
    # Get pool ID
    local pool_id=$(gcloud iam workload-identity-pools describe "$pool_name" \
        --project="$project_id" \
        --location="global" \
        --format="value(name)")
    
    # Create OIDC provider (if not exists)
    if ! gcloud iam workload-identity-pools providers describe "$provider_name" \
        --project="$project_id" \
        --location="global" \
        --workload-identity-pool="$pool_name" 2>/dev/null; then
        
        log_info "Creating OIDC provider: $provider_name"
        gcloud iam workload-identity-pools providers create-oidc "$provider_name" \
            --project="$project_id" \
            --location="global" \
            --workload-identity-pool="$pool_name" \
            --display-name="GitHub Actions Provider" \
            --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
            --issuer-uri="https://$OIDC_PROVIDER"
        
        log_success "OIDC provider created"
    else
        log_info "Using existing OIDC provider: $provider_name"
    fi
    
    # Create service account (if not exists)
    if ! gcloud iam service-accounts describe "$service_account@$project_id.iam.gserviceaccount.com" \
        --project="$project_id" 2>/dev/null; then
        
        log_info "Creating service account: $service_account"
        gcloud iam service-accounts create "$service_account" \
            --project="$project_id" \
            --display-name="GitHub Actions Service Account"
        
        log_success "Service account created"
    else
        log_info "Using existing service account: $service_account"
    fi
    
    # Grant access to service account
    local member="principalSet://iam.googleapis.com/$pool_id/attribute.repository/$repository"
    
    log_info "Granting access to service account for repository: $repository"
    gcloud iam service-accounts add-iam-policy-binding \
        "$service_account@$project_id.iam.gserviceaccount.com" \
        --project="$project_id" \
        --role="roles/iam.workloadIdentityUser" \
        --member="$member"
    
    # Grant necessary roles to service account
    local roles=("roles/container.developer" "roles/storage.admin" "roles/iam.serviceAccountUser")
    
    for role in "${roles[@]}"; do
        log_info "Granting role $role to service account"
        gcloud projects add-iam-policy-binding "$project_id" \
            --member="serviceAccount:$service_account@$project_id.iam.gserviceaccount.com" \
            --role="$role" >/dev/null
    done
    
    log_success "GCP OIDC configuration completed"
    log_info "Service Account: $service_account@$project_id.iam.gserviceaccount.com"
    log_info "Workload Pool: $pool_name"
    log_info "Provider: $provider_name"
}

# Generate GitHub workflow configuration
generate_github_oidc_config() {
    local cloud_provider=$1
    local role_arn=$2
    local session_name=${3:-"github-actions-deployment"}
    
    log_info "Generating GitHub Actions OIDC configuration for: $cloud_provider"
    
    case $cloud_provider in
        "aws")
            cat <<EOF
# AWS OIDC Configuration
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: $role_arn
    role-session-name: $session_name
    aws-region: us-east-1
EOF
            ;;
        "azure")
            cat <<EOF
# Azure OIDC Configuration
- name: Azure login
  uses: azure/login@v1
  with:
    client-id: $(echo "$role_arn" | cut -d':' -f6)
    tenant-id: \${{ secrets.AZURE_TENANT_ID }}
    subscription-id: \${{ secrets.AZURE_SUBSCRIPTION_ID }}
EOF
            ;;
        "gcp")
            cat <<EOF
# GCP OIDC Configuration
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: $role_arn
    service_account: $session_name
EOF
            ;;
        *)
            log_error "Unknown cloud provider: $cloud_provider"
            exit 1
            ;;
    esac
}

# Main function
main() {
    local command=$1
    shift
    
    case $command in
        "aws")
            configure_aws_oidc "$@"
            ;;
        "azure")
            configure_azure_oidc "$@"
            ;;
        "gcp")
            configure_gcp_oidc "$@"
            ;;
        "generate-config")
            generate_github_oidc_config "$@"
            ;;
        *)
            echo "Usage: $0 {aws|azure|gcp|generate-config} [parameters...]"
            echo ""
            echo "AWS: $0 aws <account_id> <role_name> <repository> [environment]"
            echo "Azure: $0 azure <subscription_id> <resource_group> <app_name> <repository>"
            echo "GCP: $0 gcp <project_id> <service_account> <repository> [pool_name] [provider_name]"
            echo "Generate Config: $0 generate-config <cloud_provider> <role_arn> [session_name]"
            exit 1
            ;;
    esac
}

# Main entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 {aws|azure|gcp|generate-config} [parameters...]"
        exit 1
    fi
    
    main "$@"
fi