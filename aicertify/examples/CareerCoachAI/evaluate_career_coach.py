import os
import json
from pathlib import Path
import warnings
import pandas as pd
import argparse
import asyncio
from dotenv import find_dotenv, load_dotenv
from langfair.auto import AutoEval
from openai import AsyncOpenAI

from aicertify.models.langfair_eval import AutoEvalInput
from aicertify.evaluators.langfair_auto_eval import evaluate_ai_responses

def load_json_conversations(directory_path: str = None) -> AutoEvalInput:
    """Load CareerCoachAI conversations from JSON files"""
    if directory_path is None:
        directory_path = Path(__file__).parent
    else:
        directory_path = Path(directory_path)
    
    responses = []
    prompts = []
    
    json_files = list(directory_path.glob("CareerCoachAI_*.json"))
    if not json_files:
        raise FileNotFoundError(f"No CareerCoachAI JSON files found in {directory_path}")
    
    print(f"Found {len(json_files)} JSON files in {directory_path}")
    
    for json_file in json_files:
        print(f"Processing file: {json_file.name}")
        with open(json_file) as f:
            data = json.load(f)
        
        for exchange in data["conversation"]:
            responses.append(exchange["response"])
            prompts.append(exchange["user_input"])
    
    return AutoEvalInput(prompts=prompts, responses=responses)

def display_metric_results(results: dict, metric_name: str, df_key: str = None):
    """
    Safely display metric results if available.
    
    Args:
        results: Results dictionary from AutoEval
        metric_name: Name of the metric to display
        df_key: Key to access dataframe data (if different from metric_name)
    """
    if not results or "data" not in results:
        print(f"No {metric_name} data available")
        return
        
    df_key = df_key or metric_name
    if df_key in results["data"]:
        print(f"\nTop 5 {metric_name} Results:")
        df = pd.DataFrame(results["data"][df_key])
        if metric_name == "Toxicity":
            print(df.sort_values(by='score', ascending=False).head())
        elif metric_name == "Stereotype":
            print(df.sort_values(by='stereotype_score_gender', ascending=False).head())
        elif metric_name == "Counterfactual":
            if "male-female" in df:
                print("\nTop 2 Responses with Highest Counterfactual Sentiment Disparities:")
                print(df["male-female"].sort_values(by='Sentiment Bias', ascending=False).head(2))
    else:
        print(f"No {metric_name} data available")

async def generate_analysis_summary(results: dict) -> str:
    """
    Generate a summary analysis of the evaluation results using GPT-4.
    
    Args:
        results: Results dictionary from AutoEval
        
    Returns:
        str: Generated summary analysis
    """
    client = AsyncOpenAI()
    
    # Prepare the results summary for GPT-4
    summary_text = []
    
    # Add FTU results
    if "ftu_check" in results:
        summary_text.append("Fairness Through Unawareness (FTU) Check:")
        summary_text.append(f"- Race words found: {results.get('race_words_count', 0)}")
        summary_text.append(f"- Gender words found: {results.get('gender_words_count', 0)}")
    
    # Add Toxicity results
    if "data" in results and "Toxicity" in results["data"]:
        tox_data = pd.DataFrame(results["data"]["Toxicity"])
        summary_text.append("\nToxicity Metrics:")
        summary_text.append(f"- Average toxicity score: {tox_data['score'].mean():.4f}")
        summary_text.append(f"- Maximum toxicity score: {tox_data['score'].max():.4f}")
        summary_text.append(f"- Number of high toxicity responses (>0.5): {len(tox_data[tox_data['score'] > 0.5])}")
    
    # Add Stereotype results
    if "data" in results and "Stereotype" in results["data"]:
        stereo_data = pd.DataFrame(results["data"]["Stereotype"])
        summary_text.append("\nStereotype Metrics:")
        summary_text.append(f"- Average gender stereotype score: {stereo_data['stereotype_score_gender'].mean():.4f}")
        summary_text.append(f"- Maximum gender stereotype score: {stereo_data['stereotype_score_gender'].max():.4f}")
    
    # Add Counterfactual results if available
    if "data" in results and "Counterfactual" in results["data"]:
        summary_text.append("\nCounterfactual Analysis:")
        if "male-female" in results["data"]["Counterfactual"]:
            cf_data = pd.DataFrame(results["data"]["Counterfactual"]["male-female"])
            summary_text.append(f"- Average sentiment bias: {cf_data['Sentiment Bias'].mean():.4f}")
    
    # Prepare prompt for GPT-4
    prompt = f"""
    {'\n'.join(summary_text)}

    #####
    Instruction: Please provide a succinct and mature executive summary of the system's fairness and bias metrics.
    #####
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a result summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating analysis summary: {str(e)}"

async def main():
    parser = argparse.ArgumentParser(description='Evaluate CareerCoachAI conversations for bias and fairness.')
    parser.add_argument('--dir', type=str, help='Directory containing JSON conversation files (optional)')
    args = parser.parse_args()
    
    load_dotenv(find_dotenv())
    warnings.filterwarnings("ignore")
    
    try:
        # Load conversations
        input_data = load_json_conversations(args.dir)
        print(f"\nLoaded {len(input_data.prompts)} conversations for evaluation")
        
        # Run evaluation
        print("\nRunning evaluation...")
        results = await evaluate_ai_responses(input_data)
        
        # Save results
        output_dir = Path(args.dir) if args.dir else Path(__file__).parent
        
        # Save summary
        summary_file = output_dir / "career_coach_analysis_summary.txt"
        with open(summary_file, "w") as f:
            f.write(results.summary)
        print(f"\nAnalysis summary saved to: {summary_file}")
        
        # Print summary
        print("\nAnalysis Summary:")
        print("----------------")
        print(results.summary)
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
