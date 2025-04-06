"""
Create a Hugging Face dataset from the existing toxic responses.

This script extracts the responses from ToxicCareerCoachAI.py and uploads them
to a Hugging Face dataset with the appropriate structure.
"""

import os
import re
import logging
from pathlib import Path
import argparse
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from datasets import Dataset, DatasetDict
    from huggingface_hub import login

    HUGGINGFACE_AVAILABLE = True
except ImportError:
    logger.error("Hugging Face libraries not found. Please install with:")
    logger.error("pip install datasets huggingface_hub")
    HUGGINGFACE_AVAILABLE = False


def extract_responses_from_file(file_path: Path) -> Dict[str, List[str]]:
    """
    Extract the toxic, gender-biased, and racial-biased responses from the source file.

    Args:
        file_path: Path to the ToxicCareerCoachAI.py file

    Returns:
        Dictionary with response types as keys and lists of responses as values
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Define regex patterns to extract the responses
    toxic_pattern = r"self\.toxic_responses\s*=\s*\[(.*?)\]"
    gender_pattern = r"self\.gender_biased_responses\s*=\s*\[(.*?)\]"
    racial_pattern = r"self\.racial_biased_responses\s*=\s*\[(.*?)\]"

    # Extract all response types using regex
    toxic_matches = re.search(toxic_pattern, content, re.DOTALL)
    gender_matches = re.search(gender_pattern, content, re.DOTALL)
    racial_matches = re.search(racial_pattern, content, re.DOTALL)

    # Process the matches into clean responses
    def process_matches(matches):
        if not matches:
            return []
        raw_text = matches.group(1)
        # Split by commas, but only if not within quotes
        items = []
        current = ""
        in_quotes = False
        for char in raw_text:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
            current += char
            if char == "," and not in_quotes and current.strip():
                items.append(current.strip())
                current = ""
        if current.strip():
            items.append(current.strip())

        # Clean up each item (remove quotes and leading/trailing whitespace)
        clean_items = []
        for item in items:
            # Remove trailing comma if present
            if item.endswith(","):
                item = item[:-1]
            # Remove quotes
            if (item.startswith('"') and item.endswith('"')) or (
                item.startswith("'") and item.endswith("'")
            ):
                item = item[1:-1]
            clean_items.append(item)

        return clean_items

    toxic_responses = process_matches(toxic_matches)
    gender_biased_responses = process_matches(gender_matches)
    racial_biased_responses = process_matches(racial_matches)

    return {
        "toxic": toxic_responses,
        "gender_biased": gender_biased_responses,
        "racial_biased": racial_biased_responses,
    }


def create_and_push_dataset(
    responses: Dict[str, List[str]], dataset_name: str, token: str = None
):
    """
    Create and push the dataset to Hugging Face.

    Args:
        responses: Dictionary with response types as keys and lists of responses as values
        dataset_name: Name of the dataset on Hugging Face (e.g., "aicertify/toxic-responses")
        token: Hugging Face API token (optional if logged in with huggingface-cli login)
    """
    if not HUGGINGFACE_AVAILABLE:
        logger.error("Hugging Face libraries not available. Cannot create dataset.")
        return

    # Login to Hugging Face if token is provided
    if token:
        logger.info(f"Logging in to Hugging Face with provided token")
        login(token=token, add_to_git_credential=True)

    # Create datasets for each response type
    datasets = {}
    for response_type, response_list in responses.items():
        if not response_list:
            logger.warning(f"No responses found for type: {response_type}")
            continue

        # Create a Dataset object for this response type
        data = {"text": response_list}
        dataset = Dataset.from_dict(data)
        datasets[response_type] = dataset
        logger.info(
            f"Created dataset for {response_type} with {len(response_list)} responses"
        )

    # Create a DatasetDict from all datasets
    dataset_dict = DatasetDict(datasets)

    # Push to the Hugging Face Hub
    try:
        dataset_dict.push_to_hub(dataset_name, private=False)
        logger.info(f"Successfully pushed dataset to {dataset_name}")
    except Exception as e:
        logger.error(f"Error pushing dataset to Hugging Face: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a Hugging Face dataset from toxic responses"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="ToxicCareerCoachAI.py",
        help="Path to the ToxicCareerCoachAI.py file",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="aicertify/toxic-responses",
        help="Name of the Hugging Face dataset",
    )
    parser.add_argument("--token", type=str, help="Hugging Face API token (optional)")
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Only print extracted responses without pushing to Hugging Face",
    )

    args = parser.parse_args()

    # Get the file path, handling both absolute and relative paths
    if os.path.isabs(args.file):
        file_path = Path(args.file)
    else:
        file_path = Path(__file__).parent / args.file

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return

    # Extract responses
    responses = extract_responses_from_file(file_path)

    # Print a summary of extracted responses
    for response_type, response_list in responses.items():
        logger.info(f"{response_type}: {len(response_list)} responses extracted")
        if response_list:
            # Print the first response as an example
            logger.info(f"Example: {response_list[0][:100]}...")

    # Push to Hugging Face if not in print-only mode
    if not args.print_only:
        create_and_push_dataset(responses, args.dataset, args.token)
    else:
        logger.info("Print-only mode. Not pushing to Hugging Face.")


if __name__ == "__main__":
    main()
