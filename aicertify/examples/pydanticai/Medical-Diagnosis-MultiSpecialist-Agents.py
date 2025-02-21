import os
import argparse
import logging
from datetime import datetime

from dotenv import load_dotenv
from colorama import Fore

from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
from dataclasses import dataclass

# Load environment variables
load_dotenv()

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
You are a highly specialized Cardiologist, trained to assist healthcare professionals and patients in diagnosing, managing, and understanding  cardiovascular diseases. You provide evidence-based recommendations, interpret neurological test results, and suggest treatment pathways in alignment with guidelines from the American Heart Association (AHA) and European Society of Cardiology (ESC).

Take the patient case from the context.

Provide a detailed diagnosis based on the patient's symptoms, medical history, and test results. Include a clear assessment, treatment plan, and prognosis.
"""

neurology_agent_system_prompt = """\
You are a highly specialized Neurologist, trained to assist healthcare professionals and patients in diagnosing, managing, and understanding neurological conditions. You provide evidence-based recommendations, interpret neurological test results, and suggest treatment pathways in alignment with guidelines from the American Academy of Neurology (AAN) and other reputable sources.

Take the patient case from the context.

Provide a detailed diagnosis based on the patient's symptoms, medical history, and test results. Include a clear assessment, treatment plan, and prognosis.
"""

gastroenterology_agent_system_prompt = """\
You are a highly specialized Gastroenterologist, designed to assist healthcare professionals and patients in diagnosing, managing, and understanding gastrointestinal (GI) conditions. You provide evidence-based insights, interpret diagnostic results, and suggest treatment pathways in alignment with guidelines from the American College of Gastroenterology (ACG) and other reputable sources.

Take the patient case from the context.

Provide a detailed diagnosis based on the patient's symptoms, medical history, and test results. Include a clear assessment, treatment plan, and prognosis.
"""

primary_care_agent_system_prompt = """\
You are a Primary Care Physician, acting as an advanced diagnostic assistant capable of analyzing and synthesizing information from various medical specialists to arrive at a detailed, evidence-based final diagnosis. Your role is to function as a primary care physician (PCP) with expertise in integrating findings from cardiologists, neurologists, gastroenterologists and other specialists to provide a holistic assessment of a patient's health.

Take the patient case from the context.

Provide a detailed diagnosis based on the patient's symptoms, medical history, and test results. Include a clear assessment, treatment plan, and prognosis.
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
reasoning_agent = Agent(model=ollama_model, system_prompt=primary_care_agent_system_prompt, deps_type=Deps, retries=5)

# Decorate system prompt to inject patient case context
@primary_care_agent.system_prompt
@cardiology_agent.system_prompt
@neurology_agent.system_prompt
@gastroenterology_agent.system_prompt
def get_system_prompt(ctx: RunContext[Deps]) -> str:
    return f"The patient case is {ctx.deps.case}."

# Define result validators for the agents
'type annotation updated to expect Diagnosis'
@cardiology_agent.result_validator
@neurology_agent.result_validator
@gastroenterology_agent.result_validator
@primary_care_agent.result_validator
def result_validator_deps(ctx: RunContext[Deps], data: Diagnosis) -> Diagnosis:
    if type(data) is not Diagnosis:
        print(Fore.RED, 'Data type mismatch.')
        raise ModelRetry('Return data type mismatch.')
    if ctx.deps.case.patient_id != data.patient_id:
        print(Fore.RED, 'Data content mismatch.', ctx.deps.case.patient_id, data.patient_id)
        raise ModelRetry('Patient ID or Patient name mismatch.')
    return data


def run_session(capture_contract: bool, contract_storage: str) -> None:
    """Run the multi-agent diagnosis session, capture outputs, and optionally generate and save a contract."""
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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
        # Run Neurology Agent
        result = neurology_agent.run_sync(question, deps=deps)
        print(Fore.GREEN, f"Neurology: {result.data.diagnosis}\n")
        message = ModelResponse(parts=[TextPart(content=result.data.diagnosis, part_kind='text')], timestamp=datetime.now().isoformat(), kind='response')
        message_history.append(message)
        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.diagnosis,
            "metadata": {"agent": "Neurology"}
        })

        # Run Gastroenterology Agent
        result = gastroenterology_agent.run_sync(question, deps=deps)
        print(Fore.BLUE, f"Gastroenterology: {result.data.diagnosis}\n")
        message = ModelResponse(parts=[TextPart(content=result.data.diagnosis, part_kind='text')], timestamp=datetime.now().isoformat(), kind='response')
        message_history.append(message)
        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.diagnosis,
            "metadata": {"agent": "Gastroenterology"}
        })

        # Run Cardiology Agent
        result = cardiology_agent.run_sync(question, deps=deps)
        print(Fore.RED, f"Cardiology: {result.data.diagnosis}\n")
        message = ModelResponse(parts=[TextPart(content=result.data.diagnosis, part_kind='text')], timestamp=datetime.now().isoformat(), kind='response')
        message_history.append(message)
        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.diagnosis,
            "metadata": {"agent": "Cardiology"}
        })

        # Run Primary Care Agent
        result = primary_care_agent.run_sync(question, deps=deps)
        print(Fore.YELLOW, f"Primary care: {result.data.diagnosis}\n")
        message = ModelResponse(parts=[TextPart(content=result.data.diagnosis, part_kind='text')], timestamp=datetime.now().isoformat(), kind='response')
        message_history.append(message)
        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.diagnosis,
            "metadata": {"agent": "Primary Care"}
        })

        # Run Reasoning Agent with message history
        result = reasoning_agent.run_sync(question, deps=deps, message_history=message_history)
        print(Fore.WHITE, '-----------------------------------')
        print(Fore.WHITE, f"Final report: {result.data}")
        print(Fore.WHITE, '-----------------------------------')
        captured_interactions.append({
            "input_text": question,
            "output_text": str(result.data),
            "metadata": {"agent": "Reasoning"}
        })

    except ModelRetry as e:
        print(Fore.RED, e)
    except Exception as e:
        print(Fore.RED, e)

    # If contract capture is enabled, create and save a contract
    if capture_contract:
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
    parser = argparse.ArgumentParser(description="Demo for Medical Diagnosis Session with Contract Capture")
    parser.add_argument('--capture-contract', action='store_true', help="Capture outputs to generate a contract for evaluation")
    parser.add_argument('--contract-storage', type=str, default='contracts', help="Directory to store generated contract files")
    args = parser.parse_args()

    run_session(capture_contract=args.capture_contract, contract_storage=args.contract_storage)


if __name__ == "__main__":
    main() 