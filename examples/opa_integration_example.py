import uuid

from contract_models import AiCertifyContract
from evaluation_models import AiEvaluationResult, AiComplianceInput
from aicertify.opa_core.compliance_evaluator import run_opa_on_compliance_input


def main() -> None:
    """Example usage of OPA integration with compliance input."""
    # Create a dummy aggregated contract
    contract = AiCertifyContract(
        contract_id=uuid.uuid4(),
        application_name="CareerCoachAI",
        model_info={"model": "dummy-model"},
        interactions=[],
        final_output="Success",
        context={}
    )

    # Create a dummy evaluation result
    evaluation = AiEvaluationResult(
        contract_id=str(contract.contract_id),
        application_name=contract.application_name,
        fairness_metrics={"toxicity": {"toxic_fraction": 0.05}},
        pii_detected=False,
        pii_details=None,
        security_findings=None,
        summary_text="Evaluation successful",
        aggregated_from_contract_count=3,
        evaluation_mode="batch_aggregate"
    )

    # Assemble the compliance input
    compliance_input = AiComplianceInput(
        contract=contract,
        evaluation=evaluation
    )

    # Evaluate policies in the 'compliance/fairness' category
    results = run_opa_on_compliance_input(compliance_input, "compliance/fairness")
    print("OPA Evaluation Results:")
    print(results)


if __name__ == "__main__":
    main() 