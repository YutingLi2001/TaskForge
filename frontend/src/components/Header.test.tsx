import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';

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

describe('Header', () => {
  it('shows the logout button on the dashboard', () => {
    localStorage.setItem('token', 'access-token');
    render(<Dashboard />);
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });
});
