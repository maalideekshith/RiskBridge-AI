from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.merchants import router as merchants_router
from app.routes.payments import router as payments_router
from app.routes.refunds import router as refunds_router
from app.routes.disputes import router as disputes_router
from app.routes.risk import router as risk_router
from app.routes.what_if import router as what_if_router
from app.routes.simulation import router as simulation_router
from app.routes.risk_review import router as risk_review_router
from app.routes.evidence import router as evidence_router
from app.routes.evidence_agent import router as evidence_agent_router
from app.routes.audit import router as audit_router
from app.routes.audit_log import router as audit_log_router
from app.routes.ai_risk import router as ai_risk_router
from app.routes.remediation import router as remediation_router
from app.routes.actions import router as actions_router
from app.routes.razorpay import router as razorpay_router
from app.routes.razorpay_webhook import router as razorpay_webhook_router
from app.routes.risk_alerts import router as risk_alerts_router
app = FastAPI(
    title="RiskBridge AI API",
    description="AI-powered payment risk intelligence platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(merchants_router)
app.include_router(refunds_router)
app.include_router(disputes_router)
app.include_router(payments_router)
app.include_router(risk_router)
app.include_router(simulation_router)
app.include_router(what_if_router)
app.include_router(risk_review_router)
app.include_router(evidence_router)
app.include_router(evidence_agent_router)
app.include_router(audit_router)
app.include_router(audit_log_router)
app.include_router(ai_risk_router)
app.include_router(remediation_router)
app.include_router(actions_router)
app.include_router(razorpay_router)
app.include_router(razorpay_webhook_router)
app.include_router(risk_alerts_router)
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "riskbridge-api",
    }