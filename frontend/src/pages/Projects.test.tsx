import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import Projects from './Projects';

vi.mock('../api/client', () => ({
  projectsApi: {
    list: vi.fn(),
    create: vi.fn(),
  },
}));

const mockLogout = vi.fn();

vi.mock('../hooks/useLogout', () => ({
  useLogout: () => ({ logout: mockLogout }),
}));

import { projectsApi } from '../api/client';

describe('Projects page', () => {
  beforeEach(() => {
    vi.mocked(projectsApi.list).mockReset();
    vi.mocked(projectsApi.create).mockReset();
    mockLogout.mockReset();
  });

  it('renders project list', async () => {
    vi.mocked(projectsApi.list).mockResolvedValue({
      data: [
        {
          id: 1,
          name: 'Launch Plan',
          user_id: 1,
          created_at: '2026-01-21T00:00:00Z',
          updated_at: '2026-01-21T00:00:00Z',
        },
      ],
    });

    render(<Projects />);

    expect(await screen.findByText('Launch Plan')).toBeInTheDocument();
  });

  it('creates a project and adds it to the list', async () => {
    vi.mocked(projectsApi.list).mockResolvedValue({ data: [] });
    vi.mocked(projectsApi.create).mockResolvedValue({
      data: {
        id: 2,
        name: 'New Project',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-21T00:00:00Z',
      },
    });

    render(<Projects />);

    await screen.findByText(/you have not created any projects yet/i);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'New Project' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(projectsApi.create).toHaveBeenCalledWith({ name: 'New Project' });
    });
    expect(await screen.findByText('New Project')).toBeInTheDocument();
  });

  it('shows validation error for empty name', async () => {
    vi.mocked(projectsApi.list).mockResolvedValue({ data: [] });

    render(<Projects />);

    await screen.findByText(/you have not created any projects yet/i);

    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    expect(await screen.findByText(/project name is required/i)).toBeInTheDocument();
    expect(projectsApi.create).not.toHaveBeenCalled();
  });

  it('shows empty state when there are no projects', async () => {
    vi.mocked(projectsApi.list).mockResolvedValue({ data: [] });

    render(<Projects />);

    expect(
      await screen.findByText(/you have not created any projects yet/i)
    ).toBeInTheDocument();
  });

  it('logs out on unauthorized list response', async () => {
    vi.mocked(projectsApi.list).mockRejectedValue(new Error('401 Unauthorized'));

    render(<Projects />);

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('logs out on unauthorized create response', async () => {
    vi.mocked(projectsApi.list).mockResolvedValue({ data: [] });
    vi.mocked(projectsApi.create).mockRejectedValue(new Error('403 Forbidden'));

    render(<Projects />);

    await screen.findByText(/you have not created any projects yet/i);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'New Project' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });
});
