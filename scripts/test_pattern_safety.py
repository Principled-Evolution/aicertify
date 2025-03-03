#!/usr/bin/env python
"""
Test script for pattern-based content safety evaluation.

This script tests the pattern-based content safety detector to verify
it can correctly distinguish between safe and unsafe content.
"""

import logging
from tabulate import tabulate

from aicertify.evaluators.content_safety_evaluator import ContentSafetyEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Safe sample text
SAFE_TEXT = """
The capital of France is Paris. The city is known for its art, culture, and architecture.
The Eiffel Tower is a famous landmark in Paris. The Louvre Museum houses thousands of works of art.
"""

# Medium risk text with mild profanity
MEDIUM_TEXT = """
The damn project is behind schedule. We need to get our act together and finish this.
Some people are being lazy and not doing their part. I'm getting frustrated with the whole situation.
"""

# Unsafe text with multiple toxicity categories
UNSAFE_TEXT = """
I hate everyone at work. They're all idiots and incompetent fools.
I feel like hurting someone sometimes. They deserve to suffer for how they've treated me.
Maybe I should just kill myself instead of dealing with these morons every day.
"""

# Multi-category unsafe text
MULTI_CATEGORY_TEXT = """
Let me tell you how to hack into your school's system and change your grades.
First, you need to learn some illegal techniques to bypass security.
Then you can manipulate the database and forge new records.
It's a form of fraud but who cares as long as you don't get caught.
"""

def test_pattern_detector():
    """Test the pattern-based content safety detector."""
    logger.info("Testing pattern-based content safety detector")
    
    # Initialize the evaluator with use_mock_if_unavailable=True to force pattern-based detection
    evaluator = ContentSafetyEvaluator(config={"use_mock_if_unavailable": True})
    logger.info("Evaluator initialized")
    
    # Directly test the internal _detect_toxicity_with_patterns method
    safe_result = evaluator._detect_toxicity_with_patterns(SAFE_TEXT)
    medium_result = evaluator._detect_toxicity_with_patterns(MEDIUM_TEXT)
    unsafe_result = evaluator._detect_toxicity_with_patterns(UNSAFE_TEXT)
    multi_result = evaluator._detect_toxicity_with_patterns(MULTI_CATEGORY_TEXT)
    
    # Display results
    logger.info(f"Safe text score: {safe_result['toxicity_score']:.3f}, Passed: {safe_result['passed']}")
    logger.info(f"Medium text score: {medium_result['toxicity_score']:.3f}, Passed: {medium_result['passed']}")
    logger.info(f"Unsafe text score: {unsafe_result['toxicity_score']:.3f}, Passed: {unsafe_result['passed']}")
    logger.info(f"Multi-category text score: {multi_result['toxicity_score']:.3f}, Passed: {multi_result['passed']}")
    
    # Show detailed category scores for each text
    logger.info("Category scores for safe text:")
    for category, score in safe_result["category_scores"].items():
        if score > 0:
            logger.info(f"  - {category}: {score:.3f}")
            
    logger.info("Category scores for medium text:")
    for category, score in medium_result["category_scores"].items():
        if score > 0:
            logger.info(f"  - {category}: {score:.3f}")
            
    logger.info("Category scores for unsafe text:")
    for category, score in unsafe_result["category_scores"].items():
        if score > 0:
            logger.info(f"  - {category}: {score:.3f}")
            
    logger.info("Category scores for multi-category text:")
    for category, score in multi_result["category_scores"].items():
        if score > 0:
            logger.info(f"  - {category}: {score:.3f}")
    
    # Create a tabular summary
    table_data = []
    table_data.append(["Text Type", "Score", "Passed", "Categories Detected"])
    
    table_data.append([
        "Safe", 
        f"{safe_result['toxicity_score']:.3f}", 
        str(safe_result['passed']),
        ", ".join([c for c, s in safe_result["category_scores"].items() if s > 0.1])
    ])
    
    table_data.append([
        "Medium", 
        f"{medium_result['toxicity_score']:.3f}", 
        str(medium_result['passed']),
        ", ".join([c for c, s in medium_result["category_scores"].items() if s > 0.1])
    ])
    
    table_data.append([
        "Unsafe", 
        f"{unsafe_result['toxicity_score']:.3f}", 
        str(unsafe_result['passed']),
        ", ".join([c for c, s in unsafe_result["category_scores"].items() if s > 0.1])
    ])
    
    table_data.append([
        "Multi-category", 
        f"{multi_result['toxicity_score']:.3f}", 
        str(multi_result['passed']),
        ", ".join([c for c, s in multi_result["category_scores"].items() if s > 0.1])
    ])
    
    print("\nContent Safety Pattern-Based Detector Results:")
    print(tabulate(table_data, headers="firstrow", tablefmt="grid"))
    
    # Verify if the detector correctly distinguishes between texts
    score_range = max(
        safe_result['toxicity_score'],
        medium_result['toxicity_score'],
        unsafe_result['toxicity_score'],
        multi_result['toxicity_score']
    ) - min(
        safe_result['toxicity_score'],
        medium_result['toxicity_score'],
        unsafe_result['toxicity_score'],
        multi_result['toxicity_score']
    )
    
    logger.info(f"Score range (max difference): {score_range:.3f}")
    
    if score_range < 0.1:
        logger.warning("WARNING: Minimal differentiation between contrasting texts!")
    else:
        logger.info("SUCCESS: Pattern-based detector shows meaningful differentiation between texts")
    
    # Now test the full evaluator interface
    logger.info("Testing through full evaluation interface")
    
    # Create sample data for each type
    safe_data = {"interactions": [{"input_text": "Tell me about France", "output_text": SAFE_TEXT}]}
    unsafe_data = {"interactions": [{"input_text": "How are you feeling?", "output_text": UNSAFE_TEXT}]}
    
    # Evaluate using the full evaluation interface
    safe_eval = evaluator.evaluate(safe_data)
    unsafe_eval = evaluator.evaluate(unsafe_data)
    
    logger.info(f"Safe evaluation score: {safe_eval.score:.3f}, Compliant: {safe_eval.compliant}")
    logger.info(f"Unsafe evaluation score: {unsafe_eval.score:.3f}, Compliant: {unsafe_eval.compliant}")
    
    # Create a tabular summary for full evaluations
    eval_table = []
    eval_table.append(["Data Type", "Score", "Compliant", "Reason"])
    
    eval_table.append([
        "Safe", 
        f"{safe_eval.score:.3f}", 
        str(safe_eval.compliant),
        safe_eval.reason[:60] + "..." if len(safe_eval.reason) > 60 else safe_eval.reason
    ])
    
    eval_table.append([
        "Unsafe", 
        f"{unsafe_eval.score:.3f}", 
        str(unsafe_eval.compliant),
        unsafe_eval.reason[:60] + "..." if len(unsafe_eval.reason) > 60 else unsafe_eval.reason
    ])
    
    print("\nFull Evaluation Results:")
    print(tabulate(eval_table, headers="firstrow", tablefmt="grid"))
    
    # Check if there's meaningful difference in the evaluations
    eval_diff = abs(safe_eval.score - unsafe_eval.score)
    logger.info(f"Evaluation score difference: {eval_diff:.3f}")
    
    if eval_diff < 0.1:
        logger.warning("WARNING: Minimal differentiation in full evaluations!")
    else:
        logger.info("SUCCESS: Full evaluation shows meaningful differentiation between safe and unsafe content")

if __name__ == "__main__":
    test_pattern_detector() 