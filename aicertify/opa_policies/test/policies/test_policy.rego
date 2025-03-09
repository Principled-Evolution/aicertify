package test.policies

import data.test.utils
import rego.v1

# Main policy rule that evaluates if a model meets compliance requirements
compliant_model if {
	# Get the model's fairness score from input
	fairness_score := input.model.fairness_score

	# Use the imported utility function to check if it passes threshold
	utils.passes_threshold(fairness_score, 0.7)

	# Additional compliance checks
	input.model.has_documentation == true
}

# Calculate an overall compliance score
calculate_compliance_score if {
	# Get scores from input or use defaults
	fairness_score := input.model.fairness_score
	robustness_score := input.model.robustness_score

	# If transparency score is missing, use the default from utils
	transparency_score := object.get(input.model, "transparency_score", utils.get_default_score)

	# Use the weighted average function from utils
	score := utils.weighted_average(
		[fairness_score, robustness_score, transparency_score],
		[0.4, 0.4, 0.2],
	)
}
