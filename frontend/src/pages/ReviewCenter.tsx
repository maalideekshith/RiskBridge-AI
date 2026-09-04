import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  FileSearch,
  Loader2,
  MessageSquareText,
  ShieldAlert,
  Clock3,
  RefreshCw,
} from "lucide-react";
import api from "../services/api";

type RiskSignals = {
  amount_anomaly?: boolean;
  transaction_velocity?: boolean;
  failed_payment?: boolean;
  transaction_frequency?: boolean;
  high_value_transaction?: boolean;
  refund_rate?: boolean;
  dispute_rate?: boolean;
  refund_trend?: boolean;
  dispute_trend?: boolean;
  transaction_volume?: boolean;
  device_ip_anomaly?: boolean;
  geographic_anomaly?: boolean;
  behavior_change?: boolean;
};

type RiskAssessment = {
  assessment_id: number;
  id?: number;
  payment_id: number;
  risk_score: number;
  risk_category: string;
  signals: RiskSignals;
  created_at?: string;
};

type ReviewCase = {
  id?: number;
  case_id?: number;
  merchant_id: number;
  risk_reason: string;
  status: string;
  risk_assessment?: RiskAssessment;
  timeline?: Array<{
    event: string;
    status: string;
  }>;
  timeline_count?: number;
};
type EvidenceState = {
  transactions: unknown[];
  refunds: unknown[];
  disputes: unknown[];
  policies: unknown[];
  risk_signals: unknown[];
};
type ChecklistState = {
  checklist?: unknown[];
  checklist_count?: number;
  [key: string]: unknown;
};

const signalLabels: Record<string, string> = {
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

function getActiveSignals(signals: RiskSignals = {}) {
  return Object.keys(signals).filter(
    (key) => signals[key as keyof RiskSignals] === true,
  );
}

function getSeverity(score: number) {
  if (score >= 70) return "Critical";
  if (score >= 50) return "High";
  if (score >= 30) return "Medium";
  return "Low";
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

function formatDate(value?: string) {
  if (!value) return "Not available";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function extractArray<T = Record<string, unknown>>(value: unknown): T[] {
  if (Array.isArray(value)) return value as T[];

  if (
    value &&
    typeof value === "object" &&
    "items" in value &&
    Array.isArray((value as { items?: unknown }).items)
  ) {
    return (value as { items: unknown[] }).items as T[];
  }

  return [];
}

function extractText(value: unknown): string {
  if (typeof value === "string") return value;

  if (value && typeof value === "object") {
    const object = value as Record<string, unknown>;

    const candidates = [
      object.summary,
      object.analysis,
      object.message,
      object.explanation,
      object.result,
      object.text,
      object.content,
    ];

    for (const candidate of candidates) {
      if (typeof candidate === "string") {
        return candidate;
      }
    }
  }

  return "";
}

export default function ReviewCenter() {
  

  const [merchantId, setMerchantId] = useState<number | null>(null);

const [assessments, setAssessments] = useState<RiskAssessment[]>([]);
const [selectedAssessment, setSelectedAssessment] =
  useState<RiskAssessment | null>(null);

const [reviewCase, setReviewCase] = useState<ReviewCase | null>(null);

  const [evidence, setEvidence] = useState<EvidenceState>({
    transactions: [],
    refunds: [],
    disputes: [],
    policies: [],
    risk_signals: [],
  });

  const [checklist, setChecklist] = useState<ChecklistState | null>(null);
  const [summary, setSummary] = useState<unknown>(null);

  const [loading, setLoading] = useState(true);
  const [caseLoading, setCaseLoading] = useState(false);
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [checklistLoading, setChecklistLoading] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);

  const [error, setError] = useState("");

  /*
   * ---------------------------------------------------------
   * LOAD REAL MERCHANT + REAL RISK DATA
   * ---------------------------------------------------------
   */

 const loadReviewData = async () => {
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
      throw new Error("User ID was not found in access token.");
    }

    /*
     * Resolve the real merchant.
     */
    const merchantResponse = await api.get(
      `/merchants/${userId}`,
    );

    const resolvedMerchantId =
      merchantResponse.data?.id ??
      merchantResponse.data?.merchant_id;

    if (!resolvedMerchantId) {
      throw new Error("Merchant ID was not found.");
    }

    const resolvedId = Number(resolvedMerchantId);

    setMerchantId(resolvedId);

    /*
     * Get the merchant's real payments.
     *
     * /payments/{merchant_id}
     * returns payments belonging to this merchant.
     */
    const paymentsResponse = await api.get(
      `/payments/${resolvedId}`,
    );

    const payments = extractArray(
      paymentsResponse.data,
    ) as Array<{ id: number }>;

    /*
     * Risk assessments are attached to PAYMENT IDs,
     * not merchant IDs.
     *
     * Therefore we query:
     *
     * /payments/{payment_id}/risk/assessments
     */
    const assessmentResponses = await Promise.all(
      payments.map(async (payment) => {
        try {
          const response = await api.get(
            `/payments/${payment.id}/risk/assessments`,
          );

          return extractArray(response.data) as RiskAssessment[];
        } catch (err) {
          console.warn(
            `Unable to load assessments for payment ${payment.id}:`,
            err,
          );

          return [];
        }
      }),
    );

    const allAssessments = assessmentResponses
  .flat()
  .map((assessment) => ({
    ...assessment,
    assessment_id: assessment.assessment_id ?? assessment.id,
  }))
  .sort(
    (a, b) =>
      (b.created_at ?? "").localeCompare(
        a.created_at ?? "",
      ),
  );
/*
 * One payment should appear only once in the Case List.
 *
 * Multiple risk assessments can exist for the same payment.
 * Since the assessments are sorted newest-first, the first
 * assessment we encounter for a payment is its latest assessment.
 */
const latestAssessmentByPayment = new Map<
  number,
  RiskAssessment
>();

for (const assessment of allAssessments) {
  if (!latestAssessmentByPayment.has(assessment.payment_id)) {
    latestAssessmentByPayment.set(
      assessment.payment_id,
      assessment,
    );
  }
}

const realAssessments = Array.from(
  latestAssessmentByPayment.values(),
);

setAssessments(realAssessments);

/*
 * Automatically select the latest assessment
 * from the first unique payment.
 */
setSelectedAssessment(null);
  } catch (err) {
    console.error("FAILED REVIEW CENTER:", err);

    setError(
      err instanceof Error
        ? err.message
        : "Unable to load Review Center data.",
    );
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    loadReviewData();
  }, []);

  /*
   * ---------------------------------------------------------
   * STEP 1 + STEP 2
   * CREATE REAL REVIEW CASE
   * ---------------------------------------------------------
   */

  const createReviewCase = async (assessment: RiskAssessment) => {
    if (!merchantId) {
      setError("Merchant ID is not available.");
      return;
    }

    try {
      setCaseLoading(true);
      setError("");

      const activeSignals = getActiveSignals(assessment.signals);

      const riskReason =
        activeSignals.length > 0
          ? `${assessment.risk_category} risk detected: ${activeSignals
              .map((signal) => signalLabels[signal] ?? signal)
              .join(", ")}`
          : `${assessment.risk_category} risk detected for payment #${assessment.payment_id}`;

      const createResponse = await api.post(
        "/risk-review/cases",
        null,
        {
          params: {
            merchant_id: merchantId,
            risk_reason: riskReason,
          },
        },
      );

      let currentCase: ReviewCase = createResponse.data;

      /*
       * Assign reason to the case.
       */
      const reasonResponse = await api.post(
        "/risk-review/cases/reason",
        currentCase,
        {
          params: {
            risk_reason: riskReason,
          },
        },
      );

      currentCase = reasonResponse.data;

      /*
       * Attach the real risk assessment returned
       * by the Risk Intelligence API.
       */
      const assessmentResponse = await api.post(
        "/risk-review/cases/assessment",
        {
          case: currentCase,
          risk_assessment: assessment,
        },
      );

      currentCase = assessmentResponse.data;

      /*
       * Move the case into investigation.
       */
      const statusResponse = await api.patch(
        "/risk-review/cases/status",
        currentCase,
        {
          params: {
            status: "in_progress",
          },
        },
      );

      currentCase = statusResponse.data;

      setReviewCase(currentCase);

      /*
       * Add the real investigation-started event.
       */
      const timelineResponse = await api.post(
        "/risk-review/cases/timeline",
        currentCase,
        {
          params: {
            event: "Risk analyst started investigation",
          },
        },
      );

      setReviewCase(timelineResponse.data);

      /*
       * Automatically continue to evidence collection.
       */
      await collectEvidence(currentCase);
    } catch (err) {
      console.error("FAILED TO CREATE REVIEW CASE:", err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to create the risk review case.",
      );
    } finally {
      setCaseLoading(false);
    }
  };

  /*
   * ---------------------------------------------------------
   * STEP 3 — REAL EVIDENCE
   * ---------------------------------------------------------
   */

  const collectEvidence = async (caseData: ReviewCase) => {
    if (!merchantId) return;

    try {
      setEvidenceLoading(true);
      setError("");

      /*
       * Evidence endpoints require arrays in their request body.
       *
       * We first obtain the real merchant data already exposed
       * by the existing RiskBridge APIs, then send that data to
       * the Risk Review evidence collectors.
       */

      const [
        transactionsResponse,
        refundsResponse,
        disputesResponse,
        riskSignalsResponse,
      ] = await Promise.all([
        api.get(`/payments/${merchantId}`),
        api.get(`/risk/ai/context/refunds/${merchantId}`),
        api.get(`/risk/ai/context/disputes/${merchantId}`),
        api.get(`/risk/ai/context/risk-signals/${merchantId}`),
      ]);

      const transactions = extractArray(
  transactionsResponse.data,
).map((transaction) => ({
  ...transaction,
  merchant_id: transaction.merchant_id ?? merchantId,
}));

const refunds = extractArray(
  refundsResponse.data,
).map((refund) => ({
  ...refund,
  merchant_id: refund.merchant_id ?? merchantId,
}));

const disputes = extractArray(
  disputesResponse.data,
).map((dispute) => ({
  ...dispute,
  merchant_id: dispute.merchant_id ?? merchantId,
}));

const riskSignals = extractArray(
  riskSignalsResponse.data,
).map((signal) => ({
  ...signal,
  merchant_id: signal.merchant_id ?? merchantId,
}));

      /*
       * Policies are collected through the backend endpoint.
       * The endpoint expects an array. We do not invent policies.
       * An empty array means no policy records were supplied by
       * the application yet.
       */
      const policies: unknown[] = [];

      const [
        collectedTransactions,
        collectedRefunds,
        collectedDisputes,
        collectedPolicies,
        collectedRiskSignals,
      ] = await Promise.all([
        api.post(
          "/risk-review/evidence/transactions",
          transactions,
          {
            params: { merchant_id: merchantId },
          },
        ),
        api.post(
          "/risk-review/evidence/refunds",
          refunds,
          {
            params: { merchant_id: merchantId },
          },
        ),
        api.post(
          "/risk-review/evidence/disputes",
          disputes,
          {
            params: { merchant_id: merchantId },
          },
        ),
        api.post(
          "/risk-review/evidence/policies",
          policies,
          {
            params: { merchant_id: merchantId },
          },
        ),
        api.post(
          "/risk-review/evidence/risk-signals",
          riskSignals,
          {
            params: { merchant_id: merchantId },
          },
        ),
      ]);

      const collectedEvidence = {
  transactions:
    collectedTransactions.data?.transactions ?? [],
  refunds:
    collectedRefunds.data?.refunds ?? [],
  disputes:
    collectedDisputes.data?.disputes ?? [],
  policies:
    collectedPolicies.data?.policies ?? [],
  risk_signals:
    collectedRiskSignals.data?.risk_signals ?? [],
};

setEvidence(collectedEvidence);

      /*
       * Generate the real AI checklist from the evidence
       * collected above.
       */
      await generateChecklist(caseData, collectedEvidence);
    } catch (err) {
      console.error("FAILED TO COLLECT REVIEW EVIDENCE:", err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to collect review evidence.",
      );
    } finally {
      setEvidenceLoading(false);
    }
  };

  /*
   * ---------------------------------------------------------
   * STEP 3 — AI CHECKLIST
   * ---------------------------------------------------------
   */

  const generateChecklist = async (
  caseData: ReviewCase,
  evidenceData: EvidenceState,
) => {
  try {
    setChecklistLoading(true);
    setError("");

    /*
     * First identify which evidence categories are missing.
     */
    const missingResponse = await api.post(
      "/risk-review/ai/missing-evidence",
      {
        transactions: evidenceData.transactions,
        refunds: evidenceData.refunds,
        disputes: evidenceData.disputes,
        policies: evidenceData.policies,
        risk_signals: evidenceData.risk_signals,
      },
    );

    /*
     * Then generate the checklist from the
     * missing evidence returned by the backend.
     */
    const checklistResponse = await api.post(
      "/risk-review/ai/checklist",
      {
        missing_evidence:
          missingResponse.data?.missing_evidence ?? [],
      },
    );

    setChecklist(checklistResponse.data);

    /*
     * Continue to the AI-generated summary.
     */
    await generateSummary(caseData, evidenceData);
  } catch (err) {
    console.error("FAILED TO GENERATE CHECKLIST:", err);

    setError(
      err instanceof Error
        ? err.message
        : "Unable to generate evidence checklist.",
    );
  } finally {
    setChecklistLoading(false);
  }
};

  /*
   * ---------------------------------------------------------
   * STEP 4 — AI SUMMARY
   * ---------------------------------------------------------
   */

  const generateSummary = async (
  caseData: ReviewCase,
  evidenceData: EvidenceState,
) => {
  try {
  setSummaryLoading(true);
  setError("");

    const totalEvidenceItems =
      evidenceData.transactions.length +
      evidenceData.refunds.length +
      evidenceData.disputes.length +
      evidenceData.policies.length +
      evidenceData.risk_signals.length;

    const analysis = {
      merchant_id: merchantId,
      risk_reason:
        caseData.risk_reason ??
        `Medium risk detected: ${getActiveSignals(
          caseData.risk_assessment?.signals ?? {},
        ).join(", ")}`,
      assessment:
        caseData.risk_assessment?.risk_category ??
        "medium_risk",
      total_evidence_items: totalEvidenceItems,
    };

    const response = await api.post(
      "/risk-review/ai/summary",
      {
        analysis,
        evidence: evidenceData,
      },
    );

    setSummary(response.data);
  } catch (err) {
    console.error("FAILED TO GENERATE SUMMARY:", err);

    setError(
      err instanceof Error
        ? err.message
        : "Unable to generate AI summary.",
    );
  } finally {
    setSummaryLoading(false);
  }
};

  const activeSignals = useMemo(
    () =>
      selectedAssessment
        ? getActiveSignals(selectedAssessment.signals)
        : [],
    [selectedAssessment],
  );

  const severity = selectedAssessment
    ? getSeverity(selectedAssessment.risk_score)
    : "Low";

  const evidenceCounts = {
    transactions: evidence.transactions.length,
    refunds: evidence.refunds.length,
    disputes: evidence.disputes.length,
    policies: evidence.policies.length,
    risk_signals: evidence.risk_signals.length,
  };

  /*
   * ---------------------------------------------------------
   * LOADING
   * ---------------------------------------------------------
   */

  if (loading) {
    return (
      <div className="min-h-screen bg-[#060914] text-white">
        <main className="mx-auto flex min-h-screen max-w-[1600px] items-center justify-center px-5">
          <div className="text-center">
            <Loader2
              size={28}
              className="mx-auto animate-spin text-indigo-400"
            />

            <p className="mt-4 text-sm font-medium text-slate-300">
              Loading Review Center...
            </p>

            <p className="mt-1 text-xs text-slate-600">
              Loading real merchant risk data.
            </p>
          </div>
        </main>
      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * PAGE
   * ---------------------------------------------------------
   */

  return (
    <div className="min-h-screen bg-[#060914] text-white">
      <main className="mx-auto max-w-[1600px] px-5 py-7 sm:px-8 lg:px-10 lg:py-9">
        

        {/* HEADER */}
        <div className="mb-8">
          <div className="mb-3 flex items-center gap-2 text-xs font-medium text-slate-500">
            <span>Review</span>
            <span>/</span>
            <span className="text-indigo-400">
              Risk Review Center
            </span>
          </div>

          <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                Risk Review Center
              </h1>

              <p className="mt-2 max-w-2xl text-sm text-slate-400 sm:text-base">
                Investigate merchant risk cases using real assessments,
                evidence, AI analysis, and case history.
              </p>
            </div>

            <div className="flex items-center gap-2 rounded-xl border border-emerald-500/10 bg-emerald-500/[0.05] px-3.5 py-2.5">
              <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50" />
              <span className="text-xs font-medium text-emerald-300">
                Review engine active
              </span>
            </div>
          </div>
        </div>

        {/* ERROR */}
        {error && (
          <div className="mb-6 rounded-2xl border border-red-500/20 bg-red-500/[0.06] p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle
                size={18}
                className="mt-0.5 shrink-0 text-red-400"
              />

              <div>
                <p className="text-sm font-medium text-red-300">
                  Review Center error
                </p>

                <p className="mt-1 text-xs leading-5 text-red-300/70">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* SUMMARY */}
        <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10">
                <FileSearch size={18} className="text-indigo-400" />
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Assessments
                </p>

                <p className="mt-1 text-2xl font-bold text-white">
                  {assessments.length}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10">
                <ShieldAlert
                  size={18}
                  className="text-amber-400"
                />
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Risk score
                </p>

                <p className="mt-1 text-2xl font-bold text-white">
                  {selectedAssessment?.risk_score ?? "—"}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10">
                <Activity size={18} className="text-cyan-400" />
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Active signals
                </p>

                <p className="mt-1 text-2xl font-bold text-white">
                  {activeSignals.length}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10">
                <CheckCircle2
                  size={18}
                  className="text-emerald-400"
                />
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Case status
                </p>

                <p className="mt-1 text-sm font-semibold text-emerald-300">
                  {reviewCase?.status ?? "Not created"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* STEP 1 — CASE LIST */}
        <section className="mb-6 rounded-2xl border border-white/[0.07] bg-[#0b1120]">
          <div className="border-b border-white/[0.07] p-6">
            <div className="flex items-center gap-3">
  <div>
    <h2 className="text-sm font-semibold text-white">
      Case List
    </h2>

                <p className="mt-1 text-xs text-slate-500">
                  Select a real risk assessment to create a review case.
                </p>
              </div>
            </div>
          </div>

          {assessments.length === 0 ? (
            <div className="flex min-h-52 items-center justify-center p-6">
              <div className="text-center">
                <FileSearch
                  size={28}
                  className="mx-auto text-slate-600"
                />

                <p className="mt-3 text-sm font-medium text-slate-400">
                  No risk assessments available
                </p>

                <p className="mt-1 text-xs text-slate-600">
                  Review cases can only be created from real risk
                  assessments.
                </p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-white/[0.05]">
              {assessments.map((assessment) => {
                const itemSeverity = getSeverity(
                  assessment.risk_score,
                );

                const itemSignals = getActiveSignals(
                  assessment.signals,
                );

                const selected =
                  selectedAssessment?.assessment_id ===
                  assessment.assessment_id;

                return (
                  <div
                    key={assessment.assessment_id}
                    className={`p-5 transition sm:p-6 ${
                      selected
                        ? "bg-indigo-500/[0.04]"
                        : "hover:bg-white/[0.02]"
                    }`}
                  >
                    <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span
                            className={`rounded-lg border px-2 py-1 text-[10px] font-semibold ${severityClasses(
                              itemSeverity,
                            )}`}
                          >
                            {itemSeverity}
                          </span>

                          <span className="text-xs text-slate-600">
                            Assessment #{assessment.assessment_id}
                          </span>

                          <span className="text-xs text-slate-600">
                            Payment #{assessment.payment_id}
                          </span>
                        </div>

                        <div className="mt-3 flex items-baseline gap-2">
                          <span className="text-2xl font-bold text-white">
                            {assessment.risk_score}
                          </span>

                          <span className="text-xs text-slate-500">
                            risk score
                          </span>

                          <span className="text-xs text-slate-600">
                            •
                          </span>

                          <span className="text-xs text-slate-400">
                            {assessment.risk_category}
                          </span>
                        </div>

                        <div className="mt-3 flex flex-wrap gap-2">
                          {itemSignals.length > 0 ? (
                            itemSignals.map((signal) => (
                              <span
                                key={signal}
                                className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1.5 text-[11px] text-slate-300"
                              >
                                {signalLabels[signal] ?? signal}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-slate-600">
                              No active signals
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p className="text-[10px] uppercase tracking-wider text-slate-600">
                            Detected
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            {formatDate(assessment.created_at)}
                          </p>
                        </div>

                        <button
                          type="button"
                          onClick={() =>
                            setSelectedAssessment(assessment)
                          }
                          className={`rounded-xl border px-4 py-2.5 text-xs font-medium transition ${
                            selected
                              ? "border-indigo-500/30 bg-indigo-500/10 text-indigo-300"
                              : "border-white/[0.08] bg-white/[0.025] text-slate-300 hover:border-indigo-500/30 hover:bg-indigo-500/10 hover:text-white"
                          }`}
                        >
                          {selected ? "Selected" : "Select"}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {selectedAssessment && !reviewCase && (
            <div className="border-t border-white/[0.07] p-6">
              <button
                type="button"
                disabled={caseLoading}
                onClick={() =>
                  createReviewCase(selectedAssessment)
                }
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {caseLoading ? (
                  <Loader2
                    size={16}
                    className="animate-spin"
                  />
                ) : (
                  <FileSearch size={16} />
                )}

                {caseLoading
                  ? "Creating review case..."
                  : "Create Review Case"}
              </button>
            </div>
          )}
        </section>

        {/* STEP 2 — CASE DETAIL */}
        <section className="mb-6 rounded-2xl border border-white/[0.07] bg-[#0b1120]">
          <div className="border-b border-white/[0.07] p-6">
           <div className="flex items-center gap-3">
  <div>
    <h2 className="text-sm font-semibold text-white">
      Case Detail
    </h2>

                <p className="mt-1 text-xs text-slate-500">
                  Review the assessment attached to the case.
                </p>
              </div>
            </div>
          </div>

          {!reviewCase ? (
            <div className="flex min-h-44 items-center justify-center p-6">
              <div className="text-center">
                <FileSearch
                  size={26}
                  className="mx-auto text-slate-600"
                />

                <p className="mt-3 text-sm text-slate-500">
                  Create a review case to view case details.
                </p>
              </div>
            </div>
          ) : (
            <div className="grid gap-4 p-6 lg:grid-cols-2">
              <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-5">
                <p className="text-[10px] uppercase tracking-wider text-slate-600">
                  Risk reason
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {reviewCase.risk_reason}
                </p>
              </div>

              <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-5">
                <p className="text-[10px] uppercase tracking-wider text-slate-600">
                  Case status
                </p>

                <p className="mt-2 text-sm font-semibold text-indigo-300">
                  {reviewCase.status}
                </p>
              </div>

              {reviewCase.risk_assessment && (
                <>
                  <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-5">
                    <p className="text-[10px] uppercase tracking-wider text-slate-600">
                      Risk assessment
                    </p>

                    <div className="mt-3 flex items-center gap-4">
                      <span className="text-3xl font-bold text-white">
                        {reviewCase.risk_assessment.risk_score}
                      </span>

                      <div>
                        <p
                          className={`inline-flex rounded-lg border px-2 py-1 text-[10px] font-semibold ${severityClasses(
  getSeverity(reviewCase.risk_assessment.risk_score),
)}`}
                        >
                          {severity}
                        </p>

                        
                      </div>
                    </div>
                  </div>

                  <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-5">
                    <p className="text-[10px] uppercase tracking-wider text-slate-600">
                      Payment
                    </p>

                    <p className="mt-2 text-lg font-semibold text-white">
                      #{reviewCase.risk_assessment.payment_id}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Assessment #
                      {reviewCase.risk_assessment.assessment_id}
                    </p>
                  </div>
                </>
              )}

              <div className="lg:col-span-2">
                <p className="mb-3 text-[10px] uppercase tracking-wider text-slate-600">
                  Active risk signals
                </p>

                <div className="flex flex-wrap gap-2">
                  {activeSignals.length > 0 ? (
                    activeSignals.map((signal) => (
                      <span
                        key={signal}
                        className="rounded-lg border border-red-500/10 bg-red-500/[0.05] px-3 py-2 text-xs text-red-300"
                      >
                        {signalLabels[signal] ?? signal}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-600">
                      No active risk signals.
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* STEP 3 — EVIDENCE */}
        <section className="mb-6 rounded-2xl border border-white/[0.07] bg-[#0b1120]">
          <div className="border-b border-white/[0.07] p-6">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
  <div>
    <h2 className="text-sm font-semibold text-white">
      Evidence Checklist
    </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Evidence collected from the real merchant data.
                  </p>
                </div>
              </div>

              {evidenceLoading && (
                <Loader2
                  size={18}
                  className="animate-spin text-indigo-400"
                />
              )}
            </div>
          </div>

          {!reviewCase ? (
            <div className="flex min-h-44 items-center justify-center p-6">
              <p className="text-xs text-slate-600">
                Evidence will appear after a review case is created.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-5">
              
                {[
  {
    label: "Transactions",
    key: "transactions",
    Icon: Activity,
  },
  {
    label: "Refunds",
    key: "refunds",
    Icon: RefreshCw,
  },
  {
    label: "Disputes",
    key: "disputes",
    Icon: AlertTriangle,
  },
  {
    label: "Policies",
    key: "policies",
    Icon: ClipboardCheck,
  },
  {
    label: "Risk signals",
    key: "risk_signals",
    Icon: ShieldAlert,
  },
  ].map(({ label, key, Icon }) => {
                const count =
                  evidenceCounts[
                    key as keyof typeof evidenceCounts
                  ];

                return (
                  <div
                    key={key}
                    className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-4"
                  >
                    <div className="flex items-center justify-between">
                      <Icon
                        size={17}
                        className="text-indigo-400"
                      />

                      {count > 0 ? (
                        <CheckCircle2
                          size={16}
                          className="text-emerald-400"
                        />
                      ) : (
                        <span className="text-[10px] text-slate-600">
                          Empty
                        </span>
                      )}
                    </div>

                    <p className="mt-4 text-xs font-medium text-slate-400">
                      {label}
                    </p>

                    <p className="mt-1 text-2xl font-bold text-white">
                      {count}
                    </p>

                    <p className="mt-1 text-[10px] text-slate-600">
                      records collected
                    </p>
                  </div>
                );
              })}
            </div>
          )}

          {checklist && (
            <div className="border-t border-white/[0.07] p-6">
              <div className="flex items-center gap-2">
                <ClipboardCheck
                  size={17}
                  className="text-indigo-400"
                />

                <h3 className="text-sm font-semibold text-white">
                  AI Evidence Checklist
                </h3>
              </div>

              <div className="mt-4 space-y-3">
  {Array.isArray(checklist?.checklist) &&
  checklist.checklist.length > 0 ? (
    <>
      <div className="flex items-center justify-between rounded-xl border border-amber-500/20 bg-amber-500/[0.06] px-4 py-3">
        <div>
          <p className="text-sm font-medium text-amber-300">
            {checklist.checklist_count ?? checklist.checklist.length}{" "}
            evidence item
            {(checklist.checklist_count ?? checklist.checklist.length) !== 1
              ? "s"
              : ""}{" "}
            missing
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Additional evidence is required for the investigation.
          </p>
        </div>
      </div>

      {checklist.checklist.map((item, index) => {
        const checklistItem = item as {
          category?: string;
          requirement?: string;
          status?: string;
        };

        return (
          <div
            key={`${checklistItem.category ?? "item"}-${index}`}
            className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium capitalize text-white">
                  {checklistItem.category ?? "Evidence"}
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-400">
                  {checklistItem.requirement ??
                    "Additional evidence is required."}
                </p>
              </div>

              <span className="shrink-0 rounded-full border border-amber-500/20 bg-amber-500/10 px-2.5 py-1 text-[11px] font-medium capitalize text-amber-300">
                {checklistItem.status ?? "missing"}
              </span>
            </div>
          </div>
        );
      })}
    </>
  ) : (
    <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/[0.06] px-4 py-3">
      <p className="text-sm font-medium text-emerald-300">
        All required evidence is available.
      </p>
      <p className="mt-1 text-xs text-slate-400">
        No additional evidence is currently missing.
      </p>
    </div>
  )}
</div>
            </div>
          )}

          {checklistLoading && (
            <div className="border-t border-white/[0.07] p-6">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Loader2
                  size={15}
                  className="animate-spin text-indigo-400"
                />
                Generating AI evidence checklist...
              </div>
            </div>
          )}
        </section>

        {/* STEP 4 — AI SUMMARY */}
        <section className="mb-6 rounded-2xl border border-white/[0.07] bg-[#0b1120]">
          <div className="border-b border-white/[0.07] p-6">
            <div className="flex items-center gap-3">
  <div>
    <h2 className="text-sm font-semibold text-white">
      AI-Generated Summary
    </h2>

                <p className="mt-1 text-xs text-slate-500">
                  AI summary generated from the real case analysis and evidence.
                </p>
              </div>
            </div>
          </div>

          <div className="p-6">
  <div className="mb-5 flex items-center justify-between">
    <div>
      <p className="text-xs text-slate-500">
        Generate a case summary from the collected evidence.
      </p>
    </div>

    <button
      type="button"
      onClick={() => {
        if (reviewCase) {
          generateSummary(reviewCase, evidence);
        }
      }}
      disabled={
        summaryLoading ||
        evidenceLoading ||
        !reviewCase ||
        evidenceCounts.transactions +
          evidenceCounts.refunds +
          evidenceCounts.disputes +
          evidenceCounts.policies +
          evidenceCounts.risk_signals ===
          0
      }
      className="inline-flex items-center gap-2 rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-4 py-2.5 text-xs font-medium text-indigo-300 transition hover:bg-indigo-500/20 disabled:cursor-not-allowed disabled:opacity-40"
    >
      {summaryLoading ? (
        <Loader2 size={15} className="animate-spin" />
      ) : (
        <MessageSquareText size={15} />
      )}

      {summaryLoading
        ? "Generating..."
        : summary
          ? "Regenerate Summary"
          : "Generate AI Summary"}
    </button>
  </div>

  {summaryLoading ? (
              <div className="flex min-h-44 items-center justify-center">
                <div className="text-center">
                  <Loader2
                    size={26}
                    className="mx-auto animate-spin text-indigo-400"
                  />

                  <p className="mt-3 text-sm text-slate-400">
                    Generating AI summary...
                  </p>
                </div>
              </div>
            ) : summary ? (
              <div className="rounded-xl border border-indigo-500/10 bg-indigo-500/[0.04] p-5">
                <div className="flex items-center gap-2">
                  <MessageSquareText
                    size={17}
                    className="text-indigo-400"
                  />

                  <h3 className="text-sm font-semibold text-white">
                    Investigation Summary
                  </h3>
                </div>

                {extractText(summary) ? (
                  <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-300">
                    {extractText(summary)}
                  </p>
                ) : (
                  <pre className="mt-4 overflow-x-auto text-xs leading-6 text-slate-400">
                    {JSON.stringify(summary, null, 2)}
                  </pre>
                )}
              </div>
            ) : (
              <div className="flex min-h-44 items-center justify-center text-center">
                <div>
                  <MessageSquareText
                    size={26}
                    className="mx-auto text-slate-600"
                  />

                  <p className="mt-3 text-sm text-slate-500">
                    AI summary will appear after evidence analysis.
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* STEP 5 — TIMELINE */}
        <section className="rounded-2xl border border-white/[0.07] bg-[#0b1120]">
          <div className="border-b border-white/[0.07] p-6">
            <div className="flex items-center gap-3">
  <div>
    <h2 className="text-sm font-semibold text-white">
      Case Timeline
    </h2>

                <p className="mt-1 text-xs text-slate-500">
                  Investigation events recorded by the Risk Review system.
                </p>
              </div>
            </div>
          </div>

          {!reviewCase?.timeline ||
          reviewCase.timeline.length === 0 ? (
            <div className="flex min-h-44 items-center justify-center p-6">
              <div className="text-center">
                <Clock3
                  size={26}
                  className="mx-auto text-slate-600"
                />

                <p className="mt-3 text-sm text-slate-500">
                  No timeline events available.
                </p>
              </div>
            </div>
          ) : (
            <div className="p-6">
              <div className="space-y-4">
                {reviewCase.timeline.map((item, index) => (
                  <div
                    key={`${item.event}-${index}`}
                    className="flex gap-4"
                  >
                    <div className="flex flex-col items-center">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full border border-indigo-500/20 bg-indigo-500/10">
                        <Clock3
                          size={15}
                          className="text-indigo-400"
                        />
                      </div>

                      {index <
                        reviewCase.timeline!.length - 1 && (
                        <div className="mt-2 h-full min-h-8 w-px bg-white/[0.07]" />
                      )}
                    </div>

                    <div className="flex-1 rounded-xl border border-white/[0.07] bg-white/[0.02] p-4">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <p className="text-sm font-medium text-slate-300">
                          {item.event}
                        </p>

                        <span className="rounded-lg border border-indigo-500/10 bg-indigo-500/[0.05] px-2 py-1 text-[10px] font-medium text-indigo-300">
                          {item.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* FOOTER */}
        <div className="mt-6 flex flex-col justify-between gap-3 border-t border-white/[0.06] pt-5 text-[11px] text-slate-600 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Review system operational
          </div>

          <div className="flex items-center gap-4">
            <span>RiskBridge AI</span>
            <span>•</span>
            <span>Risk Review Center</span>
          </div>
        </div>
      </main>
    </div>
  );
}