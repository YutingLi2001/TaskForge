import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import PublicRoute from './PublicRoute';
import Login from '../pages/Login';

vi.mock('../api/client', async () => {
  const actual = await vi.importActual<typeof import('../api/client')>(
    '../api/client'
  );
  return {
    ...actual,
    authApi: {
      me: vi.fn(),
    },
  };
});

import { ApiRequestError, authApi } from '../api/client';

describe('PublicRoute', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.mocked(authApi.me).mockReset();
  });

  const makeToken = (expOffsetSeconds: number) => {
    const payload = btoa(
      JSON.stringify({ exp: Math.floor(Date.now() / 1000) + expOffsetSeconds })
    )
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/g, '');
    return ['header', payload, 'signature'].join('.');
  };

  it('redirects authenticated users to dashboard', async () => {
    localStorage.setItem('token', makeToken(60));
    vi.mocked(authApi.me).mockResolvedValue({ data: {} });

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <div>Login</div>
            </PublicRoute>
          } />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Dashboard')).toBeInTheDocument();
  });

  it('renders children when not authenticated', async () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <div>Login</div>
            </PublicRoute>
          } />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Login')).toBeInTheDocument();
  });

  it('redirects authenticated users away from the login page', async () => {
    localStorage.setItem('token', makeToken(60));
    vi.mocked(authApi.me).mockResolvedValue({ data: {} });

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Dashboard')).toBeInTheDocument();
  });

  it('keeps unauthenticated users on login when token is rejected', async () => {
    localStorage.setItem('token', makeToken(60));
    vi.mocked(authApi.me).mockRejectedValue(new ApiRequestError(401, 'Not authenticated'));

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <div>Login</div>
            </PublicRoute>
          } />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Login')).toBeInTheDocument();
  });

  it('redirects authenticated users when server error is transient', async () => {
    localStorage.setItem('token', makeToken(60));
    vi.mocked(authApi.me).mockRejectedValue(new ApiRequestError(500, 'Server error'));

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <div>Login</div>
            </PublicRoute>
          } />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Dashboard')).toBeInTheDocument();
  });
});
