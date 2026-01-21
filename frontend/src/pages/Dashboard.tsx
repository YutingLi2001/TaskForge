import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { useLogout } from '../hooks/useLogout';

export default function Dashboard() {
  const userEmail = localStorage.getItem('user_email');
  const { logout } = useLogout();
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onLogout={logout} userEmail={userEmail} />
      <main className="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-6 pt-20">
        <div className="rounded-lg bg-white p-8 shadow-md">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">You are logged in.</p>
        </div>
      </main>
    </div>
  );
}
