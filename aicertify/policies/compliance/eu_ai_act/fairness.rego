package compliance.eu_ai_act

# Default deny
default allow = false

# Allow if model bias is within acceptable range
allow if {
    input.model_bias < 0.05
}

