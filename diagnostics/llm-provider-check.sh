#!/bin/bash
# LLM Provider Health Check & Diagnostics
# Run this script to diagnose the API provider at 10.1.160.84:9527

set -e

API_BASE="${API_HUB_BASE_URL:-http://10.1.160.84:9527/v1}"
API_KEY="${API_HUB_KEY}"

echo "=========================================="
echo "LLM Provider Diagnostics"
echo "=========================================="
echo "Base URL: $API_BASE"
echo "API Key: ${API_KEY:0:20}... (truncated)"
echo ""

# 1. Health Check
echo "[1] Health endpoint check..."
HEALTH=$(curl -s -w "\n%{http_code}" "$API_BASE/../health" 2>&1 || echo "FAILED")
echo "Response: $HEALTH"
echo ""

# 2. List Models
echo "[2] List models endpoint..."
MODELS=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $API_KEY" \
  "$API_BASE/models" 2>&1 || echo "FAILED")
echo "Response: $MODELS"
echo ""

# 3. Test Completion (Simple)
echo "[3] Test chat completion endpoint..."
PAYLOAD='{
  "model": "glm-4.7",
  "messages": [{"role": "user", "content": "Say hello"}],
  "max_tokens": 10
}'
COMPLETION=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$API_BASE/chat/completions" 2>&1 || echo "FAILED")
echo "Response: $COMPLETION"
echo ""

# 4. Network Connectivity
echo "[4] Network connectivity test..."
PING=$(ping -c 2 10.1.160.84 2>&1 || echo "FAILED")
echo "$PING"
echo ""

# 5. Check OpenClaw config
echo "[5] OpenClaw API provider configuration..."
grep -A 20 '"occ"' ~/.openclaw/openclaw.json | head -25
echo ""

# 6. Environment variables
echo "[6] API environment variables..."
env | grep -E 'API_HUB' || echo "No API_HUB variables found"
echo ""

echo "=========================================="
echo "Diagnosis Complete"
echo "=========================================="