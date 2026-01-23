import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import Header from '../components/Header';
import { ApiRequestError, projectsApi, tasksApi } from '../api/client';
import type { ProjectData, TaskData } from '../api/client';
import { useLogout } from '../hooks/useLogout';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const { logout } = useLogout();
  const navigate = useNavigate();
  const userEmail = localStorage.getItem('user_email');
  const [project, setProject] = useState<ProjectData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [tasks, setTasks] = useState<TaskData[]>([]);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [tasksLoaded, setTasksLoaded] = useState(false);
  const [taskError, setTaskError] = useState<string | null>(null);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [creatingTask, setCreatingTask] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editTaskTitle, setEditTaskTitle] = useState('');
  const [editTaskError, setEditTaskError] = useState<string | null>(null);
  const [savingTask, setSavingTask] = useState(false);

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editError, setEditError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!id) {
      setError('Project not found.');
      setLoading(false);
      return;
    }

    let active = true;
    setLoading(true);
    projectsApi
      .get(parseInt(id, 10))
      .then((response) => {
        if (!active) return;
        setProject(response.data);
        setError(null);
        setDeleteError(null);
      })
      .catch((err) => {
        if (!active) return;
        if (err instanceof ApiRequestError) {
          if (err.status === 401) {
            logout();
            return;
          }
          if (err.status === 403) {
            setError('You do not have access to this project.');
            return;
          }
          if (err.status === 404) {
            setError('Project not found.');
            return;
          }
        }
        setError(err instanceof Error ? err.message : 'Failed to load project');
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleEdit = () => {
    setEditName(project?.name ?? '');
    setEditError(null);
    setDeleteError(null);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditError(null);
  };

  const handleSave = async () => {
    const trimmed = editName.trim();
    if (!trimmed) {
      setEditError('Project name is required.');
      return;
    }

    if (!project) return;

    setSaving(true);
    setEditError(null);

    try {
      const response = await projectsApi.update(project.id, { name: trimmed });
      setProject(response.data);
      setIsEditing(false);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        if (err.status === 401) {
          logout();
          return;
        }
        if (err.status === 403) {
          setEditError('You do not have permission to edit this project.');
          return;
        }
        if (err.status === 404) {
          setEditError('Project not found.');
          return;
        }
      }
      setEditError(err instanceof Error ? err.message : 'Failed to update project');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!project) return;
    if (deleting) return;
    setDeleting(true);
    const confirmed = window.confirm('Delete this project?');
    if (!confirmed) {
      setDeleting(false);
      return;
    }

    setDeleteError(null);

    try {
      await projectsApi.delete(project.id);
      setDeleteError(null);
      navigate('/projects');
    } catch (err) {
      if (err instanceof ApiRequestError) {
        if (err.status === 401) {
          logout();
          return;
        }
        if (err.status === 403) {
          setDeleteError('You do not have permission to delete this project.');
          return;
        }
        if (err.status === 404) {
          setDeleteError('Project not found.');
          return;
        }
      }
      setDeleteError(err instanceof Error ? err.message : 'Failed to delete project');
    } finally {
      setDeleting(false);
    }
  };

  useEffect(() => {
    if (!project) return;

    let active = true;
    setTasks([]);
    setTasksLoading(true);
    setTasksLoaded(false);
    setTaskError(null);
    tasksApi
      .list(project.id)
      .then((response) => {
        if (!active) return;
        setTasks(response.data);
        setTasksLoaded(true);
      })
      .catch((err) => {
        if (!active) return;
        if (err instanceof ApiRequestError) {
          if (err.status === 401) {
            logout();
            return;
          }
          if (err.status === 403) {
            setTaskError('You do not have permission to view tasks for this project.');
            return;
          }
          if (err.status === 404) {
            setTaskError('Project not found.');
            return;
          }
        }
        setTaskError(err instanceof Error ? err.message : 'Failed to load tasks');
      })
      .finally(() => {
        if (!active) return;
        setTasksLoading(false);
      });

    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [project?.id]);

  const handleCreateTask = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!project) return;
    if (creatingTask) return;

    const trimmed = newTaskTitle.trim();
    if (!trimmed) {
      setTaskError('Task title is required.');
      return;
    }
    if (trimmed.length > 200) {
      setTaskError('Task title must be 200 characters or less.');
      return;
    }

    setCreatingTask(true);
    setTaskError(null);

    try {
      const response = await tasksApi.create(project.id, { title: trimmed });
      setTasks((current) => [...current, response.data]);
      setNewTaskTitle('');
    } catch (err) {
      if (err instanceof ApiRequestError) {
        if (err.status === 401) {
          logout();
          return;
        }
        if (err.status === 422) {
          setTaskError(err.detail ?? 'Task title is invalid.');
          return;
        }
        if (err.status === 403) {
          setTaskError('You do not have permission to create tasks for this project.');
          return;
        }
        if (err.status === 404) {
          setTaskError('Project not found.');
          return;
        }
      }
      setTaskError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setCreatingTask(false);
    }
  };

  const handleEditTask = (task: TaskData) => {
    if (savingTask) return;
    setEditingTaskId(task.id);
    setEditTaskTitle(task.title);
    setEditTaskError(null);
  };

  const handleCancelEditTask = () => {
    setEditingTaskId(null);
    setEditTaskTitle('');
    setEditTaskError(null);
  };

  const handleSaveTask = async (taskId: number) => {
    if (!project) return;
    if (savingTask) return;

    const trimmed = editTaskTitle.trim();
    if (!trimmed) {
      setEditTaskError('Task title is required.');
      return;
    }
    if (trimmed.length > 200) {
      setEditTaskError('Task title must be 200 characters or less.');
      return;
    }

    setSavingTask(true);
    setEditTaskError(null);

    try {
      const response = await tasksApi.update(project.id, taskId, {
        title: trimmed,
      });
      setTasks((current) =>
        current.map((task) => (task.id === taskId ? response.data : task))
      );
      setEditingTaskId(null);
      setEditTaskTitle('');
      setEditTaskError(null);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        if (err.status === 401) {
          logout();
          return;
        }
        if (err.status === 403) {
          setEditTaskError('You do not have permission to edit this task.');
          return;
        }
        if (err.status === 404) {
          setEditTaskError('Task not found.');
          return;
        }
        if (err.status === 422) {
          setEditTaskError('Invalid task title.');
          return;
        }
      }
      setEditTaskError(
        err instanceof Error ? err.message : 'Failed to update task'
      );
    } finally {
      setSavingTask(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onLogout={logout} userEmail={userEmail} />
      <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-6 px-6 pb-12 pt-24">
        <Link to="/projects" className="text-sm text-blue-600 hover:underline">
          &larr; Back to Projects
        </Link>

        {loading ? (
          <p className="text-sm text-gray-600">Loading project...</p>
        ) : error ? (
          <div className="rounded-lg bg-white p-6 shadow-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : project ? (
          <>
            <section className="rounded-lg bg-white p-6 shadow-md">
              {isEditing ? (
                <div className="space-y-4">
                  <div>
                    <label htmlFor="project-name" className="text-sm font-medium text-gray-700">
                      Project name
                    </label>
                    <input
                      id="project-name"
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="mt-2 w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  {editError && (
                    <p className="text-sm text-red-600">{editError}</p>
                  )}
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={handleSave}
                      disabled={saving}
                      className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
                    >
                      {saving ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      type="button"
                      onClick={handleCancel}
                      disabled={saving}
                      className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-70"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between">
                    <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={handleEdit}
                        disabled={deleting}
                        className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={handleDelete}
                        disabled={deleting}
                        className="inline-flex items-center justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
                      >
                        {deleting ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2 text-sm text-gray-600">
                    <p>
                      Created:{' '}
                      {new Date(project.created_at).toLocaleString(undefined, {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                    <p>
                      Updated:{' '}
                      {new Date(project.updated_at).toLocaleString(undefined, {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                  {deleteError ? (
                    <p className="mt-4 text-sm text-red-600">{deleteError}</p>
                  ) : null}
                </>
              )}
            </section>

            <section className="rounded-lg bg-white p-6 shadow-md">
              <h2 className="text-lg font-semibold text-gray-900">Tasks</h2>
              <form onSubmit={handleCreateTask} className="mt-4 flex gap-2">
                <input
                  type="text"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="New task title"
                  className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  disabled={creatingTask || tasksLoading}
                  className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {creatingTask ? 'Adding...' : 'Add Task'}
                </button>
              </form>
              {taskError ? (
                <p className="mt-2 text-sm text-red-600">{taskError}</p>
              ) : null}

              {tasksLoading ? (
                <p className="mt-4 text-sm text-gray-600">Loading tasks...</p>
              ) : taskError ? null : !tasksLoaded ? null : tasks.length === 0 ? (
                <p className="mt-4 text-sm text-gray-500">
                  No tasks yet. Add one above!
                </p>
              ) : (
                <ul className="mt-4 space-y-2">
                  {tasks.map((task) => (
                    <li
                      key={task.id}
                      className="flex items-center gap-3 rounded-md border border-gray-200 px-4 py-3"
                    >
                      {editingTaskId === task.id ? (
                        <div className="flex w-full flex-col gap-2">
                          <div className="flex w-full items-center gap-2">
                            <input
                              type="text"
                              value={editTaskTitle}
                              onChange={(event) =>
                                setEditTaskTitle(event.target.value)
                              }
                              className="flex-1 rounded-md border border-gray-300 px-2 py-1 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                              disabled={savingTask}
                              aria-label="Edit task title"
                            />
                            <button
                              type="button"
                              onClick={() => handleSaveTask(task.id)}
                              disabled={savingTask}
                              className="rounded-md bg-blue-600 px-3 py-1 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
                            >
                              {savingTask ? 'Saving...' : 'Save'}
                            </button>
                            <button
                              type="button"
                              onClick={handleCancelEditTask}
                              disabled={savingTask}
                              className="rounded-md border border-gray-300 bg-white px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-70"
                            >
                              Cancel
                            </button>
                          </div>
                          {editTaskError ? (
                            <p className="text-sm text-red-600">
                              {editTaskError}
                            </p>
                          ) : null}
                        </div>
                      ) : (
                        <>
                          <span
                            className={`h-3 w-3 rounded-full ${
                              task.is_complete ? 'bg-green-500' : 'bg-gray-300'
                            }`}
                          />
                          <span
                            className={
                              task.is_complete
                                ? 'text-gray-500 line-through'
                                : 'text-gray-900'
                            }
                          >
                            {task.title}
                          </span>
                          <button
                            type="button"
                            onClick={() => handleEditTask(task)}
                            disabled={savingTask}
                            className="ml-auto text-sm font-medium text-blue-600 hover:underline disabled:cursor-not-allowed disabled:opacity-60"
                            aria-label={`Edit task ${task.title}`}
                          >
                            Edit
                          </button>
                        </>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        ) : null}
      </main>
    </div>
  );
}
