"""
LLM Client abstraction for supporting multiple providers (OpenAI, Gemini).
"""

import logging
from typing import List, Optional, Dict, Any
import openai
import anthropic
import google.generativeai as genai
from src.config.settings import Config

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Unified client for interacting with different LLM providers.
    """

    def __init__(self, config: Config):
        self.config = config
        self.provider = config.llm_provider
        
        # Initialize OpenAI if key is present
        self.openai_client = None
        if config.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=config.openai_api_key)
            if self.provider == "openai" or not hasattr(self, 'model_name'):
                self.model_name = config.openai_model
            
        # Initialize Gemini if key is present
        self.gemini_model = None
        if config.google_api_key:
            try:
                genai.configure(api_key=config.google_api_key)
                # Store the model name string
                self.gemini_model_name = config.gemini_model
                # Initialize the default model object
                self.gemini_model = genai.GenerativeModel(self.gemini_model_name)
                if self.provider == "gemini":
                    self.model_name = self.gemini_model_name
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")

        # Initialize Anthropic if key is present
        self.anthropic_client = None
        if config.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=config.anthropic_api_key)
            if self.provider == "anthropic":
                self.model_name = config.anthropic_model
            
        logger.info(f"LLMClient initialized. Active Provider: {self.provider}")

    def call(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: Optional[float] = None,
        max_tokens: Optional[float] = None,
        json_mode: bool = False,
        force_provider: Optional[str] = None,
        force_model: Optional[str] = None
    ) -> str:
        """
        Execute a call to the configured LLM provider.
        """
        temp = temperature if temperature is not None else self.config.agent_temperature
        tokens = max_tokens if max_tokens is not None else self.config.agent_max_tokens
        
        # Determine which provider to use
        active_provider = force_provider if force_provider else self.provider

        # Default fallback order: what to try if main provider fails
        # We prioritize Gemini (fast/cheap) as backup, then OpenAI (reliable)
        fallback_order = []
        if self.gemini_model: fallback_order.append("gemini")
        if self.openai_client: fallback_order.append("openai")
        if self.anthropic_client: fallback_order.append("anthropic")
        
        # Ensure active_provider is tried first
        if active_provider in fallback_order:
            fallback_order.remove(active_provider)
        fallback_order.insert(0, active_provider)
        
        last_error = None
        
        for provider in fallback_order:
            try:
                if provider == "openai":
                    return self._call_openai(system_prompt, user_prompt, temp, tokens, json_mode)
                elif provider == "gemini":
                    return self._call_gemini(system_prompt, user_prompt, temp, tokens, json_mode)
                elif provider == "anthropic":
                    return self._call_anthropic(system_prompt, user_prompt, temp, tokens, json_mode, model=force_model)
            except Exception as e:
                logger.warning(f"LLM Provider '{provider}' failed: {e}. Trying next backup...")
                last_error = e
                continue
        
        # If we get here, all providers failed
        logger.error("All LLM providers failed.")
        raise last_error if last_error else RuntimeError("All configured LLM providers failed")

    def _call_openai(self, system: str, user: str, temp: float, tokens: int, json_mode: bool) -> str:
        kwargs = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "temperature": temp,
            "max_tokens": tokens,
            "timeout": 120.0  # 2 minute timeout
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = self.openai_client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()

    def _call_gemini(self, system: str, user: str, temp: float, tokens: int, json_mode: bool) -> str:
        # Gemini treats system prompt as a separate part of the configuration or initial message
        full_prompt = f"SYSTEM: {system}\n\nUSER: {user}"
        
        generation_config = genai.types.GenerationConfig(
            temperature=temp,
            max_output_tokens=tokens,
        )
        
        # Request options with timeout
        request_options = {"timeout": 120.0}
        
        if json_mode:
            # Gemini 1.5+ supports response_mime_type
            generation_config.response_mime_type = "application/json"

        max_retries = 5
        base_delay = 5

        for attempt in range(max_retries + 1):
            try:
                # Using system_instruction if available in this SDK version
                try:
                    model = genai.GenerativeModel(
                        model_name=self.gemini_model_name,
                        system_instruction=system
                    )
                    response = model.generate_content(user, generation_config=generation_config, request_options=request_options)
                except Exception as e:
                    if "429" in str(e) or "Quota exceeded" in str(e):
                        raise e
                    logger.warning(f"Failed to use system_instruction: {e}. Falling back to combined prompt.")
                    response = self.gemini_model.generate_content(full_prompt, generation_config=generation_config, request_options=request_options)
                
                return response.text.strip()
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota exceeded" in error_str:
                    logger.warning(f"Gemini Rate Limit/Quota Exceeded: {e}. Raising to trigger fallback.")
                    # Do not sleep, just raise so the orchestrator switches provider
                    raise e
                
                # For other errors, also raise so we can fallback or fail
                logger.error(f"Gemini API Error: {e}")
                raise e

    def _call_anthropic(self, system: str, user: str, temp: float, tokens: int, json_mode: bool, model: Optional[str] = None) -> str:
        """Execute call to Anthropic Claude."""
        try:
            system_instruction = system
            if json_mode:
                system_instruction += "\nOutput ONLY valid JSON."

            model_to_use = model if model else self.config.anthropic_model
            
            message = self.anthropic_client.messages.create(
                model=model_to_use,
                max_tokens=tokens,
                temperature=temp,
                system=system_instruction,
                timeout=120.0,  # 2 minute timeout
                messages=[
                    {"role": "user", "content": user}
                ]
            )
            
            # Anthropic returns a list of ContentBlock objects
            if message.content and len(message.content) > 0:
                return message.content[0].text
            return ""

        except Exception as e:
            logger.error(f"Anthropic API Error: {e}")
            raise

def get_llm_client(config: Config) -> LLMClient:
    """Factory function for LLMClient."""
    return LLMClient(config)
