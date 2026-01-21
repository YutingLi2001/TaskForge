interface HeaderProps {
  onLogout: () => void;
  userEmail?: string | null;
}

export default function Header({ onLogout, userEmail }: HeaderProps) {
  return (
    <header className="fixed top-0 z-10 w-full bg-white shadow">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="text-lg font-semibold text-gray-900">TaskForge</span>
          {userEmail ? (
            <span className="text-sm text-gray-600">{userEmail}</span>
          ) : null}
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
