import { useEffect, useState } from "react";
import { useNavigate, useLocation, Outlet } from "react-router-dom";
import {
  ChevronDown,
  LayoutDashboard,
  LogOut,
  Menu,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Activity,
  FileText,
  X,
} from "lucide-react";
import api from "../services/api";
const navigation = [
  {
    section: "OVERVIEW",
    items: [
      {
        label: "Dashboard",
        icon: LayoutDashboard,
        path: "/dashboard",
      },
    ],
  },
  {
    section: "INTELLIGENCE",
    items: [
      {
        label: "Risk Monitor",
        icon: Activity,
        path: "/risk-monitor",
      },
      {
        label: "Risk Simulator",
        icon: SlidersHorizontal,
        path: "/risk-simulator",
      },
    ],
  },
  {
    section: "REVIEW",
    items: [
      {
        label: "Review Center",
        icon: ShieldCheck,
        path: "/risk-review",
      },
    ],
  },
  {
    section: "COMPLIANCE",
    items: [
      {
        label: "Audit Log",
        icon: FileText,
        path: "/audit-logs",
      },
    ],
  },
];

export default function DashboardLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const [sidebarOpen, setSidebarOpen] = useState(false);
const [userName, setUserName] = useState("Merchant");
useEffect(() => {
  const loadProfile = async () => {
    try {
      const response = await api.get("/auth/me");
      setUserName(response.data.name || "Merchant");
    } catch {
      const storedUser = localStorage.getItem("user");

      if (storedUser) {
        try {
          const user = JSON.parse(storedUser);
          setUserName(user.name || "Merchant");
        } catch {
          setUserName("Merchant");
        }
      }
    }
  };

  loadProfile();
}, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    navigate("/login", { replace: true });
  };

  const isActive = (path: string) => {
    if (path === "/risk-monitor") {
      return (
        location.pathname === "/risk-monitor" ||
        location.pathname.startsWith("/risk-monitor/")
      );
    }

    return location.pathname === path;
  };

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

      {/* SIDEBAR */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-white/[0.07] bg-[#090e1c] transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand */}
        <div className="flex h-20 items-center justify-between border-b border-white/[0.07] px-6">
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-3 text-left"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-600/25">
              <ShieldCheck size={21} strokeWidth={2.5} />
            </div>

            <div>
              <div className="text-[15px] font-bold tracking-tight">
                RiskBridge AI
              </div>

              <div className="mt-0.5 text-[10px] font-medium uppercase tracking-[0.12em] text-slate-500">
                Payment Intelligence
              </div>
            </div>
          </button>

          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-white lg:hidden"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-4 py-6">
          {navigation.map((group) => (
            <div key={group.section} className="mb-7">
              <p className="mb-2 px-3 text-[10px] font-semibold tracking-[0.16em] text-slate-600">
                {group.section}
              </p>

              <div className="space-y-1">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.path);

                  return (
                    <button
                      key={item.label}
                      type="button"
                      onClick={() => {
                        navigate(item.path);
                        setSidebarOpen(false);
                      }}
                      className={`group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition ${
                        active
                          ? "bg-indigo-600/15 text-indigo-300 ring-1 ring-inset ring-indigo-500/20"
                          : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
                      }`}
                    >
                      <Icon
                        size={18}
                        strokeWidth={active ? 2.3 : 1.9}
                        className={
                          active
                            ? "text-indigo-400"
                            : "text-slate-500 group-hover:text-slate-300"
                        }
                      />

                      <span>{item.label}</span>

                      {active && (
                        <span className="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-400" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* AI status */}
        <div className="mx-4 mb-4 rounded-xl border border-indigo-500/10 bg-gradient-to-br from-indigo-500/[0.08] to-cyan-500/[0.04] p-4">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10">
              <Sparkles size={14} className="text-indigo-400" />
            </div>

            <div>
              <p className="text-xs font-semibold text-slate-200">
                AI Intelligence
              </p>

              <p className="text-[10px] text-slate-500">
                Monitoring active
              </p>
            </div>

            <span className="ml-auto h-2 w-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50" />
          </div>
        </div>

        {/* Bottom navigation */}
        <div className="border-t border-white/[0.07] p-4">
          <button
  type="button"
  onClick={() => {
    navigate("/settings");
    setSidebarOpen(false);
  }}
  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
    isActive("/settings")
      ? "bg-indigo-600/15 text-indigo-300 ring-1 ring-inset ring-indigo-500/20"
      : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
  }`}
>
  <Settings
    size={18}
    className={isActive("/settings") ? "text-indigo-400" : ""}
  />
  Settings

  {isActive("/settings") && (
    <span className="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-400" />
  )}
</button>

          <button
            type="button"
            onClick={handleLogout}
            className="mt-1 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-400 transition hover:bg-red-500/10 hover:text-red-300"
          >
            <LogOut size={18} />
            Sign out
          </button>
        </div>
      </aside>

      {/* MAIN AREA */}
<div className="lg:pl-72">
  {/* TOP NAVBAR */}
  <header className="sticky top-0 z-30 flex h-20 items-center border-b border-white/[0.07] bg-[#060914]/90 px-5 backdrop-blur-xl sm:px-8">
          <div className="flex flex-1 items-center gap-4">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="rounded-xl border border-white/[0.08] bg-white/[0.03] p-2.5 text-slate-400 hover:text-white lg:hidden"
            >
              <Menu size={20} />
            </button>

            {/* Search */}
            <div className="hidden max-w-md flex-1 md:block">
              <div className="relative">
                <Search
                  size={17}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600"
                />

                <input
                  type="text"
                  placeholder="Search transactions, risks, cases..."
                  className="w-full rounded-xl border border-white/[0.07] bg-white/[0.025] py-2.5 pl-10 pr-4 text-sm text-white outline-none placeholder:text-slate-600 transition focus:border-indigo-500/40 focus:bg-white/[0.04]"
                />

                <div className="absolute right-3 top-1/2 hidden -translate-y-1/2 rounded-md border border-white/[0.08] px-1.5 py-0.5 text-[10px] text-slate-600 xl:block">
                  ⌘ K
                </div>
              </div>
            </div>

            <div className="ml-auto flex items-center gap-2 sm:gap-3">
              <div className="mx-1 hidden h-7 w-px bg-white/[0.07] sm:block" />

              {/* User */}
              <button
                type="button"
                className="flex items-center gap-2.5 rounded-xl px-2 py-1.5 transition hover:bg-white/[0.04]"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-xs font-bold">
  {userName.charAt(0).toUpperCase()}
</div>

                <div className="hidden text-left sm:block">
                  <p className="text-xs font-semibold text-slate-200">
  {userName}
</p>

                  <p className="text-[10px] text-slate-500">
                    Account
                  </p>
                </div>

                <ChevronDown
                  size={15}
                  className="hidden text-slate-600 sm:block"
                />
              </button>
                       </div>
          </div>
  </header>

  {/* PAGE CONTENT */}
<Outlet />
      </div>
    </div>
  );
}