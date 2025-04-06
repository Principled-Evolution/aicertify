import logging
import sys
import os

# Add parent directory to path to ensure imports work
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import AICertify modules
from aicertify.opa_core.policy_loader import PolicyLoader  # noqa: E402
from aicertify.opa_core.evaluator import OpaEvaluator  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def test_opa_integration():
    """Test the integration with OPA policies."""

    logger.info("Testing OPA policy integration...")

    try:
        # Initialize policy loader
        policy_loader = PolicyLoader()

        # Try loading some policies
        global_policies = policy_loader.get_policies("global")
        logger.info(f"Found {len(global_policies)} global policies")

        # Try loading EU AI Act policies
        eu_policies = policy_loader.get_policies_by_category("international/eu_ai_act")
        logger.info(f"Found {len(eu_policies)} EU AI Act policies")

        # Initialize OPA evaluator
        opa_evaluator = OpaEvaluator()

        # Create minimal test input
        test_input = {
            "contract": {
                "interactions": [{"input_text": "test", "output_text": "test"}]
            },
            "evaluation": {
                "fairness_score": 0.8,
                "content_safety_score": 0.9,
                "risk_management_score": 0.7
            }
        }

        # Try evaluating with a policy if any are found
        if global_policies:
            policy = global_policies[0]
            logger.info(f"Testing evaluation with policy: {policy}")
            result = opa_evaluator.evaluate_policy(policy, test_input)
            logger.info(f"Policy evaluation result: {result}")

        logger.info("OPA policy integration test passed")
        return True
    except Exception as e:
        logger.error(f"OPA policy integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_opa_integration()
    if success:
        logger.info("OPA integration validation successful")
        sys.exit(0)
    else:
        logger.error("OPA integration validation failed")
        sys.exit(1)