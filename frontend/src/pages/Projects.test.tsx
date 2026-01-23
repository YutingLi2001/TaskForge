import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Projects from './Projects';

vi.mock('../api/client', async () => {
  const actual = await vi.importActual<typeof import('../api/client')>(
    '../api/client'
  );
  return {
    ...actual,
    projectsApi: {
      list: vi.fn(),
      create: vi.fn(),
    },
  };
});

const mockLogout = vi.fn();

vi.mock('../hooks/useLogout', () => ({
  useLogout: () => ({ logout: mockLogout }),
}));

import { ApiRequestError, projectsApi } from '../api/client';

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

    render(
      <MemoryRouter>
        <Projects />
      </MemoryRouter>
    );

    const link = await screen.findByRole('link', { name: /launch plan/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/projects/1');
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

    render(
      <MemoryRouter>
        <Projects />
      </MemoryRouter>
    );

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

    render(
      <MemoryRouter>
        <Projects />
      </MemoryRouter>
    );

    await screen.findByText(/you have not created any projects yet/i);

    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    expect(await screen.findByText(/project name is required/i)).toBeInTheDocument();
    expect(projectsApi.create).not.toHaveBeenCalled();
  });

  it('shows empty state when there are no projects', async () => {
    vi.mocked(projectsApi.list).mockResolvedValue({ data: [] });

    render(
      <MemoryRouter>
        <Projects />
      </MemoryRouter>
    );

    expect(
      await screen.findByText(/you have not created any projects yet/i)
    ).toBeInTheDocument();
  });

  it('logs out on unauthorized list response', async () => {
    vi.mocked(projectsApi.list).mockRejectedValue(new ApiRequestError(401, 'Not authenticated'));

    render(
      <MemoryRouter>
        <Projects />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('logs out on unauthorized create response', async () => {
    vi.mocked(projectsApi.list).mockResolvedValue({ data: [] });
    vi.mocked(projectsApi.create).mockRejectedValue(new ApiRequestError(403, 'Forbidden'));

    render(
      <MemoryRouter>
        <Projects />
      </MemoryRouter>
    );

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
