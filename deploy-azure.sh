#!/bin/bash

# Azure Production Deployment Script
# Digital Twin Voice Intelligence Platform

set -e

# Configuration
RESOURCE_GROUP="rg-digitaltwin-prod"
LOCATION="eastus2"
ENVIRONMENT="prod"
APP_NAME="digitaltwin"

echo "🚀 Deploying Digital Twin Voice Intelligence to Azure..."

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! az account show &> /dev/null; then
    echo "❌ Please login to Azure first: az login"
    exit 1
fi

echo "✅ Azure CLI ready"

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy infrastructure using Bicep
echo "🏗️ Deploying infrastructure..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file azure-deployment/main.bicep \
  --parameters environment=$ENVIRONMENT enableGpu=true \
  --query 'properties.outputs' \
  --output json)

# Extract important values
CONTAINER_REGISTRY=$(echo $DEPLOYMENT_OUTPUT | jq -r '.containerRegistryName.value')
ACR_LOGIN_SERVER=$(echo $DEPLOYMENT_OUTPUT | jq -r '.containerRegistryLoginServer.value')
WEB_APP_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r '.webAppUrl.value')
WHISPER_API_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r '.whisperApiUrl.value')
COLLABORATION_API_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r '.collaborationApiUrl.value')

echo "✅ Infrastructure deployed successfully"

# Login to Container Registry
echo "🔐 Logging into Container Registry..."
az acr login --name $CONTAINER_REGISTRY

# Build and push Whisper service
echo "🐳 Building and pushing Whisper service..."
az acr build \
  --registry $CONTAINER_REGISTRY \
  --image whisper-service:latest \
  --file whisper_service/Dockerfile \
  ./whisper_service

# Build and push Collaboration API
echo "🤝 Building and pushing Collaboration API..."
az acr build \
  --registry $CONTAINER_REGISTRY \
  --image collaboration-api:latest \
  --file collaboration.Dockerfile \
  .

# Build and push Web App
echo "🌐 Building and pushing Web App..."
az acr build \
  --registry $CONTAINER_REGISTRY \
  --image webapp:latest \
  --file web_app/Dockerfile \
  ./web_app

echo "✅ All containers built and pushed successfully"

# Configure auto-scaling for Whisper service
echo "⚖️ Setting up auto-scaling..."
az monitor autoscale create \
  --resource-group $RESOURCE_GROUP \
  --resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/${APP_NAME}-${ENVIRONMENT}-whisper" \
  --min-count 2 \
  --max-count 10 \
  --count 2 \
  --scale-out-cooldown 300 \
  --scale-in-cooldown 300

# Add CPU-based scaling rule
az monitor autoscale rule create \
  --resource-group $RESOURCE_GROUP \
  --autoscale-name "${APP_NAME}-${ENVIRONMENT}-whisper" \
  --scale-out 3 \
  --condition "Percentage CPU > 70 avg 5m" \
  --cooldown 300

az monitor autoscale rule create \
  --resource-group $RESOURCE_GROUP \
  --autoscale-name "${APP_NAME}-${ENVIRONMENT}-whisper" \
  --scale-in 1 \
  --condition "Percentage CPU < 30 avg 10m" \
  --cooldown 600

echo "✅ Auto-scaling configured"

# Set up monitoring alerts
echo "📊 Setting up monitoring alerts..."

# High latency alert
az monitor metrics alert create \
  --name "whisper-high-latency" \
  --resource-group $RESOURCE_GROUP \
  --scopes "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/${APP_NAME}-${ENVIRONMENT}-whisper" \
  --condition "avg ResponseTime > 5000" \
  --description "Whisper API response time is too high" \
  --evaluation-frequency 1m \
  --window-size 5m \
  --severity 2

# High error rate alert
az monitor metrics alert create \
  --name "whisper-high-errors" \
  --resource-group $RESOURCE_GROUP \
  --scopes "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/${APP_NAME}-${ENVIRONMENT}-whisper" \
  --condition "total Requests_Failed > 10" \
  --description "Whisper API error rate is too high" \
  --evaluation-frequency 1m \
  --window-size 5m \
  --severity 1

echo "✅ Monitoring alerts configured"

# Create deployment verification script
cat > verify-deployment.sh << EOF
#!/bin/bash
echo "🔍 Verifying Azure deployment..."

# Test main web app
if curl -s $WEB_APP_URL/health > /dev/null; then
    echo "✅ Web App: $WEB_APP_URL"
else
    echo "❌ Web App health check failed"
fi

# Test Whisper API
if curl -s $WHISPER_API_URL/health > /dev/null; then
    echo "✅ Whisper API: $WHISPER_API_URL"
else
    echo "❌ Whisper API health check failed"
fi

# Test Collaboration API
if curl -s $COLLABORATION_API_URL/health > /dev/null; then
    echo "✅ Collaboration API: $COLLABORATION_API_URL"
else
    echo "❌ Collaboration API health check failed"
fi

echo ""
echo "🎉 Azure deployment verification complete!"
echo "📱 Access your application at: $WEB_APP_URL"
EOF

chmod +x verify-deployment.sh

echo ""
echo "🎉 Azure deployment completed successfully!"
echo ""
echo "📱 Application URLs:"
echo "   Main Application: $WEB_APP_URL"
echo "   Whisper API: $WHISPER_API_URL"
echo "   Collaboration API: $COLLABORATION_API_URL"
echo ""
echo "🔧 Management:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Container Registry: $ACR_LOGIN_SERVER"
echo ""
echo "🔍 Verify deployment:"
echo "   ./verify-deployment.sh"
echo ""
echo "📊 Monitor with:"
echo "   az monitor metrics list --resource /subscriptions/\$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/${APP_NAME}-${ENVIRONMENT}-whisper"
echo ""
echo "💰 Estimated monthly cost: \$300-800 (depending on usage)"
echo "   • App Service: \$150-250"
echo "   • Container Instances: \$100-400" 
echo "   • Storage & Database: \$50-150"