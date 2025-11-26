import { useEffect, useState } from 'react';
import { useParams, Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { projectService, pageService } from '../api/services';
import type { Project } from '../types';
import CollaboratorBadge from '../components/project/CollaboratorBadge';
import CreatePageModal from '../components/modals/CreatePageModal';

export interface ProjectContextType {
  project: Project;
  refreshProject: () => void;
}

// Helper component for Sidebar Item
const SidebarPageLink = ({ pageId }: { pageId: string }) => {
  const [pageName, setPageName] = useState('Loading...');
  
  useEffect(() => {
    // Отримуємо назву сторінки по ID [cite: 391]
    pageService.getOne(pageId)
        .then(res => setPageName(res.data.name))
        .catch(() => setPageName('Error loading'));
  }, [pageId]);

  return (
    <NavLink
      to={`page/${pageId}`}
      className={({ isActive }) =>
        `block px-3 py-2 mx-3 rounded-md text-sm font-medium transition mb-1 truncate ${
          isActive 
            ? 'bg-[#1B5448]/10 text-[#1B5448]' 
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
        }`
      }
    >
      {pageName}
    </NavLink>
  );
};

export default function ProjectView() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [isPageModalOpen, setIsPageModalOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

// Функція для оновлення проекту (щоб побачити нову сторінку в списку)
  const refreshProject = () => {
    if (projectId) {
       projectService.getOne(projectId).then(res => setProject(res.data));
    }
  };

  useEffect(() => {
    if (projectId) {
      // Отримуємо проект [cite: 516]
      projectService.getOne(projectId)
        .then(res => setProject(res.data))
        .catch(err => console.error("Error loading project", err));
    }
  }, [projectId]);

  // Автоматичний редірект на першу сторінку, якщо ми в корені проекту
  useEffect(() => {
    if (project && project.page_ids.length > 0 && location.pathname === `/project/${projectId}`) {
        navigate(`page/${project.page_ids[0]}`, { replace: true });
    }
  }, [project, location, navigate, projectId]);

  if (!project) return <div className="flex h-screen items-center justify-center text-[#1B5448] animate-pulse">Loading Project...</div>;

  return (
    <div className="flex h-[calc(100vh-64px)]">
      
      {/* SIDEBAR */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col flex-shrink-0 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)] z-10">
        <div className="p-5 border-b border-gray-100">
           <h1 className="font-bold text-gray-800 truncate font-['Montserrat'] text-lg" title={project.name}>
             {project.name}
           </h1>
           <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Admin ID: {project.admin_id}</span>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 custom-scrollbar">
            <div className="px-5 text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">
                Pages
            </div>
            {project.page_ids.map(id => (
                <SidebarPageLink key={id} pageId={id} />
            ))}
            
            <button onClick={() => setIsPageModalOpen(true)} className="w-full text-left px-5 py-2 text-sm text-gray-500 hover:text-[#1B5448] flex items-center gap-2 mt-1 group">
                <span className="group-hover:bg-[#1B5448]/10 w-5 h-5 flex items-center justify-center rounded transition">+</span> Create Page
            </button>
        </nav>

        {/* Team Section */}
        <div className="p-4 bg-gray-50/50 border-t border-gray-200">
            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-3">Team ({project.collaborators.length})</div>
            <div className="flex flex-col gap-2 max-h-40 overflow-y-auto custom-scrollbar pr-1">
                {project.collaborators.map((collab, idx) => (
                    <CollaboratorBadge key={idx} collab={collab} />
                ))}
                {project.collaborators.length === 0 && (
                    <span className="text-xs text-gray-400 italic pl-1">No team members yet</span>
                )}
            </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 overflow-hidden relative bg-[#F9FAFB]">
        {project.page_ids.length === 0 ? (
            /* ... заглушка ... */
             <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <p>This project has no pages yet.</p>
                <button className="mt-4 text-[#1B5448] font-medium hover:underline">Create first page</button>
            </div>
        ) : (
            // ВАЖЛИВО: Передаємо об'єкт проекту вниз
            <Outlet context={{ project, refreshProject: () => {/* логіка оновлення */} } satisfies ProjectContextType} />
        )}
      </main>

      {project && (
      <CreatePageModal 
        isOpen={isPageModalOpen}
        onClose={() => setIsPageModalOpen(false)}
        onSuccess={refreshProject}
        projectId={project._id}
      />
    )}
    </div>
  );
}