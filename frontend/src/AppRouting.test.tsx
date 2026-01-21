import { describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';

vi.mock('./api/client', () => ({
  authApi: {
    me: vi.fn(),
  },
}));

import { authApi } from './api/client';

describe('App routing integration', () => {
  const makeToken = (expOffsetSeconds: number) => {
    const payload = btoa(
      JSON.stringify({ exp: Math.floor(Date.now() / 1000) + expOffsetSeconds })
    )
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/g, '');
    return ['header', payload, 'signature'].join('.');
  };

  it('handles protected route access across auth changes', async () => {
    localStorage.clear();
    vi.mocked(authApi.me).mockReset();

    const { unmount } = render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/login" element={<div>Login</div>} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>Dashboard</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Login')).toBeInTheDocument();
    unmount();

    localStorage.setItem('token', makeToken(60));
    vi.mocked(authApi.me).mockResolvedValue({ data: {} });
    const { unmount: unmountAuthed } = render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/login" element={<div>Login</div>} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>Dashboard</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Dashboard')).toBeInTheDocument();
    unmountAuthed();

    localStorage.clear();
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/login" element={<div>Login</div>} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>Dashboard</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Login')).toBeInTheDocument();
  });

  it('redirects authenticated users from login to dashboard', async () => {
    localStorage.setItem('token', makeToken(60));
    vi.mocked(authApi.me).mockResolvedValue({ data: {} });

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route
            path="/login"
            element={
              <PublicRoute>
                <div>Login</div>
              </PublicRoute>
            }
          />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Dashboard')).toBeInTheDocument();
  });
});
