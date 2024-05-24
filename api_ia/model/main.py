from api_ia.model.training import training
import argparse

# Create an argument parser
parser = argparse.ArgumentParser(description="Run training with specified run name")

# Define the run_name argument
parser.add_argument('run_name', type=str, help='The name of the run')

# Parse the command-line arguments
args = parser.parse_args()

# Access the arguments
run_name = args.run_name

# Call the training function with the provided run name
training(run_name)