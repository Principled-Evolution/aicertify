package compliance.ai_fairness

default allow = false

allow if {
    input.toxicity_score < 0.1
}
