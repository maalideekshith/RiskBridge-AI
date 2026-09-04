import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Bot,
  CheckCircle2,
  Clock,
  FileText,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import api from "../services/api";

interface AuditLogEntry {
  id: number;
  merchant_id: number;
  user_id: number | null;
  action: string;
  entity_type: string | null;
  entity_id: number | null;
  description: string;
  created_at: string;
}

const actionConfig: Record<
  string,
  {
    label: string;
    icon: typeof Activity;
  }
> = {
  ONBOARDING_COMPLETED: {
    label: "Onboarding completed",
    icon: CheckCircle2,
  },
  RAZORPAY_CONNECTED: {
    label: "Razorpay connected",
    icon: ShieldCheck,
  },
  RAZORPAY_SYNCED: {
    label: "Razorpay synchronized",
    icon: RefreshCw,
  },
  RISK_ASSESSMENT_CREATED: {
    label: "Risk assessment created",
    icon: Activity,
  },
  RISK_ALERT_CREATED: {
    label: "Risk alert created",
    icon: AlertTriangle,
  },
  RISK_REVIEW_CASE_CREATED: {
    label: "Review case created",
    icon: FileText,
  },
  RISK_REVIEW_CASE_STATUS_CHANGED: {
    label: "Review case status changed",
    icon: Clock,
  },
  AI_EVIDENCE_CHECKLIST_GENERATED: {
    label: "AI evidence checklist generated",
    icon: Bot,
  },
  AI_CASE_SUMMARY_GENERATED: {
    label: "AI case summary generated",
    icon: Bot,
  },
  AI_RISK_INVESTIGATION_GENERATED: {
    label: "AI risk investigation generated",
    icon: Bot,
  },
  AI_RISK_EXPLANATION_GENERATED: {
    label: "AI risk explanation generated",
    icon: Bot,
  },
  AI_RISK_RECOMMENDATION_GENERATED: {
    label: "AI risk recommendation generated",
    icon: Bot,
  },
};

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function AuditLog() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAuditLogs = async () => {
    try {
      setLoading(true);
      setError("");

      const userResponse = await api.get("/auth/me");
      const userId = userResponse.data?.id;

      if (!userId) {
        throw new Error("User ID is not available.");
      }

      const merchantResponse = await api.get(`/merchants/${userId}`);
      const merchantId = merchantResponse.data?.id;

      if (!merchantId) {
        throw new Error("Merchant ID is not available.");
      }

      const response = await api.get(`/audit-logs/${merchantId}`);

      setLogs(response.data ?? []);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load audit logs.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLogs();
  }, []);

  return (
    <main className="min-h-[calc(100vh-5rem)] px-5 py-6 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10">
                <FileText size={18} className="text-indigo-400" />
              </div>

              <span className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-400">
                Compliance
              </span>
            </div>

            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Audit Log
            </h1>

            <p className="mt-2 max-w-2xl text-sm text-slate-500">
              Track important merchant, risk, review, and AI activity across
              RiskBridge.
            </p>
          </div>

          <button
            type="button"
            onClick={loadAuditLogs}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-white/[0.06] hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={loading ? "animate-spin" : ""}
            />
            Refresh
          </button>
        </div>

        {/* Summary */}
        <div className="mb-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-5">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-600">
              Total events
            </p>
            <p className="mt-2 text-2xl font-bold text-white">
              {logs.length}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-5">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-600">
              AI events
            </p>
            <p className="mt-2 text-2xl font-bold text-white">
              {
                logs.filter((log) =>
                  log.action.startsWith("AI_"),
                ).length
              }
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-5">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-600">
              Risk events
            </p>
            <p className="mt-2 text-2xl font-bold text-white">
              {
                logs.filter((log) =>
                  log.action.startsWith("RISK_"),
                ).length
              }
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-hidden rounded-2xl border border-white/[0.07] bg-white/[0.02]">
          {loading ? (
            <div className="flex min-h-80 items-center justify-center">
              <div className="flex items-center gap-3 text-sm text-slate-500">
                <RefreshCw size={17} className="animate-spin" />
                Loading audit activity...
              </div>
            </div>
          ) : error ? (
            <div className="flex min-h-80 flex-col items-center justify-center px-6 text-center">
              <AlertTriangle size={28} className="text-red-400" />
              <p className="mt-4 text-sm font-medium text-slate-200">
                Unable to load audit logs
              </p>
              <p className="mt-2 max-w-md text-sm text-slate-500">
                {error}
              </p>

              <button
                type="button"
                onClick={loadAuditLogs}
                className="mt-5 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500"
              >
                Try again
              </button>
            </div>
          ) : logs.length === 0 ? (
            <div className="flex min-h-80 flex-col items-center justify-center px-6 text-center">
              <FileText size={30} className="text-slate-600" />
              <p className="mt-4 text-sm font-medium text-slate-300">
                No audit activity yet
              </p>
              <p className="mt-2 text-sm text-slate-600">
                Important merchant and risk events will appear here.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-white/[0.06]">
              {logs.map((log) => {
                const config = actionConfig[log.action];
                const Icon = config?.icon ?? Activity;
                const label = config?.label ?? log.action.replaceAll("_", " ");

                return (
                  <div
                    key={log.id}
                    className="flex flex-col gap-4 px-5 py-5 transition hover:bg-white/[0.02] sm:flex-row sm:items-start sm:px-6"
                  >
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-500/10">
                      <Icon size={18} className="text-indigo-400" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                        <h2 className="text-sm font-semibold capitalize text-slate-200">
                          {label}
                        </h2>

                        <time className="text-xs text-slate-600">
                          {formatDate(log.created_at)}
                        </time>
                      </div>

                      <p className="mt-1 text-sm leading-6 text-slate-500">
                        {log.description}
                      </p>

                      <div className="mt-3 flex flex-wrap gap-2">
                        <span className="rounded-lg border border-white/[0.06] bg-white/[0.025] px-2.5 py-1 text-[11px] text-slate-500">
                          {log.action}
                        </span>

                        {log.entity_type && (
                          <span className="rounded-lg border border-white/[0.06] bg-white/[0.025] px-2.5 py-1 text-[11px] text-slate-500">
                            {log.entity_type}
                            {log.entity_id !== null
                              ? ` #${log.entity_id}`
                              : ""}
                          </span>
                        )}

                        {log.user_id !== null && (
                          <span className="rounded-lg border border-white/[0.06] bg-white/[0.025] px-2.5 py-1 text-[11px] text-slate-500">
                            User #{log.user_id}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}