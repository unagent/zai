import json, os
import warnings

def load_config(path=None):
    """Load configuration from config.json file"""
    if path is None:
        path = 'config.json'
    with open(path) as f:
        config = json.load(f)

    # Environment variables take precedence over config file
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_API_URL": os.getenv("OPENAI_API_URL"),
        "OPENAI_API_MODEL": os.getenv("OPENAI_API_MODEL")
    }
    
    for key, value in env_vars.items():
        if value and key not in config:
            config[key] = value

    if config['OPENAI_API_URL'].endswith('/v1'):
        warnings.warn("OPENAI_API_URL should end with '/v1' for API compatibility")

    return config
