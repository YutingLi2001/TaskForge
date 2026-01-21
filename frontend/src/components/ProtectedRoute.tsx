import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { authApi } from '../api/client';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation();
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
      const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '=');
      const payload = JSON.parse(atob(padded));
      const exp = payload.exp;
      return typeof exp === 'number' && exp > Math.floor(Date.now() / 1000);
    } catch {
      return false;
    }
  };
  const [status, setStatus] = useState<'checking' | 'allowed' | 'denied'>(() => {
    return !token || !isTokenValid(token) ? 'denied' : 'checking';
  });

  useEffect(() => {
    if (!token || !isTokenValid(token)) {
      setStatus('denied');
      return;
    }
    let active = true;
    authApi.me()
      .then(() => {
        if (active) {
          setStatus('allowed');
        }
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : '';
        const isAuthError = message.toLowerCase().includes('401') || message.toLowerCase().includes('403');
        if (isAuthError) {
          localStorage.removeItem('token');
        }
        if (active) {
          setStatus(isAuthError ? 'denied' : 'allowed');
        }
      });
    return () => {
      active = false;
    };
  }, [token]);

  if (status === 'checking') {
    return null;
  }

  if (status === 'denied') {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
