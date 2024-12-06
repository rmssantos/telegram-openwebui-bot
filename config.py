from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ['API_KEY']
OPENWEBUI_API_KEY = os.environ['OPENWEBUI_API_KEY']
OPENWEBUI_BASE_URL = os.environ['OPENWEBUI_BASE_URL']
MODEL_NAME = os.environ.get('MODEL_NAME', 'neon-nomad')
MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 500))
TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.7))
KNOWLEDGE_BASE_ID = os.environ.get('KNOWLEDGE_BASE_ID', '662306b6-1dea-441e-b571-7cb121a5e371')
HISTORY_LENGTH = int(os.environ.get('HISTORY_LENGTH', 10))
KEYWORD = os.environ.get('KEYWORD', 'seedify')
