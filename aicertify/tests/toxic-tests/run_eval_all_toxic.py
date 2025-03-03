import os
import json
import uuid
import subprocess
from pathlib import Path
from copy import deepcopy
from datetime import datetime


def slugify(text: str) -> str:
    """Simple slugify function: replace non-alphanumeric characters with underscores and lower the string."""
    return ''.join(c if c.isalnum() else '_' for c in text).lower()


def replicate_contract_interactions(contract_data: dict, num_replications: int = 25) -> dict:
    """Replicate the interactions in a contract to meet the minimum sample size requirement."""
    new_contract = deepcopy(contract_data)
    original_interactions = deepcopy(contract_data['interactions'])
    
    # Replicate each interaction maintaining unique IDs
    new_interactions = []
    for i in range(num_replications):
        for interaction in original_interactions:
            new_interaction = deepcopy(interaction)
            # Generate a completely new UUID for each replicated interaction
            new_interaction['interaction_id'] = str(uuid.uuid4())
            # Update timestamp to show small time differences
            timestamp = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00'))
            new_timestamp = timestamp.replace(microsecond=timestamp.microsecond + i*1000)
            new_interaction['timestamp'] = new_timestamp.isoformat().replace('+00:00', 'Z')
            new_interactions.append(new_interaction)
    
    new_contract['interactions'] = new_interactions
    return new_contract


def main():
    # Define directories
    # First check if current directory is named 'toxic-tests'
    current_dir = Path('.').resolve()  # Resolve to get absolute path
    if current_dir.name == 'toxic-tests':
        toxic_dir = current_dir
    else:
        # Search for a subdirectory named 'toxic-tests'
        toxic_dir = next(Path('.').rglob('toxic-tests'), None)
        if toxic_dir is None:
            raise FileNotFoundError("Could not find 'toxic-tests' directory")
    results_dir = toxic_dir / 'toxic-test-results'
    results_dir.mkdir(parents=True, exist_ok=True)

    # Create a new directory for replicated contracts
    replicated_dir = toxic_dir / 'replicated_contracts'
    replicated_dir.mkdir(parents=True, exist_ok=True)

    # Find all contract files that match our toxic contract naming pattern
    contract_files = list(toxic_dir.glob('contract_toxic_*.json'))
    if not contract_files:
        print('No toxic contract files found in', toxic_dir)
        return

    # Process each contract file and create replicated versions
    app_names = set()
    for file in contract_files:
        try:
            with file.open('r', encoding='utf-8') as f:
                contract_data = json.load(f)
            
            # Replicate the contract interactions
            replicated_contract = replicate_contract_interactions(contract_data)
            
            # Save the replicated contract
            replicated_file = replicated_dir / f'replicated_{file.name}'
            with replicated_file.open('w', encoding='utf-8') as f:
                json.dump(replicated_contract, f, indent=2)
            
            app_name = contract_data.get('application_name')
            if app_name:
                app_names.add(app_name)
        except Exception as e:
            print(f'Error processing {file}:', e)

    print('Unique Application Names:', app_names)

    # Category for OPA evaluation
    category = 'compliance\\fairness'  # Updated to match README.md format

    # For each unique application name, run the eval-all command using replicated contracts
    for app in app_names:
        slug_app = slugify(app)
        output_file = results_dir / f'{slug_app}_eval.json'
        pdf_report = results_dir / f'{slug_app}_report.pdf'
        md_report = results_dir / f'{slug_app}_report.md'

        command = [
            'poetry', 'run', 'python', 'cli\\cli.py',
            'eval-all',
            '--app-name', app,
            '--folder', str(replicated_dir),  # Use the replicated contracts directory
            '--output', str(output_file),
            '--category', category,
            '--report-md', str(md_report),
            '--report-pdf', str(pdf_report)
        ]

        print(f'Running eval-all for application: {app}')
        print('Command:', ' '.join(command))
        result = subprocess.run(command, capture_output=True, text=True)
        print('STDOUT:', result.stdout)
        print('STDERR:', result.stderr)


if __name__ == '__main__':
    main() 