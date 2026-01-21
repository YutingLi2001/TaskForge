import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { useLogout } from './useLogout';

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom'
  );
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../api/client', () => ({
  authApi: {
    logout: vi.fn(),
  },
}));

import { authApi } from '../api/client';

function LogoutTester() {
  const { logout } = useLogout();

  return (
    <button type="button" onClick={logout}>
      Logout
    </button>
  );
}

describe('useLogout', () => {
  beforeEach(() => {
    localStorage.clear();
    mockNavigate.mockReset();
    vi.mocked(authApi.logout).mockReset();
  });

  it('calls logout API, clears tokens, and redirects', async () => {
    localStorage.setItem('token', 'access-token');
    localStorage.setItem('refresh_token', 'refresh-token');
    vi.mocked(authApi.logout).mockResolvedValue(null);

    render(<LogoutTester />);
    fireEvent.click(screen.getByRole('button', { name: /logout/i }));

    await waitFor(() => {
      expect(authApi.logout).toHaveBeenCalledWith('refresh-token');
    });
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('user_email')).toBeNull();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('clears tokens and redirects even when logout fails', async () => {
    localStorage.setItem('token', 'access-token');
    localStorage.setItem('refresh_token', 'refresh-token');
    vi.mocked(authApi.logout).mockRejectedValue(new Error('Network error'));

    render(<LogoutTester />);
    fireEvent.click(screen.getByRole('button', { name: /logout/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('user_email')).toBeNull();
  });

  it('skips logout API when refresh token missing, but still clears and redirects', async () => {
    localStorage.setItem('token', 'access-token');

    render(<LogoutTester />);
    fireEvent.click(screen.getByRole('button', { name: /logout/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
    expect(authApi.logout).not.toHaveBeenCalled();
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('user_email')).toBeNull();
  });
});
