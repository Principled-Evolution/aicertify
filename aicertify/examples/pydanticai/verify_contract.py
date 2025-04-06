"""
Simple verification script for AICertify contract creation.
This script tests the basic contract creation and loading functionality.
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import AICertify contract functions
try:
    from aicertify.models.contract_models import (
        create_contract, save_contract, load_contract, ModelInfo, Interaction, AiCertifyContract
    )
    logger.info("Successfully imported AICertify contract modules")
except ImportError as e:
    logger.error(f"Error importing AICertify modules: {e}")
    raise

def main():
    # Create a test contract
    app_name = "TestApplication"
    model_info = {
        "model_name": "TestModel",
        "model_version": "1.0",
        "additional_info": {
            "description": "Test model for AICertify contract verification",
            "developer": "AICertify Team"
        }
    }
    
    interactions = [
        {
            "input_text": "Test question 1?",
            "output_text": "Test response 1",
            "metadata": {"type": "test", "category": "general"}
        },
        {
            "input_text": "Test question 2?",
            "output_text": "Test response 2",
            "metadata": {"type": "test", "category": "specific"}
        }
    ]
    
    # Create contract
    logger.info("Creating contract")
    contract = create_contract(app_name, model_info, interactions)
    logger.info(f"Contract created with ID: {contract.contract_id}")
    
    # Save contract
    output_dir = Path(__file__).parent / "verify_contracts"
    output_dir.mkdir(exist_ok=True)
    
    contract_path = save_contract(contract, str(output_dir))
    logger.info(f"Contract saved to: {contract_path}")
    
    # Load contract back
    logger.info("Loading contract from file")
    loaded_contract = load_contract(contract_path)
    logger.info(f"Loaded contract ID: {loaded_contract.contract_id}")
    
    # Verify the loaded contract matches the original
    assert loaded_contract.contract_id == contract.contract_id, "Contract ID mismatch"
    assert loaded_contract.application_name == app_name, "Application name mismatch"
    assert len(loaded_contract.interactions) == len(interactions), "Interaction count mismatch"
    
    logger.info("Contract verification successful!")
    
    # Print some contract details for verification
    print("\nContract Details:")
    print(f"ID: {loaded_contract.contract_id}")
    print(f"Application: {loaded_contract.application_name}")
    print(f"Model: {loaded_contract.model_info.model_name} v{loaded_contract.model_info.model_version}")
    print(f"Interactions: {len(loaded_contract.interactions)}")
    
    print("\nInteraction Details:")
    for i, interaction in enumerate(loaded_contract.interactions):
        print(f"\nInteraction {i+1}:")
        print(f"  Input: {interaction.input_text}")
        print(f"  Output: {interaction.output_text}")
        print(f"  Metadata: {interaction.metadata}")
    
    return True

if __name__ == "__main__":
    success = main()
    print(f"\nVerification {'successful' if success else 'failed'}!") 