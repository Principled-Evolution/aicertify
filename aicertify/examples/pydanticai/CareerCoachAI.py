import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from datetime import datetime
import json
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import argparse
import sys

print("Python path:", sys.path)
try:
    import pydantic_ai
    print(f"pydantic_ai found at: {pydantic_ai.__file__}")
except ImportError:
    print("pydantic_ai not found in sys.path")

load_dotenv()
# This example demonstrates how to use dependency injection in Pydantic AI to pass additional context to the system prompt. Here, we define a system prompt that uses dependency injection to pass the user's industry specialization to the system prompt. The system prompt then uses this information to provide a more personalized response to the user.

# Add Pydantic model for structured logging
class InteractionLog(BaseModel):
    application_name: str
    model_info: dict
    timestamp: datetime
    prompts: dict
    conversation: list
    metadata: dict = {}

# Create logs directory if not exists
Path("logs").mkdir(exist_ok=True)

# Define the model with correct parameters
model = OpenAIModel(
    'gpt-4o-mini',
    api_key=os.getenv('OPENAI_API_KEY')  # Remove temperature from here
)

# Define the agent with model settings
agent = Agent(
    model=model,
    system_prompt="You are an experienced career coach. Guide the user as they transition from a tradtional career to one where AI plays a greater role. Use the industry specialization provided by the user to provide a 10 steps plan for a career overhaul. Refer to the industry in your answer.",
    deps_type=str,
    model_settings={'temperature': 0.7}  # Add temperature here via ModelSettings
)

# Define a system prompt with dependency injection
@agent.system_prompt
def get_industry(ctx: RunContext[str]) -> str:
    return f"Your industry specialization is in {ctx.deps}."

# Add logging function
def log_interaction(
    app_name: str,
    model_info: dict,
    user_input: str,
    response: str,
    sequence_number: int = 1,
    existing_log_path: Optional[Path] = None
):
    if existing_log_path and existing_log_path.exists():
        with open(existing_log_path) as f:
            existing_data = json.load(f)
            log_entry = InteractionLog(**existing_data)
            
        log_entry.conversation.append(
            Exchange(
                user_input=user_input,
                response=response,
                sequence_number=sequence_number
            )
        )
    else:
        # Create new conversation log
        log_entry = InteractionLog(
            application_name=app_name,
            model_info=model_info,
            timestamp=datetime.now(),
            prompts={
                "system_prompt": "You are an experienced career coach. Guide the user as they transition from a tradtional career to one where AI plays a greater role. Use the industry specialization provided by the user to provide a 10 steps plan for a career overhaul. Refer to the industry in your answer.",
                "injection_prompt": get_industry.__doc__ or "Your industry specialization is in {ctx.deps}."
            },
            conversation=[
                {
                    "user_input": user_input,
                    "response": response,
                    "sequence_number": 1
                }
            ]
        )
    
    # Create a sanitized version of the industry name for the filename
    sanitized_industry = "".join(c if c.isalnum() else "_" for c in user_input.lower())
    
    # Format: logs/CareerCoachAI_chef_2025-02-17_191449.json
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{app_name}_{sanitized_industry}_{timestamp_str}.json"
    log_path = Path("logs") / filename
    
    # Write the single interaction to its own file
    with open(log_path, "w") as f:
        json.dump(log_entry.model_dump(mode='json'), f, indent=2)

# Update the main_loop to optionally capture interactions

def main_loop(capture_contract: bool = False):
    captured_interactions = []  # list to accumulate interactions if capturing is enabled
    while True:
        user_input = input(">> I am your career coach. Please provide an industry specialization: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Run the agent
        result = agent.run_sync("Provide a 10 steps plan for a career overhaul.", deps=user_input)
        print(f"Career advice: {result.data}")
        
        # Existing logging function call
        log_interaction(
            app_name="CareerCoachAI",
            model_info={
                "model_name": agent.model.model_name,
                "provider": "OpenAI",
                "temperature": getattr(agent.model, 'temperature', 'default')
            },
            user_input=user_input,
            response=result.data
        )

        # If capturing is enabled, store the interaction for contract creation
        if capture_contract:
            captured_interactions.append({
                "input_text": user_input,
                "output_text": result.data,
                "metadata": {}
            })

    # After loop, if capturing is enabled and interactions were captured, create contract
    if capture_contract and captured_interactions:
        try:
            from aicertify.models.contract_models import create_contract, validate_contract
        except ImportError:
            from contract_models import create_contract, validate_contract

        application_name = "CareerCoachAI Interactive Session"
        model_info = {
            "model_name": agent.model.model_name,
            "model_version": "N/A",
            "additional_info": {
                "provider": "OpenAI",
                "temperature": getattr(agent.model, 'temperature', 'default')
            }
        }
        contract = create_contract(application_name, model_info, captured_interactions)
        if validate_contract(contract):
            print("Interactive contract successfully validated.")
        else:
            print("Interactive contract validation failed.")
        
        try:
            from aicertify.models.contract_models import save_contract
        except ImportError:
            from contract_models import save_contract
        file_path = save_contract(contract, storage_dir=args.contract_storage)
        print(f"Interactive contract saved to {file_path}")

# Update CLI argument parser to include --capture-contract flag
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo for Career Coach Agent and AICertify Contract Validation")
    parser.add_argument('--contract-demo', action='store_true', help="Run Phase 1 Contract demo")
    parser.add_argument('--agent-demo', action='store_true', help="Run Career Coach Agent demo (interactive)")
    parser.add_argument('--capture-contract', action='store_true', help="Capture interactive inputs to generate a contract for evaluation")
    parser.add_argument('--contract-storage', type=str, default='contracts', help="Directory to store generated contract files")
    args = parser.parse_args()

    def contract_demo():
        try:
            from aicertify.models.contract_models import create_contract, validate_contract
        except ImportError:
            from contract_models import create_contract, validate_contract
        
        application_name = "HelloWorldApp"
        model_info = {
            "model_name": "SampleModel",
            "model_version": "1.0",
            "additional_info": {"language": "English"}
        }
        interactions = [
            {"input_text": "Hello", "output_text": "Hi there!"},
            {"input_text": "How are you?", "output_text": "I'm fine, thank you."}
        ]
        contract = create_contract(application_name, model_info, interactions)
        if validate_contract(contract):
            print("Contract is valid!")
        else:
            print("Contract validation failed.")
        try:
            from aicertify.models.contract_models import save_contract
        except ImportError:
            from contract_models import save_contract
        file_path = save_contract(contract, storage_dir=args.contract_storage)
        print(f"Contract saved to {file_path}")
    
    if args.contract_demo:
        contract_demo()
    elif args.agent_demo:
        main_loop(capture_contract=args.capture_contract)
    else:
        # Default behavior: run agent demo interactive mode that captures contract if specified
        main_loop(capture_contract=args.capture_contract)