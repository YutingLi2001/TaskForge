import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/client';

export function useLogout() {
  const navigate = useNavigate();

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch {
      // Ignore errors - still clear tokens and redirect.
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
    }
  };

  return { logout };
}
