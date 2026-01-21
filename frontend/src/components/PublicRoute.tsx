import { Navigate } from 'react-router-dom';

interface PublicRouteProps {
  children: React.ReactNode;
}

export default function PublicRoute({ children }: PublicRouteProps) {
  const token = localStorage.getItem('token');
  const isTokenValid = (value: string | null) => {
    if (!value) {
      return false;
    }
    const parts = value.split('.');
    if (parts.length !== 3) {
      return false;
    }
    try {
      const payload = JSON.parse(atob(parts[1]));
      const exp = payload.exp;
      return typeof exp === 'number' && exp > Math.floor(Date.now() / 1000);
    } catch {
      return false;
    }
  };

  if (isTokenValid(token)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
