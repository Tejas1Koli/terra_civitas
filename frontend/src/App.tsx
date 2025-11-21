import { ConfigProvider, theme } from "antd";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useState, useEffect } from "react";
import { DashboardPage } from "./pages/Dashboard";
import { DualCameraDashboard } from "./pages/DualCameraDashboard";
import { AlertsPage } from "./pages/Alerts";
import { VerifiedAlertsPage } from "./pages/VerifiedAlerts";
import { LoginPage } from "./pages/Login";
import { AppShell } from "./components/AppShell";

// Protected route wrapper
const ProtectedRoute = ({ isAuthenticated }: { isAuthenticated: boolean }) => {
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
};

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem("cctv_token");
  });

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorBgBase: "#050711",
          colorTextBase: "#f8fbff",
        },
      }}
    >
      <Routes>
        <Route 
          path="/login" 
          element={<LoginPage onLoginSuccess={() => setIsAuthenticated(true)} />} 
        />
        
        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />}>
          <Route element={<AppShell onLogout={() => setIsAuthenticated(false)} />}>
            <Route index element={<DashboardPage />} />
            <Route path="/dual" element={<DualCameraDashboard />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/verified" element={<VerifiedAlertsPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} replace />} />
      </Routes>
    </ConfigProvider>
  );
};

export default App;
