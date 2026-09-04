from pydantic import BaseModel


class CreateActionRequest(BaseModel):
    problem: str
    action: str
    priority: str


class ActionResponse(BaseModel):
    problem: str
    action: str
    priority: str
    status: str

class MarkActionPendingRequest(BaseModel):
    problem: str
    action: str
    priority: str
    status: str


class MarkActionPendingResponse(BaseModel):
    problem: str
    action: str
    priority: str
    status: str

class MarkActionCompletedRequest(BaseModel):
    problem: str
    action: str
    priority: str
    status: str


class MarkActionCompletedResponse(BaseModel):
    problem: str
    action: str
    priority: str
    status: str

class CalculateUpdatedRiskRequest(BaseModel):
    remediation_result: dict
    completed_actions: int


class CalculateUpdatedRiskResponse(BaseModel):
    problem: str
    original_risk: float
    estimated_total_reduction: float
    completed_actions: int
    total_actions: int
    completion_percentage: float
    applied_risk_reduction: float
    updated_risk: float
    remaining_potential_reduction: float
    status: str
class MaintainActionHistoryRequest(BaseModel):
    action: dict
    history: list[dict] | None = None


class MaintainActionHistoryResponse(BaseModel):
    problem: str
    action: str
    priority: str
    current_status: str
    history: list[dict]
    history_count: int
    status: str