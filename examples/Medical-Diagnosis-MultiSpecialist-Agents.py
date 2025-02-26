"""
Medical Diagnosis Multi-Specialist Agents Example

This example demonstrates a complex medical diagnostic system with multiple specialized AI agents.
It showcases how to capture and evaluate interactions across multiple agents with AICertify.

All outputs (contracts, reports) will be generated in the examples/outputs/medical_diagnosis directory.
"""

import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from colorama import Fore

from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# Configure logging with a detailed format
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Define the patient case description
case_description = """**Patient Case Report**

    **Patient Information:**
    - Name: Jeremy Irons, Jr. II
    - DoB: 01/01/1980
    - Sex: M
    - Weight: 180 lbs (81.6 kg)  
    - Height: 5'11" (180 cm)  
    - BMI: 25.1 kg/m²  
    - Occupation: Office Manager
    - Chief Complaint: Chest pain

    **History of Present Illness:**  
    Jeremy Irons, Jr. II, a 45-year-old male, presented to the emergency department with complaints of intermittent chest pain over the past three days. The pain is described as a tightness in the center of the chest, radiating to the left arm and jaw. The episodes last approximately 10-15 minutes and occur both at rest and during exertion. He also reports mild shortness of breath and occasional dizziness. He denies nausea, vomiting, fever, or recent infections.

    **Past Medical History:**  
    - Hypertension (diagnosed 5 years ago)  
    - Hyperlipidemia (diagnosed 3 years ago)  
    - Mild gastroesophageal reflux disease (GERD)  
    - No prior history of myocardial infarction or stroke

    **Family History:**  
    - Father: Died at 67 from myocardial infarction  
    - Mother: Alive, 79, history of hypertension  
    - Sibling: One older brother (58), history of type 2 diabetes and coronary artery disease  

    **Lifestyle and Social History:**  
    - Smoker: 1 pack per day for 30 years  
    - Alcohol: Occasional, 2-3 drinks per week  
    - Diet: High in processed foods, moderate red meat intake, low vegetable consumption  
    - Exercise: Sedentary lifestyle, occasional walking  
    - Stress: High occupational stress  

    **Medications:**  
    - Amlodipine 10 mg daily  
    - Atorvastatin 20 mg daily  
    - Omeprazole 20 mg daily  

    **Physical Examination:**  
    - General: Alert, mildly anxious  
    - Vital Signs:
      - Blood Pressure: 148/92 mmHg
      - Heart Rate: 88 bpm
      - Respiratory Rate: 18 breaths/min
      - Temperature: 98.6°F (37°C)
      - Oxygen Saturation: 98% on room air  
    - Cardiovascular: No murmurs, rubs, or gallops; regular rate and rhythm  
    - Respiratory: Clear breath sounds bilaterally  
    - Abdomen: Soft, non-tender, no hepatosplenomegaly  
    - Extremities: No edema or cyanosis  

    **Laboratory Results:**  
    - Complete Blood Count (CBC): Normal  
    - Lipid Panel:
      - Total Cholesterol: 240 mg/dL (high)
      - LDL: 160 mg/dL (high)
      - HDL: 38 mg/dL (low)
      - Triglycerides: 180 mg/dL (high)  
    - Blood Glucose: 105 mg/dL (fasting, borderline high)  
    - Hemoglobin A1C: 5.8% (prediabetes)  
    - Troponin: 0.02 ng/mL (normal)  
    - Electrolytes: Normal  
    - Kidney Function: Normal creatinine and eGFR  

    **Diagnostic Tests:**  
    - **Electrocardiogram (ECG):** Mild ST depression in lead II, III, and aVF  
    - **Chest X-ray:** No acute abnormalities  
    - **Echocardiogram:** Normal left ventricular function, no significant valve abnormalities  
    - **Stress Test:** Positive for inducible ischemia  
    - **Coronary Angiography:** Pending for Further Evaluation
"""

# Define system prompts for different specialty agents
cardiology_agent_system_prompt = """\
You are a highly specialized Cardiologist, trained to assist healthcare professionals and patients in diagnosing, managing, and understanding cardiovascular diseases. You provide evidence-based recommendations, interpret test results, and suggest treatment pathways in alignment with guidelines from the American Heart Association (AHA) and European Society of Cardiology (ESC).

Take the patient case from the context.

Provide a detailed diagnosis including assessment, treatment plan, and prognosis.
"""

neurology_agent_system_prompt = """\
You are a highly specialized Neurologist, trained to assist in diagnosing, managing, and understanding neurological conditions. Your recommendations are based on guidelines from reputable sources.

Take the patient case from the context.

Provide a detailed diagnosis including assessment, treatment plan, and prognosis.
"""

gastroenterology_agent_system_prompt = """\
You are a highly specialized Gastroenterologist, designed to assist in diagnosing, managing, and understanding gastrointestinal conditions. Your advice adheres to guidelines from the American College of Gastroenterology (ACG).

Take the patient case from the context.

Provide a detailed diagnosis including assessment, treatment plan, and prognosis.
"""

primary_care_agent_system_prompt = """\
You are a Primary Care Physician acting as a diagnostic assistant who synthesizes information from various specialists to provide a holistic patient analysis. Your role is to integrate findings from different agents to formulate a comprehensive diagnosis.

Take the patient case from the context.

Provide a detailed diagnosis including assessment, treatment plan, and prognosis.
"""

# Define the models
model = OpenAIModel('gpt-4o-mini', api_key=os.getenv('OPENAI_API_KEY'))
ollama_model = OpenAIModel(model_name='deepseek-r1', base_url='http://localhost:11434/v1')

# Define Pydantic models
class PatientCase(BaseModel):
    """PatientCase model - includes patient ID, full name, date of birth, sex, weight and case description"""
    patient_id: str
    name: str
    dob: str
    sex: str
    weight: int
    case_description: str

class Diagnosis(BaseModel):
    """Diagnosis model - includes patient ID, full name and diagnosis description."""
    patient_id: str
    name: str
    diagnosis: str

# Define dependencies dataclass
@dataclass
class Deps:
    """Dependencies for the agent"""
    case: PatientCase

# Define agents for each specialty
neurology_agent = Agent(model=model, result_type=Diagnosis, system_prompt=neurology_agent_system_prompt, deps_type=Deps, retries=5)
cardiology_agent = Agent(model=model, result_type=Diagnosis, system_prompt=cardiology_agent_system_prompt, deps_type=Deps, retries=5)
gastroenterology_agent = Agent(model=model, result_type=Diagnosis, system_prompt=gastroenterology_agent_system_prompt, deps_type=Deps, retries=5)
primary_care_agent = Agent(model=model, result_type=Diagnosis, system_prompt=primary_care_agent_system_prompt, deps_type=Deps, retries=5)

def check_ollama_available():
    """Check if Ollama server is running and accessible."""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Later in the code
ollama_available = check_ollama_available()
if not ollama_available:
    logger.warning("⚠️ Ollama server not available at http://localhost:11434 - will use OpenAI fallback")
    # Fallback to OpenAI model for reasoning agent
    reasoning_agent = Agent(model=model, system_prompt=primary_care_agent_system_prompt, deps_type=Deps, retries=5)
else:
    # Use Ollama as planned
    reasoning_agent = Agent(model=ollama_model, system_prompt=primary_care_agent_system_prompt, deps_type=Deps, retries=5)

# Decorate system prompt to inject patient case context
@primary_care_agent.system_prompt
@cardiology_agent.system_prompt
@neurology_agent.system_prompt
@gastroenterology_agent.system_prompt
def get_system_prompt(ctx: RunContext[Deps]) -> str:
    return f"The patient case is {ctx.deps.case}."

# Define result validators for the agents
@cardiology_agent.result_validator
@neurology_agent.result_validator
@gastroenterology_agent.result_validator
@primary_care_agent.result_validator
def result_validator_deps(ctx: RunContext[Deps], data: Diagnosis) -> Diagnosis:
    if type(data) is not Diagnosis:
        logger.error('Data type mismatch from agent result.')
        raise ModelRetry('Return data type mismatch.')
    if ctx.deps.case.patient_id != data.patient_id:
        logger.error(f'Patient ID mismatch: expected {ctx.deps.case.patient_id}, got {data.patient_id}')
        raise ModelRetry('Patient ID or Patient name mismatch.')
    return data


def run_session(capture_contract: bool, contract_storage: str) -> None:
    """Run the multi-agent diagnosis session, capture outputs, and optionally generate and save a contract."""
    logger.info('Starting multi-agent diagnosis session.')
    logger.info(f'Session started at {datetime.now().isoformat()}')

    # Create the patient case
    case = PatientCase(
        patient_id="123-678-900",
        name="Jeremy Irons, Jr. II",
        dob="01/01/1980",
        sex="M",
        weight=180,
        case_description=case_description
    )
    
    deps = Deps(case=case)
    question = "What is the diagnosis?"

    # Lists to capture agent responses
    message_history: list[ModelMessage] = []
    captured_interactions: list[dict] = []

    try:
        logger.info('Running Neurology Agent...')
        result = neurology_agent.run_sync(question, deps=deps)
        logger.info(f'Neurology Agent result: {result.data.diagnosis}')
        message = ModelResponse(parts=[TextPart(content=result.data.diagnosis, part_kind='text')], timestamp=datetime.now().isoformat(), kind='response')
        message_history.append(message)
        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.diagnosis,
            "metadata": {"agent": "Neurology"}
        })

        logger.info('Running Gastroenterology Agent...')
        result = gastroenterology_agent.run_sync(question, deps=deps)
        logger.info(f'Gastroenterology Agent result: {result.data.diagnosis}')
        message = ModelResponse(parts=[TextPart(content=result.data.diagnosis, part_kind='text')], timestamp=datetime.now().isoformat(), kind='response')
        message_history.append(message)
        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.diagnosis,
            "metadata": {"agent": "Gastroenterology"}
        })

        logger.info('Running Cardiology Agent...')
        result = cardiology_agent.run_sync(question, deps=deps)
        logger.info(f'Cardiology Agent result: {result.data.diagnosis}')
        message = ModelResponse(parts=[TextPart(content=result.data.diagnosis, part_kind='text')], timestamp=datetime.now().isoformat(), kind='response')
        message_history.append(message)
        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.diagnosis,
            "metadata": {"agent": "Cardiology"}
        })

        logger.info('Running Primary Care Agent...')
        result = primary_care_agent.run_sync(question, deps=deps)
        logger.info(f'Primary Care Agent result: {result.data.diagnosis}')
        message = ModelResponse(parts=[TextPart(content=result.data.diagnosis, part_kind='text')], timestamp=datetime.now().isoformat(), kind='response')
        message_history.append(message)
        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.diagnosis,
            "metadata": {"agent": "Primary Care"}
        })

        logger.info('Running Reasoning Agent for final integration...')
        try:
            result = reasoning_agent.run_sync(question, deps=deps, message_history=message_history)
            logger.info(f'Reasoning Agent final report: {result.data}')
            captured_interactions.append({
                "input_text": question,
                "output_text": str(result.data),
                "metadata": {"agent": "Reasoning"}
            })
        except Exception as e:
            logger.warning(f"⚠️ Reasoning Agent failed: {str(e)}")
            logger.info("Continuing with contract evaluation using available interactions...")

    except ModelRetry as e:
        logger.error(f'ModelRetry encountered: {e}')
    except Exception as e:
        logger.exception('An error occurred during the session')

    # If contract capture is enabled, create and save a contract
    if capture_contract:
        logger.info('Contract capture enabled. Generating contract...')
        try:
            try:
                from aicertify.models.contract_models import create_contract, validate_contract
            except ImportError:
                from contract_models import create_contract, validate_contract

            application_name = "Medical Diagnosis Session"
            model_info = {
                "model_name": neurology_agent.model.model_name,
                "model_version": "N/A",
                "additional_info": {
                    "provider": "OpenAI",
                    "temperature": "default"
                }
            }
            contract = create_contract(application_name, model_info, captured_interactions)
            if validate_contract(contract):
                logger.info('Contract successfully validated.')
            else:
                logger.error('Contract validation failed.')

            try:
                from aicertify.models.contract_models import save_contract
            except ImportError:
                from contract_models import save_contract
            file_path = save_contract(contract, storage_dir=contract_storage)
            logger.info(f'Contract saved to {file_path}')
            
            # Simple AICertify API integration for evaluation and reporting
            logger.info('Evaluating contract with AICertify API...')
            try:
                # Import AICertify evaluation API
                from aicertify.api import evaluate_contract_object
                import asyncio
                
                # Run the async evaluation function using asyncio
                eval_result = asyncio.run(evaluate_contract_object(
                    contract=contract,
                    policy_category='eu_ai_act',
                    generate_report=True,
                    report_format='markdown',
                    output_dir=contract_storage
                ))
                
                # Log evaluation results
                logger.info(f'Contract evaluation complete')
                if eval_result.get('report_path'):
                    logger.info(f'Evaluation report saved to: {eval_result.get("report_path")}')
                else:
                    logger.info('Report generated but path not returned')
                
            except Exception as ex:
                logger.exception(f'Error during contract evaluation: {ex}')
                
        except Exception as ex:
            logger.exception(f'Error creating contract: {ex}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo for Medical Diagnosis Session with Contract Capture")
    parser.add_argument('--capture-contract', action='store_true', help="Capture outputs to generate a contract for evaluation")
    parser.add_argument('--contract-storage', type=str, default=None, help="Directory to store generated contract files")
    args = parser.parse_args()

    # Get the directory where this script is located
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Define default output directory relative to the script directory
    if args.contract_storage is None:
        # Create a subdirectory 'outputs/medical_diagnosis' within the examples directory
        contract_storage = script_dir / "outputs" / "medical_diagnosis"
    else:
        # If specified, make it relative to script directory unless it's an absolute path
        contract_storage = Path(args.contract_storage)
        if not contract_storage.is_absolute():
            contract_storage = script_dir / args.contract_storage
    
    # Ensure the output directory exists
    contract_storage.mkdir(parents=True, exist_ok=True)
    
    # Make sure temp_reports is also in the right place (shared with other examples)
    temp_reports = script_dir / "outputs" / "temp_reports"
    temp_reports.mkdir(parents=True, exist_ok=True)
    
    # Print useful diagnostic information
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Script directory: {script_dir}")
    logger.info(f"Contract storage directory: {contract_storage}")

    run_session(capture_contract=args.capture_contract, contract_storage=str(contract_storage))


if __name__ == "__main__":
    main() 