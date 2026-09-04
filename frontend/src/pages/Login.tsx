import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, ShieldCheck, ArrowRight, Zap } from "lucide-react";
import api from "../services/api";
export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");

    if (!email.trim() || !password) {
      setError("Please enter your email and password.");
      return;
    }

    try {
      setLoading(true);

      const body = new URLSearchParams();
      body.append("username", email.trim());
      body.append("password", password);

      const response = await api.post("/auth/login", body, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      localStorage.setItem("access_token", response.data.access_token);

const userResponse = await api.get("/auth/me");
const userId = userResponse.data?.id;

if (!userId) {
  throw new Error("Unable to identify your account.");
}

try {
  await api.get(`/merchants/${userId}`);
  navigate("/dashboard", { replace: true });
} catch (merchantError: any) {
  if (merchantError?.response?.status === 404) {
    navigate("/onboarding", { replace: true });
    return;
  }

  throw merchantError;
}
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        "Unable to sign in. Please check your credentials.";

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
      <div className="grid min-h-screen lg:grid-cols-2">
        {/* LEFT — PRODUCT BRANDING */}
        <div className="relative hidden overflow-hidden lg:flex lg:flex-col lg:justify-between border-r border-white/10 bg-gradient-to-br from-indigo-950/70 via-[#0a1020] to-[#070b14] p-12 xl:p-16">
          <div className="absolute -left-32 top-20 h-80 w-80 rounded-full bg-indigo-600/20 blur-3xl" />
          <div className="absolute bottom-10 right-0 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />

          <div className="relative">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-600/30">
                <ShieldCheck size={24} strokeWidth={2.5} />
              </div>

              <div>
                <div className="text-xl font-bold tracking-tight">
                  RiskBridge AI
                </div>
                <div className="text-xs text-slate-400">
                  Payment Risk Intelligence
                </div>
              </div>
            </div>
          </div>

          <div className="relative max-w-xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-400/20 bg-indigo-500/10 px-3 py-1.5 text-sm text-indigo-300">
              <Zap size={15} />
              AI-powered risk intelligence
            </div>

            <h1 className="text-5xl font-bold leading-[1.08] tracking-tight xl:text-6xl">
              See payment risk
              <span className="block bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                before it becomes loss.
              </span>
            </h1>

            <p className="mt-6 max-w-lg text-lg leading-8 text-slate-400">
              Monitor transaction risk, investigate suspicious activity, and
              make smarter decisions with AI-powered intelligence.
            </p>

            <div className="mt-10 grid grid-cols-3 gap-4">
              <Feature
                title="Risk Intelligence"
                description="Real-time visibility"
              />
              <Feature title="AI Analysis" description="Actionable insights" />
              <Feature title="Secure" description="Built for fintech" />
            </div>
          </div>

          <div className="relative text-sm text-slate-500">
            © 2026 RiskBridge AI · Built for modern fintech teams
          </div>
        </div>

        {/* RIGHT — LOGIN */}
        <div className="flex items-center justify-center px-6 py-12 sm:px-10">
          <div className="w-full max-w-md">
            {/* Mobile logo */}
            <div className="mb-10 flex items-center gap-3 lg:hidden">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600">
                <ShieldCheck size={24} />
              </div>

              <div>
                <div className="text-xl font-bold">RiskBridge AI</div>
                <div className="text-xs text-slate-400">
                  Payment Risk Intelligence
                </div>
              </div>
            </div>

            <div className="mb-8">
              <p className="mb-3 text-sm font-medium text-indigo-400">
                WELCOME BACK
              </p>

              <h2 className="text-3xl font-bold tracking-tight">
                Sign in to your account
              </h2>

              <p className="mt-3 text-slate-400">
                Access your payment risk intelligence dashboard.
              </p>
            </div>

            {error && (
              <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Email address
                </label>

                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@company.com"
                  autoComplete="email"
                  className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3.5 text-white placeholder:text-slate-600 outline-none transition focus:border-indigo-500 focus:bg-white/[0.06] focus:ring-4 focus:ring-indigo-500/10"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Password
                </label>

                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3.5 pr-12 text-white placeholder:text-slate-600 outline-none transition focus:border-indigo-500 focus:bg-white/[0.06] focus:ring-4 focus:ring-indigo-500/10"
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword((value) => !value)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 text-slate-500 transition hover:bg-white/5 hover:text-slate-300"
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff size={18} />
                    ) : (
                      <Eye size={18} />
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="group flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3.5 font-semibold text-white shadow-lg shadow-indigo-600/20 transition hover:bg-indigo-500 hover:shadow-indigo-600/30 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Signing in..." : "Sign in"}

                {!loading && (
                  <ArrowRight
                    size={18}
                    className="transition-transform group-hover:translate-x-1"
                  />
                )}
              </button>
            </form>

            <div className="mt-8 flex items-center justify-center gap-2 text-xs text-slate-500">
              <ShieldCheck size={15} />
              Secure authentication
            </div>

            <div className="my-8 h-px bg-white/10" />

            <p className="text-center text-sm text-slate-400">
              Don't have an account?{" "}
              <Link
                to="/register"
                className="font-semibold text-indigo-400 transition hover:text-indigo-300"
              >
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Feature({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4 backdrop-blur-sm">
      <div className="text-sm font-semibold text-white">{title}</div>
      <div className="mt-1 text-xs text-slate-500">{description}</div>
    </div>
  );
}

