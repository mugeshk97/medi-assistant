from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI, ChatOpenAI
import logging
from langchain_core.messages import BaseMessage

from app.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize a separate smaller/faster model for guardrails if possible,
# but we will use the configured model for now.
if settings.AZURE_OPENAI_API_KEY:
    llm = AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_deployment=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        api_version="2024-12-01-preview",
        api_key=settings.AZURE_OPENAI_API_KEY,
    )
else:
    llm = ChatOpenAI(model=settings.MODEL_NAME, api_key=settings.OPENAI_API_KEY)

guardrail_system_prompt = """You are a medical domain guardrail for MediAssistant.
Your job is to analyze the user's input and determine if it is related to medical topics.
You will be provided with the conversation history. The last message is the user's current input.

ACCEPT (return "SAFE") if the input is about:
- Medical conditions, diseases, symptoms, or diagnoses
- Medications, treatments, or therapies
- Medical studies, research, or clinical trials
- Health and wellness topics
- Anatomy, physiology, or medical science
- Healthcare procedures or medical advice
- Medical terminology or education
- Public health or epidemiology
- A valid follow-up question or response to the ongoing medical conversation (e.g., "tell me more about that", "what are the side effects of the second one?", "yes I have those symptoms").

REJECT (return "UNSAFE") if the input is:
- Completely unrelated to medical/health topics AND not a valid follow-up to the conversation (e.g., cooking recipes, sports, weather, general knowledge)
- Harmful content (hate speech, violence, illegal acts)
- Gibberish or nonsensical text

Only return the single word "SAFE" or "UNSAFE".
"""

validation_prompt = ChatPromptTemplate.from_messages(
    [("system", guardrail_system_prompt), ("placeholder", "{messages}")]
)

guardrail_chain = validation_prompt | llm | StrOutputParser()


async def validate_input(messages: list[BaseMessage]) -> bool:
    """
    Validates the user input using an LLM-based guardrail.
    Takes the full conversation history to understand context for follow-up questions.
    Returns True if safe, False if unsafe.
    """
    try:
        result = await guardrail_chain.ainvoke({"messages": messages})
        is_safe = result.strip().upper() == "SAFE"

        if not is_safe:
            last_message = messages[-1].content if messages else ""
            logger.warning(f"Input blocked by guardrail: {last_message[:50]}...")

        return is_safe
    except Exception as e:
        # Fail closed for safety - block if we can't verify
        logger.error(f"Guardrail validation error: {str(e)}", exc_info=True)
        logger.warning("Failing closed - blocking input due to guardrail error")
        return False


response_guardrail_system_prompt = """You are a medical response quality guardrail for MediAssistant.
Analyze the assistant's response for quality and appropriateness.

ACCEPT (return "SAFE") if the response:
- Provides medical/health information accurately
- Stays within the medical domain
- Includes appropriate medical disclaimers when giving health advice
- Is evidence-based and factual
- Maintains professional medical communication standards

REJECT (return "UNSAFE") if the response:
- Strays from medical topics into unrelated domains
- Provides potentially harmful medical misinformation
- Contains personal identifiable information (PII)
- Makes definitive diagnoses without proper disclaimers
- Replaces professional medical consultation inappropriately
- Contains harmful content or promotes dangerous practices

Only return the single word "SAFE" or "UNSAFE".
"""

response_validation_prompt = ChatPromptTemplate.from_messages(
    [("system", response_guardrail_system_prompt), ("assistant", "{response}")]
)

response_guardrail_chain = response_validation_prompt | llm | StrOutputParser()


async def validate_response(response_text: str) -> bool:
    """
    Validates the assistant's response using a medical-domain guardrail.

    Checks that responses:
    - Stay within medical/health topics
    - Provide accurate, evidence-based information
    - Include appropriate medical disclaimers
    - Maintain professional standards
    - Don't contain PII or harmful misinformation

    Args:
        response_text: The AI-generated response to validate

    Returns:
        True if the response passes quality checks, False otherwise

    Note: Currently designed for non-streaming scenarios. In streaming mode,
    quality is ensured through the system prompt and input guardrails.
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
