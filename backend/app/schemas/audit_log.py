from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    merchant_id: int
    user_id: int | None
    action: str
    entity_type: str | None
    entity_id: int | None
    description: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }