// src/pages/Dashboard.tsx
import { useEffect, useState } from 'react';
import { projectService } from '../api/services';
import type { Project } from '../types';
import { Link } from 'react-router-dom';
import CreateProjectModal from '../components/modals/CreateProjectModal';

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const { data } = await projectService.getAll();
      setProjects(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load projects');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8">
      {/* Заголовок (Тепер без зайвої кнопки) */}
      <div className="max-w-6xl mx-auto mb-6">
          <h2 className="text-2xl font-bold text-gray-800 font-['Montserrat']">My Projects</h2>
      </div>

      {isLoading && (
        <div className="flex justify-center mt-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1B5448]"></div>
        </div>
      )}

      {error && !isLoading && (
        <div className="max-w-6xl mx-auto bg-red-100 text-red-700 p-4 rounded-md mb-6">
          {error}
        </div>
      )}

      {!isLoading && !error && (
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Велика картка створення (Залишаємо тільки її) */}
          <button 
            onClick={() => setIsModalOpen(true)}
            className="flex flex-col items-center justify-center h-48 border-2 border-dashed border-gray-300 rounded-xl hover:border-[#1B5448] hover:bg-green-50 transition group cursor-pointer bg-white"
          >
            <div className="h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center group-hover:bg-[#1B5448]/10 transition mb-2">
               <span className="text-2xl text-gray-500 group-hover:text-[#1B5448] pb-1">+</span>
            </div>
            <span className="text-gray-500 font-medium group-hover:text-[#1B5448]">Create New Project</span>
          </button>

          {/* Список проектів */}
          {projects.map((project) => (
            <Link 
              key={project._id} 
              to={`/project/${project._id}`}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition flex flex-col justify-between h-48 group"
            >
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-2 truncate group-hover:text-[#1B5448] transition" title={project.name}>
                    {project.name}
                </h3>
                <p className="text-gray-500 text-sm line-clamp-3">
                    {project.description || "No description provided."}
                </p>
              </div>
              
              <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
                <span className="text-xs text-gray-400 font-mono">
                    ID: {project._id.slice(-4)}
                </span>
                <span className="text-sm font-semibold text-green-600 bg-green-50 px-2 py-1 rounded">
                   ${project.cost}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      <CreateProjectModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onSuccess={fetchProjects} 
      />
    </div>
  );
}