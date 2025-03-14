#!/bin/bash
# Test script for AICertify CLI

# Set variables
CONTRACT_PATH="examples/outputs/medical_diagnosis/contract_2025-03-03_183048.json"
POLICY_FOLDER="eu_fairness"
OUTPUT_DIR="./test_reports"
REPORT_FORMAT="pdf"
PARAMS_FILE="example_params.json"

# Create output directory
mkdir -p $OUTPUT_DIR

echo "=== Testing AICertify CLI ==="
echo "Contract: $CONTRACT_PATH"
echo "Policy: $POLICY_FOLDER"
echo "Output Directory: $OUTPUT_DIR"
echo "Report Format: $REPORT_FORMAT"
echo "Parameters File: $PARAMS_FILE"
echo ""

# Run the CLI tool without parameters
echo "Running AICertify CLI without custom parameters..."
python aicertify_cli.py \
  --contract $CONTRACT_PATH \
  --policy $POLICY_FOLDER \
  --output-dir $OUTPUT_DIR \
  --report-format $REPORT_FORMAT \
  --verbose

# Check if the command was successful
if [ $? -eq 0 ]; then
  echo ""
  echo "Basic test completed successfully!"
  echo "Check the output directory for the generated report."
else
  echo ""
  echo "Basic test failed. See error messages above."
  exit 1
fi

echo ""
echo "=== Testing AICertify CLI with Custom Parameters ==="
echo ""

# Run the CLI tool with parameters
echo "Running AICertify CLI with custom parameters..."
python aicertify_cli.py \
  --contract $CONTRACT_PATH \
  --policy $POLICY_FOLDER \
  --output-dir $OUTPUT_DIR \
  --report-format $REPORT_FORMAT \
  --params $PARAMS_FILE \
  --verbose

# Check if the command was successful
if [ $? -eq 0 ]; then
  echo ""
  echo "Parameters test completed successfully!"
  echo "Check the output directory for the generated report."
else
  echo ""
  echo "Parameters test failed. See error messages above."
  exit 1
fi

echo ""
echo "All tests completed successfully!" 