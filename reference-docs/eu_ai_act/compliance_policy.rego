package ai_act_compliance
# I have generated an Open Policy Agent (OPA) Rego policy for AI Act compliance, prohibition, and governance enforcement. You can download the policy file from the link below:

# [Download AI Act OPA Policy](sandbox:/mnt/data/ai_act_opa_policy.rego)

# This policy includes enforcement for:
# - **Prohibited AI practices**
# - **High-risk AI classification and certification**
# - **Transparency obligations**
# - **Logging and traceability**
# - **Governance and compliance**
# - **User and provider responsibilities**
# - **Cybersecurity safeguards**
# - **Regulatory sandbox oversight**
# - **AI database registration requirements**

# Let me know if you need modifications or integration suggestions!

# Prohibited AI Practices
deny[msg] {
    input.ai_system.category == "prohibited"
    msg := "This AI system is explicitly prohibited under the EU AI Act."
}

# High-Risk AI Classification - Ensure AI systems meet risk assessment before use
deny[msg] {
    input.ai_system.category == "high-risk"
    not input.ai_system.certified
    msg := "High-risk AI system must be certified before deployment."
}

# Enforce Transparency Obligations - AI systems must disclose their nature
deny[msg] {
    input.ai_system.requires_transparency
    not input.ai_system.discloses_information
    msg := "AI system must disclose its nature and processing details to users."
}

# Logging and Traceability - AI systems must enable logging
deny[msg] {
    input.ai_system.requires_logging
    not input.ai_system.logs_enabled
    msg := "Logging must be enabled for traceability and compliance."
}

# Governance and Compliance - AI systems must be registered and audited
deny[msg] {
    input.ai_system.high_risk
    not input.ai_system.registered_in_eu_database
    msg := "High-risk AI systems must be registered in the EU compliance database."
}

deny[msg] {
    input.ai_system.high_risk
    not input.ai_system.audited_compliant
    msg := "High-risk AI system has not passed required compliance audits."
}

# User and Provider Obligations
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

# Cybersecurity Requirements - AI systems must have security measures enabled
deny[msg] {
    input.ai_system.requires_security_measures
    not input.ai_system.security_measures_enabled
    msg := "High-risk AI systems must have cybersecurity measures enabled."
}

# Regulatory Sandbox Compliance - AI systems must be supervised in sandboxes
deny[msg] {
    input.ai_sandbox.in_use
    not input.ai_sandbox.supervised
    msg := "AI sandboxes must be supervised by competent authorities."
}

# AI Database Registration - High-risk AI systems must be registered before deployment
deny[msg] {
    input.ai_system.category == "high-risk"
    not input.ai_system.registered_in_database
    msg := "High-risk AI system must be registered in an approved EU AI database."
}
