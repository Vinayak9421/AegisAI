import { Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { RoleSelectionPage } from '../features/auth/pages/RoleSelectionPage';
import AdminOverviewPage from '../features/admin/pages/AdminOverviewPage';
import UserDashboardPage from '../features/dashboard/pages/UserDashboardPage';
import LiveSimulationPage from '../features/simulation/pages/LiveSimulationPage';
import TestSuitePage from '../features/testSuites/pages/TestSuitePage';
import ConnectChatbotPage from '../features/connect/pages/ConnectChatbotPage';
import SafetyReportPage from '../features/report/pages/SafetyReportPage';

export default function AppRouter() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        {/* Default: Role Selection */}
        <Route path="/" element={<RoleSelectionPage />} />

        {/* Admin routes */}
        <Route path="/admin/overview" element={<AdminOverviewPage />} />
        <Route path="/admin/test-suites" element={<TestSuitePage />} />
        <Route path="/admin/evaluations" element={<AdminOverviewPage />} />
        <Route path="/admin/users" element={<AdminOverviewPage />} />
        <Route path="/admin/settings" element={<AdminOverviewPage />} />

        {/* User routes */}
        <Route path="/user/dashboard" element={<UserDashboardPage />} />

        {/* Shared routes */}
        <Route path="/simulation" element={<LiveSimulationPage />} />
        <Route path="/connect" element={<ConnectChatbotPage />} />
        <Route path="/report/:reportId" element={<SafetyReportPage />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}
