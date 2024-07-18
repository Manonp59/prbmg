from api_ia.model.training import training
import sys 
from datetime import datetime



n_cluster = 30

# Access the arguments
run_name = f"kmeans_{n_cluster}"

# Call the training function with the provided run name
training(run_name)