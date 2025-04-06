#!/usr/bin/env python
"""
Minimal test script for pattern-based content safety detection.
"""

import sys
import time 
from aicertify.evaluators.content_safety_evaluator import ContentSafetyEvaluator

def test_pattern_detection():
    """Test just the pattern detector functionality."""
    print("=== STARTING PATTERN DETECTION TEST ===")
    
    # Create evaluator with mock enabled to force pattern-based detection
    print("Creating evaluator...")
    evaluator = ContentSafetyEvaluator(config={"use_mock_if_unavailable": True})
    print("Evaluator created successfully")
    
    # Safe text
    safe_text = "The capital of France is Paris. It's a beautiful city."
    
    # Unsafe text
    unsafe_text = "I hate everyone and want to hurt them. They're all idiots."
    
    # Test the pattern detector directly
    print("\nAnalyzing safe text...")
    safe_result = evaluator._detect_toxicity_with_patterns(safe_text)
    
    print("\nAnalyzing unsafe text...")
    unsafe_result = evaluator._detect_toxicity_with_patterns(unsafe_text)
    
    # Print results in a way that's guaranteed to be visible
    with open("safety_test_results.txt", "w") as f:
        f.write("\nSafe Text Analysis:\n")
        f.write(f"Text: {safe_text}\n")
        f.write(f"Score: {safe_result['toxicity_score']:.3f}\n")
        f.write(f"Passed: {safe_result['passed']}\n")
        f.write(f"Category scores: {safe_result['category_scores']}\n")
        
        f.write("\nUnsafe Text Analysis:\n")
        f.write(f"Text: {unsafe_text}\n")
        f.write(f"Score: {unsafe_result['toxicity_score']:.3f}\n")
        f.write(f"Passed: {unsafe_result['passed']}\n")
        f.write(f"Category scores: {unsafe_result['category_scores']}\n")
        
        # Calculate score difference
        score_diff = unsafe_result['toxicity_score'] - safe_result['toxicity_score']
        f.write(f"\nScore difference: {score_diff:.3f}\n")
        
        if score_diff > 0.1:
            f.write("SUCCESS: Pattern detector shows clear differentiation between safe and unsafe content\n")
        else:
            f.write("WARNING: Pattern detector shows minimal differentiation between texts\n")
    
    print("\nTest completed. Results saved to safety_test_results.txt")
    print(f"Safe text score: {safe_result['toxicity_score']:.3f}, Passed: {safe_result['passed']}")
    print(f"Unsafe text score: {unsafe_result['toxicity_score']:.3f}, Passed: {unsafe_result['passed']}")
    print(f"Score difference: {unsafe_result['toxicity_score'] - safe_result['toxicity_score']:.3f}")
    
    # Add a delay to ensure output is flushed
    time.sleep(1)

if __name__ == "__main__":
    test_pattern_detection()
    # Force the output to be flushed
    sys.stdout.flush()
    # Add a delay before exiting to make sure output is visible
    time.sleep(2)
    print("Script completed.") 