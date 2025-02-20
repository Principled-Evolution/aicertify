# Evaluate all AI apps in the logs directory
python -m aicertify.cli.evaluate evaluate --log-dir ./logs

# Evaluate specific AI system
python -m aicertify.cli.evaluate evaluate --log-dir ./logs --system-name CareerCoachAI

# Evaluate recent interactions
python -m aicertify.cli.evaluate evaluate --log-dir ./logs --days 7

# Save results to custom directory
python -m aicertify.cli.evaluate evaluate --log-dir ./logs --output ./evaluations