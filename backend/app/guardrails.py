from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import logging

from app.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize a separate smaller/faster model for guardrails if possible,
# but we will use the configured model for now.
llm = ChatOpenAI(model=settings.MODEL_NAME, api_key=settings.OPENAI_API_KEY)

guardrail_system_prompt = """You are a content safety guardrail. 
Your job is to analyze the user's input and determine if it is safe, appropriate, and relevant for a general purpose assistant.
If the input is unsafe (hate speech, explicit violence, illegal acts) or completely irrelevant (e.g., gibberish), return "UNSAFE".
Otherwise, return "SAFE".
Only return the single word "SAFE" or "UNSAFE".
"""

validation_prompt = ChatPromptTemplate.from_messages(
    [("system", guardrail_system_prompt), ("user", "{input}")]
)

guardrail_chain = validation_prompt | llm | StrOutputParser()


async def validate_input(user_input: str) -> bool:
    """
    Validates the user input using an LLM-based guardrail.
    Returns True if safe, False if unsafe.
    """
    try:
        result = await guardrail_chain.ainvoke({"input": user_input})
        is_safe = result.strip().upper() == "SAFE"

        if not is_safe:
            logger.warning(f"Input blocked by guardrail: {user_input[:50]}...")

        return is_safe
    except Exception as e:
        # Fail closed for safety - block if we can't verify
        logger.error(f"Guardrail validation error: {str(e)}", exc_info=True)
        logger.warning("Failing closed - blocking input due to guardrail error")
        return False


response_guardrail_system_prompt = """You are a response safety guardrail.
Analyze the assistant's response.
If the response contains harmful content, PII, or is hallucinating wildly (if you can tell), return "UNSAFE".
Otherwise, return "SAFE".
"""

response_validation_prompt = ChatPromptTemplate.from_messages(
    [("system", response_guardrail_system_prompt), ("assistant", "{response}")]
)

response_guardrail_chain = response_validation_prompt | llm | StrOutputParser()


async def validate_response(response_text: str) -> bool:
    """
    Validates the assistant's response using an LLM-based guardrail.
    Returns True if safe, False if unsafe.
    Note: Currently disabled for streaming support.
    """
    try:
        result = await response_guardrail_chain.ainvoke({"response": response_text})
        is_safe = result.strip().upper() == "SAFE"

        if not is_safe:
            logger.warning(
                f"Response blocked by output guardrail: {response_text[:50]}..."
            )

        return is_safe
    except Exception as e:
        # Fail open for responses - show response if guardrail fails
        logger.error(f"Response guardrail error: {str(e)}", exc_info=True)
        logger.warning("Failing open - allowing response despite guardrail error")
        return True
