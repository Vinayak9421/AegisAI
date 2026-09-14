import { Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { useAuth } from '../store/AuthContext';
import LoginPage from '../features/auth/pages/LoginPage';
import RegisterPage from '../features/auth/pages/RegisterPage';
import { RoleSelectionPage } from '../features/auth/pages/RoleSelectionPage';
import AdminOverviewPage from '../features/admin/pages/AdminOverviewPage';
import UserDashboardPage from '../features/dashboard/pages/UserDashboardPage';
import LiveSimulationPage from '../features/simulation/pages/LiveSimulationPage';
import TestSuitePage from '../features/testSuites/pages/TestSuitePage';
import ConnectChatbotPage from '../features/connect/pages/ConnectChatbotPage';
import SafetyReportPage from '../features/report/pages/SafetyReportPage';
import LandingPage from '../features/landing/pages/LandingPage';
import ProtectedRoute from '../shared/components/ProtectedRoute';

function RootRedirect() {
  const { isAuthenticated, isAdmin } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return isAdmin ? <Navigate to="/admin/overview" replace /> : <Navigate to="/user/dashboard" replace />;
}

export default function AppRouter() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        {/* Public Landing Page */}
        <Route path="/" element={<LandingPage />} />

        {/* Public authentication routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/roles" element={<RoleSelectionPage />} />

        {/* Admin routes (Restricted to role === 'ADMIN') */}
        <Route element={<ProtectedRoute requiredRole="ADMIN" />}>
          <Route path="/admin/overview" element={<AdminOverviewPage />} />
          <Route path="/admin/test-suites" element={<TestSuitePage />} />
          <Route path="/admin/evaluations" element={<AdminOverviewPage />} />
          <Route path="/admin/users" element={<AdminOverviewPage />} />
          <Route path="/admin/settings" element={<AdminOverviewPage />} />
        </Route>

        {/* User & shared authenticated routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<RootRedirect />} />
          <Route path="/user/dashboard" element={<UserDashboardPage />} />
          <Route path="/connect" element={<ConnectChatbotPage />} />
          <Route path="/simulation" element={<LiveSimulationPage />} />
          <Route path="/report/:reportId" element={<SafetyReportPage />} />
          <Route path="/reports/:reportId" element={<SafetyReportPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<RootRedirect />} />
      </Routes>
    </AnimatePresence>
  );
}
