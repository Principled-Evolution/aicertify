
package ai_act_compliance

# Prohibited AI practices
deny[msg] {
    input.ai_system.prohibited == true
    msg := "This AI system is prohibited under the AI Act."
}

# High-risk AI classification
high_risk_ai {
    input.ai_system.category == "high-risk"
}

# Ensure high-risk AI systems undergo proper assessment before deployment
deny[msg] {
    high_risk_ai
    not input.ai_system.certified
    msg := "High-risk AI system must be certified before deployment."
}

# Enforce transparency obligations
deny[msg] {
    input.ai_system.requires_transparency
    not input.ai_system.discloses_information
    msg := "AI system must disclose its nature and processing details to users."
}

# Enforce logging requirements for AI systems
deny[msg] {
    input.ai_system.requires_logging
    not input.ai_system.logs_enabled
    msg := "Logging must be enabled for traceability and compliance."
}

# User and provider obligations
deny[msg] {
    input.user.role == "provider"
    not input.ai_system.complies_with_ai_act
    msg := "Providers must ensure AI system compliance before deployment."
}

deny[msg] {
    input.user.role == "user"
    input.ai_system.high_risk
    not input.ai_system.operates_within_guidelines
    msg := "Users must operate high-risk AI systems within compliance guidelines."
}

# Governance and oversight
deny[msg] {
    input.ai_system.high_risk
    not input.ai_system.registered_in_eu_database
    msg := "High-risk AI systems must be registered in the EU compliance database."
}

# Ensuring only authorized personnel can access high-risk AI systems
deny[msg] {
    input.ai_system.high_risk
    not input.user.has_proper_clearance
    msg := "User does not have the required clearance to access this high-risk AI system."
}

# Cybersecurity requirements
deny[msg] {
    input.ai_system.requires_security_measures
    not input.ai_system.security_measures_enabled
    msg := "High-risk AI systems must have cybersecurity measures enabled."
}

# Ensure that AI sandboxes comply with testing and regulatory standards
deny[msg] {
    input.ai_sandbox.in_use
    not input.ai_sandbox.supervised
    msg := "AI sandboxes must be supervised by competent authorities."
}
