import { useEffect, useState } from "react";
import {
  Activity,
  ChevronDown,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  TriangleAlert,
  Zap,
} from "lucide-react";
import api from "../services/api";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export default function Dashboard() {
  
const [sidebarOpen, setSidebarOpen] = useState(false);
  const [riskScore, setRiskScore] = useState<number | null>(null);
  const [riskCategory, setRiskCategory] = useState<string>("");
  const [riskLoading, setRiskLoading] = useState(true);
  const [userName, setUserName] = useState("Merchant");
  const [paymentCount, setPaymentCount] = useState(0);
  const [paymentTotal, setPaymentTotal] = useState(0);
  const [refundRate, setRefundRate] = useState(0);
  const [refundTotal, setRefundTotal] = useState(0);
  const [disputeRate, setDisputeRate] = useState(0);
const [activeDisputes, setActiveDisputes] = useState(0);
const [riskTrendPeriod, setRiskTrendPeriod] = useState<
  "7" | "30" | "90" | "all"
>("30");

const [riskTrendMenuOpen, setRiskTrendMenuOpen] = useState(false);
type RiskTrendPoint = {
  id: number;
  payment_id: number;
  risk_score: number;
  risk_category: string;
  created_at: string;
};
type RiskSignalItem = {
  key: string;
  assessment_id: number;
  payment_id: number;
  risk_category: string;
  created_at: string;
};

type RiskSignalDetail = {
  detected: boolean;
  current_amount?: string;
  historical_average?: string;
  ratio?: string;
  reason?: string;
};

type RiskSignalAssessment = {
  assessment_id: number;
  payment_id: number;
  risk_score: number;
  risk_category: string;
  signals: Record<string, RiskSignalDetail>;
  created_at: string;
};

const [riskSignals, setRiskSignals] =
  useState<RiskSignalItem[]>([]);

const [riskSignalsLoading, setRiskSignalsLoading] =
  useState(true);

const [riskTrend, setRiskTrend] = useState<RiskTrendPoint[]>([]);
const [riskTrendLoading, setRiskTrendLoading] = useState(true);
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setRiskLoading(true);

        const token = localStorage.getItem("access_token");

        if (!token) {
          return;
        }

        const payload = JSON.parse(atob(token.split(".")[1]));
const userId = payload.sub;

if (!userId) {
  return;
}

// Get registered user
const userResponse = await api.get("/auth/me");
setUserName(userResponse.data.name);

// Get merchant
const merchantResponse = await api.get(`/merchants/${userId}`);

        const merchantId =
          merchantResponse.data?.id ??
          merchantResponse.data?.merchant_id;

        if (!merchantId) {
          console.error("Merchant ID not found");
          return;
        }
        // Get current risk signals
const riskSignalsResponse = await api.get(
  `/risk/ai/context/risk-signals/${merchantId}`,
);

const riskSignalAssessments: RiskSignalAssessment[] =
  Array.isArray(riskSignalsResponse.data)
    ? riskSignalsResponse.data
    : [];

console.log(
  "DASHBOARD RISK SIGNALS:",
  riskSignalAssessments,
);

// Build a list of recent detected risk signals
const recentSignals: RiskSignalItem[] = [];

for (const assessment of riskSignalAssessments) {
  for (const [key, value] of Object.entries(
    assessment.signals ?? {},
  )) {
    if (value?.detected === true) {
      recentSignals.push({
        key,
        assessment_id: assessment.assessment_id,
        payment_id: assessment.payment_id,
        risk_category: assessment.risk_category,
        created_at: assessment.created_at,
      });
    }
  }
}

// API already returns newest assessments first.
// Keep only the latest 10 detected signals.
setRiskSignals(recentSignals.slice(0, 10));

setRiskSignalsLoading(false);

        // Get all payments
        const paymentsResponse = await api.get(
          `/payments/${merchantId}`,
        );

        const payments = Array.isArray(paymentsResponse.data)
          ? paymentsResponse.data
          : paymentsResponse.data?.payments ?? [];

        console.log("Dashboard payments:", payments);

        // Payment metrics
        setPaymentCount(payments.length);

        const total = payments.reduce(
          (sum: number, payment: { amount: string | number }) =>
            sum + Number(payment.amount),
          0,
        );

        setPaymentTotal(total);

        // Get refunds for every payment
        const refundResponses = await Promise.allSettled(
          payments.map(async (payment: { id: number }) => {
            const response = await api.get(
              `/payments/${payment.id}/refunds`,
            );

            console.log(
              `Refunds for payment ${payment.id}:`,
              response.data,
            );

            return response;
          }),
        );

        // Collect successful refund responses
        const refunds = refundResponses.flatMap((result) => {
          if (result.status !== "fulfilled") {
            console.log(
              "Refund request failed:",
              result.reason,
            );
            return [];
          }

          return Array.isArray(result.value.data)
            ? result.value.data
            : [];
        });

        console.log("ALL DASHBOARD REFUNDS:", refunds);

        // Calculate total refunded amount
        const totalRefunded = refunds.reduce(
          (sum: number, refund: { amount: string | number }) =>
            sum + Number(refund.amount),
          0,
        );

        // Calculate refund percentage
        const calculatedRefundRate =
          total > 0
            ? (totalRefunded / total) * 100
            : 0;

        console.log("TOTAL REFUNDED:", totalRefunded);
        console.log("REFUND RATE:", calculatedRefundRate);

        setRefundTotal(totalRefunded);
        setRefundRate(calculatedRefundRate);
        // Get disputes for every payment
const disputeResponses = await Promise.allSettled(
  payments.map(async (payment: { id: number }) => {
    const response = await api.get(
      `/payments/${payment.id}/disputes`,
    );

    console.log(
      `Disputes for payment ${payment.id}:`,
      response.data,
    );

    return response;
  }),
);

// Collect successful dispute responses
const disputes = disputeResponses.flatMap((result) => {
  if (result.status !== "fulfilled") {
    console.log(
      "Dispute request failed:",
      result.reason,
    );
    return [];
  }

  return Array.isArray(result.value.data)
    ? result.value.data
    : [];
});

console.log("ALL DASHBOARD DISPUTES:", disputes);

// Count active disputes
const openedDisputes = disputes.filter(
  (dispute: { status: string }) =>
    dispute.status.toLowerCase() === "opened",
);

const activeDisputeCount = openedDisputes.length;

// Calculate dispute rate
const calculatedDisputeRate =
  payments.length > 0
    ? (activeDisputeCount / payments.length) * 100
    : 0;

console.log("ACTIVE DISPUTES:", activeDisputeCount);
console.log("DISPUTE RATE:", calculatedDisputeRate);

setActiveDisputes(activeDisputeCount);
setDisputeRate(calculatedDisputeRate);
        // Get risk assessments for every payment
        const riskAssessmentResponses = await Promise.allSettled(
          payments.map(async (payment: { id: number }) => {
            const response = await api.get(
              `/payments/${payment.id}/risk/assessments`,
            );

            console.log(
              `Risk assessments for payment ${payment.id}:`,
              response.data,
            );

            return response;
          }),
        );

        // Collect successful risk assessment responses
        const riskAssessments = riskAssessmentResponses.flatMap(
          (result) => {
            if (result.status !== "fulfilled") {
              console.log(
                "Risk assessment request failed:",
                result.reason,
              );
              return [];
            }

            return Array.isArray(result.value.data)
              ? result.value.data
              : [];
          },
        );

        console.log(
          "ALL DASHBOARD RISK ASSESSMENTS:",
          riskAssessments,
        );

        // Sort assessments chronologically
        const sortedRiskAssessments = [...riskAssessments]
  .filter(
    (assessment: RiskTrendPoint) =>
      assessment.created_at &&
      typeof assessment.risk_score === "number",
  )
  .sort(
    (a: RiskTrendPoint, b: RiskTrendPoint) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  );

// Keep only the latest assessment for each calendar day
// Keep every assessment so same-day risk activity
// is visible as a real-time timeline.
const detailedRiskTrend = sortedRiskAssessments;

setRiskTrend(detailedRiskTrend);
setRiskTrendLoading(false);
        // Get latest payment for risk score
        if (payments.length === 0) {
  setRiskCategory("No payment data");
  setRiskTrend([]);
  setRiskTrendLoading(false);
  return;
}

        const latestPayment = payments[0];

        const paymentId =
          latestPayment?.id ??
          latestPayment?.payment_id;

        if (!paymentId) {
          console.error("Payment ID not found");
          return;
        }

        // Get risk score
        const riskResponse = await api.get(
          `/payments/${paymentId}/risk/score`,
        );

        setRiskScore(riskResponse.data.risk_score);
        setRiskCategory(riskResponse.data.risk_category);
      } catch (error) {
        console.error(
          "Failed to load dashboard data:",
          error,
        );
        setRiskCategory("Unavailable");
      } finally {
        setRiskLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const stats = [
    {
      label: "Risk Score",
      value: riskLoading
        ? "..."
        : riskScore !== null
          ? String(riskScore)
          : "—",
      description: riskLoading
        ? "Calculating risk..."
        : riskCategory,
      trend: "Live",
      trendType: "up",
      icon: ShieldCheck,
    },
    {
      label: "Payments",
      value: paymentCount.toLocaleString(),
      description: `₹${paymentTotal.toLocaleString("en-IN")} processed`,
      trend: "Live",
      trendType: "positive",
      icon: Activity,
    },
    {
      label: "Refunds",
      value: `${refundRate.toFixed(1)}%`,
      description: `₹${refundTotal.toLocaleString("en-IN")} refunded`,
      trend: "Live",
      trendType: "negative",
      icon: TrendingUp,
    },
    {
  label: "Disputes",
  value: `${disputeRate.toFixed(1)}%`,
  description: `${activeDisputes} active disputes`,
  trend: "Live",
  trendType: "negative",
  icon: TriangleAlert,
},
  ];


  return (
    <div className="min-h-screen bg-[#060914] text-white">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
        />
      )}

      
        {/* DASHBOARD CONTENT */}
<main className="mx-auto max-w-[1600px] px-5 py-7 sm:px-8 lg:px-10 lg:py-9">
          {/* PAGE HEADER */}
          <div className="mb-8 flex flex-col justify-between gap-5 xl:flex-row xl:items-end">
            <div>
              <div className="mb-3 flex items-center gap-2 text-xs font-medium text-slate-500">
                <span>Overview</span>
                <span>/</span>
                <span className="text-indigo-400">Dashboard</span>
              </div>

              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
  Hi, {userName} 👋
</h1>

<p className="mt-2 text-sm font-medium text-slate-300 sm:text-base">
  Risk Intelligence Overview
</p>

<p className="mt-1 text-sm text-slate-500">
  Monitor your merchant activity, risk exposure, and emerging signals in real time.
</p>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 rounded-xl border border-emerald-500/10 bg-emerald-500/[0.05] px-3.5 py-2.5">
                <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50" />
                <span className="text-xs font-medium text-emerald-300">
                  Risk engine active
                </span>
              </div>

              <button
                type="button"
                className="hidden items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-white/[0.05] hover:text-white sm:flex"
              >
                <Zap size={15} />
                Live data
              </button>
            </div>
          </div>

          {/* STAT CARDS */}
<div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
  

  {stats.map((stat) => {
              const Icon = stat.icon;

              return (
                <div
                  key={stat.label}
                  className="group relative overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5 transition duration-200 hover:-translate-y-0.5 hover:border-indigo-500/20"
                >
                  <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-indigo-500/[0.04] blur-2xl transition group-hover:bg-indigo-500/[0.08]" />

                  <div className="relative flex items-start justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.04] text-slate-400">
                      <Icon size={19} />
                    </div>

                    <span
                      className={`rounded-lg px-2 py-1 text-[10px] font-semibold ${
                        stat.trendType === "negative"
                          ? "bg-red-500/10 text-red-300"
                          : stat.trendType === "up"
                            ? "bg-amber-500/10 text-amber-300"
                            : "bg-emerald-500/10 text-emerald-300"
                      }`}
                    >
                      {stat.trend}
                    </span>
                  </div>

                  <p className="relative mt-5 text-xs font-medium uppercase tracking-wider text-slate-500">
                    {stat.label}
                  </p>

                  <div className="relative mt-2 flex items-baseline gap-2">
                    <p className="text-3xl font-bold tracking-tight text-white">
                      {stat.value}
                    </p>
                  </div>

                  <p className="relative mt-1 text-xs text-slate-600">
                    {stat.description}
                  </p>
                </div>
              );
            })}
          </div>

          
          {/* LOWER DASHBOARD */}
          <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_380px]">
            {/* RISK TREND */}
            <section className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-6">
              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10">
                      <TrendingDown
                        size={15}
                        className="text-indigo-400"
                      />
                    </div>

                    <h2 className="text-sm font-semibold text-white">
                      Risk trend
                    </h2>
                  </div>

                  <p className="mt-2 text-xs text-slate-500">
                    Risk score movement over the selected period
                  </p>
                </div>

                {/* PERIOD SELECTOR */}
                <div className="relative self-start">
                  <button
                    type="button"
                    onClick={() =>
                      setRiskTrendMenuOpen((open) => !open)
                    }
                    className="flex items-center gap-2 rounded-lg border border-white/[0.07] px-3 py-2 text-xs text-slate-400 transition hover:bg-white/[0.04] hover:text-white"
                  >
                    {riskTrendPeriod === "7"
                      ? "Last 7 days"
                      : riskTrendPeriod === "30"
                        ? "Last 30 days"
                        : riskTrendPeriod === "90"
                          ? "Last 90 days"
                          : "All time"}

                    <ChevronDown
                      size={13}
                      className={`transition-transform ${
                        riskTrendMenuOpen ? "rotate-180" : ""
                      }`}
                    />
                  </button>

                  {riskTrendMenuOpen && (
                    <div className="absolute right-0 top-full z-30 mt-2 w-36 overflow-hidden rounded-xl border border-white/[0.08] bg-[#0f172a] p-1 shadow-xl">
                      {[
                        { value: "7", label: "Last 7 days" },
                        { value: "30", label: "Last 30 days" },
                        { value: "90", label: "Last 90 days" },
                        { value: "all", label: "All time" },
                      ].map((option) => (
                        <button
                          key={option.value}
                          type="button"
                          onClick={() => {
                            setRiskTrendPeriod(
                              option.value as
                                | "7"
                                | "30"
                                | "90"
                                | "all",
                            );
                            setRiskTrendMenuOpen(false);
                          }}
                          className={`w-full rounded-lg px-3 py-2 text-left text-xs transition ${
                            riskTrendPeriod === option.value
                              ? "bg-indigo-500/10 text-indigo-300"
                              : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
                          }`}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* RISK TREND CHART */}
              <div className="mt-8 h-64">
                {riskTrendLoading ? (
                  <div className="flex h-full items-center justify-center rounded-xl border border-white/[0.07] bg-white/[0.01]">
                    <div className="text-center">
                      <Activity
                        size={20}
                        className="mx-auto animate-pulse text-indigo-400"
                      />

                      <p className="mt-3 text-sm text-slate-400">
                        Loading risk trend...
                      </p>
                    </div>
                  </div>
                ) : (
                  (() => {
                    const filteredRiskTrend =
                      riskTrend.filter((assessment) => {
                        if (riskTrendPeriod === "all") {
                          return true;
                        }

                        const days = Number(riskTrendPeriod);

                        const cutoff = new Date();
                        cutoff.setDate(
                          cutoff.getDate() - days,
                        );

                        return (
                          new Date(assessment.created_at) >=
                          cutoff
                        );
                      });

                    if (filteredRiskTrend.length === 0) {
                      return (
                        <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-white/[0.07] bg-white/[0.01]">
                          <div className="text-center">
                            <Activity
                              size={20}
                              className="mx-auto text-slate-600"
                            />

                            <p className="mt-3 text-sm font-medium text-slate-400">
                              No risk assessment data
                            </p>

                            <p className="mt-1 text-xs text-slate-600">
                              No assessments are available for this period.
                            </p>
                          </div>
                        </div>
                      );
                    }

                    return (
                      <ResponsiveContainer
                        width="100%"
                        height="100%"
                      >
                        <LineChart
                          data={filteredRiskTrend}
                          margin={{
                            top: 10,
                            right: 10,
                            left: -20,
                            bottom: 0,
                          }}
                        >
                          <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="rgba(255,255,255,0.06)"
                          />

                          <XAxis
                            dataKey="created_at"
                            tickFormatter={(value) =>
    new Date(value).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }
                            tick={{
                              fill: "#64748b",
                              fontSize: 11,
                            }}
                            axisLine={false}
                            tickLine={false}
                          />

                          <YAxis
                            domain={[0, 100]}
                            tick={{
                              fill: "#64748b",
                              fontSize: 11,
                            }}
                            axisLine={false}
                            tickLine={false}
                          />

                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#0f172a",
                              border:
                                "1px solid rgba(255,255,255,0.1)",
                              borderRadius: "10px",
                              color: "#fff",
                            }}
                            labelFormatter={(value) =>
  new Date(String(value)).toLocaleString(
                                "en-IN",
                                {
                                  day: "2-digit",
                                  month: "short",
                                  year: "numeric",
                                  hour: "2-digit",
                                  minute: "2-digit",
                                },
                              )
                            }
                            formatter={(value) => [
                              `${value}`,
                              "Risk score",
                            ]}
                          />

                          <Line
                            type="monotone"
                            dataKey="risk_score"
                            name="Risk score"
                            stroke="#818cf8"
                            strokeWidth={2}
                            dot={{
                              r: 4,
                              strokeWidth: 2,
                            }}
                            activeDot={{
                              r: 6,
                            }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    );
                  })()
                )}
              </div>
            </section>

            {/* RISK SIGNALS */}
            <section className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-6">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500/10">
                      <TriangleAlert
                        size={15}
                        className="text-red-400"
                      />
                    </div>

                    <h2 className="text-sm font-semibold text-white">
                      Risk signals
                    </h2>
                  </div>

                  <p className="mt-2 text-xs text-slate-500">
                    Signals requiring attention
                  </p>
                </div>

                <span className="rounded-lg bg-red-500/10 px-2 py-1 text-[10px] font-semibold text-red-300">
  {riskSignals.length} recent
</span>
              </div>

              <div className="mt-6 space-y-3">
  {riskSignalsLoading ? (
    <div className="py-8 text-center text-xs text-slate-500">
      Loading risk signals...
    </div>
  ) : (
    (() => {
      if (riskSignals.length === 0) {
        return (
          <div className="py-8 text-center text-xs text-slate-500">
            No recent risk signals
          </div>
        );
      }

      return riskSignals.map((signal, index) => (
        <RiskSignal
          key={`${signal.assessment_id}-${signal.key}-${index}`}
          severity={
  signal.risk_category.toLowerCase() as
    | "critical"
    | "high"
    | "medium"
    | "low"
}
          title={formatRiskSignalName(signal.key)}
          description={`Detected • Assessment #${signal.assessment_id}`}
        />
      ));
    })()
  )}
</div>

              
            </section>
          </div>



          {/* FOOTER STATUS */}
          <div className="mt-6 flex flex-col justify-between gap-3 border-t border-white/[0.06] pt-5 text-[11px] text-slate-600 sm:flex-row sm:items-center">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              All systems operational
            </div>

            <div className="flex items-center gap-4">
              <span>RiskBridge AI</span>
              <span>•</span>
              <span>Real-time risk intelligence</span>
            </div>
          </div>
        </main>
        
      </div>
    
  );
}

function RiskSignal({
  severity,
  title,
  description,
}: {
  severity: "critical" | "high" | "medium" | "low";
  title: string;
  description: string;
}) {
  const styles = {
  critical: {
    dot: "bg-red-400",
    badge: "bg-red-500/10 text-red-300",
    label: "Critical",
  },
  high: {
    dot: "bg-orange-400",
    badge: "bg-orange-500/10 text-orange-300",
    label: "High",
  },
  medium: {
    dot: "bg-amber-400",
    badge: "bg-amber-500/10 text-amber-300",
    label: "Medium",
  },
  low: {
    dot: "bg-emerald-400",
    badge: "bg-emerald-500/10 text-emerald-300",
    label: "Low",
  },
};
  const style = styles[severity];

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.015] p-3.5 transition hover:border-white/[0.1] hover:bg-white/[0.025]">
      <div className="flex items-start gap-3">
        <span
          className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${style.dot}`}
        />

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-xs font-semibold text-slate-200">
              {title}
            </p>

            <span
              className={`rounded-md px-1.5 py-0.5 text-[9px] font-semibold ${style.badge}`}
            >
              {style.label}
            </span>
          </div>

          <p className="mt-1 text-[11px] leading-5 text-slate-600">
            {description}
          </p>
        </div>
      </div>
    </div>
  );
}
function formatRiskSignalName(key: string) {
  const names: Record<string, string> = {
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
    customer_history: "Customer history",
    customer_average: "Customer average",
    device_ip_anomaly: "Device / IP anomaly",
    geographic_anomaly: "Geographic anomaly",
    behavior_change: "Behavior change",
  };

  return names[key] ?? key.replaceAll("_", " ");
}
