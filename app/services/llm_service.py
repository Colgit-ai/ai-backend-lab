import logging 
from google import genai
from app.core.exceptions import LLMServiceError
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.llm_api_key)
        self.llm_model = settings.llm_model
    
    def generate_response(self, message: str)-> str:
        try:
            interaction = self.client.interactions.create(
                model=self.llm_model,
                input=message
            )

            if not interaction.output_text:
                logger.error("No output text received from LLM service")
                raise LLMServiceError("Unable to generate response")

            logger.info("Returning response from LLM service")
            return interaction.output_text
        
        except LLMServiceError:
            raise  # Re-raise the LLMServiceError to be handled by FastAPI

        except Exception as exc:
            logger.exception("Error generating LLM response") 
            raise LLMServiceError("An error occurred while generating the response") from exc

def get_llm_service()-> LLMService:
    return LLMService()