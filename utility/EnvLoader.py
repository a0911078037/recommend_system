import yaml


def load_env_file(env_path='./env/api_config.yml'):
    with open(env_path, 'r') as f:
        config = yaml.safe_load(f)
    if not config:
        raise Exception('env file not found')
    return config

