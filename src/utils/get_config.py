import yaml
from src.utils.logger import get_logger
logger = get_logger(__name__)

def get_config(config_file: str, target_config: str):
    try:    
        with open(config_file) as file:
            config = yaml.safe_load(file)
        return config.get(target_config)
    except Exception as e:
        logger.error(f"Problem occured while reading from {config_file}: {e}")
        raise