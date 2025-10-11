"""
LLM Client for AI chat functionality.
Uses LangChain with local Hugging Face models for inference.
"""

from typing import Dict, Optional
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from config import LLM_MODELS, DEFAULT_LLM_MODEL


class LLMClient:
    """Client for managing local LLM inference."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            model_name: Name of the model from LLM_MODELS config. Uses DEFAULT_LLM_MODEL if None.
        """
        self.model_name = model_name or DEFAULT_LLM_MODEL
        self.model_config = LLM_MODELS.get(self.model_name)

        if not self.model_config:
            raise ValueError(f"Model '{self.model_name}' not found in LLM_MODELS config")

        self.llm = None
        self.tokenizer = None
        self.model = None
        self._initialized = False

    def initialize(self) -> Dict[str, str]:
        """
        Load the model and tokenizer. This can take time on first run.

        Returns:
            Status dictionary with 'status' and 'message' keys
        """
        if self._initialized:
            return {
                'status': 'success',
                'message': f'Model {self.model_name} already initialized'
            }

        try:
            model_id = self.model_config['model_id']

            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"

            print(f"Loading model: {model_id}")
            print(f"Using device: {device}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                trust_remote_code=True
            )

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )

            if device == "cpu":
                self.model = self.model.to(device)

            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=self.model_config['max_tokens'],
                temperature=self.model_config['temperature'],
                do_sample=True,
                top_p=0.95,
                repetition_penalty=1.1
            )

            # Wrap in LangChain
            self.llm = HuggingFacePipeline(pipeline=pipe)
            self._initialized = True

            return {
                'status': 'success',
                'message': f'Model {self.model_name} loaded successfully on {device}'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to load model: {str(e)}'
            }

    def generate_response(self, prompt: str, max_length: int = 132) -> Dict[str, str]:
        """
        Generate a response to the user's prompt.

        Args:
            prompt: User's input question/message
            max_length: Maximum character length for response (Vestaboard limit)

        Returns:
            Dictionary with 'status', 'message', and 'response' keys
        """
        if not self._initialized:
            init_result = self.initialize()
            if init_result['status'] != 'success':
                return {
                    'status': 'error',
                    'message': init_result['message'],
                    'response': ''
                }

        try:
            # Format the prompt for instruct models
            formatted_prompt = self._format_prompt(prompt)

            # Generate response
            response = self.llm.invoke(formatted_prompt)

            # Clean and truncate response
            cleaned_response = self._clean_response(response, formatted_prompt)
            truncated_response = self._truncate_response(cleaned_response, max_length)

            return {
                'status': 'success',
                'message': 'Response generated successfully',
                'response': truncated_response
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error generating response: {str(e)}',
                'response': ''
            }

    def _format_prompt(self, user_prompt: str) -> str:
        """
        Format the prompt for the instruct model.

        Args:
            user_prompt: Raw user input

        Returns:
            Formatted prompt string
        """
        # Add system instruction to keep responses concise
        system_msg = "You are a helpful assistant. Provide concise answers in 132 characters or less."

        # Qwen format
        formatted = f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"

        return formatted

    def _clean_response(self, response: str, original_prompt: str) -> str:
        """
        Clean the model's response by removing prompt echoes and special tokens.

        Args:
            response: Raw model output
            original_prompt: The original formatted prompt

        Returns:
            Cleaned response text
        """
        # Remove the prompt if it was echoed
        if response.startswith(original_prompt):
            response = response[len(original_prompt):]

        # Remove special tokens
        special_tokens = ['<|im_start|>', '<|im_end|>', '<|endoftext|>']
        for token in special_tokens:
            response = response.replace(token, '')

        # Strip whitespace
        response = response.strip()

        return response

    def _truncate_response(self, response: str, max_length: int) -> str:
        """
        Truncate response to fit Vestaboard display.

        Args:
            response: Cleaned response text
            max_length: Maximum character length

        Returns:
            Truncated response
        """
        if len(response) <= max_length:
            return response

        # Try to truncate at sentence boundary
        truncated = response[:max_length]

        # Look for last sentence ending
        for delimiter in ['. ', '! ', '? ']:
            last_sentence = truncated.rfind(delimiter)
            if last_sentence > max_length * 0.5:  # At least 50% of max length
                return truncated[:last_sentence + 1].strip()

        # Otherwise, truncate at word boundary
        last_space = truncated.rfind(' ')
        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated.strip() + '...'

    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the current model.

        Returns:
            Dictionary with model configuration details
        """
        return {
            'name': self.model_name,
            'initialized': self._initialized,
            'config': self.model_config
        }

    def change_model(self, model_name: str) -> Dict[str, str]:
        """
        Change to a different model.

        Args:
            model_name: Name of the new model from LLM_MODELS config

        Returns:
            Status dictionary
        """
        if model_name not in LLM_MODELS:
            return {
                'status': 'error',
                'message': f"Model '{model_name}' not found in config"
            }

        # Clear current model
        if self._initialized:
            del self.model
            del self.tokenizer
            del self.llm
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

        # Set new model
        self.model_name = model_name
        self.model_config = LLM_MODELS[model_name]
        self._initialized = False

        # Initialize new model
        return self.initialize()
