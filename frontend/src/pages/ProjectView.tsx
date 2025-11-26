import { useEffect, useState } from 'react';
import { useParams, Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { projectService, pageService } from '../api/services';
import type { Project } from '../types';
import CollaboratorBadge from '../components/project/CollaboratorBadge';
import CreatePageModal from '../components/modals/CreatePageModal';
import EditProjectModal from '../components/modals/EditProjectModal';

export interface ProjectContextType {
  project: Project;
  refreshProject: () => Promise<void>; 
}

const SidebarPageLink = ({ pageId }: { pageId: string }) => {
  const [pageName, setPageName] = useState('Loading...');
  useEffect(() => {
    pageService.getOne(pageId).then(res => setPageName(res.data.name)).catch(() => setPageName('Error'));
  }, [pageId]);
  return (
    <NavLink to={`page/${pageId}`} className={({ isActive }) => `block px-3 py-2 mx-3 rounded-md text-sm font-medium transition mb-1 truncate ${isActive ? 'bg-[#1B5448]/10 text-[#1B5448]' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'}`}>
      {pageName}
    </NavLink>
  );
};

export default function ProjectView() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  
  const [isPageModalOpen, setIsPageModalOpen] = useState(false);
  const [isEditProjectOpen, setIsEditProjectOpen] = useState(false);

  const refreshProject = async () => {
    if (projectId) {
       return projectService.getOne(projectId).then(res => setProject(res.data));
    }
  };

  useEffect(() => {
    refreshProject();
  }, [projectId]);

  useEffect(() => {
    if (project && project.page_ids.length > 0 && location.pathname === `/project/${projectId}`) {
        navigate(`page/${project.page_ids[0]}`, { replace: true });
    }
  }, [project, location, navigate, projectId]);

  const handleProjectDelete = () => {
      navigate('/');
  };

  if (!project) return <div className="flex h-screen items-center justify-center text-[#1B5448] animate-pulse">Loading Project...</div>;

  return (
    <div className="flex h-[calc(100vh-64px)]">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col flex-shrink-0 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)] z-10">
        <div className="p-5 border-b border-gray-100">
           <div className="flex justify-between items-start">
                <h1 className="font-bold text-gray-800 truncate font-['Montserrat'] text-lg max-w-[180px]" title={project.name}>{project.name}</h1>
                <button onClick={() => setIsEditProjectOpen(true)} className="text-gray-400 hover:text-[#1B5448] transition" title="Project Settings">⋮</button>
           </div>
           <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Admin ID: {project.admin_id}</span>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 custom-scrollbar">
            <div className="px-5 text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Pages</div>
            {project.page_ids.map(id => <SidebarPageLink key={id} pageId={id} />)}
            <button onClick={() => setIsPageModalOpen(true)} className="w-full text-left px-5 py-2 text-sm text-gray-500 hover:text-[#1B5448] flex items-center gap-2 mt-1 group">
                <span className="group-hover:bg-[#1B5448]/10 w-5 h-5 flex items-center justify-center rounded transition">+</span> Create Page
            </button>
        </nav>

        <div className="p-4 bg-gray-50/50 border-t border-gray-200">
            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-3">Team ({project.collaborators.length})</div>
            <div className="flex flex-col gap-2 max-h-40 overflow-y-auto custom-scrollbar pr-1">
                {project.collaborators.map((collab, idx) => <CollaboratorBadge key={idx} collab={collab} />)}
                {project.collaborators.length === 0 && <span className="text-xs text-gray-400 italic pl-1">No team members yet</span>}
            </div>
        </div>
      </aside>

      <main className="flex-1 overflow-hidden relative bg-[#F9FAFB]">
        {project.page_ids.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <div className="bg-gray-100 p-4 rounded-full mb-4">📄</div>
                <p>This project has no pages yet.</p>
                <button onClick={() => setIsPageModalOpen(true)} className="mt-4 text-[#1B5448] font-medium hover:underline">Create first page</button>
            </div>
        ) : (
            <Outlet context={{ project, refreshProject } satisfies ProjectContextType} />
        )}
      </main>

      <CreatePageModal 
        isOpen={isPageModalOpen}
        onClose={() => setIsPageModalOpen(false)}
        onSuccess={refreshProject}
        projectId={project._id}
      />
      
      <EditProjectModal 
        isOpen={isEditProjectOpen}
        onClose={() => setIsEditProjectOpen(false)}
        project={project}
        // 👇 ТУТ ВАЖЛИВА ЗМІНА: Ми просто записуємо отриманий об'єкт у стейт
        onUpdate={(updatedProject) => setProject(updatedProject)} 
        onDelete={handleProjectDelete}
      />
    </div>
  );
}