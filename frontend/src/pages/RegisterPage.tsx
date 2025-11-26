// src/pages/RegisterPage.tsx
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../api/services';
import { useNavigate, Link } from 'react-router-dom';

export default function RegisterPage() {
  const [formData, setFormData] = useState({ email: '', username: '', password: '' });
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Проста валідація
    if (formData.username.length < 3) return setError('Username must be at least 3 chars');
    if (formData.password.length < 6) return setError('Password must be at least 6 chars');

    try {
      // 1. Реєструємося (бекенд повертає токен)
      const { data: token } = await authService.register(formData);
      // 2. Одразу логінимо юзера цим токеном
      login(token);
      // 3. Перекидаємо на головну
      navigate('/');
    } catch (err: any) {
      // Виводимо помилку від бекенду (наприклад "User already exists")
      const msg = err.response?.data?.detail || 'Registration failed';
      setError(msg);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
        <div className="mb-8 flex flex-col items-center">
        <img src="/logo.png" alt="LiriliLarila Logo" className="h-16 w-16 mb-4" />
        <h1 className="text-3xl font-bold tracking-tight text-[#1B5448] font-['Montserrat']">LiriliLarila</h1>
      </div>
      <div className="p-8 bg-white rounded shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6 text-center">Create Account</h1>
        
        {error && (
            <div className="bg-red-100 text-red-700 p-2 rounded mb-4 text-sm">
                {error}
            </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            className="border p-2 rounded"
            type="email"
            placeholder="Email"
            required
            value={formData.email}
            onChange={e => setFormData({...formData, email: e.target.value})}
          />
          <input
            className="border p-2 rounded"
            type="text"
            placeholder="Username"
            required
            value={formData.username}
            onChange={e => setFormData({...formData, username: e.target.value})}
          />
          <input
            className="border p-2 rounded"
            type="password"
            placeholder="Password (min 6 chars)"
            required
            value={formData.password}
            onChange={e => setFormData({...formData, password: e.target.value})}
          />
          <button className="bg-green-600 text-white p-2 rounded hover:bg-green-700 font-medium">
            Register
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 hover:underline">
            Log in
          </Link>
        </div>
      </div>
    </div>
  );
}