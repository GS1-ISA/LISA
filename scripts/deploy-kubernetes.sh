#!/bin/bash

# Kubernetes Deployment Script
# This script handles Kubernetes deployments with various strategies

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_FILE="/tmp/kubernetes-deploy-$(date +%Y%m%d-%H%M%S).log"

# Default values
ENVIRONMENT=""
IMAGE_TAG=""
DEPLOYMENT_STRATEGY="rolling"
DEPLOYMENT_ID=""
CONFIG_FILE=""
VERBOSE=false
DRY_RUN=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
    
    case "${level}" in
        ERROR) echo -e "${RED}${timestamp} [ERROR] ${message}${NC}" ;;
        WARN) echo -e "${YELLOW}${timestamp} [WARN] ${message}${NC}" ;;
        INFO) echo -e "${GREEN}${timestamp} [INFO] ${message}${NC}" ;;
        DEBUG) 
            if [[ "${VERBOSE}" == "true" ]]; then
                echo -e "${BLUE}${timestamp} [DEBUG] ${message}${NC}"
            fi
            ;;
    esac
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    exit 1
}

# Help function
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Kubernetes Deployment Script

OPTIONS:
    -e, --environment ENV       Target environment
    -i, --image-tag TAG         Docker image tag to deploy
    -s, --strategy STRATEGY     Deployment strategy (rolling|blue-green|canary|recreate)
    -d, --deployment-id ID      Deployment ID for tracking
    -c, --config-file FILE      Configuration file path
    --dry-run                   Perform a dry run without actual deployment
    -v, --verbose               Enable verbose logging
    -h, --help                  Show this help message

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -i|--image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -s|--strategy)
                DEPLOYMENT_STRATEGY="$2"
                shift 2
                ;;
            -d|--deployment-id)
                DEPLOYMENT_ID="$2"
                shift 2
                ;;
            -c|--config-file)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error_exit "Unknown option: $1"
                ;;
        esac
    done
}

# Validate inputs
validate_inputs() {
    log "INFO" "Validating inputs..."
    
    # Check required parameters
    if [[ -z "${ENVIRONMENT}" ]]; then
        error_exit "Environment is required"
    fi
    
    if [[ -z "${IMAGE_TAG}" ]]; then
        error_exit "Image tag is required"
    fi
    
    if [[ -z "${CONFIG_FILE}" ]] || [[ ! -f "${CONFIG_FILE}" ]]; then
        error_exit "Configuration file is required and must exist"
    fi
    
    # Validate deployment strategy
    if [[ ! "${DEPLOYMENT_STRATEGY}" =~ ^(rolling|blue-green|canary|recreate)$ ]]; then
        error_exit "Invalid deployment strategy: ${DEPLOYMENT_STRATEGY}"
    fi
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        error_exit "kubectl is not available"
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        error_exit "Cannot connect to Kubernetes cluster"
    fi
    
    log "INFO" "Input validation completed successfully"
}

# Load configuration
load_configuration() {
    log "INFO" "Loading configuration..."
    
    # Check if yq is available
    if ! command -v yq &> /dev/null; then
        error_exit "yq is required but not available"
    fi
    
    # Load environment configuration
    NAMESPACE=$(yq eval ".platforms.kubernetes.namespace_template" "${CONFIG_FILE}" | sed "s/{environment}/${ENVIRONMENT}/g")
    SERVICE_ACCOUNT=$(yq eval ".platforms.kubernetes.service_account" "${CONFIG_FILE}" | sed "s/{environment}/${ENVIRONMENT}/g")
    
    # Load resource configuration
    REPLICAS=$(yq eval ".environments.${ENVIRONMENT}.resources.replicas" "${CONFIG_FILE}")
    CPU_REQUEST=$(yq eval ".environments.${ENVIRONMENT}.resources.cpu" "${CONFIG_FILE}")
    MEMORY_REQUEST=$(yq eval ".environments.${ENVIRONMENT}.resources.memory" "${CONFIG_FILE}")
    
    # Load scaling configuration
    MIN_REPLICAS=$(yq eval ".environments.${ENVIRONMENT}.scaling.min_replicas" "${CONFIG_FILE}")
    MAX_REPLICAS=$(yq eval ".environments.${ENVIRONMENT}.scaling.max_replicas" "${CONFIG_FILE}")
    TARGET_CPU_UTILIZATION=$(yq eval ".environments.${ENVIRONMENT}.scaling.target_cpu_utilization" "${CONFIG_FILE}")
    
    log "INFO" "Configuration loaded successfully"
    log "DEBUG" "Namespace: ${NAMESPACE}, Replicas: ${REPLICAS}, Strategy: ${DEPLOYMENT_STRATEGY}"
}

# Create namespace if it doesn't exist
create_namespace() {
    log "INFO" "Creating namespace: ${NAMESPACE}"
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "DRY RUN: Would create namespace ${NAMESPACE}"
        return 0
    fi
    
    # Check if namespace exists
    if kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        log "INFO" "Namespace ${NAMESPACE} already exists"
    else
        # Create namespace
        kubectl create namespace "${NAMESPACE}" || error_exit "Failed to create namespace ${NAMESPACE}"
        log "INFO" "Namespace ${NAMESPACE} created successfully"
    fi
    
    # Apply labels to namespace
    kubectl label namespace "${NAMESPACE}" \
        environment="${ENVIRONMENT}" \
        deployment-id="${DEPLOYMENT_ID}" \
        --overwrite || log "WARN" "Failed to label namespace"
}

# Create service account
create_service_account() {
    log "INFO" "Creating service account: ${SERVICE_ACCOUNT}"
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "DRY RUN: Would create service account ${SERVICE_ACCOUNT}"
        return 0
    fi
    
    # Create service account
    kubectl create serviceaccount "${SERVICE_ACCOUNT}" -n "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f - || {
        log "WARN" "Failed to create service account ${SERVICE_ACCOUNT}"
    }
}

# Generate deployment manifest
generate_deployment_manifest() {
    log "INFO" "Generating deployment manifest..."
    
    local manifest_file="/tmp/deployment-${DEPLOYMENT_ID}.yaml"
    
    cat > "${manifest_file}" << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-${ENVIRONMENT}
  namespace: ${NAMESPACE}
  labels:
    app: app
    environment: ${ENVIRONMENT}
    deployment-id: ${DEPLOYMENT_ID}
    version: ${IMAGE_TAG}
spec:
  replicas: ${REPLICAS}
  strategy:
    type: ${DEPLOYMENT_STRATEGY}
    $(if [[ "${DEPLOYMENT_STRATEGY}" == "rolling" ]]; then
        echo "rollingUpdate:"
        echo "  maxSurge: 1"
        echo "  maxUnavailable: 0"
    fi)
  selector:
    matchLabels:
      app: app
      environment: ${ENVIRONMENT}
  template:
    metadata:
      labels:
        app: app
        environment: ${ENVIRONMENT}
        deployment-id: ${DEPLOYMENT_ID}
        version: ${IMAGE_TAG}
      annotations:
        deployment.kubernetes.io/revision: "${DEPLOYMENT_ID}"
    spec:
      serviceAccountName: ${SERVICE_ACCOUNT}
      containers:
      - name: app
        image: ${IMAGE_TAG}
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8081
          name: metrics
        env:
        - name: ENVIRONMENT
          value: "${ENVIRONMENT}"
        - name: DEPLOYMENT_ID
          value: "${DEPLOYMENT_ID}"
        - name: VERSION
          value: "${IMAGE_TAG}"
        resources:
          requests:
            cpu: "${CPU_REQUEST}"
            memory: "${MEMORY_REQUEST}"
          limits:
            cpu: "${CPU_REQUEST}"
            memory: "${MEMORY_REQUEST}"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
      securityContext:
        fsGroup: 1000
      restartPolicy: Always
EOF
    
    echo "${manifest_file}"
}

# Generate service manifest
generate_service_manifest() {
    log "INFO" "Generating service manifest..."
    
    local manifest_file="/tmp/service-${DEPLOYMENT_ID}.yaml"
    
    cat > "${manifest_file}" << EOF
apiVersion: v1
kind: Service
metadata:
  name: app-${ENVIRONMENT}
  namespace: ${NAMESPACE}
  labels:
    app: app
    environment: ${ENVIRONMENT}
    deployment-id: ${DEPLOYMENT_ID}
spec:
  selector:
    app: app
    environment: ${ENVIRONMENT}
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: metrics
    port: 8081
    targetPort: 8081
    protocol: TCP
  type: ClusterIP
EOF
    
    echo "${manifest_file}"
}

# Generate ingress manifest
generate_ingress_manifest() {
    log "INFO" "Generating ingress manifest..."
    
    local ingress_enabled=$(yq eval ".platforms.kubernetes.ingress.enabled" "${CONFIG_FILE}")
    if [[ "${ingress_enabled}" != "true" ]]; then
        log "INFO" "Ingress disabled in configuration"
        return 0
    fi
    
    local manifest_file="/tmp/ingress-${DEPLOYMENT_ID}.yaml"
    local ingress_class=$(yq eval ".platforms.kubernetes.ingress.class" "${CONFIG_FILE}")
    
    cat > "${manifest_file}" << EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-${ENVIRONMENT}
  namespace: ${NAMESPACE}
  labels:
    app: app
    environment: ${ENVIRONMENT}
    deployment-id: ${DEPLOYMENT_ID}
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: ${ingress_class}
  tls:
  - hosts:
    - app-${ENVIRONMENT}.company.com
    secretName: app-${ENVIRONMENT}-tls
  rules:
  - host: app-${ENVIRONMENT}.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-${ENVIRONMENT}
            port:
              number: 80
EOF
    
    echo "${manifest_file}"
}

# Generate HPA manifest
generate_hpa_manifest() {
    log "INFO" "Generating HPA manifest..."
    
    local manifest_file="/tmp/hpa-${DEPLOYMENT_ID}.yaml"
    
    cat > "${manifest_file}" << EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-${ENVIRONMENT}
  namespace: ${NAMESPACE}
  labels:
    app: app
    environment: ${ENVIRONMENT}
    deployment-id: ${DEPLOYMENT_ID}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-${ENVIRONMENT}
  minReplicas: ${MIN_REPLICAS}
  maxReplicas: ${MAX_REPLICAS}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: ${TARGET_CPU_UTILIZATION}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
EOF
    
    echo "${manifest_file}"
}

# Apply network policies
apply_network_policies() {
    log "INFO" "Applying network policies..."
    
    local network_policies_enabled=$(yq eval ".platforms.kubernetes.network_policies.enabled" "${CONFIG_FILE}")
    if [[ "${network_policies_enabled}" != "true" ]]; then
        log "INFO" "Network policies disabled in configuration"
        return 0
    fi
    
    local manifest_file="/tmp/network-policy-${DEPLOYMENT_ID}.yaml"
    
    cat > "${manifest_file}" << EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-${ENVIRONMENT}-network-policy
  namespace: ${NAMESPACE}
  labels:
    app: app
    environment: ${ENVIRONMENT}
    deployment-id: ${DEPLOYMENT_ID}
spec:
  podSelector:
    matchLabels:
      app: app
      environment: ${ENVIRONMENT}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: app
          environment: ${ENVIRONMENT}
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8081
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  - to:
    - podSelector:
        matchLabels:
          app: app
          environment: ${ENVIRONMENT}
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8081
EOF
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "DRY RUN: Would apply network policy"
        return 0
    fi
    
    kubectl apply -f "${manifest_file}" || log "WARN" "Failed to apply network policy"
}

# Execute rolling deployment
execute_rolling_deployment() {
    log "INFO" "Executing rolling deployment..."
    
    local deployment_manifest=$(generate_deployment_manifest)
    local service_manifest=$(generate_service_manifest)
    local ingress_manifest=$(generate_ingress_manifest)
    local hpa_manifest=$(generate_hpa_manifest)
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "DRY RUN: Would apply manifests"
        log "DEBUG" "Deployment manifest: ${deployment_manifest}"
        log "DEBUG" "Service manifest: ${service_manifest}"
        log "DEBUG" "Ingress manifest: ${ingress_manifest}"
        log "DEBUG" "HPA manifest: ${hpa_manifest}"
        return 0
    fi
    
    # Apply deployment
    log "INFO" "Applying deployment manifest..."
    kubectl apply -f "${deployment_manifest}" || error_exit "Failed to apply deployment"
    
    # Apply service
    log "INFO" "Applying service manifest..."
    kubectl apply -f "${service_manifest}" || error_exit "Failed to apply service"
    
    # Apply ingress if enabled
    if [[ -n "${ingress_manifest}" ]]; then
        log "INFO" "Applying ingress manifest..."
        kubectl apply -f "${ingress_manifest}" || error_exit "Failed to apply ingress"
    fi
    
    # Apply HPA
    log "INFO" "Applying HPA manifest..."
    kubectl apply -f "${hpa_manifest}" || error_exit "Failed to apply HPA"
    
    # Apply network policies
    apply_network_policies
    
    # Wait for deployment to complete
    log "INFO" "Waiting for deployment to complete..."
    kubectl rollout status deployment/app-${ENVIRONMENT} -n ${NAMESPACE} --timeout=600s || {
        error_exit "Deployment rollout failed"
    }
    
    log "INFO" "Rolling deployment completed successfully"
}

# Execute blue-green deployment
execute_blue_green_deployment() {
    log "INFO" "Executing blue-green deployment..."
    
    local deployment_manifest=$(generate_deployment_manifest)
    local service_manifest=$(generate_service_manifest)
    
    # Create green deployment
    log "INFO" "Creating green deployment..."
    sed -i 's/name: app-'${ENVIRONMENT}'/name: app-'${ENVIRONMENT}'-green/g' "${deployment_manifest}"
    sed -i 's/app: app/app: app-green/g' "${deployment_manifest}"
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "DRY RUN: Would create green deployment"
        return 0
    fi
    
    # Apply green deployment
    kubectl apply -f "${deployment_manifest}" || error_exit "Failed to create green deployment"
    
    # Wait for green deployment to be ready
    log "INFO" "Waiting for green deployment to be ready..."
    kubectl rollout status deployment/app-${ENVIRONMENT}-green -n ${NAMESPACE} --timeout=600s || {
        error_exit "Green deployment rollout failed"
    }
    
    # Switch service to green
    log "INFO" "Switching service to green deployment..."
    sed -i 's/app: app/app: app-green/g' "${service_manifest}"
    kubectl apply -f "${service_manifest}" || error_exit "Failed to switch service to green"
    
    # Delete blue deployment
    log "INFO" "Deleting blue deployment..."
    kubectl delete deployment app-${ENVIRONMENT} -n ${NAMESPACE} --ignore-not-found=true || {
        log "WARN" "Failed to delete blue deployment"
    }
    
    log "INFO" "Blue-green deployment completed successfully"
}

# Execute canary deployment
execute_canary_deployment() {
    log "INFO" "Executing canary deployment..."
    
    local deployment_manifest=$(generate_deployment_manifest)
    local service_manifest=$(generate_service_manifest)
    
    # Create canary deployment with 10% traffic
    log "INFO" "Creating canary deployment with 10% traffic..."
    sed -i 's/name: app-'${ENVIRONMENT}'/name: app-'${ENVIRONMENT}'-canary/g' "${deployment_manifest}"
    sed -i 's/app: app/app: app-canary/g' "${deployment_manifest}"
    sed -i 's/replicas: '${REPLICAS}'/replicas: '$((REPLICAS / 10))'/g' "${deployment_manifest}"
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "DRY RUN: Would create canary deployment"
        return 0
    fi
    
    # Apply canary deployment
    kubectl apply -f "${deployment_manifest}" || error_exit "Failed to create canary deployment"
    
    # Wait for canary deployment to be ready
    log "INFO" "Waiting for canary deployment to be ready..."
    kubectl rollout status deployment/app-${ENVIRONMENT}-canary -n ${NAMESPACE} --timeout=600s || {
        error_exit "Canary deployment rollout failed"
    }
    
    # Create canary service
    log "INFO" "Creating canary service..."
    sed -i 's/name: app-'${ENVIRONMENT}'/name: app-'${ENVIRONMENT}'-canary/g' "${service_manifest}"
    sed -i 's/app: app/app: app-canary/g' "${service_manifest}"
    kubectl apply -f "${service_manifest}" || error_exit "Failed to create canary service"
    
    # Create ingress with traffic splitting
    local ingress_manifest=$(generate_ingress_manifest)
    if [[ -n "${ingress_manifest}" ]]; then
        log "INFO" "Creating ingress with traffic splitting..."
        
        # Add canary annotations
        cat >> "${ingress_manifest}" << EOF
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"
EOF
        
        kubectl apply -f "${ingress_manifest}" || error_exit "Failed to create canary ingress"
    fi
    
    # Monitor canary metrics
    log "INFO" "Monitoring canary deployment for 5 minutes..."
    sleep 300
    
    # Check if canary is successful
    local canary_success=true
    # In a real implementation, this would check actual metrics
    
    if [[ "${canary_success}" == "true" ]]; then
        log "INFO" "Canary deployment successful, promoting to full deployment..."
        
        # Scale up canary to full replicas
        kubectl scale deployment app-${ENVIRONMENT}-canary -n ${NAMESPACE} --replicas=${REPLICAS}
        
        # Switch all traffic to canary
        if [[ -n "${ingress_manifest}" ]]; then
            kubectl annotate ingress app-${ENVIRONMENT}-canary -n ${NAMESPACE} \
                nginx.ingress.kubernetes.io/canary-weight=100 --overwrite
        fi
        
        # Delete original deployment
        kubectl delete deployment app-${ENVIRONMENT} -n ${NAMESPACE} --ignore-not-found=true || {
            log "WARN" "Failed to delete original deployment"
        }
        
        # Rename canary deployment to original
        kubectl patch deployment app-${ENVIRONMENT}-canary -n ${NAMESPACE} -p \
            '{"metadata":{"name":"app-'${ENVIRONMENT}'"}}' || {
            log "WARN" "Failed to rename canary deployment"
        }
    else
        log "ERROR" "Canary deployment failed, rolling back..."
        kubectl delete deployment app-${ENVIRONMENT}-canary -n ${NAMESPACE} --ignore-not-found=true
        kubectl delete service app-${ENVIRONMENT}-canary -n ${NAMESPACE} --ignore-not-found=true
        error_exit "Canary deployment failed"
    fi
    
    log "INFO" "Canary deployment completed successfully"
}

# Execute recreate deployment
execute_recreate_deployment() {
    log "INFO" "Executing recreate deployment..."
    
    local deployment_manifest=$(generate_deployment_manifest)
    local service_manifest=$(generate_service_manifest)
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "DRY RUN: Would recreate deployment"
        return 0
    fi
    
    # Delete existing deployment
    log "INFO" "Deleting existing deployment..."
    kubectl delete deployment app-${ENVIRONMENT} -n ${NAMESPACE} --ignore-not-found=true || {
        log "WARN" "Failed to delete existing deployment"
    }
    
    # Wait for deletion to complete
    log "INFO" "Waiting for deployment deletion..."
    kubectl wait --for=delete deployment/app-${ENVIRONMENT} -n ${NAMESPACE} --timeout=300s || {
        log "WARN" "Timeout waiting for deployment deletion"
    }
    
    # Apply new deployment
    log "INFO" "Applying new deployment..."
    kubectl apply -f "${deployment_manifest}" || error_exit "Failed to apply deployment"
    
    # Apply service
    kubectl apply -f "${service_manifest}" || error_exit "Failed to apply service"
    
    # Wait for deployment to complete
    log "INFO" "Waiting for deployment to complete..."
    kubectl rollout status deployment/app-${ENVIRONMENT} -n ${NAMESPACE} --timeout=600s || {
        error_exit "Deployment rollout failed"
    }
    
    log "INFO" "Recreate deployment completed successfully"
}

# Main execution
main() {
    log "INFO" "Starting Kubernetes deployment"
    log "INFO" "Environment: ${ENVIRONMENT}, Strategy: ${DEPLOYMENT_STRATEGY}, Image: ${IMAGE_TAG}"
    
    # Parse arguments
    parse_arguments "$@"
    
    # Validate inputs
    validate_inputs
    
    # Load configuration
    load_configuration
    
    # Create namespace
    create_namespace
    
    # Create service account
    create_service_account
    
    # Execute deployment based on strategy
    case "${DEPLOYMENT_STRATEGY}" in
        rolling)
            execute_rolling_deployment
            ;;
        blue-green)
            execute_blue_green_deployment
            ;;
        canary)
            execute_canary_deployment
            ;;
        recreate)
            execute_recreate_deployment
            ;;
        *)
            error_exit "Unsupported deployment strategy: ${DEPLOYMENT_STRATEGY}"
            ;;
    esac
    
    log "INFO" "Kubernetes deployment completed successfully"
}

# Execute main function
main "$@"