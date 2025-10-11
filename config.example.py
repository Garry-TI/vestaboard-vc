"""
Example configuration file for Vestaboard application.
Copy this to config.py and fill in your actual credentials.
"""

# Local Vestaboard Configuration
# Use the API key you received after enabling the Local API (not the enablement token)
VESTABOARD_CONFIG = {
    'ip': '10.1.10.61',
    'api_key': 'YOUR API KEY HERE'  # Replace with your actual API key
}
# LLM Model Configuration
# Configure local LLM models for AI chat feature
LLM_MODELS = {
    'Qwen3-4B-2507': {
        'model_id': 'Qwen/Qwen3-4B-Instruct-2507',
        'max_tokens': 132,  # Vestaboard character limit (6 rows × 22 chars)
        'temperature': 0.7,
        'description': 'Qwen 3 4B Instruct - Fast and efficient'
    },
        'Llama-3.2-1B-Instruct': {
        'model_id': 'meta-llama/Llama-3.2-1B-Instruct',
        'max_tokens': 132,  # Vestaboard character limit (6 rows × 22 chars)
        'temperature': 0.7,
        'description': 'Llama 3.2 1B Instruct - Fast and efficient'
    },

    # Add more models here as needed
}

# Default model for AI chat
DEFAULT_LLM_MODEL = 'Qwen3-4B-2507'
