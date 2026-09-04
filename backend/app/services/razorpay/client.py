import razorpay

from app.database import settings


def get_razorpay_client() -> razorpay.Client:
    return razorpay.Client(
        auth=(
            settings.razorpay_key_id,
            settings.razorpay_key_secret,
        )
    )