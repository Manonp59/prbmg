from api_ia.model.training import training
from config import cfg
from datetime import datetime



n_cluster = cfg.model.n_clusters

# Access the arguments
run_name = f"kmeans_{n_cluster}"

# Call the training function with the provided run name
training(run_name)