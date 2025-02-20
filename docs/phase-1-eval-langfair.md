Below is a **phase 1 plan** for **integrating the existing contract-based approach** (from `contract_models.py` and similar) with **LangFair auto-evaluation** (from `langfair_eval.py` and `langfair_auto_eval.py`). The goal is to provide a **generic, consistent** way to:

1. **Parse** existing `AiCertifyContract` objects (the “contracts”),  
2. **Extract** the text prompts / responses from each contract’s interactions,  
3. **Run** LangFair’s “auto eval” to produce fairness/bias/toxicity metrics,  
4. **Return** a structured evaluation result that can be stored, logged, or passed downstream to OPA.

Below is a step-by-step outline on how to connect these pieces for **Phase 1**.

---

## 1. Overview of the Components

1. **`AiCertifyContract`** (from `contract_models.py`)  
   - Contains:
     - `application_name`, `model_info`, `final_output`, etc.  
     - A list of `interactions` (each with `input_text` and `output_text`).  
   - Possibly stored offline as a JSON file (e.g., `contract_2025-02-20_115226.json`).

2. **LangFair AutoEval** (from `langfair_eval.py`, `langfair_auto_eval.py`)  
   - Expects an `AutoEvalInput` with:
     - `prompts` (list of user prompts)  
     - `responses` (list of AI-generated responses)  
   - Produces an `AutoEvalResult` containing metrics (`FairnessMetrics`, toxicity/stereotype/counterfactual breakdown, etc.).

3. **Phase 1**: Focus on **offline** or “batch mode” processing:
   - Developer has one or more contract JSON files.  
   - We run a pipeline that loads each contract, extracts prompts/responses, runs LangFair, and obtains a final “auto eval” result.

---

## 2. Proposed Data Flow

Here’s a **high-level** pipeline:

1. **Load a Contract**  
   - Either read from JSON file using `AiCertifyContract.parse_file(...)` or an equivalent function from `aggregate_contracts`.

2. **Convert** to `AutoEvalInput`  
   - `prompts`: `[interaction.input_text for interaction in contract.interactions]`  
   - `responses`: `[interaction.output_text for interaction in contract.interactions]`

3. **Run** LangFair’s `evaluate_ai_responses` (async function in `langfair_auto_eval.py`)  
   - This returns an `AutoEvalResult`.

4. **Store** or **log** the resulting `AutoEvalResult`:
   - Possibly embed it back into an extended contract or keep it in a separate file/object referencing the `contract_id`.  
   - E.g., `evaluation_results_<contract_id>.json` or a dedicated field in the aggregator data.

---

## 3. Example Implementation Sketch

Below is a simplified function that shows how we might implement the process of **loading** a contract, **extracting** inputs/responses, **calling** LangFair, and **storing** the results.

```python
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
from .contract_models import AiCertifyContract
from .langfair_eval import AutoEvalInput
from .langfair_auto_eval import evaluate_ai_responses

logger = logging.getLogger(__name__)

async def evaluate_contract_with_langfair(
    contract_json_path: str, 
    output_dir: str = "evaluations"
) -> Optional[dict]:
    """
    1) Loads a contract from JSON,
    2) Converts interactions to AutoEvalInput,
    3) Runs LangFair auto-evaluation,
    4) Saves the results to disk (and/or returns them).
    """
    try:
        contract = AiCertifyContract.parse_file(contract_json_path)
    except Exception as e:
        logger.error(f"Error loading contract file {contract_json_path}: {str(e)}")
        return None

    # Prepare AutoEvalInput from contract interactions
    prompts = []
    responses = []
    for interaction in contract.interactions:
        prompts.append(interaction.input_text)
        responses.append(interaction.output_text)

    eval_input = AutoEvalInput(prompts=prompts, responses=responses)
    logger.info("Running LangFair auto-eval...")

    # Run the asynchronous evaluation
    auto_eval_result = await evaluate_ai_responses(eval_input)
    logger.info("LangFair evaluation completed.")

    # Convert result to dict for serialization
    result_dict = auto_eval_result.dict()
    result_dict["contract_id"] = str(contract.contract_id)
    result_dict["application_name"] = contract.application_name

    # Optionally store the results in a JSON file
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    output_file = Path(output_dir) / f"evaluation_{contract.contract_id}.json"
    with open(output_file, "w") as f:
        json.dump(result_dict, f, indent=2)

    logger.info(f"Evaluation results saved to {output_file}")
    return result_dict

def batch_evaluate_langfair(contract_paths: list[str], output_dir: str = "evaluations") -> None:
    """
    Iterates over multiple contract JSON files, calls evaluate_contract_with_langfair,
    and collects all results in one step.
    """
    loop = asyncio.get_event_loop()
    tasks = [evaluate_contract_with_langfair(cp, output_dir=output_dir) for cp in contract_paths]
    loop.run_until_complete(asyncio.gather(*tasks))
    logger.info("All contracts evaluated with LangFair.")
```

**Key Points**:

- We use the existing `AiCertifyContract` pydantic model.  
- We map `interaction.input_text` → prompts, and `interaction.output_text` → responses.  
- We then pass `eval_input` to `evaluate_ai_responses()`.  
- The final `AutoEvalResult` is either **saved** to a file or integrated further (e.g., appended to an aggregator object or passed into OPA).

---

## 4. Testing & Validation

1. **Single Contract Test**  
   - Provide one contract file (e.g., `contract_2025-02-20_115226.json`), call `evaluate_contract_with_langfair(...)`, and check that a JSON with the correct metrics is saved.
2. **Batch Test**  
   - Provide multiple contract files in a list.  
   - Use `batch_evaluate_langfair` to run them all.  
   - Confirm each produces a corresponding `evaluation_*.json`.

3. **Edge Cases**  
   - Contract with no interactions (should fail gracefully).  
   - Interactions with empty text.  
   - Exception handling if the auto-eval or LLM calls fail.

---

## 5. Phase 1 Roadmap: Key Points

1. **Pydantic Contract**:  
   - Continue using `AiCertifyContract` from `contract_models.py`.  
   - The developer must produce these offline or via their pipeline.

2. **LangFair AutoEval**:  
   - We'll adopt the approach of **extracting** `input_text` and `output_text` from the contract’s interactions.  
   - The `evaluate_ai_responses` function in `langfair_auto_eval.py` does the heavy lifting (toxicity, stereotype, etc.).

3. **Offline / Batch**:  
   - For now, we focus on **offline** usage (loading pre-collected contract JSONs).  
   - We generate an **evaluation output** for each contract.  
   - Optionally produce an aggregator that merges final results for multiple contracts.

4. **Evaluation → OPA**:  
   - If you want to pass the evaluation data to OPA, you can store them in the result JSON. Later, an OPA policy might read fields like `metrics.toxicity.toxic_fraction` or `metrics.stereotype.gender_bias_detected`.
   - Phase 1 simply ensures that these **evaluation** steps are consistent and produce a standard object.

---

## 6. Conclusion & Next Steps

By following the above plan, we have a **consistent** Phase 1 approach to:

1. **Load** the standard contract model (`AiCertifyContract`).  
2. **Extract** prompts/responses for LangFair.  
3. **Run** the `evaluate_ai_responses` asynchronous function.  
4. **Store** or **aggregate** the `AutoEvalResult` in offline mode.

Future expansions might:

- Integrate the **evaluation** results **back** into the contract (i.e., add a new field like `evaluation_results` to the contract schema).  
- Add a **decorator** or helper function for real-time or streaming scenarios.  
- Provide a **multi-LLM bench** or additional evaluators (PII, security) that follow the same model of reading from `AiCertifyContract` interactions.

For now, this ensures a **clean, generic** pipeline connecting your contract-based data capture to LangFair’s auto-evaluation for Phase 1.

Below is a **consolidated plan** for evaluating **all contract outputs** in a folder that pertain to the **same app** as a **single** aggregated set of prompts and responses, so that **LangFair auto_eval** can process them together. This enables you to produce a single **overall** fairness/bias/toxicity evaluation, rather than multiple disjoint runs.

---

## **1. Rationale and Goals**

1. **Aggregate** interactions from multiple **contract** JSON files (all for the same “app”) into a **single** set of prompts & responses.
2. **Run** a **unified** LangFair evaluation on this combined data, generating a single set of **comprehensive** fairness/auto_eval metrics.
3. **Produce** one consolidated result for a given app, giving you a more **statistically robust** or representative measure of overall performance.

---

## **2. Data Flow Overview**

1. **Identify** a folder (e.g., `./contracts/<app_name>`) that holds many `.json` contract files from the same app.
2. **Load & Filter** these files:
   - Parse each JSON file into an `AiCertifyContract`.
   - Ensure `contract.application_name == <target_app>` (if needed for filtering).
3. **Collect** all `input_text` and `output_text` from **each** contract’s interactions. 
   - Flatten them into a **single** list of prompts and a **single** list of responses.
4. **Create** an **`AutoEvalInput`** object with these aggregated prompts & responses.
5. **Call** the LangFair `evaluate_ai_responses` function once, passing the entire array.
6. **Save** or **log** the resulting `AutoEvalResult` as the aggregated evaluation for that app.

---

## **3. Detailed Steps**

Below is a step-by-step outline of a potential function `evaluate_app_folder` that merges all contract interactions, then runs a **single** LangFair evaluation.

```python
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
from .contract_models import AiCertifyContract
from .langfair_eval import AutoEvalInput
from .langfair_auto_eval import evaluate_ai_responses

logger = logging.getLogger(__name__)

async def evaluate_app_folder(app_name: str, folder_path: str, output_json: str) -> None:
    """
    1) Loads all contract JSON files in folder_path for the specified app_name.
    2) Aggregates prompts & responses from all interactions.
    3) Runs a single LangFair evaluation over the combined data.
    4) Saves the consolidated AutoEvalResult to output_json.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        logger.error(f"Folder {folder_path} does not exist or is not a directory.")
        return

    # Step 1: Gather all .json files
    contract_files = list(folder.glob("*.json"))
    if not contract_files:
        logger.warning(f"No contract JSON files found in {folder_path}")
        return

    # Step 2: Parse + Filter by app_name
    aggregated_prompts = []
    aggregated_responses = []
    total_contract_count = 0

    for cf in contract_files:
        try:
            contract_data = json.loads(cf.read_text())
            contract = AiCertifyContract.parse_obj(contract_data)
            
            # If we strictly only want those matching app_name
            if contract.application_name != app_name:
                logger.debug(f"Skipping contract {cf}, different application_name: {contract.application_name}")
                continue
            
            # Step 3: Collect prompts/responses
            for interaction in contract.interactions:
                aggregated_prompts.append(interaction.input_text)
                aggregated_responses.append(interaction.output_text)

            total_contract_count += 1

        except Exception as e:
            logger.error(f"Error parsing {cf}: {e}")

    if not aggregated_prompts:
        logger.warning(f"No interactions found for app '{app_name}' in {folder_path}.")
        return

    logger.info(f"Collected {len(aggregated_prompts)} total prompts/responses from {total_contract_count} contract(s).")

    # Step 4: Create AutoEvalInput
    auto_eval_input = AutoEvalInput(
        prompts=aggregated_prompts,
        responses=aggregated_responses
    )

    # Step 5: Run LangFair
    logger.info("Running a single auto-eval across all collected data.")
    auto_eval_result = await evaluate_ai_responses(auto_eval_input)

    # Step 6: Save result
    result_dict = auto_eval_result.dict()
    result_dict["combined_contract_count"] = total_contract_count
    result_dict["app_name"] = app_name
    result_dict["evaluation_mode"] = "batch_aggregate"

    with open(output_json, "w") as f:
        json.dump(result_dict, f, indent=2)

    logger.info(f"Aggregated evaluation saved to {output_json} for app '{app_name}'.")
```

### **Explanation**

1. **Load All Contracts**: The function iterates through each JSON in the target folder.  
2. **Filter** by `application_name` if you only want the app you’re evaluating.  
3. **Aggregate** all interactions from these contracts into two big lists:
   - `aggregated_prompts[]`
   - `aggregated_responses[]`
4. **LangFair**: Use these lists to create an `AutoEvalInput` and pass to `evaluate_ai_responses`.  
5. **Save** the final single `AutoEvalResult` in a JSON (or another format).

---

## **4. Handling Edge Cases**

1. **No Contracts**: If no `.json` files are found, log a warning and do nothing.  
2. **Mixed App Names**: Some files might contain other app names. We skip them or unify them if that’s acceptable.  
3. **Large Datasets**: If the number of interactions is very large, consider chunking them or verifying that auto-eval can handle them within memory/time constraints.

---

## **5. Advantages & Next Steps**

- This approach **ensures** that the **LangFair** auto-eval is run **once** for an entire set of scenarios, giving you a single set of metrics for the entire app.  
- If you want to break it down further (e.g., separate scenario groups or time windows), you can partition the contract files into sub-batches.  
- The next step might be to **pass** these metrics to OPA policies or store them in a final compliance record.

---

## **6. Summary**

1. **All contract JSON files** for a given app are aggregated to produce **one** set of `prompts` and `responses`.
2. **LangFair** runs **once**, generating a single set of **fairness**/**toxicity** results for the entire set.  
3. The **plan** is straightforward: gather data → combine → call auto-eval → store results.  

This ensures a **comprehensive** offline/batch evaluation of multiple scenarios, giving a more robust measure of how the AI system performs across a variety of user inputs—**all** via the existing pydantic contract and LangFair auto-eval.