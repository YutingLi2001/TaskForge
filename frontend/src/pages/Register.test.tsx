import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Register from './Register';

vi.mock('../api/client', () => ({
  authApi: {
    register: vi.fn(),
  },
}));

import { authApi } from '../api/client';

describe('Register page', () => {
  beforeEach(() => {
    vi.mocked(authApi.register).mockReset();
  });

  it('shows success message on successful registration', async () => {
    vi.mocked(authApi.register).mockResolvedValue({
      data: {
        id: 1,
        email: 'newuser@example.com',
        created_at: '2026-01-22T00:00:00Z',
      },
    });

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'newuser@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'securepassword123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(authApi.register).toHaveBeenCalledWith({
        email: 'newuser@example.com',
        password: 'securepassword123',
      });
    });

    expect(
      await screen.findByText(/registration successful/i)
    ).toBeInTheDocument();
  });

  it('shows error message when registration fails with duplicate email', async () => {
    vi.mocked(authApi.register).mockRejectedValue(
      new Error('Email already registered')
    );

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'existing@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'securepassword123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    expect(
      await screen.findByText(/email already registered/i)
    ).toBeInTheDocument();
  });

  it('normalizes email to lowercase and trims whitespace', async () => {
    vi.mocked(authApi.register).mockResolvedValue({
      data: {
        id: 1,
        email: 'user@example.com',
        created_at: '2026-01-22T00:00:00Z',
      },
    });

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: '  User@Example.com  ' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'securepassword123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(authApi.register).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'securepassword123',
      });
    });
  });

  it('shows link to login page', () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    const loginLink = screen.getByRole('link', { name: /log in/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  it('clears form after successful registration', async () => {
    vi.mocked(authApi.register).mockResolvedValue({
      data: {
        id: 1,
        email: 'newuser@example.com',
        created_at: '2026-01-22T00:00:00Z',
      },
    });

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;

    fireEvent.change(emailInput, {
      target: { value: 'newuser@example.com' },
    });
    fireEvent.change(passwordInput, {
      target: { value: 'securepassword123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText(/registration successful/i)).toBeInTheDocument();
    });

    expect(emailInput.value).toBe('');
    expect(passwordInput.value).toBe('');
  });

  it('shows generic error message for unknown errors', async () => {
    vi.mocked(authApi.register).mockRejectedValue('Unknown error');

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'securepassword123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    expect(await screen.findByText(/registration failed/i)).toBeInTheDocument();
  });
});
