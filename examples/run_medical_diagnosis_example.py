#!/usr/bin/env python
"""
Helper script to run the Medical-Diagnosis-MultiSpecialist-Agents.py example
with the correct OPA configuration.
"""
import os
import sys
import subprocess
import traceback
import logging
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Run the Medical-Diagnosis-MultiSpecialist-Agents.py example with the correct OPA configuration."""
    logger.info("🚀 Running Medical-Diagnosis-MultiSpecialist-Agents.py with OPA server configuration")
    
    # Set the OPA environment variables to use the Windows host
    os.environ["OPA_PATH"] = "/mnt/c/opa/opa.exe"
    os.environ["OPA_SERVER_URL"] = "http://172.29.176.1:8182"
    os.environ["OPA_USE_EXTERNAL_SERVER"] = "true"  # Use the external server mode
    
    # Set Python to display full traceback
    os.environ["PYTHONFAULTHANDLER"] = "1"
    os.environ["PYTHONASYNCIODEBUG"] = "1"
    
    logger.info(f"✅ Set OPA_PATH to {os.environ['OPA_PATH']}")
    logger.info(f"✅ Set OPA_SERVER_URL to {os.environ['OPA_SERVER_URL']}")
    logger.info(f"✅ Set OPA_USE_EXTERNAL_SERVER to {os.environ['OPA_USE_EXTERNAL_SERVER']}")
    
    # Check if the target file exists
    target_file = "Medical-Diagnosis-MultiSpecialist-Agents.py"
    if not Path(target_file).exists():
        logger.error(f"❌ Target file '{target_file}' does not exist!")
        sys.exit(1)
        
    # First, try to check the file for syntax errors
    logger.info("📋 Checking file for syntax errors...")
    try:
        subprocess.run(
            [sys.executable, "-m", "py_compile", target_file],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("✅ Syntax check passed!")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Syntax check failed with exit code {e.returncode}")
        logger.error(f"📥 STDERR:\n{e.stderr}")
    
    # Set up the command to run as subprocess
    cmd = [
        sys.executable,
        "-u",  # Unbuffered output
        "-v",  # Verbose import information
        target_file,
        "--capture-contract",
        "--report-format", "markdown"
    ]
    
    logger.info(f"💻 Running command: {' '.join(cmd)}")
    
    # Run the command and redirect output to the console
    try:
        process = subprocess.run(
            cmd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("✅ Command completed successfully!")
        logger.info(f"📤 STDOUT:\n{process.stdout}")
        logger.info(f"📥 STDERR:\n{process.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Command failed with exit code {e.returncode}")
        logger.error(f"📤 STDOUT:\n{e.stdout}")
        logger.error(f"📥 STDERR:\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error running command: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Unhandled exception: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1) 