
from pydantic import BaseModel, Field


class WhatIfRequest(BaseModel):
    scenario: str = Field(
        min_length=1,
        description="Natural-language risk scenario requested by the user.",
    )

class WhatIfInterpretation(BaseModel):
    refund_rate: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    dispute_rate: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    transaction_volume_change: float | None = Field(
        default=None,
        ge=-100,
    )
class WhatIfExplanationRequest(BaseModel):
    scenario: str = Field(
        min_length=1,
        description="Original natural-language What-If scenario.",
    )

    impact: dict = Field(
        description="Risk simulation result from Phase 2 Step 3.",
    )
class WhatIfRecommendationRequest(BaseModel):
    scenario: str = Field(
        min_length=1,
        description="Original natural-language What-If scenario.",
    )

    interpretation: WhatIfInterpretation = Field(
        description="AI interpretation from Phase 2 Step 2.",
    )

    impact: dict = Field(
        description="Risk simulation result from Phase 2 Step 3.",
    )