package test.utils

import rego.v1

# A simple utility function to check if a score passes a threshold
passes_threshold(score, threshold) if {
	score >= threshold
}

# A function to get a default score if none is provided
get_default_score := 0.75

# A function to calculate a weighted average of scores
# This is a simplified version that works with exactly 3 scores and weights
weighted_average(scores, weights) if {
	# Calculate the weighted sum manually
	sum_products := ((scores[0] * weights[0]) + (scores[1] * weights[1])) + (scores[2] * weights[2])

	# Calculate the sum of weights
	sum_weights := (weights[0] + weights[1]) + weights[2]

	# Calculate the weighted average
	result := sum_products / sum_weights

	# Return the result
	weighted_average := result
}
