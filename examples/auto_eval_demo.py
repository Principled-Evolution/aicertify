#!/usr/bin/env python
"""
Auto Evaluation Demo - Dialogue Summarization

This script demonstrates how to use LangFair's AutoEval class to compute
toxicity, stereotype, and counterfactual metrics for a set of input prompts.
It is adapted from a notebook demo for easy debugging in an IDE.
"""

import os
import warnings
import asyncio
import logging

import pandas as pd
from dotenv import load_dotenv, find_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter

from langfair.auto import AutoEval
from langfair.utils.dataloader import load_dialogsum

# Set up logging to display messages in the console.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """
    Load API configuration from a .env file.
    """
    load_dotenv(find_dotenv())
    config = {
        "OPENAI_API_KEY": os.getenv('OPENAI_API_KEY'),
        "OPENAI_API_BASE": os.getenv('OPENAI_API_BASE'),
        "OPENAI_API_TYPE": os.getenv('OPENAI_API_TYPE'),
        "OPENAI_API_VERSION": os.getenv('OPENAI_API_VERSION'),
        "OPENAI_MODEL_VERSION": os.getenv('OPENAI_MODEL_VERSION'),
        "OPENAI_DEPLOYMENT_NAME": os.getenv('OPENAI_DEPLOYMENT_NAME')
    }
    return config


async def main():
    """
    Main asynchronous function to run the AutoEval demonstration.
    """
    config = load_config()
    if not config["OPENAI_API_KEY"]:
        logger.error("API_KEY not found. Please set it in your .env file.")
        return

    # Optionally suppress any benign warnings.
    warnings.filterwarnings("ignore")

    # Load a sample of dialogues. Adjust `n` as needed.
    n = 100  # number of dialogues to test
    dialogue = load_dialogsum(n=n)
    logger.info("Loaded %d dialogues.", n)
    logger.info("Example dialogue: %s", dialogue[0])

    # Build the list of prompts.
    instruction = "You are to summarize the following conversation in no more than 3 sentences:\n"
    prompts = [instruction + str(text) for text in dialogue]

    # Create a rate limiter to avoid rate-limit errors.
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=10,
        check_every_n_seconds=10,
        max_bucket_size=1000,
    )

    # Create the LangChain LLM instance.
    # We use AzureChatOpenAI in this example.
    import openai
    from langchain_openai import AzureChatOpenAI

    llm = AzureChatOpenAI(
        deployment_name=config["DEPLOYMENT_NAME"],
        openai_api_key=config["API_KEY"],
        azure_endpoint=config["API_BASE"],
        openai_api_type=config["API_TYPE"],
        openai_api_version=config["API_VERSION"],
        temperature=1,  # Set the desired temperature
        rate_limiter=rate_limiter
    )

    # Define exceptions to suppress (e.g., errors due to content filtering).
    suppressed_exceptions = (openai.BadRequestError, ValueError)

    # Instantiate the AutoEval class.
    ae = AutoEval(
        prompts=prompts,
        langchain_llm=llm,
        suppressed_exceptions=suppressed_exceptions,
        # toxicity_device can be set to GPU if available:
        # toxicity_device=torch.device("cuda")
    )

    logger.info("Starting evaluation...")
    # Execute the evaluation asynchronously.
    results = await ae.evaluate(return_data=True)

    # Print the evaluation results in a clean format.
    ae.print_results()
    export_filename = "final_metrics.txt"
    # Export the results to a text file.
    ae.export_results(file_name=export_filename)
    logger.info("Results exported to %s", export_filename)

    # Optionally, view the top toxicity and stereotype scores.
    toxicity_data = pd.DataFrame(results["data"]["Toxicity"])
    logger.info("Top toxicity scores:\n%s",
                toxicity_data.sort_values(by='score', ascending=False).head())

    stereotype_data = pd.DataFrame(results["data"]["Stereotype"])
    logger.info("Top stereotype scores:\n%s",
                stereotype_data.sort_values(by='stereotype_score_gender', ascending=False).head())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("An error occurred during evaluation: %s", e) 