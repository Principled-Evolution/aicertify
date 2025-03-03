import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
from datetime import datetime, timedelta

from ..models.langfair_eval import AutoEvalInput
from ..models.evaluation_models import (
    BehaviorEvaluation,
    SystemType,
    SystemInteraction
)
from ..evaluators.langfair_auto_eval import evaluate_ai_responses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_interaction_logs(
    log_dir: Path,
    system_name: Optional[str] = None,
    days: Optional[int] = None
) -> List[SystemInteraction]:
    """
    Load interaction logs from any AI app using our decorators.
    
    Args:
        log_dir: Directory containing logs
        system_name: Optional filter for specific AI system
        days: Optional filter for recent days
    """
    interactions = []
    cutoff_date = datetime.now() - timedelta(days=days) if days else None
    
    logger.info(f"Scanning {log_dir} for interaction logs...")
    
    # Handle both JSONL (streaming) and JSON (batch) logs
    for file_path in log_dir.glob("**/*.[jJ][sS][oO][nN]*"):
        try:
            if file_path.suffix.lower() == '.jsonl':
                # Handle streaming logs
                with open(file_path) as f:
                    for line in f:
                        interaction = json.loads(line)
                        if _should_include_interaction(interaction, system_name, cutoff_date):
                            interactions.append(SystemInteraction(**interaction))
            else:
                # Handle batch logs
                with open(file_path) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # Multiple interactions in one file
                        for interaction in data:
                            if _should_include_interaction(interaction, system_name, cutoff_date):
                                interactions.append(SystemInteraction(**interaction))
                    else:
                        # Single interaction or different format
                        if _should_include_interaction(data, system_name, cutoff_date):
                            interactions.append(SystemInteraction(**data))
                            
        except Exception as e:
            logger.warning(f"Error processing {file_path}: {str(e)}")
            continue
    
    logger.info(f"Loaded {len(interactions)} interactions")
    return interactions

def _should_include_interaction(
    interaction: Dict[str, Any],
    system_name: Optional[str],
    cutoff_date: Optional[datetime]
) -> bool:
    """Determine if an interaction should be included based on filters"""
    if system_name and interaction.get('system_name') != system_name:
        return False
        
    if cutoff_date:
        interaction_date = datetime.fromisoformat(interaction.get('timestamp', '').replace('Z', '+00:00'))
        if interaction_date < cutoff_date:
            return False
            
    return True

def prepare_eval_input(interactions: List[SystemInteraction]) -> AutoEvalInput:
    """Convert interactions to evaluation input format"""
    prompts = []
    responses = []
    
    for interaction in interactions:
        # Extract text content from input/output media
        input_text = next(
            (m.content_data for m in interaction.input_media 
             if m.media_type.value == "text"), None
        )
        output_text = next(
            (m.content_data for m in interaction.output_media 
             if m.media_type.value == "text"), None
        )
        
        if input_text and output_text:
            prompts.append(input_text)
            responses.append(output_text)
    
    return AutoEvalInput(prompts=prompts, responses=responses)

@click.group()
def cli():
    """AICertify evaluation tools"""
    pass

@cli.command()
@click.option('--log-dir', type=click.Path(exists=True), help='Directory containing interaction logs')
@click.option('--system-name', help='Filter by system name')
@click.option('--days', type=int, help='Evaluate only recent days')
@click.option('--output', type=click.Path(), help='Output directory for evaluation results')
async def evaluate(log_dir: str, system_name: str, days: int, output: str):
    """Evaluate AI system interactions for fairness and safety"""
    try:
        # Load interactions
        interactions = load_interaction_logs(
            Path(log_dir),
            system_name,
            days
        )
        
        if not interactions:
            logger.error("No interactions found matching criteria")
            return
            
        # Prepare evaluation input
        eval_input = prepare_eval_input(interactions)
        
        # Run evaluation
        logger.info("Running evaluation...")
        results = await evaluate_ai_responses(eval_input)
        
        # Save results
        output_path = Path(output) if output else Path(log_dir) / "evaluations"
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        system_prefix = f"{system_name}_" if system_name else ""
        
        # Save detailed results
        results_file = output_path / f"{system_prefix}evaluation_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(results.model_dump(), f, indent=2, default=str)
            
        # Save summary
        summary_file = output_path / f"{system_prefix}summary_{timestamp}.txt"
        with open(summary_file, "w") as f:
            f.write(results.summary)
            
        logger.info(f"Evaluation results saved to: {output_path}")
        
        # Print summary
        click.echo("\nEvaluation Summary:")
        click.echo("-------------------")
        click.echo(results.summary)
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise

if __name__ == "__main__":
    cli() 