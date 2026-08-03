import logging 
from google import genai
from fastapi import HTTPException
from app.core.config import settings

#logger = Logging is better than print statements because it provides granular control over message severity, output destinations, and runtime filtering without requiring code changes
logger = logging.getLogger(__name__)

api_key = settings.llm_api_key
llm_model = settings.llm_model

client = genai.Client(api_key=api_key)

def generate_response(message: str):
    try:
        interaction = client.interactions.create(
            model=llm_model,
            input=message
        )

        if not interaction.output_text:
            logger.error("No output text received from LLM service")
            raise HTTPException(
                status_code=500,
                detail="Unable to generate response"
            )

        logger.info("Returning response from LLM service")
        return interaction.output_text
    
    except HTTPException:
        raise  # Re-raise the HTTPException to be handled by FastAPI

    except Exception:
        logger.exception("Error generating LLM response") #logger.exception() automatically includes the stack trace when called inside an except block.
        raise HTTPException(
            status_code=500,
            detail="Unable to generate response"
        )