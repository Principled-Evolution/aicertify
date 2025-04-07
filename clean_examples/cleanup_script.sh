#!/bin/bash
# AICertify Repository Cleanup Script
# This script implements the cleanup plan to create a clean repository structure

set -e  # Exit on error

# Create backup of current state
echo "Creating backup of current repository state..."
BACKUP_DIR="aicertify_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
rsync -av --exclude="$BACKUP_DIR" --exclude=".git" --exclude=".venv" . "$BACKUP_DIR/"
echo "Backup created at $BACKUP_DIR"

# Create new directory structure
echo "Creating new directory structure..."
mkdir -p examples

# Copy quickstart example
echo "Copying quickstart example..."
cp clean_examples/quickstart.py examples/
cp clean_examples/README.md examples/

# Copy new README to root
echo "Updating root README..."
cp clean_examples/ROOT_README.md README.md

# Remove unnecessary directories and files
echo "Removing unnecessary directories and files..."

# Development and testing directories
rm -rf aicertify/cli
rm -rf aicertify/decorators-phase-2
rm -rf aicertify/development
rm -rf aicertify/examples
rm -rf aicertify/tests
rm -rf aicertify/system_evaluators
rm -rf aicertify_cli.py
rm -rf tests

# Documentation and scripts
rm -rf docs
rm -rf scripts

# Old examples directory
rm -rf examples/EU_AI_Act_Compliance_Example.py
rm -rf examples/Loan-Application-Evaluator.py
rm -rf examples/Medical-Diagnosis-MultiSpecialist-Agents.py
rm -rf examples/Medical-Diagnosis-Using-API.py
rm -rf examples/capture_report_data.py
rm -rf examples/external_opa_evaluator.py
rm -rf examples/medical_diagnosis_external_opa.py
rm -rf examples/opa_client.py
rm -rf examples/opa_test.py

# Temporary and output directories
rm -rf debug_output
rm -rf memory-bank
rm -rf temp_reports
rm -rf reports
find . -name "__pycache__" -type d -exec rm -rf {} +

# Clean up the cleanup files
echo "Cleaning up cleanup files..."
rm -rf clean_examples

echo "Repository cleanup complete!"
echo "Please test the quickstart example to ensure it works:"
echo "python examples/quickstart.py"
