import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  Activity,
  ShieldAlert,
  Loader2,
  Brain,
  Sparkles,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

type RiskSignals = {
  amount_anomaly: boolean;
  transaction_velocity: boolean;
  failed_payment: boolean;
  transaction_frequency: boolean;
  high_value_transaction: boolean;
  refund_rate: boolean;
  dispute_rate: boolean;
  refund_trend: boolean;
  dispute_trend: boolean;
  transaction_volume: boolean;
  device_ip_anomaly: boolean;
  geographic_anomaly: boolean;
  behavior_change: boolean;
};

type RiskSignalItem = {
  assessment_id: number;
  payment_id: number;
  risk_score: number;
  risk_category: string;
  signals: RiskSignals;
  created_at: string;
};
type RiskInvestigationResponse = {
  why_risk_increased: string;
  important_risk_signals: string[];
  risk_severity: string;
  supporting_evidence: string[];
  confidence_level: string;
};

const signalLabels: Record<keyof RiskSignals, string> = {
  amount_anomaly: "Amount anomaly",
  transaction_velocity: "Transaction velocity",
  failed_payment: "Failed payment",
  transaction_frequency: "Transaction frequency",
  high_value_transaction: "High-value transaction",
  refund_rate: "Refund rate",
  dispute_rate: "Dispute rate",
  refund_trend: "Refund trend",
  dispute_trend: "Dispute trend",
  transaction_volume: "Transaction volume",
  device_ip_anomaly: "Device / IP anomaly",
  geographic_anomaly: "Geographic anomaly",
  behavior_change: "Behavior change",
};

function getActiveSignals(signals: RiskSignals) {
  return (Object.keys(signals) as Array<keyof RiskSignals>).filter(
    (key) => signals[key],
  );
}

function severityClasses(severity: string) {
  switch (severity) {
    case "Critical":
      return "border-red-500/20 bg-red-500/10 text-red-300";
    case "High":
      return "border-orange-500/20 bg-orange-500/10 text-orange-300";
    case "Medium":
      return "border-amber-500/20 bg-amber-500/10 text-amber-300";
    default:
      return "border-emerald-500/20 bg-emerald-500/10 text-emerald-300";
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function RiskDetail() {
  const navigate = useNavigate();
  const { assessmentId } = useParams();

  const [assessment, setAssessment] =
    useState<RiskSignalItem | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [aiInvestigation, setAiInvestigation] =
  useState<RiskInvestigationResponse | null>(null);

const [aiLoading, setAiLoading] = useState(false);
const [aiError, setAiError] = useState("");

  useEffect(() => {
    const loadRiskDetail = async () => {
      try {
        setLoading(true);
        setError("");

        const accessToken = localStorage.getItem("access_token");

        if (!accessToken) {
          throw new Error("Access token was not found.");
        }

        const tokenPayload = JSON.parse(
          atob(accessToken.split(".")[1]),
        );

        const userId = tokenPayload?.sub;

        if (!userId) {
          throw new Error("User ID was not found.");
        }

        const merchantResponse = await api.get(
          `/merchants/${userId}`,
        );

        const merchantId =
          merchantResponse.data?.id ??
          merchantResponse.data?.merchant_id;

        if (!merchantId) {
          throw new Error("Merchant ID was not found.");
        }

        const response = await api.get(
          `/risk/ai/context/risk-signals/${merchantId}`,
        );

        const signals = Array.isArray(response.data)
          ? response.data
          : [];

        const found = signals.find(
          (item: RiskSignalItem) =>
            String(item.assessment_id) === String(assessmentId),
        );

        if (!found) {
          throw new Error("Risk assessment was not found.");
        }

        setAssessment(found);
      } catch (err) {
        console.error("FAILED RISK DETAIL:", err);

        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Unable to load risk assessment.");
        }
      } finally {
        setLoading(false);
      }
    };

    loadRiskDetail();
  }, [assessmentId]);
  const runAIInvestigation = async () => {
    try {
      setAiLoading(true);
      setAiError("");

      const accessToken = localStorage.getItem("access_token");

      if (!accessToken) {
        throw new Error("Access token was not found.");
      }

      const tokenPayload = JSON.parse(
        atob(accessToken.split(".")[1]),
      );

      const userId = tokenPayload?.sub;

      if (!userId) {
        throw new Error("User ID was not found.");
      }

      const merchantResponse = await api.get(
        `/merchants/${userId}`,
      );

      const merchantId =
        merchantResponse.data?.id ??
        merchantResponse.data?.merchant_id;

      if (!merchantId) {
        throw new Error("Merchant ID was not found.");
      }

      console.log(
        "AI INVESTIGATION MERCHANT ID:",
        merchantId,
      );

      const response = await api.post(
        `/risk/ai/context/investigate/${merchantId}`,
      );

      console.log(
        "AI INVESTIGATION RESPONSE:",
        response.data,
      );

      setAiInvestigation(response.data);
    } catch (err) {
      console.error(
        "FAILED AI INVESTIGATION:",
        err,
      );

      if (err instanceof Error) {
        setAiError(err.message);
      } else {
        setAiError(
          "Unable to generate AI investigation.",
        );
      }
    } finally {
      setAiLoading(false);
    }
  };
  if (loading) {
    return (
      <div className="min-h-screen bg-[#060914] text-white">
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <Loader2
              size={26}
              className="mx-auto animate-spin text-indigo-400"
            />

            <p className="mt-3 text-sm text-slate-400">
              Loading risk assessment...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="min-h-screen bg-[#060914] text-white">
        <main className="mx-auto max-w-[1200px] px-5 py-8 sm:px-8">
          <button
            type="button"
            onClick={() => navigate("/risk-monitor")}
            className="inline-flex items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-indigo-500/30 hover:bg-indigo-500/10 hover:text-white"
          >
            <ArrowLeft size={16} />
            Back to Risk Monitor
          </button>

          <div className="mt-8 rounded-2xl border border-red-500/10 bg-[#0b1120] p-8 text-center">
            <AlertTriangle
              size={28}
              className="mx-auto text-red-400"
            />

            <p className="mt-3 text-sm font-medium text-slate-300">
              {error || "Risk assessment not found."}
            </p>
          </div>
        </main>
      </div>
    );
  }

  const activeSignals = getActiveSignals(assessment.signals);

  return (
    <div className="min-h-screen bg-[#060914] text-white">
      <main className="mx-auto max-w-[1200px] px-5 py-8 sm:px-8 lg:px-10">
        {/* BACK */}
        <button
          type="button"
          onClick={() => navigate("/risk-monitor")}
          className="inline-flex items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-indigo-500/30 hover:bg-indigo-500/10 hover:text-white"
        >
          <ArrowLeft size={16} />
          Back to Risk Monitor
        </button>

        {/* HEADER */}
        <div className="mt-8">
          <div className="mb-3 flex items-center gap-2 text-xs font-medium text-slate-500">
            <span>Risk</span>
            <span>/</span>
            <span>Risk Monitor</span>
            <span>/</span>
            <span className="text-indigo-400">
              Assessment #{assessment.assessment_id}
            </span>
          </div>

          <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                Risk Assessment #{assessment.assessment_id}
              </h1>

              <p className="mt-2 text-sm text-slate-400">
                Detailed analysis of the detected risk assessment.
              </p>
            </div>

            <span
              className={`w-fit rounded-lg border px-3 py-2 text-xs font-semibold ${severityClasses(
                assessment.risk_category,
              )}`}
            >
              {assessment.risk_category} Risk
            </span>
          </div>
        </div>

        {/* SCORE */}
        <section className="mt-8 rounded-2xl border border-white/[0.07] bg-[#0b1120] p-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10">
              <Activity size={16} className="text-indigo-400" />
            </div>

            <h2 className="text-sm font-semibold text-white">
              Risk Score
            </h2>
          </div>

          <div className="mt-6 flex items-end gap-3">
            <span className="text-5xl font-bold text-white">
              {assessment.risk_score}
            </span>

            <span className="mb-2 text-sm text-slate-500">
              / 100
            </span>
          </div>

          <div className="mt-5 h-2 w-full overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className="h-full rounded-full bg-indigo-500 transition-all"
              style={{
                width: `${Math.min(
                  Math.max(assessment.risk_score, 0),
                  100,
                )}%`,
              }}
            />
          </div>
        </section>

        {/* ASSESSMENT INFO */}
        <section className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <p className="text-[10px] font-medium uppercase tracking-wider text-slate-600">
              Assessment
            </p>

            <p className="mt-2 text-lg font-semibold text-white">
              #{assessment.assessment_id}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <p className="text-[10px] font-medium uppercase tracking-wider text-slate-600">
              Payment
            </p>

            <p className="mt-2 text-lg font-semibold text-white">
              #{assessment.payment_id}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5 sm:col-span-2">
            <p className="text-[10px] font-medium uppercase tracking-wider text-slate-600">
              Detected
            </p>

            <p className="mt-2 text-sm font-medium text-slate-300">
              {formatDate(assessment.created_at)}
            </p>
          </div>
        </section>

        {/* ACTIVE SIGNALS */}
        <section className="mt-6 rounded-2xl border border-white/[0.07] bg-[#0b1120]">
          <div className="border-b border-white/[0.07] p-6">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10">
                <ShieldAlert
                  size={16}
                  className="text-amber-400"
                />
              </div>

              <h2 className="text-sm font-semibold text-white">
                Active Risk Signals
              </h2>
            </div>

            <p className="mt-2 text-xs text-slate-500">
              Signals that contributed to this risk assessment.
            </p>
          </div>

          <div className="p-6">
            {activeSignals.length === 0 ? (
              <p className="text-sm text-slate-500">
                No active signals detected.
              </p>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {activeSignals.map((signal) => (
                  <div
                    key={signal}
                    className="rounded-xl border border-white/[0.07] bg-white/[0.025] p-4"
                  >
                    <div className="flex items-center gap-3">
                      <span className="h-2 w-2 rounded-full bg-amber-400" />

                      <span className="text-sm font-medium text-slate-200">
                        {signalLabels[signal]}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
                {/* AI INVESTIGATION */}
        <section className="mt-6 rounded-2xl border border-indigo-500/10 bg-[#0b1120]">
          <div className="border-b border-white/[0.07] p-6">
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10">
                    <Brain
                      size={16}
                      className="text-indigo-400"
                    />
                  </div>

                  <h2 className="text-sm font-semibold text-white">
                    AI Risk Investigation
                  </h2>
                </div>

                <p className="mt-2 max-w-2xl text-xs leading-5 text-slate-500">
                  Use the RiskBridge AI investigation agent to analyze
                  this merchant's recent activity and explain the
                  detected risk.
                </p>
              </div>

              <button
                type="button"
                onClick={runAIInvestigation}
                disabled={aiLoading}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-indigo-500/20 bg-indigo-500/10 px-4 py-2.5 text-xs font-semibold text-indigo-300 transition hover:border-indigo-500/30 hover:bg-indigo-500/15 hover:text-indigo-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {aiLoading ? (
                  <>
                    <Loader2
                      size={14}
                      className="animate-spin"
                    />
                    Investigating...
                  </>
                ) : (
                  <>
                    <Sparkles size={14} />
                    {aiInvestigation
                      ? "Run Again"
                      : "Run AI Investigation"}
                  </>
                )}
              </button>
            </div>
          </div>

          {aiError ? (
            <div className="p-6">
              <div className="rounded-xl border border-red-500/10 bg-red-500/[0.04] p-5">
                <div className="flex items-start gap-3">
                  <AlertTriangle
                    size={18}
                    className="mt-0.5 shrink-0 text-red-400"
                  />

                  <div>
                    <p className="text-sm font-medium text-red-300">
                      AI investigation failed
                    </p>

                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      {aiError}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : !aiInvestigation ? (
            <div className="flex min-h-52 items-center justify-center p-6">
              <div className="text-center">
                <Brain
                  size={30}
                  className="mx-auto text-slate-600"
                />

                <p className="mt-3 text-sm font-medium text-slate-400">
                  AI investigation not run yet
                </p>

                <p className="mt-1 max-w-md text-xs leading-5 text-slate-600">
                  Run the AI investigation to understand why this
                  risk assessment was generated and review the
                  supporting evidence.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6 p-6">

              {/* WHY RISK INCREASED */}
              <div>
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />

                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Why Risk Increased
                  </h3>
                </div>

                <div className="mt-3 rounded-xl border border-white/[0.07] bg-white/[0.02] p-5">
                  <p className="text-sm leading-6 text-slate-300">
                    {aiInvestigation.why_risk_increased}
                  </p>
                </div>
              </div>

              {/* IMPORTANT RISK SIGNALS */}
              <div>
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />

                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Important Risk Signals
                  </h3>
                </div>

                <div className="mt-3 space-y-2">
                  {aiInvestigation.important_risk_signals.map(
                    (signal, index) => (
                      <div
                        key={`${signal}-${index}`}
                        className="flex items-start gap-3 rounded-xl border border-white/[0.07] bg-white/[0.02] p-4"
                      >
                        <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />

                        <p className="text-sm leading-5 text-slate-300">
                          {signal}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              </div>

              {/* SEVERITY + CONFIDENCE */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-5">
                  <p className="text-[10px] font-medium uppercase tracking-wider text-slate-600">
                    AI Risk Severity
                  </p>

                  <p className="mt-2 text-sm font-semibold text-amber-300">
                    {aiInvestigation.risk_severity}
                  </p>
                </div>

                <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-5">
                  <p className="text-[10px] font-medium uppercase tracking-wider text-slate-600">
                    Confidence Level
                  </p>

                  <p className="mt-2 text-sm font-semibold text-indigo-300">
                    {aiInvestigation.confidence_level}
                  </p>
                </div>
              </div>

              {/* SUPPORTING EVIDENCE */}
              <div>
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />

                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Supporting Evidence
                  </h3>
                </div>

                <div className="mt-3 space-y-2">
                  {aiInvestigation.supporting_evidence.map(
                    (evidence, index) => (
                      <div
                        key={`${evidence}-${index}`}
                        className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-4"
                      >
                        <p className="text-sm leading-5 text-slate-300">
                          {evidence}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}