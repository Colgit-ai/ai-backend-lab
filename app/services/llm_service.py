
import logging

from google import genai

from app.core.config import settings
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.llm_api_key)
        self.llm_model = settings.llm_model

    def generate_response(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        try:
            # Build the prompt using previous conversation turns.
            prompt_parts = []

            for turn in history or []:
                prompt_parts.append(
                    f"User: {turn['user_message']}\n"
                    f"Assistant: {turn['assistant_response']}"
                )

            prompt_parts.append(f"User: {message}")
            prompt_parts.append("Assistant:")

            prompt = "\n\n".join(prompt_parts)

            interaction = self.client.interactions.create(
                model=self.llm_model,
                input=prompt,
            )

            if not interaction.output_text:
                logger.error("No output text received from LLM service")
                raise LLMServiceError("Unable to generate response")

            logger.info("Returning response from LLM service")
            return interaction.output_text

        except LLMServiceError:
            raise

        except Exception as exc:
            logger.exception("Error generating LLM response")
            raise LLMServiceError(
                "An error occurred while generating the response"
            ) from exc


def get_llm_service() -> LLMService:
    return LLMService()
