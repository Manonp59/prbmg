from hydra import compose, initialize

with initialize(version_base="1.2", config_path="./configs/"):
    cfg = compose(config_name="params.yaml")