#!/bin/bash

set -euo pipefail

# Default values
ENVIRONMENT="development"
PLATFORM="kubernetes"
TIMEOUT=300
INTERVAL=10
MAX_RETRIES=30
ENDPOINT="/health"
NAMESPACE=""
SERVICE_NAME=""
CLUSTER_NAME=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    --interval)
      INTERVAL="$2"
      shift 2
      ;;
    --max-retries)
      MAX_RETRIES="$2"
      shift 2
      ;;
    --endpoint)
      ENDPOINT="$2"
      shift 2
      ;;
    --namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    --service-name)
      SERVICE_NAME="$2"
      shift 2
      ;;
    --cluster-name)
      CLUSTER_NAME="$2"
      shift 2
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Set defaults based on environment
if [ -z "$NAMESPACE" ]; then
  NAMESPACE="$ENVIRONMENT"
fi

if [ -z "$SERVICE_NAME" ]; then
  SERVICE_NAME="app-$ENVIRONMENT-service"
fi

if [ -z "$CLUSTER_NAME" ]; then
  CLUSTER_NAME="app-$ENVIRONMENT-cluster"
fi

echo "Starting health check..."
echo "Environment: $ENVIRONMENT"
echo "Platform: $PLATFORM"
echo "Timeout: $TIMEOUT"
echo "Interval: $INTERVAL"
echo "Max Retries: $MAX_RETRIES"
echo "Endpoint: $ENDPOINT"
echo "Namespace: $NAMESPACE"
echo "Service Name: $SERVICE_NAME"
echo "Cluster Name: $CLUSTER_NAME"

# Platform-specific health check logic
case "$PLATFORM" in
  "kubernetes")
    echo "Performing Kubernetes health check..."
    
    # Get service endpoint
    SERVICE_IP=$(kubectl get service -n "$NAMESPACE" -l app=app-"$ENVIRONMENT" -o jsonpath='{.items[0].spec.clusterIP}')
    SERVICE_PORT=$(kubectl get service -n "$NAMESPACE" -l app=app-"$ENVIRONMENT" -o jsonpath='{.items[0].spec.ports[0].port}')
    
    if [ -z "$SERVICE_IP" ] || [ -z "$SERVICE_PORT" ]; then
      echo "Failed to get service endpoint"
      exit 1
    fi
    
    ENDPOINT_URL="http://$SERVICE_IP:$SERVICE_PORT$ENDPOINT"
    echo "Health check endpoint: $ENDPOINT_URL"
    
    # Perform health check
    retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
      if curl -f -s -m 10 "$ENDPOINT_URL" > /dev/null; then
        echo "Health check passed"
        exit 0
      fi
      
      retry_count=$((retry_count + 1))
      echo "Health check failed (attempt $retry_count/$MAX_RETRIES), retrying in $INTERVAL seconds..."
      sleep $INTERVAL
    done
    
    echo "Health check failed after $MAX_RETRIES attempts"
    exit 1
    ;;
    
  "ecs")
    echo "Performing ECS health check..."
    
    # Get service endpoint from load balancer
    LOAD_BALANCER_ARN=$(aws ecs describe-services \
      --cluster "$CLUSTER_NAME" \
      --services "$SERVICE_NAME" \
      --query 'services[0].loadBalancers[0].targetGroupArn' \
      --output text)
    
    if [ -z "$LOAD_BALANCER_ARN" ] || [ "$LOAD_BALANCER_ARN" == "None" ]; then
      echo "No load balancer found for service"
      exit 1
    fi
    
    # Get load balancer DNS name
    TARGET_GROUP_NAME=$(aws elbv2 describe-target-groups \
      --target-group-arns "$LOAD_BALANCER_ARN" \
      --query 'TargetGroups[0].TargetGroupName' \
      --output text)
    
    LOAD_BALANCER_DNS=$(aws elbv2 describe-load-balancers \
      --query "LoadBalancers[?contains(LoadBalancerName, \`$TARGET_GROUP_NAME\`)].DNSName" \
      --output text)
    
    if [ -z "$LOAD_BALANCER_DNS" ]; then
      echo "Failed to get load balancer DNS"
      exit 1
    fi
    
    ENDPOINT_URL="http://$LOAD_BALANCER_DNS$ENDPOINT"
    echo "Health check endpoint: $ENDPOINT_URL"
    
    # Perform health check
    retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
      if curl -f -s -m 10 "$ENDPOINT_URL" > /dev/null; then
        echo "Health check passed"
        exit 0
      fi
      
      retry_count=$((retry_count + 1))
      echo "Health check failed (attempt $retry_count/$MAX_RETRIES), retrying in $INTERVAL seconds..."
      sleep $INTERVAL
    done
    
    echo "Health check failed after $MAX_RETRIES attempts"
    exit 1
    ;;
    
  "docker")
    echo "Performing Docker health check..."
    
    # Get container endpoint
    CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' app-"$ENVIRONMENT" 2>/dev/null || echo "")
    CONTAINER_PORT=$(docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{$p}}{{end}}' app-"$ENVIRONMENT" 2>/dev/null | cut -d'/' -f1 || echo "80")
    
    if [ -z "$CONTAINER_IP" ]; then
      echo "Failed to get container IP"
      exit 1
    fi
    
    ENDPOINT_URL="http://$CONTAINER_IP:$CONTAINER_PORT$ENDPOINT"
    echo "Health check endpoint: $ENDPOINT_URL"
    
    # Perform health check
    retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
      if curl -f -s -m 10 "$ENDPOINT_URL" > /dev/null; then
        echo "Health check passed"
        exit 0
      fi
      
      retry_count=$((retry_count + 1))
      echo "Health check failed (attempt $retry_count/$MAX_RETRIES), retrying in $INTERVAL seconds..."
      sleep $INTERVAL
    done
    
    echo "Health check failed after $MAX_RETRIES attempts"
    exit 1
    ;;
    
  *)
    echo "Unknown platform: $PLATFORM"
    exit 1
    ;;
esac