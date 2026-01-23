import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { ApiRequestError, authApi } from '../api/client';

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
      const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '=');
      const payload = JSON.parse(atob(padded));
      const exp = payload.exp;
      return typeof exp === 'number' && exp > Math.floor(Date.now() / 1000);
    } catch {
      return false;
    }
  };
  const [status, setStatus] = useState<'checking' | 'guest' | 'authed'>(() => {
    return !token || !isTokenValid(token) ? 'guest' : 'checking';
  });
  const tokenValid = isTokenValid(token);
  const effectiveStatus = tokenValid ? status : 'guest';

  useEffect(() => {
    if (!tokenValid) return;
    let active = true;
    authApi.me()
      .then(() => {
        if (active) {
          setStatus('authed');
        }
      })
      .catch((err: unknown) => {
        const isAuthError =
          err instanceof ApiRequestError &&
          (err.status === 401 || err.status === 403);
        if (isAuthError) {
          localStorage.removeItem('token');
        }
        if (active) {
          setStatus(isAuthError ? 'guest' : 'authed');
        }
      });
    return () => {
      active = false;
    };
  }, [tokenValid]);

  if (effectiveStatus === 'checking') {
    return null;
  }

  if (effectiveStatus === 'authed') {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
