import pytest
import asyncio

from aicertify.models.contract_models import AiCertifyContract
from aicertify.api import evaluate_contract_object

@pytest.mark.asyncio
async def test_evaluate_contract_object():
    """Test the evaluate_contract_object API using a sample contract."""
    # Create a sample contract
    contract = AiCertifyContract(
        contract_id='test-123',
        application_name='TestApp',
        interactions=[
            {
                'input_text': 'Test prompt',
                'output_text': 'Test response',
                'metadata': {}
            }
        ]
    )
    
    # Evaluate the contract
    result = await evaluate_contract_object(contract, policy_category='eu_ai_act')
    
    # Assert that the result contains expected keys
    assert 'evaluation' in result, 'Evaluation result missing'
    assert 'policies' in result, 'Policies result missing'
    
    # Optionally, check if a report is generated if requested
    # If report generation is enabled, then report key should exist
    if result.get('report'):
        assert isinstance(result['report'], dict) or isinstance(result['report'], str), 'Report format unexpected' 