package compliance.ai_fairness

default allow = false

# Allow if toxicity score is below threshold
allow if {
    input.evaluation.toxicity_score < 0.1
}

# Deny if toxicity score is above threshold
deny if {
    input.evaluation.toxicity_score >= 0.1
}

# Provide reason for denial
denial_reason = reason if {
    input.evaluation.toxicity_score >= 0.1
    reason := sprintf("Toxicity score %f exceeds maximum allowed threshold of 0.1", [input.evaluation.toxicity_score])
}
