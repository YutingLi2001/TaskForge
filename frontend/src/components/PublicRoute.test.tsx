import { beforeEach, describe, expect, it } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import PublicRoute from './PublicRoute';
import Login from '../pages/Login';

describe('PublicRoute', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  const makeToken = (expOffsetSeconds: number) => {
    const payload = btoa(
      JSON.stringify({ exp: Math.floor(Date.now() / 1000) + expOffsetSeconds })
    );
    return ['header', payload, 'signature'].join('.');
  };

  it('redirects authenticated users to dashboard', () => {
    localStorage.setItem('token', makeToken(60));

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

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders children when not authenticated', () => {
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

    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  it('redirects authenticated users away from the login page', () => {
    localStorage.setItem('token', makeToken(60));

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

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });
});
