#!/bin/bash
# Script to run debug_policy_evaluation.py with different configurations

# Default values
OPA_DEBUG=${OPA_DEBUG:-1}
LOG_LEVEL=${LOG_LEVEL:-INFO}
LOG_FILE=${LOG_FILE:-"temp_reports/debug_$(date +%Y%m%d_%H%M%S).log"}

# Create temp_reports directory if it doesn't exist
mkdir -p temp_reports

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --debug)
      OPA_DEBUG=1
      shift
      ;;
    --no-debug)
      OPA_DEBUG=0
      shift
      ;;
    --log-level=*)
      LOG_LEVEL="${1#*=}"
      shift
      ;;
    --log-file=*)
      LOG_FILE="${1#*=}"
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --debug              Enable OPA debug mode (default)"
      echo "  --no-debug           Disable OPA debug mode"
      echo "  --log-level=LEVEL    Set logging level (DEBUG, INFO, WARNING, ERROR)"
      echo "  --log-file=FILE      Set log file path"
      echo "  --help               Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo "Running debug_policy_evaluation.py with:"
echo "  OPA_DEBUG: $OPA_DEBUG"
echo "  LOG_LEVEL: $LOG_LEVEL"
echo "  LOG_FILE: $LOG_FILE"
echo ""

# Add this before running the Python script
export OPENAI_LOG_LEVEL=INFO

# Run the debug script with the specified configuration
OPA_DEBUG=$OPA_DEBUG LOG_LEVEL=$LOG_LEVEL LOG_FILE=$LOG_FILE python examples/debug_policy_evaluation.py

echo ""
echo "Debug script completed. Log file: $LOG_FILE"
