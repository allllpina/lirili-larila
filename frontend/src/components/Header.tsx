// src/components/Header.tsx
import { useAuth } from '../context/AuthContext';
import { Link, useLocation } from 'react-router-dom';

export default function Header() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isDashboard = location.pathname === '/';
  
  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 sticky top-0 z-50">
      
      {/* ЛІВА ГРУПА: Лого + Назва + Навігація */}
      <div className="flex items-center gap-6">
        
        {/* Логотип */}
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition">
          <img src="/logo.png" alt="Logo" className="h-8 w-8 object-contain" />
          <span className="text-2xl font-bold tracking-tight text-[#1B5448] font-['Montserrat']">
            LiriliLarila
          </span>
        </Link>

        {/* Кнопка "My Projects" тепер всередині лівої групи */}
        {user && !isDashboard && (
            <Link 
                to="/"
                className="text-sm font-medium text-gray-500 hover:text-[#1B5448] transition flex items-center gap-1 border-l border-gray-200 pl-6 h-8"
            >
                ← My Projects
            </Link>
        )}
      </div>

      {/* ПРАВА ЧАСТИНА: Інфо про юзера + Logout */}
      <div className="flex items-center gap-6">
        {user && (
          <div className="text-right hidden sm:block">
            <div className="text-sm font-medium text-gray-900">{user.email}</div>
            <div className="text-xs text-gray-500">User ID: {user.id}</div>
          </div>
        )}
        
        <div className="h-8 w-px bg-gray-200 hidden sm:block"></div>
        
        <button onClick={logout} className="text-sm font-medium text-red-600 hover:text-red-800 transition px-3 py-1 rounded-md hover:bg-red-50">
          Logout
        </button>
      </div>
    </header>
  );
}