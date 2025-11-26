// src/pages/LoginPage.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../api/services';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';

export default function LoginPage() {
  const [loginData, setLoginData] = useState({ login: '', password: '' });
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState('');

  useEffect(() => {
    const googleToken = searchParams.get('token');
    if (googleToken) {
      login(googleToken);
      navigate('/');
    }
  }, [searchParams, login, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const { data: token } = await authService.login(loginData);
      login(token);
      navigate('/');
    } catch (err: any) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
        <div className="mb-8 flex flex-col items-center">
        <img src="/logo.png" alt="LiriliLarila Logo" className="h-16 w-16 mb-4" />
        <h1 className="text-3xl font-bold tracking-tight text-[#1B5448] font-['Montserrat']">LiriliLarila</h1>
      </div>
      <div className="p-8 bg-white rounded shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6 text-center">Welcome Back</h1>

        {error && (
            <div className="bg-red-100 text-red-700 p-2 rounded mb-4 text-sm text-center">
                {error}
            </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            className="border p-2 rounded"
            placeholder="Username or Email"
            value={loginData.login}
            onChange={e => setLoginData({...loginData, login: e.target.value})}
          />
          <input
            className="border p-2 rounded"
            type="password"
            placeholder="Password"
            value={loginData.password}
            onChange={e => setLoginData({...loginData, password: e.target.value})}
          />
          <button className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700 font-medium">
            Sign In
          </button>
        </form>

        <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
        </div>

        {/* Кнопка з іконкою Google */}
        <a 
          href={authService.googleLoginUrl}
          className="flex items-center justify-center w-full bg-white border border-gray-300 text-gray-700 p-2 rounded hover:bg-gray-50 transition shadow-sm"
        >
           <img 
             src="https://www.svgrepo.com/show/475656/google-color.svg" 
             alt="Google" 
             className="w-5 h-5 mr-3"
           />
           <span className="font-medium">Sign in with Google</span>
        </a>

        <div className="mt-6 text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-600 hover:underline">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}