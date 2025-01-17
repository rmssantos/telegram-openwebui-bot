# config.py

from dotenv import load_dotenv
import os
import sys
import logging

# Load environment variables from a .env file
load_dotenv()

# --- Basic Configuration Constants ---
API_KEY = os.environ.get('API_KEY')
OPENWEBUI_API_KEY = os.environ.get('OPENWEBUI_API_KEY')
OPENWEBUI_BASE_URL = os.environ.get('OPENWEBUI_BASE_URL')
MODEL_NAME = os.environ.get('MODEL_NAME', 'default-model')
MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 500))
TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.7))
HISTORY_LENGTH = int(os.environ.get('HISTORY_LENGTH', 10))

# --- Persistence and Rotation Settings ---
ROTATION_THRESHOLD_HOURS = int(os.environ.get('ROTATION_THRESHOLD_HOURS', 6))
MAX_GROUP_MESSAGES = int(os.environ.get('MAX_GROUP_MESSAGES', 1000))
PERSIST_INTERVAL = int(os.environ.get('PERSIST_INTERVAL', 30))  # in seconds
MAX_CHANGES_BEFORE_PERSIST = int(os.environ.get('MAX_CHANGES_BEFORE_PERSIST', 5))

# --- Summarization Settings ---
SUMMARIZATION_HOURS = int(os.getenv('SUMMARIZATION_HOURS', 6))  # Default: 6 hours

# --- Cooldown Settings ---
COOLDOWN_MINUTES = int(os.getenv("COOLDOWN_MINUTES", 10))  # Default: 10 minutes

# --- Bing Grounding Search Settings ---
BING_GROUNDING_API_KEY = os.getenv("BING_GROUNDING_API_KEY")
BING_GROUNDING_ENDPOINT = os.getenv("BING_GROUNDING_ENDPOINT")

# --- Knowledge Base Mappings ---
KB_MAPPINGS = {
    'examplekeyword': os.environ.get('EXAMPLE_KB_ID', 'your-example-kb-id'),
    'examplekeyword2': os.environ.get('EXAMPLE_KB_ID2', 'your-example-kb-id2'),
    # Add more keyword-KB mappings as needed
}

# --- Chunk Processing ---
BASE_CHUNK_SIZE = int(os.getenv("BASE_CHUNK_SIZE", 4000))  # Default to 4000 characters

# --- Critical Configuration Validation ---
critical_vars = [
    ('API_KEY', API_KEY),
    ('OPENWEBUI_API_KEY', OPENWEBUI_API_KEY),
    ('OPENWEBUI_BASE_URL', OPENWEBUI_BASE_URL),
]

# Check for missing critical environment variables
missing_vars = [var_name for var_name, var_value in critical_vars if not var_value]
if missing_vars:
    for var_name in missing_vars:
        logging.error(f"Critical configuration '{var_name}' is missing.")
    sys.exit(1)

# Validate Knowledge Base IDs
for keyword, kb_id in KB_MAPPINGS.items():
    if not kb_id:
        logging.error(f"Knowledge Base ID for keyword '{keyword}' is missing.")
        sys.exit(1)

# --- Logging Configuration ---
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Print logs to console
        # Additional handlers (e.g., file logging) can be added here
    ]
)
