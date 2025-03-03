#!/bin/bash

# Script to run the focused OPA policy evaluation with proper environment variable handling

# Extract OpenAI API key from Windows and clean it
export OPENAI_API_KEY=$(cmd.exe /c "echo %OPENAI_API_KEY%" | tr -d '\r\n')
echo "✅ Set OPENAI_API_KEY: ${OPENAI_API_KEY:0:5}..."

# Set OPA configuration
export OPA_PATH="/mnt/c/opa/opa.exe"
export OPA_SERVER_URL="http://172.29.176.1:8182"
export OPA_USE_EXTERNAL_SERVER="true"
echo "✅ Set OPA_PATH to $OPA_PATH"
echo "✅ Set OPA_SERVER_URL to $OPA_SERVER_URL"
echo "✅ Set OPA_USE_EXTERNAL_SERVER to $OPA_USE_EXTERNAL_SERVER"

# Set debug mode for Python
export PYTHONFAULTHANDLER="1"

# Run the focused debug script
echo "🚀 Running focused OPA policy evaluation script"
poetry run python examples/debug_policy_evaluation.py 