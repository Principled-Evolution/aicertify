#!/usr/bin/env python
"""
Script to run the validation tests for AICertify Phase 1 implementation.

This script runs validation tests following the validation sequence in 
MILESTONE_EXPANDED_EVALS_VALIDATION_GUIDE.md:
1. Pre-Implementation Validation (core components, evaluators, OPA integration)
2. Phase 1 Implementation Validation (domain-specific contexts, contracts)

Usage:
    python scripts/run_phase1_validation.py [--verbose] [--stage {pre,phase1,all}]
"""

import argparse
import os
import sys
import unittest
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_pre_implementation_tests(verbose=False):
    """Run the pre-implementation validation tests."""
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Load the tests from the test_evaluator_components.py file
    test_suite = loader.discover('tests', pattern='test_evaluator_components.py')
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    
    # Run the tests
    print("\n" + "="*80)
    print(f"Running Pre-Implementation Validation Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    result = runner.run(test_suite)
    
    # Generate a report
    report = {
        "timestamp": datetime.now().isoformat(),
        "stage": "pre-implementation",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
        "success": result.wasSuccessful()
    }
    
    # Save the report
    os.makedirs('reports', exist_ok=True)
    report_path = os.path.join('reports', f'pre_implementation_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*80)
    print(f"Pre-Implementation Validation Report: {report_path}")
    print(f"Tests Run: {report['tests_run']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Success: {report['success']}")
    print("="*80 + "\n")
    
    return result.wasSuccessful()

def run_phase1_implementation_tests(verbose=False):
    """Run the Phase 1 implementation validation tests."""
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Load the tests from the test_phase1_implementation.py file
    test_suite = loader.discover('tests', pattern='test_phase1_implementation.py')
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    
    # Run the tests
    print("\n" + "="*80)
    print(f"Running Phase 1 Implementation Validation Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    result = runner.run(test_suite)
    
    # Generate a report
    report = {
        "timestamp": datetime.now().isoformat(),
        "stage": "phase1-implementation",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
        "success": result.wasSuccessful()
    }
    
    # Save the report
    os.makedirs('reports', exist_ok=True)
    report_path = os.path.join('reports', f'phase1_implementation_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*80)
    print(f"Phase 1 Implementation Validation Report: {report_path}")
    print(f"Tests Run: {report['tests_run']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Success: {report['success']}")
    print("="*80 + "\n")
    
    return result.wasSuccessful()

def run_all_validation_tests(verbose=False):
    """Run all validation tests in the correct sequence."""
    # First run pre-implementation tests
    pre_success = run_pre_implementation_tests(verbose)
    
    # Then run phase 1 implementation tests
    phase1_success = run_phase1_implementation_tests(verbose)
    
    # Generate a combined report
    report = {
        "timestamp": datetime.now().isoformat(),
        "pre_implementation": {
            "success": pre_success
        },
        "phase1_implementation": {
            "success": phase1_success
        },
        "overall_success": pre_success and phase1_success
    }
    
    # Save the report
    os.makedirs('reports', exist_ok=True)
    report_path = os.path.join('reports', f'combined_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*80)
    print(f"Combined Validation Report: {report_path}")
    print(f"Pre-Implementation Success: {report['pre_implementation']['success']}")
    print(f"Phase 1 Implementation Success: {report['phase1_implementation']['success']}")
    print(f"Overall Success: {report['overall_success']}")
    print("="*80 + "\n")
    
    return report['overall_success']

def main():
    """Main function to parse arguments and run the validation tests."""
    parser = argparse.ArgumentParser(description='Run validation tests for AICertify Phase 1 implementation.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--stage', choices=['pre', 'phase1', 'all'], default='all', 
                        help='Test stage to run: pre-implementation, phase1-implementation, or all')
    args = parser.parse_args()
    
    success = False
    
    if args.stage == 'pre':
        success = run_pre_implementation_tests(verbose=args.verbose)
    elif args.stage == 'phase1':
        success = run_phase1_implementation_tests(verbose=args.verbose)
    else:  # 'all'
        success = run_all_validation_tests(verbose=args.verbose)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 