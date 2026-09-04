import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import api from "../services/api";

export default function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");

    if (!name.trim() || !email.trim() || !password) {
      setError("Please complete all required fields.");
      return;
    }

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    try {
      setLoading(true);

      await api.post("/auth/register", {
        name: name.trim(),
        email: email.trim(),
        password,
      });

      // Registration successful → return to Login.
      navigate("/login", {
        replace: true,
        state: {
          registered: true,
          email: email.trim(),
        },
      });
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        "Unable to create your account. Please try again.";

      setError(
        Array.isArray(message)
          ? message.map((item) => item.msg).join(", ")
          : message,
      );
    } finally {
      setLoading(false);
    }
  };

  const passwordChecks = [
    {
      label: "At least 8 characters",
      valid: password.length >= 8,
    },
    {
      label: "Contains a number",
      valid: /\d/.test(password),
    },
    {
      label: "Contains an uppercase letter",
      valid: /[A-Z]/.test(password),
    },
  ];

  return (
    <div className="min-h-screen bg-[#070b14] text-white">
      <div className="grid min-h-screen lg:grid-cols-2">
        {/* LEFT */}
        <div className="relative hidden overflow-hidden border-r border-white/10 bg-gradient-to-br from-indigo-950/70 via-[#0a1020] to-[#070b14] p-12 lg:flex lg:flex-col lg:justify-between xl:p-16">
          <div className="absolute -right-32 top-10 h-96 w-96 rounded-full bg-indigo-600/20 blur-3xl" />
          <div className="absolute bottom-0 left-0 h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />

          <div className="relative">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-600/30">
                <ShieldCheck size={24} strokeWidth={2.5} />
              </div>

              <div>
                <div className="text-xl font-bold">RiskBridge AI</div>
                <div className="text-xs text-slate-400">
                  Payment Risk Intelligence
                </div>
              </div>
            </div>
          </div>

          <div className="relative max-w-xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1.5 text-sm text-cyan-300">
              <Sparkles size={15} />
              Built for modern fintech
            </div>

            <h1 className="text-5xl font-bold leading-[1.08] tracking-tight xl:text-6xl">
              Turn payment data into
              <span className="block bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                smarter decisions.
              </span>
            </h1>

            <p className="mt-6 max-w-lg text-lg leading-8 text-slate-400">
              RiskBridge AI helps payment teams understand risk, investigate
              suspicious activity, and take action before losses happen.
            </p>

            <div className="mt-10 space-y-4">
              <Benefit text="Real-time payment risk visibility" />
              <Benefit text="AI-powered risk investigation" />
              <Benefit text="Actionable remediation recommendations" />
            </div>
          </div>

          <div className="relative text-sm text-slate-500">
            Secure payment intelligence for modern businesses
          </div>
        </div>

        {/* RIGHT */}
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
                GET STARTED
              </p>

              <h2 className="text-3xl font-bold tracking-tight">
                Create your account
              </h2>

              <p className="mt-3 text-slate-400">
                Start monitoring payment risk with AI-powered intelligence.
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
                  Full name
                </label>

                <input
                  type="text"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Your full name"
                  autoComplete="name"
                  className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3.5 text-white placeholder:text-slate-600 outline-none transition focus:border-indigo-500 focus:bg-white/[0.06] focus:ring-4 focus:ring-indigo-500/10"
                />
              </div>

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
                    placeholder="Create a secure password"
                    autoComplete="new-password"
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

                <div className="mt-3 space-y-2">
                  {passwordChecks.map((check) => (
                    <div
                      key={check.label}
                      className="flex items-center gap-2 text-xs"
                    >
                      <div
                        className={`flex h-4 w-4 items-center justify-center rounded-full ${
                          check.valid
                            ? "bg-emerald-500/20 text-emerald-400"
                            : "bg-white/5 text-slate-600"
                        }`}
                      >
                        <Check size={10} strokeWidth={3} />
                      </div>

                      <span
                        className={
                          check.valid ? "text-slate-300" : "text-slate-600"
                        }
                      >
                        {check.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="group flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3.5 font-semibold text-white shadow-lg shadow-indigo-600/20 transition hover:bg-indigo-500 hover:shadow-indigo-600/30 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Creating account..." : "Create account"}

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
              Your account is protected with secure authentication
            </div>

            <div className="my-8 h-px bg-white/10" />

            <p className="text-center text-sm text-slate-400">
              Already have an account?{" "}
              <Link
                to="/login"
                className="font-semibold text-indigo-400 transition hover:text-indigo-300"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Benefit({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
        <Check size={14} strokeWidth={3} />
      </div>

      <span className="text-sm text-slate-300">{text}</span>
    </div>
  );
}

