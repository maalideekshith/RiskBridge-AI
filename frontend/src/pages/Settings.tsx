
import { useEffect, useState } from "react";
import { Check, Edit3, Lock, Mail, ShieldCheck, User } from "lucide-react";
import api from "../services/api";

type UserProfile = {
  id: number;
  name: string;
  email: string;
};
type MerchantProfile = {
  id: number;
  business_name: string;
  business_type: string;
  website?: string | null;
  country: string;
  currency: string;
  user_id: number;
};

type RazorpayStatus = {
  merchant_id: number;
  provider: string;
  status: string;
  last_synced_at?: string | null;
};

export default function Settings() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [name, setName] = useState("");
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [merchant, setMerchant] = useState<MerchantProfile | null>(null);
const [razorpay, setRazorpay] = useState<RazorpayStatus | null>(null);
const [merchantLoading, setMerchantLoading] = useState(true);
const [razorpayLoading, setRazorpayLoading] = useState(true);

  useEffect(() => {
  const loadProfile = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/auth/me");

      setProfile(response.data);
      setName(response.data.name);

      try {
        setMerchantLoading(true);

        const merchantResponse = await api.get(
          `/merchants/${response.data.id}`,
        );

        setMerchant(merchantResponse.data);
      } catch (err) {
        console.error("Unable to load merchant profile:", err);
      } finally {
        setMerchantLoading(false);
      }

      try {
        setRazorpayLoading(true);

        const razorpayResponse = await api.get(
          "/integrations/razorpay/status",
        );
        console.log("RAZORPAY STATUS:", razorpayResponse.data);

        setRazorpay(razorpayResponse.data);
      } catch (err) {
        console.error("Unable to load Razorpay status:", err);
      } finally {
        setRazorpayLoading(false);
      }
    } catch (err) {
      console.error(err);
      setError("Unable to load your account details.");
    } finally {
      setLoading(false);
    }
  };

  loadProfile();
}, []);

  const handleSave = async () => {
    const trimmedName = name.trim();

    if (!trimmedName) {
      setError("Name cannot be empty.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMessage("");

      const response = await api.put("/auth/me", {
        name: trimmedName,
      });

      setProfile(response.data);
      setName(response.data.name);
      setEditing(false);
      setMessage("Your name has been updated successfully.");

      setTimeout(() => {
        setMessage("");
      }, 3000);
    } catch (err: any) {
      console.error(err);

      setError(
        err?.response?.data?.detail ||
          "Unable to update your name. Please try again.",
      );
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setName(profile?.name ?? "");
    setEditing(false);
    setError("");
  };

  return (
    <div className="min-h-screen bg-[#060914] text-white">
      <main className="mx-auto max-w-[1400px] px-5 py-7 sm:px-8 lg:px-10 lg:py-9">
        {/* HEADER */}
        <div className="mb-8">
          <p className="mb-2 text-xs font-medium uppercase tracking-[0.16em] text-indigo-400">
            Account
          </p>

          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                Settings
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Manage your RiskBridge AI account and security preferences.
              </p>
            </div>
          </div>
        </div>

        {/* SUCCESS */}
        {message && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/[0.07] px-4 py-3 text-sm text-emerald-300">
            <Check size={17} />
            {message}
          </div>
        )}

        {/* ERROR */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/[0.07] px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[1.35fr_1fr]">
          {/* ACCOUNT CARD */}
          <section className="overflow-hidden rounded-2xl border border-white/[0.07] bg-white/[0.025]">
            <div className="border-b border-white/[0.06] px-6 py-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10">
                  <User size={19} className="text-indigo-400" />
                </div>

                <div>
                  <h2 className="text-base font-semibold text-slate-100">
                    Account information
                  </h2>
                  <p className="mt-1 text-xs text-slate-500">
                    Your registered RiskBridge AI account details.
                  </p>
                </div>
              </div>
            </div>

            <div className="p-6">
              {loading ? (
                <div className="space-y-5">
                  <div className="h-16 animate-pulse rounded-xl bg-white/[0.04]" />
                  <div className="h-16 animate-pulse rounded-xl bg-white/[0.04]" />
                  <div className="h-16 animate-pulse rounded-xl bg-white/[0.04]" />
                </div>
              ) : profile ? (
                <div className="space-y-5">
                  {/* NAME */}
                  <div>
                    <div className="mb-2 flex items-center justify-between">
                      <label className="text-xs font-medium uppercase tracking-wider text-slate-500">
                        Name
                      </label>

                      {!editing && (
                        <button
                          type="button"
                          onClick={() => {
                            setEditing(true);
                            setError("");
                            setMessage("");
                          }}
                          className="flex items-center gap-1.5 text-xs font-medium text-indigo-400 transition hover:text-indigo-300"
                        >
                          <Edit3 size={13} />
                          Rename
                        </button>
                      )}
                    </div>

                    {editing ? (
                      <div className="flex flex-col gap-3 sm:flex-row">
                        <input
                          autoFocus
                          type="text"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              handleSave();
                            }

                            if (e.key === "Escape") {
                              handleCancel();
                            }
                          }}
                          className="min-w-0 flex-1 rounded-xl border border-indigo-500/30 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/10"
                        />

                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={handleCancel}
                            disabled={saving}
                            className="rounded-xl border border-white/[0.08] px-4 py-3 text-sm text-slate-400 transition hover:bg-white/[0.04] hover:text-white disabled:opacity-50"
                          >
                            Cancel
                          </button>

                          <button
                            type="button"
                            onClick={handleSave}
                            disabled={saving}
                            className="rounded-xl bg-indigo-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {saving ? "Saving..." : "Save"}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3.5">
                        <User size={17} className="text-slate-500" />
                        <span className="text-sm font-medium text-slate-200">
                          {profile.name}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* EMAIL */}
                  <div>
                    <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                      Email address
                    </label>

                    <div className="flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3.5">
                      <Mail size={17} className="text-slate-500" />

                      <span className="text-sm text-slate-300">
                        {profile.email}
                      </span>

                      <span className="ml-auto rounded-full bg-emerald-500/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-emerald-400">
                        Verified
                      </span>
                    </div>
                  </div>

                  {/* ACCOUNT ID */}
                  <div>
                    <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                      Account ID
                    </label>

                    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3.5">
                      <span className="font-mono text-sm text-slate-400">
                        RB-{String(profile.id).padStart(6, "0")}
                      </span>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </section>

          {/* SECURITY CARD */}
          <section className="overflow-hidden rounded-2xl border border-white/[0.07] bg-white/[0.025]">
            <div className="border-b border-white/[0.06] px-6 py-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10">
                  <ShieldCheck size={19} className="text-emerald-400" />
                </div>

                <div>
                  <h2 className="text-base font-semibold text-slate-100">
                    Security
                  </h2>
                  <p className="mt-1 text-xs text-slate-500">
                    Current account security status.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3 p-6">
              <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                <div className="flex items-center gap-3">
                  <Lock size={17} className="text-slate-500" />

                  <div>
                    <p className="text-sm font-medium text-slate-200">
                      Authentication
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      JWT authentication is enabled.
                    </p>
                  </div>
                </div>

                <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-emerald-400">
                  Active
                </span>
              </div>

              <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                <div>
                  <p className="text-sm font-medium text-slate-200">
                    Account type
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    RiskBridge merchant account
                  </p>
                </div>

                <span className="rounded-full bg-indigo-500/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-indigo-400">
                  Merchant
                </span>
              </div>
            </div>
          </section>
        </div>
                {/* MERCHANT + RAZORPAY */}
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          {/* MERCHANT PROFILE */}
          <section className="overflow-hidden rounded-2xl border border-white/[0.07] bg-white/[0.025]">
            <div className="border-b border-white/[0.06] px-6 py-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10">
                  <User size={19} className="text-indigo-400" />
                </div>

                <div>
                  <h2 className="text-base font-semibold text-slate-100">
                    Merchant Profile
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Merchant information provided during onboarding.
                  </p>
                </div>
              </div>
            </div>

            <div className="p-6">
              {merchantLoading ? (
                <div className="space-y-3">
                  <div className="h-14 animate-pulse rounded-xl bg-white/[0.04]" />
                  <div className="h-14 animate-pulse rounded-xl bg-white/[0.04]" />
                  <div className="h-14 animate-pulse rounded-xl bg-white/[0.04]" />
                  <div className="h-14 animate-pulse rounded-xl bg-white/[0.04]" />
                </div>
              ) : merchant ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                      Business name
                    </p>
                    <p className="mt-2 text-sm font-medium text-slate-200">
                      {merchant.business_name}
                    </p>
                  </div>

                  <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                      Business type
                    </p>
                    <p className="mt-2 text-sm font-medium text-slate-200">
                      {merchant.business_type}
                    </p>
                  </div>

                  <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 sm:col-span-2">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                      Website
                    </p>
                    <p className="mt-2 truncate text-sm font-medium text-slate-200">
                      {merchant.website || "Not provided"}
                    </p>
                  </div>

                  <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                      Country
                    </p>
                    <p className="mt-2 text-sm font-medium text-slate-200">
                      {merchant.country}
                    </p>
                  </div>

                  <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                      Currency
                    </p>
                    <p className="mt-2 text-sm font-medium text-slate-200">
                      {merchant.currency}
                    </p>
                  </div>

                  <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 sm:col-span-2">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                      Merchant ID
                    </p>
                    <p className="mt-2 font-mono text-sm font-medium text-slate-300">
                      {merchant.id}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500">
                  Merchant profile unavailable.
                </p>
              )}
            </div>
          </section>

          {/* RAZORPAY INTEGRATION */}
          <section className="overflow-hidden rounded-2xl border border-white/[0.07] bg-white/[0.025]">
            <div className="border-b border-white/[0.06] px-6 py-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10">
                  <ShieldCheck size={19} className="text-blue-400" />
                </div>

                <div>
                  <h2 className="text-base font-semibold text-slate-100">
                    Razorpay Integration
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Payment integration configured during onboarding.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3 p-6">
              {razorpayLoading ? (
                <>
                  <div className="h-16 animate-pulse rounded-xl bg-white/[0.04]" />
                  <div className="h-16 animate-pulse rounded-xl bg-white/[0.04]" />
                  <div className="h-16 animate-pulse rounded-xl bg-white/[0.04]" />
                </>
              ) : razorpay ? (
                <>
                  <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <div>
                      <p className="text-sm font-medium text-slate-200">
                        Connection
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        Razorpay account connection status.
                      </p>
                    </div>

                    <span
                      className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide ${
                        razorpay.status === "connected"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : "bg-red-500/10 text-red-400"
                      }`}
                    >
                     {razorpay.status === "connected" ? "Connected" : "Not connected"}
                    </span>
                  </div>

                  <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <div>
                      <p className="text-sm font-medium text-slate-200">
                        Environment
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        Razorpay operating environment.
                      </p>
                    </div>

                    <span className="rounded-full bg-indigo-500/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-indigo-400">
                      Test Mode
                    </span>
                  </div>

                  <div className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <div>
                      <p className="text-sm font-medium text-slate-200">
                        Payments sync
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        Synchronization with Razorpay payment data.
                      </p>
                    </div>

                    <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-emerald-400">
                      {razorpay.last_synced_at
  ? `Last synced ${new Date(
      razorpay.last_synced_at,
    ).toLocaleString()}`
  : "Not synced yet"}
                    </span>
                  </div>
                </>
              ) : (
                <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                  <p className="text-sm text-slate-500">
                    Razorpay integration status unavailable.
                  </p>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

