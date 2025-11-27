// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProjectFinance from './pages/ProjectFinance';
import Dashboard from './pages/Dashboard';
import Layout from './components/Layout';
// 👇 НЕ ЗАБУДЬ ЦІ ІМПОРТИ
import ProjectView from './pages/ProjectView';
import PageView from './pages/PageView';
import ProjectAI from './pages/ProjectAI';

const PrivateRoute = () => {
  const { user, isLoading } = useAuth();
  if (isLoading) return <div className="flex h-screen items-center justify-center">Loading...</div>;
  
  // Якщо юзер залогінений -> показуємо Layout (з Хедером)
  // Всі дочірні роути (Dashboard, ProjectView) будуть всередині Layout
  return user ? <Layout /> : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* ЗАХИЩЕНА ЗОНА (всередині Layout) */}
          <Route element={<PrivateRoute />}>
            
            {/* 1. Головна: Дашборд */}
            <Route path="/" element={<Dashboard />} />

            {/* 2. Проект: Має свій Outlet для сторінок */}
            <Route path="/project/:projectId" element={<ProjectView />}>
               {/* 3. Сторінка: Відображається всередині ProjectView */}
               {/* Повний шлях буде: /project/123/page/456 */}
               <Route path="page/:pageId" element={<PageView />} />
               <Route path="finance" element={<ProjectFinance />} />
               <Route path="ai-analytics" element={<ProjectAI />} />
            </Route>

          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;