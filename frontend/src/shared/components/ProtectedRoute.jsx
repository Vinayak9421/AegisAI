import { Navigate, Outlet } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../../store/AuthContext';

export default function ProtectedRoute({ requiredRole, children }) {
  const { isAuthenticated, role, isAdmin } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole === 'ADMIN' && !isAdmin) {
    toast.error('Administrative access required for this section', { id: 'admin-denied' });
    return <Navigate to="/user/dashboard" replace />;
  }

  return children ? children : <Outlet />;
}
