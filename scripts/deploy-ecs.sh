#!/bin/bash

set -euo pipefail

# Default values
ENVIRONMENT="development"
STRATEGY="rolling"
DEPLOYMENT_ID=""
DRY_RUN="false"
CLUSTER_NAME=""
SERVICE_NAME=""
TASK_DEFINITION=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --strategy)
      STRATEGY="$2"
      shift 2
      ;;
    --deployment-id)
      DEPLOYMENT_ID="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="$2"
      shift 2
      ;;
    --cluster-name)
      CLUSTER_NAME="$2"
      shift 2
      ;;
    --service-name)
      SERVICE_NAME="$2"
      shift 2
      ;;
    --task-definition)
      TASK_DEFINITION="$2"
      shift 2
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Set defaults based on environment
if [ -z "$CLUSTER_NAME" ]; then
  CLUSTER_NAME="app-$ENVIRONMENT-cluster"
fi

if [ -z "$SERVICE_NAME" ]; then
  SERVICE_NAME="app-$ENVIRONMENT-service"
fi

if [ -z "$TASK_DEFINITION" ]; then
  TASK_DEFINITION="app-$ENVIRONMENT"
fi

echo "Starting ECS deployment..."
echo "Environment: $ENVIRONMENT"
echo "Strategy: $STRATEGY"
echo "Deployment ID: $DEPLOYMENT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Service: $SERVICE_NAME"
echo "Task Definition: $TASK_DEFINITION"
echo "Dry Run: $DRY_RUN"

# Apply deployment strategy
case "$STRATEGY" in
  "rolling")
    echo "Applying rolling update strategy..."
    if [ "$DRY_RUN" == "true" ]; then
      echo "Rolling update (dry run) - would update task definition and service"
    else
      # Get current task definition
      CURRENT_TASK_DEF=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --query 'services[0].taskDefinition' \
        --output text)
      
      # Create new task definition with updated image
      NEW_TASK_DEF=$(aws ecs describe-task-definition \
        --task-definition "$TASK_DEFINITION" \
        --query 'taskDefinition' | \
        jq --arg IMAGE "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" \
        '.containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.compatibilities) | del(.registeredAt) | del(.registeredBy)')
      
      # Register new task definition
      NEW_TASK_ARN=$(aws ecs register-task-definition \
        --cli-input-json "$NEW_TASK_DEF" \
        --query 'taskDefinition.taskDefinitionArn' \
        --output text)
      
      # Update service with new task definition
      aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --task-definition "$NEW_TASK_ARN" \
        --desired-count 3
      
      # Wait for service stability
      aws ecs wait services-stable \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME"
    fi
    ;;
  "blue-green")
    echo "Applying blue-green deployment strategy..."
    if [ "$DRY_RUN" == "true" ]; then
      echo "Blue-green deployment (dry run) - would create new task set and switch traffic"
    else
      # Create new task set (green)
      GREEN_TASK_SET=$(aws ecs create-task-set \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --task-definition "$TASK_DEFINITION" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS}],securityGroups=[${SECURITY_GROUP_ID}],assignPublicIp=ENABLED}" \
        --query 'taskSet.id' \
        --output text)
      
      # Wait for green task set to be ready
      aws ecs wait tasks-running \
        --cluster "$CLUSTER_NAME" \
        --tasks $(aws ecs list-tasks \
          --cluster "$CLUSTER_NAME" \
          --service-name "$SERVICE_NAME" \
          --query 'taskArns[0]' \
          --output text)
      
      # Update traffic distribution (100% to green)
      aws ecs update-service-primary-task-set \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --primary-task-set "$GREEN_TASK_SET"
      
      # Delete old task set
      aws ecs delete-task-set \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --task-set "$CURRENT_TASK_SET" \
        --force
    fi
    ;;
  "canary")
    echo "Applying canary deployment strategy..."
    if [ "$DRY_RUN" == "true" ]; then
      echo "Canary deployment (dry run) - would gradually shift traffic"
    else
      # Create canary task set with 10% traffic
      CANARY_TASK_SET=$(aws ecs create-task-set \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --task-definition "$TASK_DEFINITION" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS}],securityGroups=[${SECURITY_GROUP_ID}],assignPublicIp=ENABLED}" \
        --scale unit=10 \
        --query 'taskSet.id' \
        --output text)
      
      # Monitor and gradually increase traffic
      for scale in 25 50 75 100; do
        echo "Increasing canary traffic to $scale%"
        aws ecs update-task-set \
          --cluster "$CLUSTER_NAME" \
          --service "$SERVICE_NAME" \
          --task-set "$CANARY_TASK_SET" \
          --scale unit="$scale"
        sleep 60
      done
      
      # Promote canary to primary
      aws ecs update-service-primary-task-set \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --primary-task-set "$CANARY_TASK_SET"
      
      # Remove old task set
      aws ecs delete-task-set \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --task-set "$CURRENT_TASK_SET" \
        --force
    fi
    ;;
  "recreate")
    echo "Applying recreate deployment strategy..."
    if [ "$DRY_RUN" == "true" ]; then
      echo "Recreate deployment (dry run) - would stop all tasks and create new ones"
    else
      # Scale down to 0
      aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --desired-count 0
      
      # Wait for tasks to stop
      aws ecs wait services-stable \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME"
      
      # Update task definition
      aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --task-definition "$TASK_DEFINITION" \
        --desired-count 3
      
      # Wait for service stability
      aws ecs wait services-stable \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME"
    fi
    ;;
  *)
    echo "Unknown deployment strategy: $STRATEGY"
    exit 1
    ;;
esac

echo "Deployment completed successfully"
echo "deployment_id=$DEPLOYMENT_ID" >> $GITHUB_OUTPUT