from training import training
import argparse

# Create an argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument('run_name')
parser.add_argument('start_date')   
parser.add_argument('end_date')

# Parse the command-line arguments
args = parser.parse_args()

# Access the arguments
run_name = args.run_name
start_date = args.start_date
end_date = args.end_date

training(run_name,start_date,end_date)