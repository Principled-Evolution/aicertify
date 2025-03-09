# METADATA
# title: Common Policy Rules Library
# description: Reusable policy rules and functions for AICertify
# entrypoint: true
package global.v1.common.common_rules

import rego.v1

# Common functions and rules for reuse in other policies

# --- Common fairness rules ---

# Check gender bias in fairness metrics
fairness_gender_bias_detected(metrics) if {
	gender_bias := object.get(metrics, ["fairness", "gender_bias"], false)
	gender_bias == true
}

# Check racial bias in fairness metrics
fairness_racial_bias_detected(metrics) if {
	racial_bias := object.get(metrics, ["fairness", "racial_bias"], false)
	racial_bias == true
}

# --- Common content safety rules ---

# Check if content is toxic based on threshold
content_safety_is_toxic(metrics, threshold) if {
	toxicity_score := object.get(metrics, ["content_safety", "score"], 0)
	toxicity_score >= threshold
}

# --- Common risk management rules ---

# Check if risk score exceeds threshold
risk_management_has_high_risk(metrics, threshold) if {
	risk_score := object.get(metrics, ["risk_management", "score"], 0)
	risk_score >= threshold
}

# General utility functions

# Check if toxicity score exceeds threshold
is_toxic(metrics, threshold) if {
	metrics.toxicity.score >= threshold
}

# Check if a value is within a range
in_range(value, min_value, max_value) if {
	value >= min_value
	value <= max_value
}

# Format evaluation result with standard structure
format_result(compliant, score, threshold, details) := {
	"compliant": compliant,
	"score": score,
	"threshold": threshold,
	"details": details,
}

# Check compliance based on score and threshold
is_compliant(score, threshold) if {
	score >= threshold
}
