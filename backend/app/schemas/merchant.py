from pydantic import BaseModel, Field


class MerchantCreate(BaseModel):
    business_name: str = Field(
        min_length=2,
        max_length=150,
    )

    business_type: str = Field(
        min_length=2,
        max_length=100,
    )

    website: str | None = None

    country: str = Field(
        min_length=2,
        max_length=100,
        default="India",
    )

    currency: str = Field(
        min_length=3,
        max_length=10,
        default="INR",
    )


class MerchantResponse(BaseModel):
    id: int
    user_id: int
    business_name: str
    business_type: str
    website: str | None
    country: str
    currency: str

    model_config = {
        "from_attributes": True,
    }