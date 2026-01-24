import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProjectDetail from './ProjectDetail';

const mockLogout = vi.fn();
const mockNavigate = vi.fn();

vi.mock('../hooks/useLogout', () => ({
  useLogout: () => ({ logout: mockLogout }),
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom'
  );
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../api/client', async () => {
  const actual = await vi.importActual<typeof import('../api/client')>(
    '../api/client'
  );
  return {
    ...actual,
    projectsApi: {
      get: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
    tasksApi: {
      list: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      toggleStatus: vi.fn(),
    },
  };
});

import { ApiRequestError, projectsApi, tasksApi } from '../api/client';

describe('ProjectDetail page', () => {
  beforeEach(() => {
    vi.mocked(projectsApi.get).mockReset();
    vi.mocked(projectsApi.update).mockReset();
    vi.mocked(projectsApi.delete).mockReset();
    vi.mocked(tasksApi.list).mockReset();
    vi.mocked(tasksApi.create).mockReset();
    vi.mocked(tasksApi.update).mockReset();
    vi.mocked(tasksApi.toggleStatus).mockReset();
    mockLogout.mockReset();
    mockNavigate.mockReset();
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });
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

  // Story 2.3: Edit Project tests

  it('shows edit button when viewing project', async () => {
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

    expect(await screen.findByRole('button', { name: /edit/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument();
  });

  it('toggles edit mode when edit button clicked', async () => {
    const user = userEvent.setup();
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

    const editButton = await screen.findByRole('button', { name: /edit/i });
    await user.click(editButton);

    expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('saves updated name and exits edit mode', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(projectsApi.update).mockResolvedValue({
      data: {
        id: 1,
        name: 'Updated Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T12:00:00Z',
      },
    });

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', { name: /edit/i });
    await user.click(editButton);

    const input = screen.getByLabelText(/project name/i);
    await user.clear(input);
    await user.type(input, 'Updated Plan');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    await waitFor(() => {
      expect(projectsApi.update).toHaveBeenCalledWith(1, { name: 'Updated Plan' });
    });

    expect(await screen.findByText('Updated Plan')).toBeInTheDocument();
    expect(screen.queryByLabelText(/project name/i)).not.toBeInTheDocument();
  });

  it('shows validation error for empty name', async () => {
    const user = userEvent.setup();
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

    const editButton = await screen.findByRole('button', { name: /edit/i });
    await user.click(editButton);

    const input = screen.getByLabelText(/project name/i);
    await user.clear(input);

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    expect(await screen.findByText(/project name is required/i)).toBeInTheDocument();
    expect(projectsApi.update).not.toHaveBeenCalled();
  });

  it('cancels edit and restores original name', async () => {
    const user = userEvent.setup();
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

    const editButton = await screen.findByRole('button', { name: /edit/i });
    await user.click(editButton);

    const input = screen.getByLabelText(/project name/i);
    await user.clear(input);
    await user.type(input, 'Changed Name');

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(screen.queryByLabelText(/project name/i)).not.toBeInTheDocument();
    expect(screen.getByText('Launch Plan')).toBeInTheDocument();
    expect(projectsApi.update).not.toHaveBeenCalled();
  });

  it('confirms delete, calls API, and navigates to projects', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(projectsApi.delete).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });

    renderWithRoute('1');

    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    await waitFor(() => {
      expect(confirmSpy).toHaveBeenCalled();
      expect(projectsApi.delete).toHaveBeenCalledWith(1);
      expect(mockNavigate).toHaveBeenCalledWith('/projects');
    });

    confirmSpy.mockRestore();
  });

  it('cancels delete and does not call API', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
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

    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    expect(confirmSpy).toHaveBeenCalled();
    expect(projectsApi.delete).not.toHaveBeenCalled();
    expect(mockNavigate).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  it('disables delete button while deleting', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    let resolveDelete: (value: { data: unknown }) => void;
    const deletePromise = new Promise<{ data: unknown }>((resolve) => {
      resolveDelete = resolve;
    });

    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(projectsApi.delete).mockReturnValue(deletePromise);

    renderWithRoute('1');

    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    await waitFor(() => {
      expect(confirmSpy).toHaveBeenCalled();
      expect(deleteButton).toBeDisabled();
      expect(deleteButton).toHaveTextContent(/deleting/i);
    });

    resolveDelete!({ data: {} });
    confirmSpy.mockRestore();
  });

  it('shows error when delete returns 403', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(projectsApi.delete).mockRejectedValue(
      new ApiRequestError(403, 'Forbidden')
    );

    renderWithRoute('1');

    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    expect(await screen.findByText(/permission to delete/i)).toBeInTheDocument();
    expect(mockNavigate).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  it('shows error when delete returns 404', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(projectsApi.delete).mockRejectedValue(
      new ApiRequestError(404, 'Project not found')
    );

    renderWithRoute('1');

    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    expect(await screen.findByText(/project not found/i)).toBeInTheDocument();
    expect(mockNavigate).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  it('logs out when delete returns 401', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(projectsApi.delete).mockRejectedValue(
      new ApiRequestError(401, 'Not authenticated')
    );

    renderWithRoute('1');

    const deleteButton = await screen.findByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
    expect(mockNavigate).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  // Story 3.1: Tasks list + create

  it('renders task list', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });

    renderWithRoute('1');

    expect(await screen.findByText('Design flows')).toBeInTheDocument();
  });

  it('creates a task and adds it to the list', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });
    vi.mocked(tasksApi.create).mockResolvedValue({
      data: {
        id: 11,
        title: 'Write tests',
        is_complete: false,
        project_id: 1,
        created_at: '2026-01-23T00:00:00Z',
        updated_at: '2026-01-23T00:00:00Z',
      },
    });

    renderWithRoute('1');

    const input = await screen.findByPlaceholderText(/new task title/i);
    await user.type(input, 'Write tests');

    const addButton = screen.getByRole('button', { name: /add task/i });
    await user.click(addButton);

    await waitFor(() => {
      expect(tasksApi.create).toHaveBeenCalledWith(1, { title: 'Write tests' });
    });

    expect(await screen.findByText('Write tests')).toBeInTheDocument();
  });

  it('prevents duplicate task submissions while creating', async () => {
    const user = userEvent.setup();
    let resolveCreate: (value: { data: unknown }) => void;
    const createPromise = new Promise<{ data: unknown }>((resolve) => {
      resolveCreate = resolve;
    });
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });
    vi.mocked(tasksApi.create).mockReturnValue(createPromise);

    renderWithRoute('1');

    const input = await screen.findByPlaceholderText(/new task title/i);
    await user.type(input, 'Dedup task');

    const addButton = screen.getByRole('button', { name: /add task/i });
    await user.click(addButton);
    await user.click(addButton);

    expect(tasksApi.create).toHaveBeenCalledTimes(1);

    resolveCreate!({ data: { id: 99 } });
  });

  it('shows validation error for empty task title', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });

    renderWithRoute('1');

    const input = await screen.findByPlaceholderText(/new task title/i);
    await user.clear(input);

    const addButton = screen.getByRole('button', { name: /add task/i });
    await user.click(addButton);

    expect(await screen.findByText(/task title is required/i)).toBeInTheDocument();
    expect(tasksApi.create).not.toHaveBeenCalled();
  });

  it('shows validation error for too long task title', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });

    renderWithRoute('1');

    const input = await screen.findByPlaceholderText(/new task title/i);
    await user.type(input, 'x'.repeat(201));

    const addButton = screen.getByRole('button', { name: /add task/i });
    await user.click(addButton);

    expect(
      await screen.findByText(/200 characters or less/i)
    ).toBeInTheDocument();
    expect(tasksApi.create).not.toHaveBeenCalled();
  });

  it('shows validation error when task create returns 422', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });
    vi.mocked(tasksApi.create).mockRejectedValue(
      new ApiRequestError(422, 'Validation error')
    );

    renderWithRoute('1');

    const input = await screen.findByPlaceholderText(/new task title/i);
    await user.type(input, 'Bad title');

    const addButton = screen.getByRole('button', { name: /add task/i });
    await user.click(addButton);

    expect(await screen.findByText(/validation error/i)).toBeInTheDocument();
  });

  it('shows empty state when no tasks exist', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });

    renderWithRoute('1');

    expect(
      await screen.findByText(/no tasks yet/i)
    ).toBeInTheDocument();
  });

  it('shows tasks loading state', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockReturnValue(new Promise(() => undefined));

    renderWithRoute('1');

    expect(await screen.findByText(/loading tasks/i)).toBeInTheDocument();
  });

  it('shows error when tasks list returns 403', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockRejectedValue(
      new ApiRequestError(403, 'Forbidden')
    );

    renderWithRoute('1');

    expect(
      await screen.findByText(/permission to view tasks/i)
    ).toBeInTheDocument();
    expect(screen.queryByText(/no tasks yet/i)).not.toBeInTheDocument();
  });

  it('logs out when tasks list returns 401', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockRejectedValue(
      new ApiRequestError(401, 'Not authenticated')
    );

    renderWithRoute('1');

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('shows error when tasks list returns 404', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockRejectedValue(
      new ApiRequestError(404, 'Project not found')
    );

    renderWithRoute('1');

    expect(
      await screen.findByText(/project not found/i)
    ).toBeInTheDocument();
  });

  it('shows error when task create returns 403', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });
    vi.mocked(tasksApi.create).mockRejectedValue(
      new ApiRequestError(403, 'Forbidden')
    );

    renderWithRoute('1');

    const input = await screen.findByPlaceholderText(/new task title/i);
    await user.type(input, 'Blocked task');

    const addButton = screen.getByRole('button', { name: /add task/i });
    await user.click(addButton);

    expect(
      await screen.findByText(/permission to create tasks/i)
    ).toBeInTheDocument();
  });

  it('shows error when task create returns 404', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });
    vi.mocked(tasksApi.create).mockRejectedValue(
      new ApiRequestError(404, 'Project not found')
    );

    renderWithRoute('1');

    const input = await screen.findByPlaceholderText(/new task title/i);
    await user.type(input, 'Missing task');

    const addButton = screen.getByRole('button', { name: /add task/i });
    await user.click(addButton);

    expect(
      await screen.findByText(/project not found/i)
    ).toBeInTheDocument();
  });

  it('logs out when task create returns 401', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({ data: [] });
    vi.mocked(tasksApi.create).mockRejectedValue(
      new ApiRequestError(401, 'Not authenticated')
    );

    renderWithRoute('1');

    const input = await screen.findByPlaceholderText(/new task title/i);
    await user.type(input, 'Logout task');

    const addButton = screen.getByRole('button', { name: /add task/i });
    await user.click(addButton);

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  // Story 3.2: Edit Task

  it('shows edit controls for a task when edit clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', {
      name: /edit task/i,
    });
    await user.click(editButton);

    expect(screen.getByLabelText(/edit task title/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('saves task title updates and exits edit mode', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.update).mockResolvedValue({
      data: {
        id: 10,
        title: 'Updated flows',
        is_complete: false,
        project_id: 1,
        created_at: '2026-01-23T00:00:00Z',
        updated_at: '2026-01-24T00:00:00Z',
      },
    });

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', {
      name: /edit task/i,
    });
    await user.click(editButton);

    const input = screen.getByLabelText(/edit task title/i);
    await user.clear(input);
    await user.type(input, '  Updated flows  ');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    await waitFor(() => {
      expect(tasksApi.update).toHaveBeenCalledWith(1, 10, {
        title: 'Updated flows',
      });
    });

    expect(await screen.findByText('Updated flows')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
  });

  it('shows validation error for empty task title and does not submit', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', {
      name: /edit task/i,
    });
    await user.click(editButton);

    const input = screen.getByLabelText(/edit task title/i);
    await user.clear(input);

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    expect(await screen.findByText(/task title is required/i)).toBeInTheDocument();
    expect(tasksApi.update).not.toHaveBeenCalled();
  });

  it('shows error when task update returns 403', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.update).mockRejectedValue(
      new ApiRequestError(403, 'Forbidden')
    );

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', {
      name: /edit task/i,
    });
    await user.click(editButton);

    const input = screen.getByLabelText(/edit task title/i);
    await user.clear(input);
    await user.type(input, 'Updated');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    expect(
      await screen.findByText(/permission to edit this task/i)
    ).toBeInTheDocument();
  });

  it('shows error when task update returns 404', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.update).mockRejectedValue(
      new ApiRequestError(404, 'Task not found')
    );

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', {
      name: /edit task/i,
    });
    await user.click(editButton);

    const input = screen.getByLabelText(/edit task title/i);
    await user.clear(input);
    await user.type(input, 'Updated');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    expect(await screen.findByText(/task not found/i)).toBeInTheDocument();
  });

  it('logs out when task update returns 401', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.update).mockRejectedValue(
      new ApiRequestError(401, 'Not authenticated')
    );

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', {
      name: /edit task/i,
    });
    await user.click(editButton);

    const input = screen.getByLabelText(/edit task title/i);
    await user.clear(input);
    await user.type(input, 'Updated');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('shows error when task update returns 422', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.update).mockRejectedValue(
      new ApiRequestError(422, 'Invalid')
    );

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', {
      name: /edit task/i,
    });
    await user.click(editButton);

    const input = screen.getByLabelText(/edit task title/i);
    await user.clear(input);
    await user.type(input, 'Updated');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    expect(await screen.findByText(/invalid task title/i)).toBeInTheDocument();
  });

  it('cancels task edit and restores original title', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });

    renderWithRoute('1');

    const editButton = await screen.findByRole('button', {
      name: /edit task/i,
    });
    await user.click(editButton);

    const input = screen.getByLabelText(/edit task title/i);
    await user.clear(input);
    await user.type(input, 'Changed');

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(screen.queryByDisplayValue('Changed')).not.toBeInTheDocument();
    expect(await screen.findByText('Design flows')).toBeInTheDocument();
    expect(tasksApi.update).not.toHaveBeenCalled();
  });

  // Story 3.3: Toggle Task Status

  it('toggles task from incomplete to complete', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.toggleStatus).mockResolvedValue({
      data: {
        id: 10,
        title: 'Design flows',
        is_complete: true,
        project_id: 1,
        created_at: '2026-01-23T00:00:00Z',
        updated_at: '2026-01-24T00:00:00Z',
      },
    });

    renderWithRoute('1');

    const toggleButton = await screen.findByRole('button', {
      name: /mark task as complete/i,
    });
    await user.click(toggleButton);

    await waitFor(() => {
      expect(tasksApi.toggleStatus).toHaveBeenCalledWith(1, 10, {
        is_complete: true,
      });
    });

    expect(await screen.findByText('Design flows')).toHaveClass('line-through');
  });

  it('toggles task from complete to incomplete', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: true,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.toggleStatus).mockResolvedValue({
      data: {
        id: 10,
        title: 'Design flows',
        is_complete: false,
        project_id: 1,
        created_at: '2026-01-23T00:00:00Z',
        updated_at: '2026-01-24T00:00:00Z',
      },
    });

    renderWithRoute('1');

    const toggleButton = await screen.findByRole('button', {
      name: /mark task as incomplete/i,
    });
    await user.click(toggleButton);

    await waitFor(() => {
      expect(tasksApi.toggleStatus).toHaveBeenCalledWith(1, 10, {
        is_complete: false,
      });
    });

    expect(await screen.findByText('Design flows')).not.toHaveClass(
      'line-through'
    );
  });

  it('shows strikethrough styling for completed tasks', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: true,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });

    renderWithRoute('1');

    const title = await screen.findByText('Design flows');
    expect(title).toHaveClass('line-through');
  });

  it('shows normal styling for incomplete tasks', async () => {
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });

    renderWithRoute('1');

    const title = await screen.findByText('Design flows');
    expect(title).not.toHaveClass('line-through');
  });

  it('shows error when toggle fails', async () => {
    const user = userEvent.setup();
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.toggleStatus).mockRejectedValue(
      new ApiRequestError(403, 'Forbidden')
    );

    renderWithRoute('1');

    const toggleButton = await screen.findByRole('button', {
      name: /mark task as complete/i,
    });
    await user.click(toggleButton);

    expect(
      await screen.findByText(/permission to update this task/i)
    ).toBeInTheDocument();
  });

  it('disables toggle and edit buttons while toggle is in flight', async () => {
    const user = userEvent.setup();
    let resolveToggle: (value: { data: unknown }) => void;
    const togglePromise = new Promise<{ data: unknown }>((resolve) => {
      resolveToggle = resolve;
    });
    vi.mocked(projectsApi.get).mockResolvedValue({
      data: {
        id: 1,
        name: 'Launch Plan',
        user_id: 1,
        created_at: '2026-01-21T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
      },
    });
    vi.mocked(tasksApi.list).mockResolvedValue({
      data: [
        {
          id: 10,
          title: 'Design flows',
          is_complete: false,
          project_id: 1,
          created_at: '2026-01-23T00:00:00Z',
          updated_at: '2026-01-23T00:00:00Z',
        },
      ],
    });
    vi.mocked(tasksApi.toggleStatus).mockReturnValue(togglePromise);

    renderWithRoute('1');

    const toggleButton = await screen.findByRole('button', {
      name: /mark task as complete/i,
    });
    const editButton = await screen.findByRole('button', { name: /edit task/i });

    await user.click(toggleButton);

    expect(toggleButton).toBeDisabled();
    expect(editButton).toBeDisabled();

    resolveToggle!({
      data: {
        id: 10,
        title: 'Design flows',
        is_complete: true,
        project_id: 1,
        created_at: '2026-01-23T00:00:00Z',
        updated_at: '2026-01-24T00:00:00Z',
      },
    });
  });
});
