import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from datetime import datetime
import json
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from aicertify.monitoring.pydantic_ai.decorators import PydanticAIMonitor
from aicertify.models.evaluation_models import SystemType

load_dotenv()

# Add Pydantic model for structured logging
class InteractionLog(BaseModel):
    application_name: str
    model_info: dict
    timestamp: datetime
    prompts: dict
    conversation: list
    metadata: dict = {}

# Create logs directory in the same folder as the script
SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Define the model
model = OpenAIModel(
    'gpt-4-turbo-preview',
    api_key=os.getenv('OPENAI_API_KEY')
)

# Define the agent with model settings
agent = Agent(
    model=model,
    system_prompt="You are an experienced career coach. Guide the user as they transition from a traditional career to one where AI plays a greater role. Use the industry specialization provided by the user to provide a 10 steps plan for a career overhaul. Refer to the industry in your answer.",
    deps_type=str,
    model_settings={'temperature': 0.7}
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
            
        log_entry.conversation.append({
            "user_input": user_input,
            "response": response,
            "sequence_number": sequence_number
        })
    else:
        # Create new conversation log
        log_entry = InteractionLog(
            application_name=app_name,
            model_info=model_info,
            timestamp=datetime.now(),
            prompts={
                "system_prompt": str(agent.system_prompt),  # Convert to string
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
    log_path = LOG_DIR / filename
    
    try:
        # Write the single interaction to its own file
        with open(log_path, "w") as f:
            json.dump(log_entry.model_dump(mode='json'), f, indent=2, default=str)
    except Exception as e:
        print(f"Error writing log file: {e}")

@PydanticAIMonitor.monitor_agent(
    system_name="CareerCoachAI",
    system_type=SystemType.AI
)
async def main_loop():
    while True:
        user_input = input(">> I am your career coach. Please provide an industry specialization: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        try:
            # Run the agent
            result = await agent.run("Provide a 10 steps plan for a career overhaul.", deps=user_input)
            print(f"\nCareer advice:\n{result.data}")
            
            # Log the interaction
            log_interaction(
                app_name="CareerCoachAI",
                model_info={
                    "model_name": agent.model.model_name,
                    "provider": "OpenAI",
                    "temperature": 0.7
                },
                user_input=user_input,
                response=result.data
            )
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main_loop()) 