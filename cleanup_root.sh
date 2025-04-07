#!/bin/bash
# Cleanup script for root directory files

set -e  # Exit on error

echo "Cleaning up root directory files..."

# Remove CLI-related documentation
echo "Removing CLI-related documentation..."
rm -f CLI_ARCHITECTURE.md
rm -f CLI_README.md
rm -f CLI_SEQUENCE.md
rm -f CLI_SUMMARY.md

# Remove development planning documents
echo "Removing development planning documents..."
rm -f implementation_plan.md
rm -f integration_plan_rego_policy_integration.md

# Remove example and test files
echo "Removing example and test files..."
rm -f example_params.json
rm -f evaluation_report.html
rm -f sample_report.html
rm -f test_cli.sh

# Remove temporary directories
echo "Removing temporary directories..."
rm -rf debug_output
rm -rf reports
rm -rf clean_examples

echo "Root directory cleanup complete!"
