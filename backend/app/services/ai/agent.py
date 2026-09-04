
import json

from openai import OpenAI

from app.database import settings
from app.services.ai.validator import validate_risk_investigation


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

OPENROUTER_MODEL = settings.openrouter_model

def get_ai_client() -> OpenAI:
    """
    Create an OpenRouter client using the OpenAI-compatible API.
    """

    api_key = settings.openrouter_api_key

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY environment variable is not configured"
        )

    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
    )


def send_risk_context_to_llm(prompt: str) -> dict:
    """
    Send the structured risk investigation prompt
    to the configured OpenRouter LLM.

    The LLM must return a valid JSON object.
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "Risk investigation prompt cannot be empty"
        )

    client = get_ai_client()

    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial risk investigation assistant "
                        "for RiskBridge. Analyze only the supplied evidence "
                        "and do not invent facts. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=3000,
            temperature=0.2,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "OpenRouter returned an empty response"
            )

        try:
            parsed_response = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "OpenRouter returned invalid JSON"
            ) from exc

        if not isinstance(parsed_response, dict):
            raise RuntimeError(
                "OpenRouter returned JSON that is not an object"
            )

        return parsed_response

    except Exception as exc:
        raise RuntimeError(
            f"Failed to send risk context to OpenRouter: {exc}"
        ) from exc


def generate_risk_investigation(prompt: str) -> dict:
    """
    Generate a complete structured AI risk investigation
    from the supplied risk investigation prompt.
    """

    investigation = send_risk_context_to_llm(prompt)

    if not investigation:
        raise RuntimeError(
            "OpenRouter returned an empty risk investigation"
        )

    validated_investigation = validate_risk_investigation(
        investigation
    )

    return validated_investigation

