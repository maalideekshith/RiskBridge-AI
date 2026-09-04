from pydantic import ValidationError

from app.services.ai.schemas import RiskInvestigationResponse


def validate_risk_investigation(
    data: dict,
) -> RiskInvestigationResponse:
    """
    Validate the structured AI risk investigation response.
    """

    try:
        return RiskInvestigationResponse.model_validate(data)

    except ValidationError as exc:
        raise ValueError(
            f"Invalid AI risk investigation response: {exc}"
        ) from exc