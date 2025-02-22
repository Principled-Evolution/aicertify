import os
import argparse
import logging
from datetime import datetime

from dotenv import load_dotenv
from colorama import Fore
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
import yfinance as yf

# Load environment variables
load_dotenv()

# This example demonstrates how to use combined dependencies in PydanticAI.
# The use case is a stock market researcher agent that takes a stock name, retrieves 
# the stock symbol, and fetches the latest stock price.
# The agent is expected to provide the stock symbol and the latest stock price for 
# the given stock name.

# Define the model
model = OpenAIModel('gpt-4o-mini', api_key=os.getenv('OPENAI_API_KEY'))

class Stock(BaseModel):
    """Stock model - includes stock symbol, stock name and stock price"""
    stock_name: str = "AAPL"
    stock_symbol: str = ""
    stock_price: float = 0.0

# Define the agent with a system prompt
agent = Agent(
    model=model,
    system_prompt="You are an experienced stock market researcher. Use the tools at your disposal to research the stock provided in the context.",
    deps_type=Stock,
    result_type=Stock
)

# Define a system prompt with dependency injection
@agent.system_prompt  
def get_industry(ctx: RunContext[Stock]) -> str:
    return f"The stock requested is {ctx.deps.stock_name}."

# Define a tool with dependency injection
@agent.tool
def get_stock_price(ctx: RunContext[Stock], symbol: str) -> Stock:
    # Call the Yahoo Finance API to get the stock price
    print(Fore.WHITE + f"Getting stock price for {symbol}...")
    dat = yf.Ticker(symbol)
    stock_price = dat.history(period="1d")['Close'].iloc[0]
    return Stock(stock_name=ctx.deps.stock_name, stock_symbol=symbol, stock_price=stock_price)

# Define a result validator with dependency injection
@agent.result_validator
def validate_stock_price(ctx: RunContext[Stock], result: Stock) -> Stock:
    if result.stock_price < 0:
        raise ValueError("Stock price cannot be negative.")
    return result


def run_session(capture_contract: bool, contract_storage: str) -> None:
    """Run the stock research session in an interactive loop, capture outputs, and optionally generate a contract."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    captured_interactions: list[dict] = []

    while True:
        user_input = input(">> Enter a company name (q, quit, exit to exit): ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stock = Stock(stock_name=user_input)

        # Run the agent
        try:
            result = agent.run_sync("Find the latest price for the company name provided.", deps=stock)
            print(Fore.WHITE, '-----------------------------------')
            print(Fore.YELLOW, f"Stock name: {result.data.stock_name}")
            print(Fore.YELLOW, f"Stock symbol: {result.data.stock_symbol}")
            print(Fore.YELLOW, f"Stock price: ${result.data.stock_price:.2f}")
            print(Fore.WHITE, '-----------------------------------')
            
            captured_interactions.append({
                "input_text": user_input,
                "output_text": f"Stock name: {result.data.stock_name}\nStock symbol: {result.data.stock_symbol}\nStock price: ${result.data.stock_price:.2f}",
                "metadata": {"agent": "StockResearch"}
            })
        except Exception as e:
            print(Fore.WHITE, f"Error: {e}")

    # After the interactive session ends, if contract capture is enabled, create and save a contract.
    if capture_contract and captured_interactions:
        try:
            try:
                from aicertify.models.contract_models import create_contract, validate_contract
            except ImportError:
                from contract_models import create_contract, validate_contract

            application_name = "Stock Research Session"
            model_info = {
                "model_name": agent.model.model_name,
                "model_version": "N/A",
                "additional_info": {
                    "provider": "OpenAI",
                    "temperature": "default"
                }
            }
            contract = create_contract(application_name, model_info, captured_interactions)
            if validate_contract(contract):
                print("Contract successfully validated.")
            else:
                print("Contract validation failed.")

            try:
                from aicertify.models.contract_models import save_contract
            except ImportError:
                from contract_models import save_contract
            file_path = save_contract(contract, storage_dir=contract_storage)
            print(f"Contract saved to {file_path}")
        except Exception as ex:
            print(Fore.RED, f"Error creating contract: {ex}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo for Stock Market Research Session with Contract Capture")
    parser.add_argument('--capture-contract', action='store_true', help="Capture outputs to generate a contract for evaluation")
    parser.add_argument('--contract-storage', type=str, default='contracts', help="Directory to store generated contract files")
    args = parser.parse_args()

    run_session(capture_contract=args.capture_contract, contract_storage=args.contract_storage)


if __name__ == "__main__":
    main()