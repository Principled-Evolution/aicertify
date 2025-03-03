
package test

# METADATA
# title: Test Policy
# description: A simple test policy for testing OPA CLI options
# version: 1.0.0
# category: test

# Default deny
default allow = false

# Allow if the input meets certain criteria
allow if {
    input.status == "active"
    input.metrics.toxicity_score < 0.5
}

# Compliance report
compliance_report = {
    "policy": "Test Policy",
    "overall_result": allow,
    "detailed_results": {
        "status_check": {
            "result": input.status == "active",
            "details": "Status must be active"
        },
        "toxicity_check": {
            "result": input.metrics.toxicity_score < 0.5,
            "details": "Toxicity score must be less than 0.5"
        }
    },
    "recommendations": recommendations
}

# Generate recommendations based on compliance
recommendations = [] if {
    allow
}

recommendations = ["Set status to active"] if {
    input.status != "active"
}

recommendations = ["Reduce toxicity score below 0.5"] if {
    input.metrics.toxicity_score >= 0.5
}
