from pydantic import BaseModel, Field


class RiskInvestigationResponse(BaseModel):
    why_risk_increased: str = Field(
        min_length=1,
    )

    important_risk_signals: list[str] = Field(
        min_length=1,
    )

    risk_severity: str = Field(
        min_length=1,
    )

    supporting_evidence: list[str] = Field(
        min_length=1,
    )

    confidence_level: str = Field(
        min_length=1,
    )
class RiskRecommendationResponse(BaseModel):
    immediate_actions: list[str] = Field(
        min_length=1,
    )

    preventive_actions: list[str] = Field(
        min_length=1,
    )

    priority_order: list[str] = Field(
        min_length=1,
    )

    expected_impact: list[str] = Field(
        min_length=1,
    )