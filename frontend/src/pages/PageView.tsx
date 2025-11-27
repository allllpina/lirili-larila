import { useEffect, useState } from 'react';
import { useParams, useNavigate, useOutletContext } from 'react-router-dom';
import { DragDropContext } from '@hello-pangea/dnd';
import type { DropResult } from '@hello-pangea/dnd';
import { pageService, taskService } from '../api/services';
import type { Page } from '../types';
import BoardColumn from '../components/project/BoardColumn';
import CreateBoardModal from '../components/modals/CreateBoardModal';
import EditPageModal from '../components/modals/EditPageModal';
import type { ProjectContextType } from './ProjectView';

export default function PageView() {
  const { pageId } = useParams<{ pageId: string }>();
  const navigate = useNavigate();
  const [page, setPage] = useState<Page | null>(null);
  
  const [isBoardModalOpen, setIsBoardModalOpen] = useState(false);
  const [isEditPageModalOpen, setIsEditPageModalOpen] = useState(false);
  
  const [boardRefreshTriggers, setBoardRefreshTriggers] = useState<Record<string, number>>({});

  // 👇 ДОДАНО: Стан для фільтрації
  const [filterTag, setFilterTag] = useState<string | null>(null);

  const { refreshProject, project, globalUpdateTrigger } = useOutletContext<ProjectContextType>();

  const fetchPage = () => {
    if (pageId) {
        pageService.getOne(pageId).then(res => setPage(res.data)).catch(console.error);
    }
  };

  useEffect(() => {
    setPage(null);
    setFilterTag(null);
    fetchPage();
  }, [pageId, globalUpdateTrigger]);

  const handlePageUpdate = () => {
      fetchPage();
      refreshProject(); 
  };

  const handlePageDelete = async () => {
      await refreshProject();
      navigate(`/project/${project._id}`, { replace: true });
  };

  const onDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;
    if (!destination || (destination.droppableId === source.droppableId && destination.index === source.index)) return;

    const boardGiverId = source.droppableId;
    const boardReceiverId = destination.droppableId;
    const taskId = draggableId;

    try {
      await taskService.move({ taskId, boardGiverId, boardReceiverId });
      setBoardRefreshTriggers(prev => ({
        ...prev,
        [boardGiverId]: (prev[boardGiverId] || 0) + 1,
        [boardReceiverId]: (prev[boardReceiverId] || 0) + 1
      }));
    } catch (error) {
      console.error("Move failed", error);
      fetchPage();
    }
  };

  if (!page) return <div className="flex h-full items-center justify-center text-gray-400">Loading Page...</div>;

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="h-full flex flex-col bg-white">
        
        {/* HEADER */}
        <div className="h-16 border-b border-gray-200 flex items-center justify-between px-6 bg-white shrink-0">
           <div className="flex items-center gap-3">
              <div>
                  <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-gray-900 font-['Montserrat'] leading-tight">{page.name}</h2>
                      <button onClick={() => setIsEditPageModalOpen(true)} className="text-gray-400 hover:text-[#1B5448] hover:bg-gray-100 rounded p-1 transition">⋮</button>
                  </div>
                  {page.description && <p className="text-xs text-gray-500 mt-0.5">{page.description}</p>}
              </div>
           </div>
           
           <div className="flex items-center gap-4">
               {/* UI ФІЛЬТРУ */}
               {filterTag && (
                   <div className="flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full border border-blue-100 text-sm animate-fade-in">
                       <span className="font-bold">Filter:</span> #{filterTag}
                       <button onClick={() => setFilterTag(null)} className="ml-1 hover:text-red-500 font-bold px-1">✕</button>
                   </div>
               )}
               <div className="text-xs bg-green-50 text-green-700 px-3 py-1.5 rounded-full border border-green-100 shadow-sm">
                  Total Cost: <span className="font-bold ml-1">${page.cost}</span>
               </div>
           </div>
        </div>

        {/* KANBAN AREA */}
        <div className="flex-1 overflow-x-auto overflow-y-hidden p-4 bg-[#F9FAFB]">
          <div className="flex h-full items-start">
            {page.board_ids.map((boardId) => (
              <BoardColumn 
                  key={boardId} 
                  boardId={boardId} 
                  onBoardDeleted={fetchPage}
                  refreshTrigger={(boardRefreshTriggers[boardId] || 0) + globalUpdateTrigger}
                  // 👇 ПЕРЕДАЄМО ФІЛЬТРИ ВНИЗ
                  filterTag={filterTag}
                  onTagClick={(tag) => setFilterTag(tag)}
              />
            ))}
            
            <div className="w-72 flex-shrink-0 mx-2">
              <button onClick={() => setIsBoardModalOpen(true)} className="w-full h-12 rounded-xl bg-white/50 border-2 border-dashed border-gray-300 text-gray-500 hover:border-[#1B5448] hover:text-[#1B5448] hover:bg-white transition flex items-center justify-center font-medium shadow-sm">+ Add Another List</button>
            </div>
          </div>
        </div>

        <CreateBoardModal isOpen={isBoardModalOpen} onClose={() => setIsBoardModalOpen(false)} onSuccess={fetchPage} pageId={page._id} />
        <EditPageModal isOpen={isEditPageModalOpen} onClose={() => setIsEditPageModalOpen(false)} page={page} onUpdate={handlePageUpdate} onDelete={handlePageDelete} />
      </div>
    </DragDropContext>
  );
}