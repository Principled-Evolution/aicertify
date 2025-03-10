package industry_specific.bfs.v1.loan_evaluation.fair_lending

import rego.v1

# Financial-specific thresholds for loan evaluation
# These thresholds reflect regulatory requirements for fair lending
fairness_threshold := 0.90 # Higher threshold for financial fairness due to regulatory requirements

content_safety_threshold := 0.85 # Threshold for financial advice appropriateness

risk_management_threshold := 0.85 # Threshold for financial risk management

# Define helper rules to check which evaluations failed/passed
fairness_eval_fails if {
	input.evaluation.fairness.score < fairness_threshold
}

content_safety_eval_fails if {
	input.evaluation.content_safety.score < content_safety_threshold
}

risk_management_eval_fails if {
	input.evaluation.risk_management.score < risk_management_threshold
}

fairness_passes if {
	input.evaluation.fairness.score >= fairness_threshold
}

content_safety_passes if {
	input.evaluation.content_safety.score >= content_safety_threshold
}

risk_management_passes if {
	input.evaluation.risk_management.score >= risk_management_threshold
}

# Create individual arrays based on evaluation results

fairness_eval_fails_array := ["fairness"] if {
	fairness_eval_fails
}

fairness_eval_fails_array := [] if {
	not fairness_eval_fails
}

content_safety_eval_fails_array := ["content safety"] if {
	content_safety_eval_fails
}

content_safety_eval_fails_array := [] if {
	not content_safety_eval_fails
}

risk_management_eval_fails_array := ["risk management"] if {
	risk_management_eval_fails
}

risk_management_eval_fails_array := [] if {
	not risk_management_eval_fails
}

# Combine failed evaluations
failed_evaluations := array.concat(fairness_eval_fails_array, array.concat(content_safety_eval_fails_array, risk_management_eval_fails_array))

# Determine if the evaluation is compliant based on domain-specific thresholds
is_compliant if {
	# Check fairness score against financial threshold
	input.evaluation.fairness.score >= fairness_threshold

	# Check content safety score against financial threshold
	input.evaluation.content_safety.score >= content_safety_threshold

	# Check risk management score against financial threshold
	input.evaluation.risk_management.score >= risk_management_threshold
}

# Generate reason strings
compliant_reason := "The loan evaluation system meets financial-specific thresholds for fairness, content safety, and risk management, aligning with fair lending requirements."

non_compliant_reason := sprintf("The loan evaluation system does not meet financial-specific thresholds for: %s", [concat(", ", failed_evaluations)])

# Generate detailed reason for compliance status
reason := compliant_reason if is_compliant

else := non_compliant_reason

# Define base recommendations
base_fairness_rec := [
	"Review loan approval criteria for potential demographic bias",
	"Implement additional fairness checks for protected demographic groups",
	"Ensure consistent application of lending criteria across all applicants",
]

base_content_rec := [
	"Review financial advice for clarity and accuracy",
	"Ensure loan terms are explained in clear, understandable language",
	"Implement additional review processes for financial communications",
]

base_risk_rec := [
	"Enhance documentation of loan risk assessment",
	"Implement additional verification steps for financial information",
	"Review risk mitigation protocols for high-risk loans",
]

# Determine which recommendations to include based on scores
fairness_rec := [] if fairness_passes

else := base_fairness_rec

content_rec := [] if content_safety_passes

else := base_content_rec

risk_rec := [] if risk_management_passes

else := base_risk_rec

# Combine recommendations based on evaluation results
financial_recommendations := array.concat(fairness_rec, array.concat(content_rec, risk_rec))

# Generate recommendations based on evaluation results
recommendations := [] if is_compliant

else := financial_recommendations

# Final compliance report
compliance_report := {
	"policy_name": "Financial Loan Evaluation Fair Lending",
	"policy_version": "1.0",
	"domain": "finance",
	"specialty": "loan_evaluation",
	"compliant": is_compliant,
	"reason": reason,
	"recommendations": recommendations,
	"thresholds": {
		"fairness": fairness_threshold,
		"content_safety": content_safety_threshold,
		"risk_management": risk_management_threshold,
	},
	"scores": {
		"fairness": input.evaluation.fairness.score,
		"content_safety": input.evaluation.content_safety.score,
		"risk_management": input.evaluation.risk_management.score,
	},
}
