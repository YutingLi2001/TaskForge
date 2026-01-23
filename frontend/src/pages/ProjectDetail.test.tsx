import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import ProjectDetail from './ProjectDetail';

const mockLogout = vi.fn();

vi.mock('../hooks/useLogout', () => ({
  useLogout: () => ({ logout: mockLogout }),
}));

vi.mock('../api/client', async () => {
  const actual = await vi.importActual<typeof import('../api/client')>(
    '../api/client'
  );
  return {
    ...actual,
    projectsApi: {
      get: vi.fn(),
    },
  };
});

import { ApiRequestError, projectsApi } from '../api/client';

describe('ProjectDetail page', () => {
  beforeEach(() => {
    vi.mocked(projectsApi.get).mockReset();
    mockLogout.mockReset();
  });

  const renderWithRoute = (id: string) =>
    render(
      <MemoryRouter initialEntries={[`/projects/${id}`]}>
        <Routes>
          <Route path="/projects/:id" element={<ProjectDetail />} />
        </Routes>
      </MemoryRouter>
    );

  it('shows loading state', async () => {
    vi.mocked(projectsApi.get).mockReturnValue(new Promise(() => undefined));

    renderWithRoute('1');

    expect(screen.getByText(/loading project/i)).toBeInTheDocument();
  });

  it('renders project data', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });

    renderWithRoute('1');

    expect(await screen.findByText('Launch Plan')).toBeInTheDocument();
  });

  it('shows error for 404', async () => {
    vi.mocked(projectsApi.get).mockRejectedValue(
      new ApiRequestError(404, 'Project not found')
    );

    renderWithRoute('99');

    expect(await screen.findByText(/project not found/i)).toBeInTheDocument();
  });

  it('shows error for 403', async () => {
    vi.mocked(projectsApi.get).mockRejectedValue(
      new ApiRequestError(403, 'Forbidden')
    );

    renderWithRoute('2');

    expect(
      await screen.findByText(/do not have access/i)
    ).toBeInTheDocument();
  });

  it('logs out on 401', async () => {
    vi.mocked(projectsApi.get).mockRejectedValue(
      new ApiRequestError(401, 'Not authenticated')
    );

    renderWithRoute('2');

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('shows back link to projects', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });

    renderWithRoute('1');

    expect(await screen.findByRole('link', { name: /back to projects/i })).toBeInTheDocument();
  });
});
