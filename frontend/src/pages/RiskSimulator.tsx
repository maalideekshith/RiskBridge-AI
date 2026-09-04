
import { useEffect, useState } from "react";
import axios from "axios";
import {
  ArrowLeft,
  FlaskConical,
  RotateCcw,
  Play,
  SlidersHorizontal,
  AlertTriangle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

type Scenario = {
  refundRate: number;
  disputeRate: number;
  transactionVolume: number;
  highValueTransactions: number;
  failedPayments: number;
};
type SimulationResult = {
  merchant_id: number;
  current_risk_score: number;
  projected_risk_score: number;
  risk_change: number;
  current_refund_rate: number;
  projected_refund_rate: number;
  current_dispute_rate: number;
  projected_dispute_rate: number;
  current_transaction_volume: number;
  projected_transaction_volume: number;
  projected_high_value_transactions: number;
  projected_failed_payments: number;
  status: string;
};
type AIExplanation = {
  scenario: string;
  explanation: string;
};
type AIRecommendation = {
  scenario: string;
  recommendation: string;
};
type MerchantProfile = {
  id: number;
  user_id: number;
  business_name: string;
  business_type: string;
  website: string | null;
  country: string;
  currency: string;
};

const DEFAULT_SCENARIO: Scenario = {
  refundRate: 5,
  disputeRate: 2,
  transactionVolume: 100,
  highValueTransactions: 10,
  failedPayments: 3,
};
const getAccessToken = (): string | null => {
  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token")
  );
};

const getUserIdFromToken = (
  token: string,
): number | null => {
  try {
    const payload = JSON.parse(
      atob(token.split(".")[1]),
    );

    const userId =
      payload.sub ??
      payload.user_id ??
      payload.id;

    const parsedUserId = Number(userId);

    return Number.isFinite(parsedUserId)
      ? parsedUserId
      : null;
  } catch {
    return null;
  }
};
export default function RiskSimulator() {
  const navigate = useNavigate();

  const [merchantId, setMerchantId] =
    useState<number | null>(null);

  const [isLoadingMerchant, setIsLoadingMerchant] =
    useState(true);

  const [merchantError, setMerchantError] =
    useState<string | null>(null);

  const [isSimulating, setIsSimulating] =
    useState(false);

  const [simulationResult, setSimulationResult] =
    useState<SimulationResult | null>(null);
 const [aiExplanation, setAIExplanation] =
  useState<AIExplanation | null>(null);

const [isLoadingExplanation, setIsLoadingExplanation] =
  useState(false);

const [explanationError, setExplanationError] =
  useState<string | null>(null);
  const [aiRecommendation, setAIRecommendation] =
  useState<AIRecommendation | null>(null);

const [isLoadingRecommendation, setIsLoadingRecommendation] =
  useState(false);

const [recommendationError, setRecommendationError] =
  useState<string | null>(null);

  const [simulationError, setSimulationError] =
    useState<string | null>(null);

  const [scenario, setScenario] =
    useState<Scenario>(DEFAULT_SCENARIO);

  const [scenarioName, setScenarioName] = useState(
    "Custom Risk Scenario",
  );
 useEffect(() => {
  const loadMerchant = async () => {
    setIsLoadingMerchant(true);
    setMerchantError(null);

    try {
      const token = getAccessToken();

      if (!token) {
        throw new Error(
          "Authentication token not found. Please log in again.",
        );
      }

      const userId = getUserIdFromToken(token);

      if (!userId) {
        throw new Error(
          "Unable to identify logged-in user from authentication token.",
        );
      }

      const response = await axios.get<MerchantProfile>(
        `http://127.0.0.1:8000/merchants/${userId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      setMerchantId(response.data.id);
    } catch (error) {
      console.error("Failed to load merchant:", error);

      if (axios.isAxiosError(error)) {
        setMerchantError(
          error.response?.data?.detail ||
            "Unable to load merchant profile.",
        );
      } else if (error instanceof Error) {
        setMerchantError(error.message);
      } else {
        setMerchantError(
          "Unable to load merchant profile.",
        );
      }
    } finally {
      setIsLoadingMerchant(false);
    }
  };

  loadMerchant();
}, []);
  const updateScenario = (
    field: keyof Scenario,
    value: number,
  ) => {
    setScenario((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const resetScenario = () => {
  setScenarioName("Custom Risk Scenario");
  setScenario(DEFAULT_SCENARIO);
  setSimulationResult(null);
  setSimulationError(null);
  setAIExplanation(null);
  setExplanationError(null);
  setAIRecommendation(null);
  setRecommendationError(null);
};

const runSimulation = async () => {
  if (!merchantId) {
    setSimulationError(
      "Merchant profile is not available yet.",
    );
    return;
  }

  setIsSimulating(true);
setSimulationError(null);
setSimulationResult(null);

  try {
    const token = getAccessToken();

    if (!token) {
      setSimulationError(
        "You are not authenticated. Please log in again.",
      );
      return;
    }

    const paymentsResponse = await axios.get(
      `http://127.0.0.1:8000/payments/${merchantId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const payments = Array.isArray(paymentsResponse.data)
      ? paymentsResponse.data
      : paymentsResponse.data?.payments ?? [];

    const currentTransactionVolume = payments.length;

    const transactionVolumeChange =
      currentTransactionVolume > 0
        ? ((scenario.transactionVolume -
            currentTransactionVolume) /
            currentTransactionVolume) *
          100
        : 0;

    const response = await axios.post<SimulationResult>(
  "http://127.0.0.1:8000/api/simulation/risk",
  {
    merchant_id: merchantId,
    refund_rate: scenario.refundRate,
    dispute_rate: scenario.disputeRate,
    transaction_volume_change:
      transactionVolumeChange,
    high_value_transactions:
      scenario.highValueTransactions,
    failed_payments:
      scenario.failedPayments,
  },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    setSimulationResult(response.data);
  } catch (error) {
    console.error(
      "Risk simulation failed:",
      error,
    );

    if (axios.isAxiosError(error)) {
      setSimulationError(
        error.response?.data?.detail ||
          "Unable to run the risk simulation.",
      );
    } else {
      setSimulationError(
        "Unable to run the risk simulation.",
      );
    }
  } finally {
    setIsSimulating(false);
  }
};
const generateAIExplanation = async () => {
  if (!merchantId) {
    setExplanationError(
      "Merchant profile is not available yet.",
    );
    return;
  }

  if (!simulationResult) {
    setExplanationError(
      "Run the simulation before generating an AI explanation.",
    );
    return;
  }

  setIsLoadingExplanation(true);
  setExplanationError(null);

  try {
    const token = getAccessToken();

    if (!token) {
      setExplanationError(
        "You are not authenticated. Please log in again.",
      );
      return;
    }

    const scenarioDescription =
      `The merchant's refund rate changes to ${scenario.refundRate}%, ` +
      `dispute rate changes to ${scenario.disputeRate}%, ` +
      `transaction volume changes to ${scenario.transactionVolume}, ` +
      `high-value transactions are ${scenario.highValueTransactions}, ` +
      `and failed payments are ${scenario.failedPayments}`;

    const response = await axios.post<AIExplanation>(
      "http://127.0.0.1:8000/what-if/explain",
      {
        scenario: scenarioDescription,
        impact: simulationResult,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      },
    );

    setAIExplanation(response.data);
  } catch (error) {
    console.error(
      "AI risk explanation failed:",
      error,
    );

    if (axios.isAxiosError(error)) {
      setExplanationError(
        error.response?.data?.detail ||
          "Unable to generate AI risk explanation.",
      );
    } else if (error instanceof Error) {
      setExplanationError(error.message);
    } else {
      setExplanationError(
        "Unable to generate AI risk explanation.",
      );
    }
  } finally {
    setIsLoadingExplanation(false);
  }
};
const generateAIRecommendation = async () => {
  if (!merchantId) {
    setRecommendationError(
      "Merchant profile is not available yet.",
    );
    return;
  }

  if (!simulationResult) {
    setRecommendationError(
      "Run a risk simulation before generating recommendations.",
    );
    return;
  }

  setIsLoadingRecommendation(true);
  setRecommendationError(null);

  try {
    const token = getAccessToken();

    if (!token) {
      setRecommendationError(
        "You are not authenticated. Please log in again.",
      );
      return;
    }

    const response = await axios.post<AIRecommendation>(
      "http://127.0.0.1:8000/what-if/recommend",
      {
        scenario:
  `The merchant's refund rate changes to ${scenario.refundRate}%, ` +
  `dispute rate changes to ${scenario.disputeRate}%, ` +
  `transaction volume changes to ${scenario.transactionVolume}, ` +
  `high-value transactions are ${scenario.highValueTransactions}, ` +
  `and failed payments are ${scenario.failedPayments}`,
          

        interpretation: {
          refund_rate: scenario.refundRate,
          dispute_rate: scenario.disputeRate,
          transaction_volume_change:
            simulationResult.current_transaction_volume > 0
              ? ((scenario.transactionVolume -
                  simulationResult.current_transaction_volume) /
                  simulationResult.current_transaction_volume) *
                100
              : null,
        },

        impact: simulationResult,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      },
    );

    setAIRecommendation(response.data);
  } catch (error) {
    console.error(
      "AI risk recommendation failed:",
      error,
    );

    if (axios.isAxiosError(error)) {
      setRecommendationError(
        error.response?.data?.detail ||
          "Unable to generate recommended action.",
      );
    } else if (error instanceof Error) {
      setRecommendationError(error.message);
    } else {
      setRecommendationError(
        "Unable to generate recommended action.",
      );
    }
  } finally {
    setIsLoadingRecommendation(false);
  }
};


  return (
    <div className="w-full">
  <main className="mx-auto max-w-[1600px] px-5 pt-0 pb-7 sm:px-8 sm:pt-1 lg:px-10 lg:pt-2 lg:pb-9">
        

        {/* HEADER */}
        <div className="mt-8">
          <div className="mb-3 flex items-center gap-2 text-xs font-medium text-slate-500">
            <span>Risk</span>
            <span>/</span>
            <span>Intelligence</span>
            <span>/</span>
            <span className="text-indigo-400">
              Risk Simulator
            </span>
          </div>

          <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-indigo-500/20 bg-indigo-500/10">
                  <FlaskConical
                    size={21}
                    className="text-indigo-400"
                  />
                </div>

                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                    Risk Simulator
                  </h1>

                  <p className="mt-1 text-sm text-slate-400">
                    Model how changes in merchant activity could
                    affect payment risk.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 rounded-xl border border-indigo-500/10 bg-indigo-500/[0.06] px-4 py-2.5">
              <SlidersHorizontal
                size={15}
                className="text-indigo-400"
              />

              <span className="text-xs font-medium text-indigo-300">
                Scenario Analysis
              </span>
            </div>
          </div>
        </div>
                {/* MERCHANT STATUS */}
        {isLoadingMerchant && (
          <section className="mt-6 rounded-2xl border border-indigo-500/20 bg-indigo-500/[0.05] p-4">
            <p className="text-xs text-indigo-300">
              Loading merchant profile...
            </p>
          </section>
        )}

        {merchantError && (
          <section className="mt-6 rounded-2xl border border-red-500/20 bg-red-500/[0.05] p-4">
            <div className="flex items-center gap-3">
              <AlertTriangle
                size={16}
                className="text-red-400"
              />

              <p className="text-xs text-red-300">
                {merchantError}
              </p>
            </div>
          </section>
        )}

        {!isLoadingMerchant &&
          !merchantError &&
          merchantId && (
            <section className="mt-6 rounded-2xl border border-emerald-500/10 bg-emerald-500/[0.04] p-4">
              <p className="text-xs text-emerald-300">
                Merchant profile loaded · Merchant ID:{" "}
                <span className="font-semibold">
                  {merchantId}
                </span>
              </p>
            </section>
          )}

        

        {/* MAIN GRID */}
        <div className="mt-6 grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
          {/* SCENARIO INPUT */}
          <section className="rounded-2xl border border-white/[0.07] bg-[#0b1120]">
            <div className="border-b border-white/[0.07] p-6">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10">
                  <SlidersHorizontal
                    size={16}
                    className="text-indigo-400"
                  />
                </div>

                <div>
                  <h2 className="text-sm font-semibold text-white">
                    Scenario Input
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Define the merchant conditions you want to
                    simulate.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-6 p-6">
              {/* SCENARIO NAME */}
              <div>
                <label
                  htmlFor="scenario-name"
                  className="mb-2 block text-xs font-medium text-slate-400"
                >
                  Scenario name
                </label>

                <input
                  id="scenario-name"
                  type="text"
                  value={scenarioName}
                  onChange={(event) =>
                    setScenarioName(event.target.value)
                  }
                  placeholder="Enter scenario name"
                  className="w-full rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-indigo-500/40 focus:bg-indigo-500/[0.03]"
                />
              </div>

              {/* REFUND RATE */}
              <div>
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="refund-rate"
                    className="text-sm font-medium text-slate-300"
                  >
                    Refund rate
                  </label>

                  <span className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1 text-xs font-semibold text-slate-300">
                    {scenario.refundRate}%
                  </span>
                </div>

                <div className="mt-4">
  <input
    id="refund-rate"
    type="range"
    min="0"
    max="100"
    step="0.5"
    value={scenario.refundRate}
    onChange={(event) =>
      updateScenario(
        "refundRate",
        Number(event.target.value),
      )
    }
    className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/[0.08] accent-indigo-500"
  />

  <div className="mt-2 flex justify-between text-[10px] text-slate-600">
    <span>0%</span>
    <span>50%</span>
    <span>100%</span>
  </div>
</div>

                <p className="mt-2 text-xs text-slate-600">
                  Percentage of transactions expected to be
                  refunded.
                </p>
              </div>

              {/* DISPUTE RATE */}
              <div>
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="dispute-rate"
                    className="text-sm font-medium text-slate-300"
                  >
                    Dispute rate
                  </label>

                  <span className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1 text-xs font-semibold text-slate-300">
                    {scenario.disputeRate}%
                  </span>
                </div>

                <div className="mt-4">
  <input
    id="dispute-rate"
    type="range"
    min="0"
    max="100"
    step="0.5"
    value={scenario.disputeRate}
    onChange={(event) =>
      updateScenario(
        "disputeRate",
        Number(event.target.value),
      )
    }
    className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/[0.08] accent-indigo-500"
  />

  <div className="mt-2 flex justify-between text-[10px] text-slate-600">
    <span>0%</span>
    <span>50%</span>
    <span>100%</span>
  </div>
</div>

                <p className="mt-2 text-xs text-slate-600">
                  Percentage of transactions expected to result
                  in disputes.
                </p>
              </div>

              {/* TRANSACTION VOLUME */}
              <div>
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="transaction-volume"
                    className="text-sm font-medium text-slate-300"
                  >
                    Transaction volume
                  </label>

                  <span className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1 text-xs font-semibold text-slate-300">
                    {scenario.transactionVolume}
                  </span>
                </div>

                <div className="mt-4">
  <input
    id="transaction-volume"
    type="range"
    min="0"
    max="1000"
    step="10"
    value={scenario.transactionVolume}
    onChange={(event) =>
      updateScenario(
        "transactionVolume",
        Number(event.target.value),
      )
    }
    className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/[0.08] accent-indigo-500"
  />

  <div className="mt-2 flex justify-between text-[10px] text-slate-600">
    <span>0</span>
    <span>500</span>
    <span>1,000</span>
  </div>
</div>

                <p className="mt-2 text-xs text-slate-600">
                  Expected number of transactions in the
                  simulation period.
                </p>
              </div>

              {/* HIGH VALUE TRANSACTIONS */}
              <div>
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="high-value-transactions"
                    className="text-sm font-medium text-slate-300"
                  >
                    High-value transactions
                  </label>

                  <span className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1 text-xs font-semibold text-slate-300">
                    {scenario.highValueTransactions}
                  </span>
                </div>

                <div className="mt-4">
  <input
    id="high-value-transactions"
    type="range"
    min="0"
    max="500"
    step="5"
    value={scenario.highValueTransactions}
    onChange={(event) =>
      updateScenario(
        "highValueTransactions",
        Number(event.target.value),
      )
    }
    className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/[0.08] accent-indigo-500"
  />

  <div className="mt-2 flex justify-between text-[10px] text-slate-600">
    <span>0</span>
    <span>250</span>
    <span>500</span>
  </div>
</div>

                <p className="mt-2 text-xs text-slate-600">
                  Number of transactions expected to exceed the
                  merchant's normal value range.
                </p>
              </div>

              {/* FAILED PAYMENTS */}
              <div>
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="failed-payments"
                    className="text-sm font-medium text-slate-300"
                  >
                    Failed payments
                  </label>

                  <span className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1 text-xs font-semibold text-slate-300">
                    {scenario.failedPayments}
                  </span>
                </div>

               <div className="mt-4">
  <input
    id="failed-payments"
    type="range"
    min="0"
    max="500"
    step="1"
    value={scenario.failedPayments}
    onChange={(event) =>
      updateScenario(
        "failedPayments",
        Number(event.target.value),
      )
    }
    className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/[0.08] accent-indigo-500"
  />

  <div className="mt-2 flex justify-between text-[10px] text-slate-600">
    <span>0</span>
    <span>250</span>
    <span>500</span>
  </div>
</div>

                <p className="mt-2 text-xs text-slate-600">
                  Expected failed payment attempts during the
                  simulation period.
                </p>
              </div>
            </div>
          </section>

          {/* SCENARIO SUMMARY */}
          <section className="h-fit rounded-2xl border border-white/[0.07] bg-[#0b1120]">
            <div className="border-b border-white/[0.07] p-6">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-600">
                Scenario Preview
              </p>

              <h2 className="mt-2 text-base font-semibold text-white">
                {scenarioName || "Untitled Scenario"}
              </h2>
            </div>

            <div className="space-y-3 p-6">
              <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3">
                <span className="text-xs text-slate-500">
                  Refund rate
                </span>

                <span className="text-sm font-semibold text-white">
                  {scenario.refundRate}%
                </span>
              </div>

              <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3">
                <span className="text-xs text-slate-500">
                  Dispute rate
                </span>

                <span className="text-sm font-semibold text-white">
                  {scenario.disputeRate}%
                </span>
              </div>

              <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3">
                <span className="text-xs text-slate-500">
                  Transaction volume
                </span>

                <span className="text-sm font-semibold text-white">
                  {scenario.transactionVolume}
                </span>
              </div>

              <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3">
                <span className="text-xs text-slate-500">
                  High-value transactions
                </span>

                <span className="text-sm font-semibold text-white">
                  {scenario.highValueTransactions}
                </span>
              </div>

              <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3">
                <span className="text-xs text-slate-500">
                  Failed payments
                </span>

                <span className="text-sm font-semibold text-white">
                  {scenario.failedPayments}
                </span>
              </div>
            </div>

            {/* INFO */}
            <div className="mx-6 mb-6 rounded-xl border border-amber-500/10 bg-amber-500/[0.04] p-4">
              <div className="flex gap-3">
                <AlertTriangle
                  size={16}
                  className="mt-0.5 shrink-0 text-amber-400"
                />

                <p className="text-xs leading-5 text-slate-500">
                  These values describe a hypothetical merchant
                  scenario. No production payment data will be
                  modified.
                </p>
              </div>
            </div>

            {/* ACTIONS */}
            <div className="flex gap-3 border-t border-white/[0.07] p-6">
              <button
                type="button"
                onClick={resetScenario}
                className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-3 text-sm font-medium text-slate-400 transition hover:bg-white/[0.05] hover:text-white"
              >
                <RotateCcw size={15} />
                Reset
              </button>

             <button
  type="button"
  onClick={runSimulation}
  disabled={isSimulating || isLoadingMerchant || !merchantId}
  className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
>
  <Play size={15} />

  {isLoadingMerchant
    ? "Loading Merchant..."
    : isSimulating
      ? "Running..."
      : "Run Simulation"}
</button>
            </div>
          </section>
        </div>

       {/* SIMULATION RESULT */}
{simulationError && (
  <section className="mt-6 rounded-2xl border border-red-500/20 bg-red-500/[0.05] p-6">
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-500/10">
        <AlertTriangle
          size={16}
          className="text-red-400"
        />
      </div>

      <div>
        <h3 className="text-sm font-semibold text-red-300">
          Simulation failed
        </h3>

        <p className="mt-1 text-xs leading-5 text-red-300/70">
          {simulationError}
        </p>
      </div>
    </div>
  </section>
)}

{simulationResult && (
  <section className="mt-6 rounded-2xl border border-white/[0.07] bg-[#0b1120]">
    <div className="border-b border-white/[0.07] p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-indigo-400">
              Projected Score
          </p>

          <h2 className="mt-2 text-lg font-semibold text-white">
            Simulation analysis
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            Projected risk based on the configured merchant scenario.
          </p>
        </div>

        <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/10 px-4 py-2 text-xs font-semibold text-indigo-300">
          {simulationResult.status}
        </div>
      </div>
    </div>

    <div className="grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-3">
      {/* CURRENT RISK */}
      <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-5">
        <p className="text-xs text-slate-500">
          Current Risk Score
        </p>

        <p className="mt-3 text-3xl font-bold text-white">
          {simulationResult.current_risk_score.toFixed(1)}
        </p>

        <p className="mt-1 text-[11px] text-slate-600">
          Current merchant risk
        </p>
      </div>

      {/* PROJECTED RISK */}
      <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/[0.06] p-5">
        <p className="text-xs text-indigo-300">
          Projected Risk Score
        </p>

        <p className="mt-3 text-3xl font-bold text-white">
          {simulationResult.projected_risk_score.toFixed(1)}
        </p>

        <p className="mt-1 text-[11px] text-indigo-300/60">
          After scenario simulation
        </p>
      </div>

      {/* RISK CHANGE */}
      <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-5">
        <p className="text-xs text-slate-500">
          Risk Change
        </p>

        <p className="mt-3 text-3xl font-bold text-white">
          {simulationResult.risk_change > 0 ? "+" : ""}
          {simulationResult.risk_change.toFixed(1)}
        </p>

        <p className="mt-1 text-[11px] text-slate-600">
          Change in projected risk
        </p>
      </div>
    </div>

    {/* COMPARISON */}
    <div className="grid gap-4 border-t border-white/[0.07] p-6 lg:grid-cols-3">
      {/* REFUND */}
      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
        <p className="text-xs font-medium text-slate-400">
          Refund Rate
        </p>

        <div className="mt-3 flex items-end justify-between">
          <div>
            <p className="text-[10px] text-slate-600">
              Current
            </p>

            <p className="text-lg font-semibold text-white">
              {simulationResult.current_refund_rate}%
            </p>
          </div>

          <span className="text-slate-600">
            →
          </span>

          <div className="text-right">
            <p className="text-[10px] text-slate-600">
              Projected
            </p>

            <p className="text-lg font-semibold text-indigo-300">
              {simulationResult.projected_refund_rate}%
            </p>
          </div>
        </div>
      </div>

      {/* DISPUTE */}
      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
        <p className="text-xs font-medium text-slate-400">
          Dispute Rate
        </p>

        <div className="mt-3 flex items-end justify-between">
          <div>
            <p className="text-[10px] text-slate-600">
              Current
            </p>

            <p className="text-lg font-semibold text-white">
              {simulationResult.current_dispute_rate}%
            </p>
          </div>

          <span className="text-slate-600">
            →
          </span>

          <div className="text-right">
            <p className="text-[10px] text-slate-600">
              Projected
            </p>

            <p className="text-lg font-semibold text-indigo-300">
              {simulationResult.projected_dispute_rate}%
            </p>
          </div>
        </div>
      </div>

      {/* VOLUME */}
      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
        <p className="text-xs font-medium text-slate-400">
          Transaction Volume
        </p>

        <div className="mt-3 flex items-end justify-between">
          <div>
            <p className="text-[10px] text-slate-600">
              Current
            </p>

            <p className="text-lg font-semibold text-white">
              {simulationResult.current_transaction_volume}
            </p>
          </div>

          <span className="text-slate-600">
            →
          </span>

          <div className="text-right">
            <p className="text-[10px] text-slate-600">
              Projected
            </p>

            <p className="text-lg font-semibold text-indigo-300">
              {simulationResult.projected_transaction_volume}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div className="border-t border-white/[0.07] px-6 py-4">
      <p className="text-xs leading-5 text-slate-600">
        The projected score is calculated by the RiskBridge AI
simulation engine using the configured refund rate,
dispute rate, transaction volume, high-value transactions,
and failed payment scenario.
      </p>
    </div>
  </section>
)}
{simulationResult && (
  <section className="mt-6 rounded-2xl border border-indigo-500/20 bg-[#0b1120]">
    {/* STEP 4 HEADER */}
    <div className="border-b border-white/[0.07] p-6">
      <div className="flex items-start gap-4">
        <div>
  <h2 className="text-lg font-semibold text-white">
    AI Risk Explanation
  </h2>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Understand how the configured scenario affects
            projected merchant risk in clear, actionable language.
          </p>
        </div>
      </div>
    </div>

    {/* STEP 4 CONTENT */}
    <div className="p-6">
      {!aiExplanation && !explanationError && (
        <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium text-slate-300">
                Generate AI explanation
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-600">
                The AI will explain the projected risk impact of
                the scenario you just simulated.
              </p>
            </div>

            <button
              type="button"
              onClick={generateAIExplanation}
              disabled={isLoadingExplanation}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <FlaskConical size={15} />

              {isLoadingExplanation
                ? "Analyzing..."
                : "Generate Explanation"}
            </button>
          </div>
        </div>
      )}

      {/* ERROR */}
      {explanationError && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/[0.05] p-5">
          <div className="flex items-start gap-3">
            <AlertTriangle
              size={16}
              className="mt-0.5 shrink-0 text-red-400"
            />

            <div>
              <p className="text-sm font-semibold text-red-300">
                AI explanation failed
              </p>

              <p className="mt-1 text-xs leading-5 text-red-300/70">
                {explanationError}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* AI EXPLANATION */}
      {aiExplanation && (
        <div className="space-y-5">
          {/* SCENARIO */}
          <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-indigo-400">
              Scenario
            </p>

            <p className="mt-3 text-sm leading-6 text-slate-300">
              {aiExplanation.scenario}
            </p>
          </div>

          {/* AI EXPLANATION */}
          <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/[0.05] p-5">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-indigo-400">
              AI Explanation
            </p>

            <p className="mt-3 text-sm leading-6 text-slate-300">
              {aiExplanation.explanation}
            </p>
          </div>

          {/* REGENERATE */}
          <div className="flex justify-end">
            <button
              type="button"
              onClick={generateAIExplanation}
              disabled={isLoadingExplanation}
              className="inline-flex items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-2.5 text-xs font-medium text-slate-400 transition hover:bg-white/[0.05] hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              <RotateCcw size={14} />

              {isLoadingExplanation
                ? "Analyzing..."
                : "Regenerate Explanation"}
            </button>
          </div>
        </div>
      )}
    </div>
  </section>
)}
{simulationResult && (
  <section className="mt-6 rounded-2xl border border-indigo-500/20 bg-[#0b1120]">
    {/* STEP 5 HEADER */}
    <div className="border-b border-white/[0.07] p-6">
  <div>
    <h2 className="text-lg font-semibold text-white">
      Recommended Actions
    </h2>

    <p className="mt-1 text-xs leading-5 text-slate-500">
      Get a practical merchant action based on the
      projected What-If risk scenario.
    </p>
  </div>
</div>

    {/* STEP 5 CONTENT */}
    <div className="p-6">
      {!aiRecommendation && !recommendationError && (
        <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium text-slate-300">
                Generate recommended action
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-600">
                The AI will recommend a practical action based
                on the simulated risk impact.
              </p>
            </div>

            <button
              type="button"
              onClick={generateAIRecommendation}
              disabled={isLoadingRecommendation}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <FlaskConical size={15} />

              {isLoadingRecommendation
                ? "Analyzing..."
                : "Generate Recommendation"}
            </button>
          </div>
        </div>
      )}

      {/* ERROR */}
      {recommendationError && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/[0.05] p-5">
          <div className="flex items-start gap-3">
            <AlertTriangle
              size={16}
              className="mt-0.5 shrink-0 text-red-400"
            />

            <div>
              <p className="text-sm font-semibold text-red-300">
                Recommendation failed
              </p>

              <p className="mt-1 text-xs leading-5 text-red-300/70">
                {recommendationError}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* RECOMMENDATION */}
      {aiRecommendation && (
        <div className="space-y-5">
          {/* SCENARIO */}
          <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-indigo-400">
              Scenario
            </p>

            <p className="mt-3 text-sm leading-6 text-slate-300">
              {aiRecommendation.scenario}
            </p>
          </div>

          {/* RECOMMENDED ACTION */}
          <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/[0.05] p-5">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-indigo-400">
              Recommended Action
            </p>

            <p className="mt-3 text-sm leading-6 text-slate-300">
              {aiRecommendation.recommendation}
            </p>
          </div>

          {/* REGENERATE */}
          <div className="flex justify-end">
            <button
              type="button"
              onClick={generateAIRecommendation}
              disabled={isLoadingRecommendation}
              className="inline-flex items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-2.5 text-xs font-medium text-slate-400 transition hover:bg-white/[0.05] hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              <RotateCcw size={14} />

              {isLoadingRecommendation
                ? "Analyzing..."
                : "Regenerate Recommendation"}
            </button>
          </div>
        </div>
      )}
    </div>
  </section>
)}
      </main>
    </div>
  );
}

