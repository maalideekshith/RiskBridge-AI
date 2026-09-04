
import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Activity,
  ChevronRight,
  Loader2,
  ShieldAlert,
  Wifi,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

type RiskSignalDetail = {
  detected: boolean;
  current_amount?: string;
  historical_average?: string;
  ratio?: string;
  reason?: string;
};

type RiskSignals = Record<string, RiskSignalDetail>;

type RiskSignalItem = {
  assessment_id: number;
  payment_id: number;
  risk_score: number;
  risk_category: string;
  signals: RiskSignals;
  created_at: string;
};
type RiskAlert = {
  id: number;
  merchant_id: number;
  payment_id: number;
  assessment_id: number;
  severity: string;
  title: string;
  message: string;
  status: string;
  created_at: string;
  read_at: string | null;
  resolved_at: string | null;
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
  return Object.entries(signals ?? {})
    .filter(([, value]) => value?.detected === true)
    .map(([key]) => key);
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

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function RiskMonitor() {
  const navigate = useNavigate();

const [signals, setSignals] = useState<RiskSignalItem[]>([]);
const [alerts, setAlerts] = useState<RiskAlert[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");
const [severityFilter, setSeverityFilter] = useState("All");

  useEffect(() => {
    const loadRiskSignals = async () => {
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

    console.log("RISK MONITOR USER ID:", userId);

    const merchantResponse = await api.get(`/merchants/${userId}`);

    console.log(
      "RISK MONITOR MERCHANT RESPONSE:",
      merchantResponse.data,
    );

    const merchantId =
      merchantResponse.data?.id ??
      merchantResponse.data?.merchant_id;

    if (!merchantId) {
      throw new Error("Merchant ID was not found.");
    }

    console.log("RISK MONITOR MERCHANT ID:", merchantId);

    const paymentsResponse = await api.get(
  `/payments/${merchantId}`,
);

const payments = Array.isArray(paymentsResponse.data)
  ? paymentsResponse.data
  : [];

const assessmentResponses = await Promise.all(
  payments.map((payment: { id: number }) =>
    api.get(`/payments/${payment.id}/risk/assessments`),
  ),
);

const historicalAssessments = assessmentResponses
  .flatMap((response) =>
    Array.isArray(response.data)
      ? response.data
      : [],
  )
  .map((item) => ({
    ...item,
    assessment_id: item.id,
  }));

console.log(
  "NORMALIZED RISK ASSESSMENTS:",
  historicalAssessments,
);

setSignals(historicalAssessments);

const alertsResponse = await api.get(
  `/risk-alerts/${merchantId}`,
);

console.log(
  "RISK ALERT RESPONSE:",
  alertsResponse.data,
);

setAlerts(
  Array.isArray(alertsResponse.data)
    ? alertsResponse.data
    : [],
);
  } catch (err) {
    console.error("FAILED RISK MONITOR:", err);

    if (err instanceof Error) {
      console.error("FAILED RISK MONITOR MESSAGE:", err.message);
    }

    setError("Unable to load risk signals.");
  } finally {
    setLoading(false);
  }
};

    loadRiskSignals();
  }, []);

  const latestSignals = useMemo(() => {
  const filtered =
    severityFilter === "All"
      ? signals
      : signals.filter(
          (item) => getSeverity(item.risk_score) === severityFilter,
        );
  

  const latestByPayment = new Map<number, RiskSignalItem>();

  [...filtered]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() -
        new Date(a.created_at).getTime(),
    )
    .forEach((item) => {
      if (!latestByPayment.has(item.payment_id)) {
        latestByPayment.set(item.payment_id, item);
      }
    });

  return Array.from(latestByPayment.values()).slice(0, 20);
}, [signals, severityFilter]);

const activeSignalCount = useMemo(() => {
  return latestSignals.reduce(
    (total, item) => total + getActiveSignals(item.signals).length,
    0,
  );
}, [latestSignals]);
const timelineData = useMemo(() => {
  const sorted = [...signals].sort(
    (a, b) =>
      new Date(a.created_at).getTime() -
      new Date(b.created_at).getTime(),
  );

  const meaningful = sorted.filter(
    (item, index) =>
      index === 0 ||
      item.risk_score !== sorted[index - 1].risk_score,
  );

  return meaningful.map((item) => ({
    date: new Date(item.created_at).toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    }),
    riskScore: item.risk_score,
    assessmentId: item.assessment_id,
    paymentId: item.payment_id,
    category: item.risk_category,
  }));
}, [signals]);

  return (
  <div className="min-h-screen bg-[#060914] text-white">
     <main className="mx-auto max-w-[1600px] px-5 py-7 sm:px-8 lg:px-10 lg:py-9">
        {/* PAGE HEADER */}
        <div className="mb-8">
          <div className="mb-3 flex items-center gap-2 text-xs font-medium text-slate-500">
            <span>Risk</span>
            <span>/</span>
            <span className="text-indigo-400">Risk Monitor</span>
          </div>

          <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                Risk Monitor
              </h1>

              <p className="mt-2 max-w-2xl text-sm text-slate-400 sm:text-base">
                Monitor active risk signals and identify emerging threats
                across your merchant activity.
              </p>
            </div>

            <div className="flex items-center gap-2 rounded-xl border border-emerald-500/10 bg-emerald-500/[0.05] px-3.5 py-2.5">
              <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50" />
              <span className="text-xs font-medium text-emerald-300">
                Risk engine active
              </span>
            </div>
          </div>
        </div>

        {/* SUMMARY */}
        <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10">
                <Activity size={18} className="text-indigo-400" />
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Assessments
                </p>
                <p className="mt-1 text-2xl font-bold text-white">
                  {signals.length}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10">
                <ShieldAlert size={18} className="text-amber-400" />
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Active signals
                </p>
                <p className="mt-1 text-2xl font-bold text-white">
                  {activeSignalCount}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-[#0b1120] p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10">
                <Wifi size={18} className="text-cyan-400" />
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Monitoring status
                </p>
                <p className="mt-1 text-sm font-semibold text-emerald-300">
                  Live monitoring
                </p>
              </div>
            </div>
          </div>
        </div>
        {/* RISK TIMELINE */}
<section className="mb-6 rounded-2xl border border-white/[0.07] bg-[#0b1120]">
  <div className="border-b border-white/[0.07] p-6">
    <div className="flex items-center gap-2">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10">
        <Activity size={16} className="text-indigo-400" />
      </div>

      <h2 className="text-sm font-semibold text-white">
        Risk Timeline
      </h2>
    </div>

    <p className="mt-2 text-xs text-slate-500">
      Risk score progression across recent merchant activity.
    </p>
  </div>

  <div className="p-6">
    {timelineData.length === 0 ? (
      <div className="flex min-h-64 items-center justify-center">
        <div className="text-center">
          <Activity
            size={28}
            className="mx-auto text-slate-600"
          />

          <p className="mt-3 text-sm font-medium text-slate-400">
            No timeline data available
          </p>

          <p className="mt-1 text-xs text-slate-600">
            Risk assessments will appear here when available.
          </p>
        </div>
      </div>
    ) : (
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={timelineData}
            margin={{
              top: 10,
              right: 20,
              left: 0,
              bottom: 10,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.05)"
            />

            <XAxis
              dataKey="date"
              tick={{
                fill: "#64748b",
                fontSize: 10,
              }}
              tickLine={false}
              axisLine={false}
              minTickGap={60}
            />

            <YAxis
              domain={[0, 100]}
              tick={{
                fill: "#64748b",
                fontSize: 10,
              }}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: "#0b1120",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "10px",
                color: "#fff",
              }}
              labelStyle={{
                color: "#94a3b8",
              }}
              formatter={(value) => [
                value,
                "Risk score",
              ]}
            />

            <Line
              type="monotone"
              dataKey="riskScore"
              stroke="#818cf8"
              strokeWidth={2}
              dot={{
                r: 3,
              }}
              activeDot={{
                r: 5,
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    )}
  </div>
</section>
{/* RISK ALERTS */}
<section className="mb-6 rounded-2xl border border-white/[0.07] bg-[#0b1120]">
  <div className="border-b border-white/[0.07] p-6">
    <div className="flex items-center justify-between gap-4">
      <div>
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500/10">
            <ShieldAlert size={16} className="text-red-400" />
          </div>

          <h2 className="text-sm font-semibold text-white">
            Risk Alerts
          </h2>

          {alerts.length > 0 && (
            <span className="rounded-full border border-red-500/20 bg-red-500/10 px-2 py-0.5 text-[10px] font-semibold text-red-300">
              {alerts.length}
            </span>
          )}
        </div>

        <p className="mt-2 text-xs text-slate-500">
          Active alerts generated by the RiskBridge risk engine.
        </p>
      </div>

      <span className="rounded-lg border border-white/[0.07] bg-white/[0.02] px-3 py-2 text-xs text-slate-500">
        {alerts.filter((alert) => alert.status === "open").length} open
      </span>
    </div>
  </div>

  {alerts.length === 0 ? (
    <div className="flex min-h-40 items-center justify-center p-6">
      <div className="text-center">
        <ShieldAlert
          size={26}
          className="mx-auto text-slate-600"
        />

        <p className="mt-3 text-sm font-medium text-slate-400">
          No risk alerts
        </p>

        <p className="mt-1 max-w-sm text-xs leading-5 text-slate-600">
          New high-risk events will appear here automatically when
          the RiskBridge engine generates an alert.
        </p>
      </div>
    </div>
  ) : (
    <div className="divide-y divide-white/[0.05]">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="group p-5 transition hover:bg-white/[0.02] sm:p-6"
        >
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`rounded-lg border px-2 py-1 text-[10px] font-semibold uppercase ${
                    alert.severity === "high"
                      ? "border-red-500/20 bg-red-500/10 text-red-300"
                      : "border-amber-500/20 bg-amber-500/10 text-amber-300"
                  }`}
                >
                  {alert.severity}
                </span>

                <span
                  className={`rounded-lg border px-2 py-1 text-[10px] font-medium ${
                    alert.status === "open"
                      ? "border-orange-500/20 bg-orange-500/10 text-orange-300"
                      : "border-white/[0.07] bg-white/[0.02] text-slate-400"
                  }`}
                >
                  {alert.status}
                </span>

                <span className="text-xs text-slate-600">
                  Alert #{alert.id}
                </span>
              </div>

              <h3 className="mt-3 text-sm font-semibold text-white">
                {alert.title}
              </h3>

              <p className="mt-1 text-xs leading-5 text-slate-400">
                {alert.message}
              </p>

              <div className="mt-3 flex flex-wrap gap-3 text-[11px] text-slate-600">
                <span>Payment #{alert.payment_id}</span>
                <span>•</span>
                <span>Assessment #{alert.assessment_id}</span>
              </div>
            </div>

            <div className="shrink-0 text-left lg:text-right">
              <p className="text-[10px] uppercase tracking-wider text-slate-600">
                Created
              </p>

              <p className="mt-1 text-xs text-slate-400">
                {formatDate(alert.created_at)}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )}
</section>


        {/* RISK SIGNAL LIST */}
        <section className="rounded-2xl border border-white/[0.07] bg-[#0b1120]">
          <div className="flex flex-col justify-between gap-4 border-b border-white/[0.07] p-6 sm:flex-row sm:items-center">
            <div>
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500/10">
                  <AlertTriangle size={16} className="text-red-400" />
                </div>

                <h2 className="text-sm font-semibold text-white">
                  Risk Signals
                </h2>
              </div>

              <p className="mt-2 text-xs text-slate-500">
                Latest risk assessments detected by the RiskBridge intelligence
                engine.
              </p>
            </div>

            <div className="flex items-center gap-2">
  <div className="flex flex-wrap items-center gap-2">
  {["All", "Critical", "High", "Medium", "Low"].map(
    (severity) => (
      <button
        key={severity}
        type="button"
        onClick={() => setSeverityFilter(severity)}
        className={`rounded-lg border px-3 py-2 text-xs font-medium transition ${
          severityFilter === severity
            ? "border-indigo-500/30 bg-indigo-500/10 text-indigo-300"
            : "border-white/[0.07] bg-white/[0.02] text-slate-400 hover:border-white/[0.12] hover:bg-white/[0.04] hover:text-slate-200"
        }`}
      >
        {severity}
      </button>
    ),
  )}

  <span className="ml-1 rounded-lg border border-white/[0.07] bg-white/[0.02] px-3 py-2 text-xs text-slate-500">
    Showing {latestSignals.length}
  </span>
</div>

  <span className="rounded-lg border border-emerald-500/10 bg-emerald-500/[0.05] px-3 py-2 text-xs text-emerald-300">
    Live
  </span>
</div>
          </div>

          {loading ? (
            <div className="flex min-h-64 items-center justify-center">
              <div className="text-center">
                <Loader2
                  size={24}
                  className="mx-auto animate-spin text-indigo-400"
                />
                <p className="mt-3 text-sm text-slate-400">
                  Loading risk signals...
                </p>
              </div>
            </div>
          ) : error ? (
            <div className="flex min-h-64 items-center justify-center p-6">
              <div className="text-center">
                <AlertTriangle
                  size={24}
                  className="mx-auto text-red-400"
                />
                <p className="mt-3 text-sm font-medium text-slate-300">
                  {error}
                </p>
                <p className="mt-1 text-xs text-slate-600">
                  Check the backend connection and try again.
                </p>
              </div>
            </div>
          ) : latestSignals.length === 0 ? (
            <div className="flex min-h-64 items-center justify-center p-6">
              <div className="text-center">
                <ShieldAlert
                  size={28}
                  className="mx-auto text-slate-600"
                />
                <p className="mt-3 text-sm font-medium text-slate-400">
  {severityFilter === "All"
  ? "No risk signals detected"
  : `No ${severityFilter.toLowerCase()} risk signals found`}

</p>

<p className="mt-1 max-w-sm text-xs leading-5 text-slate-600">
  The RiskBridge engine is monitoring this merchant. New risk
  assessments will appear here automatically when signals are detected.
</p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-white/[0.05]">
              {latestSignals.map((item) => {
  const activeSignals = getActiveSignals(item.signals);
  const severity = getSeverity(item.risk_score);

  return (
    <div
      key={item.assessment_id}
      className="group p-5 transition hover:bg-white/[0.02] sm:p-6"
    >
      <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        
        <div className="min-w-0 flex-1">
          
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`rounded-lg border px-2 py-1 text-[10px] font-semibold ${severityClasses(
                severity,
              )}`}
            >
              {severity}
            </span>

            <span className="text-xs text-slate-600">
              Assessment #{item.assessment_id}
            </span>

            <span className="text-xs text-slate-600">
              Payment #{item.payment_id}
            </span>
          </div>

          {/* RISK SCORE + BAR */}
          <div className="mt-3">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">
                {item.risk_score}
              </span>

              <span className="text-xs text-slate-500">
                risk score
              </span>

              <span className="text-xs text-slate-600">
                •
              </span>

              <span className="text-xs text-slate-400">
                {item.risk_category}
              </span>

              <span className="text-xs text-slate-600">
                •
              </span>

              <span className="text-xs text-slate-400">
                {activeSignals.length}{" "}
                {activeSignals.length === 1 ? "signal" : "signals"}
              </span>
            </div>

            <div className="mt-3 h-1.5 w-full max-w-md overflow-hidden rounded-full bg-white/[0.06]">
              <div
                className="h-full rounded-full bg-indigo-500 transition-all"
                style={{
                  width: `${Math.min(
                    Math.max(item.risk_score, 0),
                    100,
                  )}%`,
                }}
              />
            </div>
          </div>

          {/* ACTIVE SIGNALS */}
          <div className="mt-3 flex flex-wrap gap-2">
            {activeSignals.length > 0 ? (
              activeSignals.map((signal) => (
                <span
                  key={signal}
                  className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1.5 text-[11px] text-slate-300"
                >
                  {signalLabels[signal]}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-600">
                No active signals
              </span>
            )}
          </div>

        </div>

        {/* DETECTED + DETAILS */}
        <div className="flex items-center justify-between gap-5 xl:justify-end">
          <div className="text-left xl:text-right">
            <p className="text-[10px] uppercase tracking-wider text-slate-600">
              Detected
            </p>

            <p className="mt-1 text-xs text-slate-400">
              {formatDate(item.created_at)}
            </p>
          </div>

          <button
  type="button"
  onClick={() =>
    navigate(`/risk-monitor/${item.assessment_id}`)
  }
  className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/[0.07] text-slate-500 transition group-hover:border-indigo-500/20 group-hover:text-indigo-400"
  title="View risk details"
>
  <ChevronRight size={16} />
</button>
        </div>

      </div>
    </div>
  );
})}
            </div>
          )}
        </section>

        {/* FOOTER */}
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

