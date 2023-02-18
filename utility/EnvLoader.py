from dotenv import load_dotenv
from pathlib import Path


def load_env_file(env_path='./env/.env'):
    env_path = Path(env_path)
    load_dotenv(dotenv_path=env_path)

