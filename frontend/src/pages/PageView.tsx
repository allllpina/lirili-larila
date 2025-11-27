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
  
  // Локальний стан для оновлення колонок після DnD
  const [boardRefreshTriggers, setBoardRefreshTriggers] = useState<Record<string, number>>({});


  // Отримуємо глобальний тригер від сокета
  const { refreshProject, project, globalUpdateTrigger } = useOutletContext<ProjectContextType>();

  const fetchPage = () => {
    if (pageId) {
        pageService.getOne(pageId).then(res => setPage(res.data)).catch(console.error);
    }
  };

  // Оновлюємо сторінку при зміні ID або якщо прийшов сигнал від сокета
  useEffect(() => {
    setPage(null);
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

  // --- DRAG AND DROP HANDLER ---
  const onDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;

    // Якщо кинули повз або туди ж, де і було
    if (!destination || (destination.droppableId === source.droppableId && destination.index === source.index)) {
      return;
    }

    const boardGiverId = source.droppableId;
    const boardReceiverId = destination.droppableId;
    const taskId = draggableId;

    try {
      // 1. Відправляємо запит на переміщення
      await taskService.move({
        taskId,
        boardGiverId,
        boardReceiverId
      });

      // 2. Оновлюємо лічильники оновлення для задіяних колонок
      setBoardRefreshTriggers(prev => ({
        ...prev,
        [boardGiverId]: (prev[boardGiverId] || 0) + 1,
        [boardReceiverId]: (prev[boardReceiverId] || 0) + 1
      }));

    } catch (error) {
      console.error("Move failed", error);
      alert("Failed to move task");
      fetchPage(); // Повний рефреш при помилці
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
                      <button 
                          onClick={() => setIsEditPageModalOpen(true)}
                          className="text-gray-400 hover:text-[#1B5448] hover:bg-gray-100 rounded p-1 transition"
                          title="Edit Page"
                      >
                          ⋮
                      </button>
                  </div>
                  {page.description && <p className="text-xs text-gray-500 mt-0.5">{page.description}</p>}
              </div>
           </div>
           
           <div className="text-xs bg-green-50 text-green-700 px-3 py-1.5 rounded-full border border-green-100 shadow-sm">
              Total Cost: <span className="font-bold ml-1">${page.cost}</span>
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
                  // Комбінуємо тригери: локальний (DnD) + глобальний (WebSocket)
                  refreshTrigger={(boardRefreshTriggers[boardId] || 0) + globalUpdateTrigger} 
              />
            ))}
            
            {/* Кнопка створення колонки */}
            <div className="w-72 flex-shrink-0 mx-2">
              <button 
                  onClick={() => setIsBoardModalOpen(true)}
                  className="w-full h-12 rounded-xl bg-white/50 border-2 border-dashed border-gray-300 text-gray-500 hover:border-[#1B5448] hover:text-[#1B5448] hover:bg-white transition flex items-center justify-center font-medium shadow-sm"
              >
                + Add Another List
              </button>
            </div>
          </div>
        </div>

        {/* MODALS */}
        <CreateBoardModal 
            isOpen={isBoardModalOpen}
            onClose={() => setIsBoardModalOpen(false)}
            onSuccess={fetchPage}
            pageId={page._id}
        />

        <EditPageModal 
            isOpen={isEditPageModalOpen}
            onClose={() => setIsEditPageModalOpen(false)}
            page={page}
            onUpdate={handlePageUpdate}
            onDelete={handlePageDelete}
        />
      </div>
    </DragDropContext>
  );
}