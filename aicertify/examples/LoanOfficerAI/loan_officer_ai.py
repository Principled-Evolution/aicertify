import os
from dotenv import load_dotenv
from colorama import Fore
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.models.openai import OpenAIModel
from dataclasses import dataclass
from aicertify.monitoring.pydantic_ai.decorators import PydanticAIMonitor

load_dotenv()

class Policy(BaseModel):
    """Policy model - includes policy number, policy type and policy status"""
    policy_number: int
    policy_type: str
    policy_status: str
    policy_deductable: int
    policy_max_coverage: int
    policy_coverage_remaining: int

class Customer(BaseModel):
    """Customer model - includes customer details for loan application"""
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
    """Loan decision response model"""
    customer: Customer
    response_type: str
    response: str
    loan_amount: int
    term: int

@dataclass
class Deps:
    """Dependencies for the agent"""
    customer: Customer

@PydanticAIMonitor.monitor_agent(
    system_name="LoanOfficerAI",
    system_type="FinancialAI"
)
class LoanOfficerAgent:
    def __init__(self):
        self.model = OpenAIModel('gpt-4-turbo-preview', api_key=os.getenv('OPENAI_API_KEY'))
        self.agent = Agent(
            model=self.model,
            result_type=LoanDecision,
            system_prompt="You are a loan officer for a lending institution. Your task is to take the customer's profile, use the credit risk tool to get a risk profile and determine if the requested loan should be approved. Provide a clear and helpful response. Ensure that your response is polite and addresses the customer's loan application effectively. Always include customer's name in your response. End your answer with Ref: Application ID.",
            deps_type=Deps
        )
        
        # Register tools and validators
        self._register_tools()
    
    def _register_tools(self):
        @self.agent.tool(retries=2)
        @PydanticAIMonitor.monitor_llm("risk_assessment")
        async def get_customer_risk_profile(ctx: RunContext[Deps]) -> str:
            """Get the customer's risk profile based on provided information."""
            risk_agent = Agent(
                model=self.model,
                result_type=str,
                system_prompt="Take the customer profile and return a risk profile for a loan application.",
                deps_type=Deps
            )
            
            @risk_agent.system_prompt
            def get_system_prompt(ctx: RunContext[str]) -> str:
                return f"The customer profile is {ctx.deps.customer}."
            
            result = await risk_agent.run("Get the customer's risk profile.", deps=ctx.deps)
            print(Fore.BLUE, f"Customer risk profile: {result.data}")
            return f"The customer risk profile is: {result.data}"

    async def process_loan_application(self, customer: Customer) -> LoanDecision:
        """Process a loan application and return a decision"""
        deps = Deps(customer=customer)
        result = await self.agent.run(
            "Please evaluate the customer's loan application.",
            deps=deps
        )
        return result.data

async def main():
    # Initialize loan officer
    loan_officer = LoanOfficerAgent()
    
    # Create sample customers
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
    
    # Process applications
    for customer in customers:
        try:
            result = await loan_officer.process_loan_application(customer)
            
            print('\n-----------------------------------\n')
            print(Fore.GREEN, f"Agent: {result.response}")
            color = Fore.GREEN if result.response_type == "Approved" else Fore.RED
            print(color, f"Response type: {result.response_type}")
            print(color, f"Loan amount: {result.loan_amount}")
            print(color, f"Loan term (mos): {result.term}")
            print('\n-----------------------------------\n')
            
        except ModelRetry as e:
            print(Fore.RED, f"Error processing application for {customer.name}: {e}")
        except Exception as e:
            print(Fore.RED, f"Unexpected error for {customer.name}: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 