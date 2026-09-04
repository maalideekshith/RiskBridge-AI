from pydantic import BaseModel, Field


class HighestImpactRequest(BaseModel):
    impact: dict


class HighestImpactResponse(BaseModel):
    problem: str
    impact_score: float = Field(ge=0)
    description: str
    risk_contributions: dict[str, float]


class RemediationPlanResponse(BaseModel):
    problem: str
    impact_score: float
    description: str
    actions: list[str]
    action_count: int
    status: str


class PrioritizedAction(BaseModel):
    action: str
    priority: str
    priority_score: int


class PrioritizedRemediationPlanResponse(BaseModel):
    problem: str
    impact_score: float
    prioritized_actions: list[PrioritizedAction]
    action_count: int
    status: str


class RiskReductionAction(BaseModel):
    action: str
    priority: str
    priority_score: int
    estimated_risk_reduction: float


class RiskReductionResponse(BaseModel):
    problem: str
    impact_score: float
    estimated_risk_reduction: float
    remaining_risk: float
    actions: list[RiskReductionAction]
    action_count: int
    status: str


class RemediationStatusResponse(BaseModel):
    problem: str
    impact_score: float
    estimated_risk_reduction: float
    remaining_risk: float
    completed_actions: int
    total_actions: int
    completion_percentage: float
    status: str