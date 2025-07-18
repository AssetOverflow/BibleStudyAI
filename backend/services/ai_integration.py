"""
Handles integration with external AI models like OpenAI, xAI (Grok), and Anthropic.
Provides a unified interface to interact with different LLMs for various tasks
such as text generation, analysis, and embeddings.
"""

from enum import Enum
import openai
from anthropic import Anthropic

# Assuming an xAI library exists or will be created
# import xai
from typing import Dict, Any, List
from loguru import logger

from utils.config import settings


class ModelProvider(Enum):
    OPENAI = "openai"
    XAI = "xai"
    ANTHROPIC = "anthropic"


class AIIntegration:
    """
    A unified client for interacting with multiple AI model providers.
    """

    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        # self.xai_client = xai.Client(api_key=settings.XAI_API_KEY)
        logger.info(
            "AIIntegration service initialized with clients for OpenAI and Anthropic."
        )

    async def generate_text(
        self,
        prompt: str,
        provider: ModelProvider = ModelProvider.OPENAI,
        model: str = "gpt-4o",
        system_prompt: str = "You are a helpful assistant.",
        max_tokens: int = 2048,
    ) -> str:
        """
        Generates text using the specified AI provider.

        Args:
            prompt: The user's prompt.
            provider: The AI model provider to use.
            model: The specific model to use (e.g., 'gpt-4o', 'claude-3-opus-20240229').
            system_prompt: The system prompt to guide the model's behavior.
            max_tokens: The maximum number of tokens to generate.

        Returns:
            The generated text as a string.
        """
        try:
            if provider == ModelProvider.OPENAI:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content

            elif provider == ModelProvider.ANTHROPIC:
                response = self.anthropic_client.messages.create(
                    model=model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                )
                return response.content[0].text

            # elif provider == ModelProvider.XAI:
            #     # Placeholder for xAI/Grok integration
            #     response = await self.xai_client.generate(prompt=prompt, model=model)
            #     return response.text

            else:
                logger.warning(f"Unsupported AI provider: {provider}")
                raise ValueError(f"Unsupported AI provider: {provider}")

        except Exception as e:
            logger.error(f"Error generating text with {provider.value}: {e}")
            # Fallback or error handling
            return "An error occurred while generating the text."

    async def get_embedding(
        self,
        text: str,
        provider: ModelProvider = ModelProvider.OPENAI,
        model: str = "text-embedding-3-small",
    ) -> List[float]:
        """
        Generates embeddings for the given text using the specified provider.

        Args:
            text: The text to embed.
            provider: The AI model provider to use.
            model: The embedding model to use.

        Returns:
            A list of floats representing the embedding.
        """
        try:
            if provider == ModelProvider.OPENAI:
                response = await self.openai_client.embeddings.create(
                    input=[text], model=model
                )
                return response.data[0].embedding
            else:
                # Add other providers like Cohere, etc., if needed
                logger.warning(f"Embedding not supported for provider: {provider}")
                raise ValueError(f"Embedding not supported for provider: {provider}")
        except Exception as e:
            logger.error(f"Error generating embedding with {provider.value}: {e}")
            return []


# A single instance to be used throughout the application
ai_integration_client = AIIntegration()
