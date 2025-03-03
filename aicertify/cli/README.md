# Evaluate all AI apps in the logs directory
python -m aicertify.cli.evaluate evaluate --log-dir ./logs

# Evaluate specific AI system
python -m aicertify.cli.evaluate evaluate --log-dir ./logs --system-name CareerCoachAI

# Evaluate recent interactions
python -m aicertify.cli.evaluate evaluate --log-dir ./logs --days 7

# Save results to custom directory
python -m aicertify.cli.evaluate evaluate --log-dir ./logs --output ./evaluations

poetry run python cli\cli.py eval-folder --app-name "CareerCoachAI Interactive Session" --folder examples\pydanticai\contracts\. --output examples\pydanticai\eval_outputs\

poetry run python cli\cli.py eval-policy --input '.\examples\pydanticai\eval_outputs\consolidated_evaluation_CareerCoachAI Interactive Session2025-02-20_160855.json' --category compliance\fairness

poetry run python cli\cli.py eval-all --app-name "CareerCoachAI Interactive Session" --folder .\examples\pydanticai\contracts\ --output consolidated_eval.json --category compliance\fairness 
