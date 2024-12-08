# config.py

from dotenv import load_dotenv
import os
import sys
import logging

# Load environment variables from a .env file
load_dotenv()

# Basic Configuration Constants
API_KEY = os.environ.get('API_KEY')
OPENWEBUI_API_KEY = os.environ.get('OPENWEBUI_API_KEY')
OPENWEBUI_BASE_URL = os.environ.get('OPENWEBUI_BASE_URL')
MODEL_NAME = os.environ.get('MODEL_NAME', 'MODEL_NAME')
MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 500))
TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.7))
HISTORY_LENGTH = int(os.environ.get('HISTORY_LENGTH', 10))

# Knowledge Base (KB) Mappings: keyword -> KB ID
KB_MAPPINGS = {
    'KEYWORD1': os.environ.get('CUSTOM1_COLLECTION_ID', 'YOUR_CUSTOM1_COLLECTION_ID'),
    'KEYWORD2': os.environ.get('CUSTOM2_COLLECTION_ID', 'YOUR_CUSTOM2_COLLECTION_ID'),
    # Add more keyword-KB mappings here as needed
    # Example:
    # 'examplekeyword': os.environ.get('EXAMPLE_KB_ID', 'your-example-kb-id'),
}

# Validate Critical Configurations
# List of tuples containing variable name and its value
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

# Optional: Validate that all KB IDs in KB_MAPPINGS are provided
for keyword, kb_id in KB_MAPPINGS.items():
    if not kb_id:
        logging.error(f"Knowledge Base ID for keyword '{keyword}' is missing.")
        sys.exit(1)

# Logging Configuration (Optional Enhancements)
# You can set up additional logging configurations here if needed
# For example, setting log levels based on environment (development vs. production)

