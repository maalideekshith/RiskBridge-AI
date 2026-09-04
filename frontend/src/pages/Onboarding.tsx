import { useState } from "react";
import type { FormEvent } from "react";
import {
  ArrowRight,
  Check,
  Globe,
  ShieldCheck,
  CreditCard,
  RefreshCw,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Onboarding() {
  const navigate = useNavigate();

  const [step, setStep] = useState<1 | 2>(1);

  const [businessName, setBusinessName] = useState("");
  const [businessType, setBusinessType] = useState("");
  const [website, setWebsite] = useState("");
  const [country, setCountry] = useState("India");
  const [currency, setCurrency] = useState("INR");

  const [connecting, setConnecting] = useState(false);
  const [connected, setConnected] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleMerchantSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setError("");

    if (!businessName.trim() || !businessType.trim()) {
      setError(
        "Please enter your business name and business type.",
      );
      return;
    }

    try {
      setLoading(true);

      const userResponse = await api.get("/auth/me");
      const userId = userResponse.data?.id;

      if (!userId) {
        throw new Error("Unable to identify your account.");
      }

      await api.post(`/merchants/${userId}`, {
        business_name: businessName.trim(),
        business_type: businessType.trim(),
        website: website.trim() || null,
        country: country.trim(),
        currency: currency.trim().toUpperCase(),
      });

      setStep(2);
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to create your merchant profile.";

      setError(
        Array.isArray(message)
          ? message.map((item) => item.msg).join(", ")
          : message,
      );
    } finally {
      setLoading(false);
    }
  };

  const handleConnectRazorpay = async () => {
    setError("");

    try {
      setConnecting(true);

      const response = await api.post(
        "/integrations/razorpay/connect",
      );

      if (response.data?.status === "connected") {
        setConnected(true);
      } else {
        throw new Error(
          "Razorpay connection could not be confirmed.",
        );
      }
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to connect Razorpay.";

      setError(
        Array.isArray(message)
          ? message.map((item) => item.msg).join(", ")
          : message,
      );
    } finally {
      setConnecting(false);
    }
  };

  const handleContinueToDashboard = async () => {
  setError("");

  try {
    setLoading(true);

    await api.post("/audit-logs/onboarding-completed");

    navigate("/dashboard", { replace: true });
  } catch (err: any) {
    const message =
      err?.response?.data?.detail ||
      err?.message ||
      "Unable to complete onboarding.";

    setError(
      Array.isArray(message)
        ? message.map((item) => item.msg).join(", ")
        : message,
    );
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="min-h-screen bg-[#070b14] text-white">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl items-center px-6 py-12 sm:px-10">
        <div className="grid w-full overflow-hidden rounded-3xl border border-white/10 bg-[#0b1120] shadow-2xl lg:grid-cols-[0.9fr_1.1fr]">
          {/* LEFT */}
          <div className="relative overflow-hidden border-b border-white/10 bg-gradient-to-br from-indigo-950/70 via-[#0a1020] to-[#070b14] p-8 sm:p-10 lg:border-b-0 lg:border-r lg:p-12">
            <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-indigo-600/20 blur-3xl" />
            <div className="absolute -bottom-24 -left-24 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />

            <div className="relative">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-600/30">
                  <ShieldCheck size={24} strokeWidth={2.5} />
                </div>

                <div>
                  <div className="text-xl font-bold">
                    RiskBridge AI
                  </div>

                  <div className="text-xs text-slate-400">
                    Payment Risk Intelligence
                  </div>
                </div>
              </div>

              <div className="mt-16">
                <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-indigo-400/20 bg-indigo-500/10 px-3 py-1.5 text-sm text-indigo-300">
                  <Check size={15} />
                  Account created
                </div>

                <h1 className="text-4xl font-bold leading-tight tracking-tight">
                  Connect your
                  <span className="block bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                    payment data.
                  </span>
                </h1>

                <p className="mt-5 max-w-md text-sm leading-7 text-slate-400">
                  Connect your Razorpay account so RiskBridge AI can
                  analyze your payment activity and identify risk
                  signals automatically.
                </p>
              </div>

              <div className="mt-10 space-y-4">
                <OnboardingBenefit
                  text="Create your merchant profile"
                  active={step >= 1}
                />

                <OnboardingBenefit
                  text="Connect your Razorpay data"
                  active={step >= 2}
                />

                <OnboardingBenefit
                  text="Monitor payment risk with AI"
                  active={connected}
                />
              </div>
            </div>
          </div>

          {/* RIGHT */}
          <div className="p-8 sm:p-10 lg:p-12">
            {step === 1 ? (
              <>
                <div className="mb-8">
                  <p className="mb-3 text-sm font-medium text-indigo-400">
                    STEP 1 OF 2
                  </p>

                  <h2 className="text-3xl font-bold tracking-tight">
                    Tell us about your business
                  </h2>

                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    This information will be used to create your
                    merchant profile.
                  </p>
                </div>

                {error && (
                  <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                    {error}
                  </div>
                )}

                <form
                  onSubmit={handleMerchantSubmit}
                  className="space-y-5"
                >
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">
                      Business name
                    </label>

                    <input
                      type="text"
                      value={businessName}
                      onChange={(event) =>
                        setBusinessName(event.target.value)
                      }
                      placeholder="Your company or business name"
                      autoComplete="organization"
                      className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3.5 text-white placeholder:text-slate-600 outline-none transition focus:border-indigo-500 focus:bg-white/[0.06] focus:ring-4 focus:ring-indigo-500/10"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">
                      Business type
                    </label>

                    <input
                      type="text"
                      value={businessType}
                      onChange={(event) =>
                        setBusinessType(event.target.value)
                      }
                      placeholder="e.g. E-commerce, SaaS, Marketplace"
                      className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3.5 text-white placeholder:text-slate-600 outline-none transition focus:border-indigo-500 focus:bg-white/[0.06] focus:ring-4 focus:ring-indigo-500/10"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">
                      Website
                      <span className="ml-2 text-xs font-normal text-slate-600">
                        Optional
                      </span>
                    </label>

                    <div className="relative">
                      <Globe
                        size={17}
                        className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600"
                      />

                      <input
                        type="url"
                        value={website}
                        onChange={(event) =>
                          setWebsite(event.target.value)
                        }
                        placeholder="https://yourcompany.com"
                        autoComplete="url"
                        className="w-full rounded-xl border border-white/10 bg-white/[0.04] py-3.5 pl-11 pr-4 text-white placeholder:text-slate-600 outline-none transition focus:border-indigo-500 focus:bg-white/[0.06] focus:ring-4 focus:ring-indigo-500/10"
                      />
                    </div>
                  </div>

                  <div className="grid gap-5 sm:grid-cols-2">
                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-300">
                        Country
                      </label>

                      <select
                        value={country}
                        onChange={(event) =>
                          setCountry(event.target.value)
                        }
                        className="w-full rounded-xl border border-white/10 bg-[#101827] px-4 py-3.5 text-white outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                      >
                        <option value="India">India</option>
                        <option value="United States">
                          United States
                        </option>
                        <option value="United Kingdom">
                          United Kingdom
                        </option>
                        <option value="Singapore">
                          Singapore
                        </option>
                        <option value="Australia">
                          Australia
                        </option>
                      </select>
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-300">
                        Currency
                      </label>

                      <select
                        value={currency}
                        onChange={(event) =>
                          setCurrency(event.target.value)
                        }
                        className="w-full rounded-xl border border-white/10 bg-[#101827] px-4 py-3.5 text-white outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                      >
                        <option value="INR">
                          INR — Indian Rupee
                        </option>
                        <option value="USD">
                          USD — US Dollar
                        </option>
                        <option value="GBP">
                          GBP — British Pound
                        </option>
                        <option value="SGD">
                          SGD — Singapore Dollar
                        </option>
                        <option value="AUD">
                          AUD — Australian Dollar
                        </option>
                      </select>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="group mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3.5 font-semibold text-white shadow-lg shadow-indigo-600/20 transition hover:bg-indigo-500 hover:shadow-indigo-600/30 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {loading
                      ? "Creating profile..."
                      : "Continue"}

                    {!loading && (
                      <ArrowRight
                        size={18}
                        className="transition-transform group-hover:translate-x-1"
                      />
                    )}
                  </button>
                </form>
              </>
            ) : (
              <>
                <div className="mb-8">
                  <p className="mb-3 text-sm font-medium text-indigo-400">
                    STEP 2 OF 2
                  </p>

                  <h2 className="text-3xl font-bold tracking-tight">
                    Connect Razorpay
                  </h2>

                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    Connect your Razorpay payment data to start
                    monitoring transactions, refunds, disputes, and
                    risk signals.
                  </p>
                </div>

                {error && (
                  <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                    {error}
                  </div>
                )}

                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                  <div className="flex items-start gap-4">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400">
                      <CreditCard size={23} />
                    </div>

                    <div>
                      <h3 className="font-semibold text-white">
                        Razorpay
                      </h3>

                      <p className="mt-1 text-sm text-slate-400">
                        Payment data integration
                      </p>
                    </div>

                    {connected && (
                      <div className="ml-auto flex items-center gap-1.5 rounded-full border border-emerald-400/20 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
                        <Check size={13} />
                        Connected
                      </div>
                    )}
                  </div>

                  <div className="mt-6 space-y-3">
                    <ConnectionFeature text="Payments and transaction activity" />
                    <ConnectionFeature text="Refund and dispute activity" />
                    <ConnectionFeature text="Risk signals for AI analysis" />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={
                    connected
                      ? handleContinueToDashboard
                      : handleConnectRazorpay
                  }
                  disabled={connecting}
                  className="group mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3.5 font-semibold text-white shadow-lg shadow-indigo-600/20 transition hover:bg-indigo-500 hover:shadow-indigo-600/30 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {connecting ? (
                    <>
                      <RefreshCw
                        size={18}
                        className="animate-spin"
                      />
                      Connecting Razorpay...
                    </>
                  ) : connected ? (
                    <>
                      Continue to Dashboard
                      <ArrowRight
                        size={18}
                        className="transition-transform group-hover:translate-x-1"
                      />
                    </>
                  ) : (
                    <>
                      Connect Razorpay
                      <ArrowRight
                        size={18}
                        className="transition-transform group-hover:translate-x-1"
                      />
                    </>
                  )}
                </button>

                <div className="mt-6 flex items-start gap-2 text-xs leading-5 text-slate-600">
                  <ShieldCheck
                    size={14}
                    className="mt-0.5 shrink-0"
                  />
                  RiskBridge AI uses your connected payment data for
                  risk monitoring and analysis.
                </div>
              </>
            )}

            <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-600">
              <ShieldCheck size={14} />
              Your merchant information is protected
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function OnboardingBenefit({
  text,
  active,
}: {
  text: string;
  active: boolean;
}) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`flex h-7 w-7 items-center justify-center rounded-full ${
          active
            ? "bg-emerald-500/10 text-emerald-400"
            : "bg-white/5 text-slate-600"
        }`}
      >
        <Check size={14} strokeWidth={3} />
      </div>

      <span
        className={`text-sm ${
          active ? "text-slate-300" : "text-slate-600"
        }`}
      >
        {text}
      </span>
    </div>
  );
}

function ConnectionFeature({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-300">
      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
        <Check size={13} strokeWidth={3} />
      </div>

      {text}
    </div>
  );
}