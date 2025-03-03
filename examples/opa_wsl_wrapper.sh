#!/bin/bash
# This is a wrapper script to call the Windows OPA executable from WSL
# It translates paths and arguments as needed

# Check if arguments are provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [opa arguments]"
    exit 1
fi

# Convert the first argument (usually a filepath) from WSL path to Windows path if it exists
if [ -f "$1" ]; then
    # Convert to Windows path if it's a file
    WINPATH=$(wslpath -w "$1")
    shift
    # Run OPA with the Windows path
    /mnt/c/opa/opa.exe "$WINPATH" "$@"
else
    # Just pass all arguments directly
    /mnt/c/opa/opa.exe "$@"
fi
