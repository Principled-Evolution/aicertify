import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

from aicertify.models.contract_models import AiCertifyContract
from aicertify.models.langfair_eval import AutoEvalInput
from aicertify.system_evaluators.langfair_auto_eval import evaluate_ai_responses

logger = logging.getLogger(__name__)


async def evaluate_contract_with_langfair(contract_json_path: str, output_dir: str = "evaluations") -> Optional[dict]:
    """
    1) Loads a contract from a JSON file,
    2) Converts its interactions to an AutoEvalInput,
    3) Runs LangFair auto-evaluation, and
    4) Saves the evaluation results to a JSON file in the output directory.

    Parameters:
        contract_json_path (str): Path to the contract JSON file.
        output_dir (str, optional): Directory to store the evaluation results. Defaults to "evaluations".

    Returns:
        Optional[dict]: The evaluation result as a dictionary, or None if an error occurs.
    """
    try:
        # Load the contract from file
        contract = AiCertifyContract.parse_file(contract_json_path)
    except Exception as e:
        logger.error(f"Error loading contract file {contract_json_path}: {str(e)}")
        return None

    # Extract prompts and responses from contract interactions
    prompts = [interaction.input_text for interaction in contract.interactions]
    responses = [interaction.output_text for interaction in contract.interactions]

    eval_input = AutoEvalInput(prompts=prompts, responses=responses)
    logger.info("Running LangFair auto-evaluation...")
    try:
        auto_eval_result = await evaluate_ai_responses(eval_input)
    except Exception as e:
        logger.error(f"Error during LangFair evaluation: {str(e)}")
        return None
    logger.info("LangFair evaluation completed.")

    # Prepare the result dictionary
    result_dict = auto_eval_result.dict()
    result_dict["contract_id"] = str(contract.contract_id)
    result_dict["application_name"] = contract.application_name

    # Ensure the output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / f"evaluation_{contract.contract_id}.json"
    with open(output_file, "w") as f:
        json.dump(result_dict, f, indent=2)

    logger.info(f"Evaluation results saved to {output_file}")
    return result_dict


def batch_evaluate_langfair(contract_paths: list[str], output_dir: str = "evaluations") -> list[Optional[dict]]:
    """
    Iterates over multiple contract JSON files, evaluates each using LangFair auto-evaluation,
    and returns a list of evaluation results.

    Parameters:
        contract_paths (list[str]): List of paths to contract JSON files.
        output_dir (str, optional): Directory to store the evaluation results. Defaults to "evaluations".

    Returns:
        list[Optional[dict]]: A list of evaluation result dictionaries.
    """
    loop = asyncio.get_event_loop()
    tasks = [evaluate_contract_with_langfair(cp, output_dir=output_dir) for cp in contract_paths]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    logger.info("All contracts evaluated with LangFair.")
    return results


async def evaluate_app_folder(app_name: str, folder_path: str, output_json: str) -> Optional[dict]:
    """
    Loads all contract JSON files in folder_path for the specified app_name,
    aggregates prompts and responses from all interactions, runs a single
    LangFair auto-evaluation over the combined data, and saves the consolidated
    evaluation to output_json.
    
    Parameters:
        app_name (str): The target application name to filter contracts.
        folder_path (str): Directory containing contract JSON files.
        output_json (str): File path where the consolidated evaluation result will be saved.
        
    Returns:
        Optional[dict]: The consolidated evaluation result dictionary, or None if an error occurs.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        logger.error(f"Folder {folder_path} does not exist or is not a directory.")
        return None

    contract_files = list(folder.glob("*.json"))
    if not contract_files:
        logger.warning(f"No contract JSON files found in {folder_path}")
        return None

    aggregated_prompts = []
    aggregated_responses = []
    total_contract_count = 0

    for cf in contract_files:
        try:
            data = json.loads(cf.read_text())
            contract = AiCertifyContract.parse_obj(data)
            if contract.application_name != app_name:
                logger.debug(f"Skipping contract {cf}, different application name: {contract.application_name}")
                continue
            for interaction in contract.interactions:
                aggregated_prompts.append(interaction.input_text)
                aggregated_responses.append(interaction.output_text)
            total_contract_count += 1
        except Exception as e:
            logger.error(f"Error parsing {cf}: {e}")

    if not aggregated_prompts:
        logger.warning(f"No interactions found for app '{app_name}' in {folder_path}.")
        return None

    logger.info(f"Collected {len(aggregated_prompts)} total prompts/responses from {total_contract_count} contract(s).")

    auto_eval_input = AutoEvalInput(prompts=aggregated_prompts, responses=aggregated_responses)
    logger.info("Running a single auto-eval across all collected data.")
    try:
        auto_eval_result = await evaluate_ai_responses(auto_eval_input)
    except Exception as e:
        logger.error(f"Error during merged LangFair evaluation: {e}")
        return None

    result_dict = auto_eval_result.dict()
    result_dict["combined_contract_count"] = total_contract_count
    result_dict["app_name"] = app_name
    result_dict["evaluation_mode"] = "batch_aggregate"

    from datetime import datetime

    output_path = Path(output_json)
    if output_path.is_dir():
        # Append a default filename in the directory if output_json is a directory
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_path / f"consolidated_evaluation_{app_name}{timestamp_str}.json"
    else:
        output_file = output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(result_dict, f, indent=2) 

    logger.info(f"Aggregated evaluation saved to {output_json} for app '{app_name}'.")
    return result_dict 