import os
from dotenv import load_dotenv
from colorama import Fore
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Optional, List
import asyncio

load_dotenv()

# Models for structured logging
class LoanInteractionLog(BaseModel):
    """Structured logging for loan officer interactions"""
    application_name: str
    model_info: dict
    timestamp: datetime
    prompts: dict
    conversation: List[dict]
    customer_profile: dict
    risk_profile: Optional[str] = None
    loan_decision: dict
    metadata: dict = {}

class Customer(BaseModel):
    """Customer model with credit-relevant information"""
    customer_id: int
    name: str
    email: str
    age: int
    annual_income: int
    credit_score: int
    zip_code: int
    assets: int
    current_debts: int
    employment_status: str
    length_credit_history: int
    payment_history: str
    purpose: str
    loan_amount_requested: int
    collateral: str
    additional_info: str

class LoanDecision(BaseModel):
    """Loan decision output model"""
    customer: Customer
    response_type: str
    response: str
    loan_amount: int
    term: int

@dataclass
class Deps:
    """Dependencies for the loan officer agent"""
    customer: Customer

# Create logs directory if not exists
Path("logs").mkdir(exist_ok=True)

# Initialize OpenAI model
model = OpenAIModel(
    'gpt-4-turbo-preview',
    api_key=os.getenv('OPENAI_API_KEY')
)

# Define the loan officer agent
agent = Agent(
    model=model,
    result_type=LoanDecision,
    system_prompt="You are a loan officer for a lending institution. Evaluate the customer's profile and risk assessment to determine loan approval. Provide clear, helpful, and polite responses. Always include the customer's name and end with 'Ref: Application ID'.",
    deps_type=Deps,
    model_settings={'temperature': 0.7}
)

@agent.tool(retries=2)
async def get_customer_risk_profile(ctx: RunContext[Deps]) -> str:
    """Get customer risk profile based on provided information"""
    risk_agent = Agent(
        model=model,
        result_type=str,
        system_prompt="Analyze the customer profile and provide a risk assessment for their loan application.",
        deps_type=Deps,
        model_settings={'temperature': 0.7}
    )
    
    @risk_agent.system_prompt
    def get_system_prompt(ctx: RunContext[Deps]) -> str:
        return f"Customer profile for risk assessment: {ctx.deps.customer}"
    
    result = await risk_agent.run("Generate risk profile.", deps=ctx.deps)
    return result.data

def log_interaction(
    app_name: str,
    model_info: dict,
    customer: Customer,
    risk_profile: str,
    loan_decision: LoanDecision,
    sequence_number: int = 1,
    existing_log_path: Optional[Path] = None
):
    """Log the loan officer interaction"""
    try:
        if existing_log_path and existing_log_path.exists():
            with open(existing_log_path) as f:
                existing_data = json.load(f)
                log_entry = LoanInteractionLog(**existing_data)
                log_entry.conversation.append({
                    "customer_input": customer.model_dump(mode='json'),
                    "risk_profile": risk_profile,
                    "loan_decision": loan_decision.model_dump(mode='json'),
                    "sequence_number": sequence_number
                })
        else:
            # Create new log entry with explicit model dumps
            log_entry = LoanInteractionLog(
                application_name=app_name,
                model_info=model_info,
                timestamp=datetime.now(),
                prompts={
                    "system_prompt": str(agent.system_prompt),  # Convert to string
                    "risk_assessment_prompt": "Generate risk profile based on customer data."
                },
                conversation=[{
                    "customer_input": customer.model_dump(mode='json'),
                    "risk_profile": risk_profile,
                    "loan_decision": loan_decision.model_dump(mode='json'),
                    "sequence_number": 1
                }],
                customer_profile=customer.model_dump(mode='json'),
                risk_profile=risk_profile,
                loan_decision=loan_decision.model_dump(mode='json')
            )
        
        # Create filename using customer ID and timestamp
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"{app_name}_customer_{customer.customer_id}_{timestamp_str}.json"
        log_path = Path("logs") / filename
        
        # Write the interaction log with explicit model dump
        with open(log_path, "w") as f:
            json.dump(log_entry.model_dump(mode='json'), f, indent=2, default=str)
        
        return log_path
        
    except Exception as e:
        logger.error(f"Error in log_interaction: {str(e)}")
        raise

async def process_loan_application(customer: Customer):
    """Process a loan application and log the interaction"""
    try:
        # Create dependencies
        deps = Deps(customer=customer)
        
        # Create a proper RunContext for the risk profile tool
        risk_context = RunContext(
            model=model,
            usage={},  # Empty usage dict as it will be filled by the model
            prompt="Generate risk profile.",
            deps=deps
        )
        
        # Get risk profile using proper context
        risk_profile = await get_customer_risk_profile(risk_context)
        print(Fore.BLUE, f"Risk Profile: {risk_profile}")
        
        # Get loan decision
        result = await agent.run(
            "Please evaluate the customer's loan application.",
            deps=deps
        )
        decision = result.data
        
        # Log the interaction
        log_interaction(
            app_name="LoanOfficerAI",
            model_info={
                "model_name": model.model_name,
                "provider": "OpenAI",
                "temperature": 0.7
            },
            customer=customer,
            risk_profile=risk_profile,
            loan_decision=decision
        )
        
        # Display results
        print('\n-----------------------------------\n')
        print(Fore.GREEN, f"Decision: {decision.response}")
        color = Fore.GREEN if decision.response_type == "Approved" else Fore.RED
        print(color, f"Response type: {decision.response_type}")
        print(color, f"Loan amount: ${decision.loan_amount:,}")
        print(color, f"Term (months): {decision.term}")
        print('\n-----------------------------------\n')
        
    except Exception as e:
        print(Fore.RED, f"Error processing application: {str(e)}")
        raise

async def main():
    """Main function to process sample loan applications"""
    # Sample customer profiles
    customers = [
        Customer(
            customer_id=123,
            name="Michaela Resilient",
            email="m.resilient@gmail.com",
            age=35,
            annual_income=50000,
            credit_score=700,
            zip_code=20000,
            assets=30000,
            current_debts=50000,
            employment_status="Full-time",
            length_credit_history=10,
            payment_history="Good",
            purpose="Home improvement",
            loan_amount_requested=1000000,
            collateral="Home",
            additional_info="No recent credit inquiries"
        ),
        # Add more sample customers here
    ]
    
    for customer in customers:
        await process_loan_application(customer)

if __name__ == "__main__":
    asyncio.run(main())
