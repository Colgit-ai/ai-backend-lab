import os
import logging 
from dotenv import load_dotenv
from google import genai
from fastapi import HTTPException
# An HTTP exception you can raise in your own code to show errors to the client.
# This is for client errors, invalid authentication, invalid data, etc. Not for server errors in your code.

load_dotenv()

#logger = Logging is better than print statements because it provides granular control over message severity, output destinations, and runtime filtering without requiring code changes
#DEBUG: Detailed diagnostic details for local development.
#INFO: Confirmation that application milestones are working smoothly.
#WARNING: Indication that something unexpected happened, but the app can still run.
#ERROR: A serious issue prevented a specific function from executing.
#CRITICAL: Severe failures that might crash the entire application

logger = logging.getLogger(__name__)

api_key = os.getenv("LLM_API_KEY")

if not api_key:
    logger.error("LLM_API_KEY is not configured")
    raise RuntimeError("LLM_API_KEY is not configured")

client = genai.Client(api_key=api_key)


def generate_response(message: str):
    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
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