#!/bin/bash

# Configuration
INTEGRATION_NAME="Tableau Dashboard Load Failures"
CURRENT_TIME="2025-02-21 14:54:09"
AUTHOR="cod-emminex"
WEBHOOK_URL="https://ping.telex.im/v1/webhooks/019528ca-ae9c-79d7-a3ed-2dc5866df56a"

echo "Deploying Tableau Dashboard Monitoring Integration"
echo "Author: ${AUTHOR}"
echo "Timestamp: ${CURRENT_TIME}"

# Check if integration.json exists
if [ ! -f integration.json ]; then
    echo "Error: integration.json file not found"
    exit 1
fi

# Load environment variables if .env exists
if [ -f .env ]; then
    source .env
fi

# Test Tableau connection first
echo "Testing Tableau connection..."
python3 src/test_tableau_connection.py
if [ $? -ne 0 ]; then
    echo "Error: Tableau connection test failed"
    exit 1
fi

# Create webhook test payload
echo "Testing webhook..."
WEBHOOK_TEST_PAYLOAD=$(cat <<EOF
{
    "event": "test",
    "timestamp": "${CURRENT_TIME}",
    "integration": "${INTEGRATION_NAME}",
    "author": "${AUTHOR}",
    "status": "testing"
}
EOF
)

# Test webhook
WEBHOOK_RESPONSE=$(curl -s -X POST "${WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -d "${WEBHOOK_TEST_PAYLOAD}")

echo "Webhook test response: ${WEBHOOK_RESPONSE}"

# Deploy integration
echo "Deploying integration..."
DEPLOY_PAYLOAD=$(cat integration.json)

# Add webhook URL to integration.json if not already present
if [[ ! $DEPLOY_PAYLOAD == *"${WEBHOOK_URL}"* ]]; then
    DEPLOY_PAYLOAD=$(echo $DEPLOY_PAYLOAD | jq --arg url "$WEBHOOK_URL" '.webhook_url = $url')
fi

# Send to Telex
echo "Sending to Telex..."
RESPONSE=$(curl -s -X POST "https://api.telex.im/v1/integrations" \
    -H "Content-Type: application/json" \
    -d "${DEPLOY_PAYLOAD}")

if [[ $RESPONSE == *"\"success\":true"* ]]; then
    echo "Integration deployed successfully!"
else
    echo "Error deploying integration:"
    echo $RESPONSE
    exit 1
fi
