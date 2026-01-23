import { FormEvent, useCallback, useEffect, useState } from 'react';
import Header from '../components/Header';
import { Link } from 'react-router-dom';
import { ApiRequestError, projectsApi } from '../api/client';
import type { ProjectData } from '../api/client';
import { useLogout } from '../hooks/useLogout';

export default function Projects() {
  const { logout } = useLogout();
  const userEmail = localStorage.getItem('user_email');
  const handleAuthError = useCallback((err: unknown) => {
    if (err instanceof ApiRequestError && (err.status === 401 || err.status === 403)) {
      logout();
      return true;
    }
    return false;
  }, [logout]);
  const [projects, setProjects] = useState<ProjectData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    projectsApi
      .list()
      .then((response) => {
        if (!active) return;
        setProjects(response.data);
        setError(null);
      })
      .catch((err) => {
        if (!active) return;
        if (handleAuthError(err)) {
          return;
        }
        setError(err instanceof Error ? err.message : 'Failed to load projects');
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [handleAuthError]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedName = name.trim();

    if (!trimmedName) {
      setFormError('Project name is required.');
      return;
    }

    setFormError(null);
    setSubmitting(true);
    try {
      const response = await projectsApi.create({ name: trimmedName });
      setProjects((prev) => [response.data, ...prev]);
      setName('');
    } catch (err) {
      if (handleAuthError(err)) {
        return;
      }
      setFormError(err instanceof Error ? err.message : 'Unable to create project');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onLogout={logout} userEmail={userEmail} />
      <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-8 px-6 pb-12 pt-24">
        <section className="rounded-lg bg-white p-6 shadow-md">
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="mt-2 text-gray-600">
            Create and organize your projects.
          </p>
          <form onSubmit={handleSubmit} className="mt-6 space-y-3">
            <div>
              <label htmlFor="project-name" className="text-sm font-medium text-gray-700">
                Project name
              </label>
              <input
                id="project-name"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                className="mt-2 w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="e.g. Marketing site refresh"
              />
            </div>
            {formError ? (
              <p className="text-sm text-red-600">{formError}</p>
            ) : null}
            <button
              type="submit"
              disabled={submitting}
              className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? 'Creating...' : 'Create Project'}
            </button>
          </form>
        </section>

        <section className="rounded-lg bg-white p-6 shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Your projects</h2>
          </div>
          <div className="mt-4">
            {loading ? (
              <p className="text-sm text-gray-600">Loading projects...</p>
            ) : error ? (
              <p className="text-sm text-red-600">{error}</p>
            ) : projects.length === 0 ? (
              <p className="text-sm text-gray-600">
                You have not created any projects yet.
              </p>
            ) : (
              <ul className="space-y-3">
                {projects.map((project) => (
                  <li key={project.id}>
                    <Link
                      to={`/projects/${project.id}`}
                      className="block rounded-md border border-gray-200 px-4 py-3 transition-colors hover:bg-gray-50"
                    >
                      <p className="text-sm font-semibold text-gray-900">
                        {project.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        Created{' '}
                        {new Date(project.created_at).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
