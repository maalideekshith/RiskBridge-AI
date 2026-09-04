import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Onboarding from "./pages/Onboarding";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./components/DashboardLayout";
import RiskMonitor from "./pages/RiskMonitor";
import RiskDetail from "./pages/RiskDetail";
import RiskSimulator from "./pages/RiskSimulator";
import ReviewCenter from "./pages/ReviewCenter";
import Settings from "./pages/Settings";
import AuditLog from "./pages/AuditLog";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Navigate to="/login" replace />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route element={<ProtectedRoute />}>
          <Route
            path="/onboarding"
            element={<Onboarding />}
          />

          <Route element={<DashboardLayout />}>
            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/risk-monitor"
              element={<RiskMonitor />}
            />

            <Route
              path="/risk-monitor/:assessmentId"
              element={<RiskDetail />}
            />

            <Route
              path="/risk-simulator"
              element={<RiskSimulator />}
            />

            <Route
              path="/risk-review"
              element={<ReviewCenter />}
            />
            <Route path="/audit-logs" element={<AuditLog />} />
            <Route
              path="/settings"
              element={<Settings />}
            />
          </Route>
        </Route>

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;