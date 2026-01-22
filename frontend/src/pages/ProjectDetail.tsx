import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Header from '../components/Header';
import { ApiRequestError, projectsApi } from '../api/client';
import type { ProjectData } from '../api/client';
import { useLogout } from '../hooks/useLogout';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const { logout } = useLogout();
  const userEmail = localStorage.getItem('user_email');
  const [project, setProject] = useState<ProjectData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
  }, [id, logout]);

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
          <section className="rounded-lg bg-white p-6 shadow-md">
            <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
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
          </section>
        ) : null}
      </main>
    </div>
  );
}
