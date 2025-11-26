// src/components/project/BoardColumn.tsx
import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Droppable } from '@hello-pangea/dnd';
import { boardService } from '../../api/services';
import type { Board } from '../../types';
import TaskCard from './TaskCard';
// import CreateTaskModal from '../components/modals/CreateTaskModal';
import CreateTaskModal from '../modals/CreateTaskModal';
// import EditBoardModal from '../components/modals/EditBoardModal';
import EditBoardModal from '../modals/EditBoardModal';
// import TaskDetailModal from '../components/modals/TaskDetailModal';
import TaskDetailModal from '../modals/TaskDetailModal';
import type { ProjectContextType } from '../../pages/ProjectView';

interface Props {
    boardId: string;
    onBoardDeleted: () => void; 
    refreshTrigger?: number; // Тригер для примусового оновлення ззовні (після DnD)
}

export default function BoardColumn({ boardId, onBoardDeleted, refreshTrigger = 0 }: Props) {
  const [board, setBoard] = useState<Board | null>(null);
  
  // Стани модалок
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  
  // Внутрішній тригер для оновлення карток
  const [tasksUpdateTrigger, setTasksUpdateTrigger] = useState(0);

  const { project } = useOutletContext<ProjectContextType>();

  const refreshBoard = () => {
    boardService.getOne(boardId).then(res => setBoard(res.data));
    setTasksUpdateTrigger(prev => prev + 1);
  };

  // Оновлюємось при старті, або якщо змінився ID, або якщо батько попросив (refreshTrigger)
  useEffect(() => {
    refreshBoard();
  }, [boardId, refreshTrigger]);

  if (!board) return <div className="w-72 h-[500px] bg-gray-100 rounded-xl animate-pulse mx-2 shrink-0" />;

  return (
    <div className="w-72 flex-shrink-0 flex flex-col max-h-full mx-2">
      <div className="bg-[#F4F5F7] rounded-xl flex flex-col max-h-full border border-gray-200/60 shadow-sm overflow-hidden">
        
        {/* HEADER */}
        <div className="p-3 shrink-0">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-2 overflow-hidden">
                <h3 className="font-bold text-gray-700 text-sm font-['Montserrat'] truncate">{board.name}</h3>
                <span className="bg-gray-200 text-gray-600 text-[10px] px-2 py-0.5 rounded-full font-bold shrink-0">
                    {board.task_ids.length}
                </span>
            </div>
            {/* Кнопка налаштувань */}
            <button 
                onClick={() => setIsEditModalOpen(true)}
                className="text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded px-1 -mr-1 transition"
            >
                ⋮
            </button>
          </div>
          {board.description && (
            <p className="text-[10px] text-gray-400 mt-1 line-clamp-2" title={board.description}>
                {board.description}
            </p>
          )}
        </div>

        {/* DROPPABLE TASK LIST */}
        <Droppable droppableId={boardId}>
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className={`flex-1 overflow-y-auto min-h-0 px-2 pb-2 space-y-2 custom-scrollbar transition-colors
                ${snapshot.isDraggingOver ? 'bg-blue-50/50' : ''}`}
            >
              {board.task_ids.map((taskId, index) => (
                <TaskCard 
                   key={taskId} 
                   taskId={taskId}
                   index={index} // Важливо для DnD
                   onClick={() => setSelectedTaskId(taskId)}
                   refreshTrigger={tasksUpdateTrigger}
                />
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>

        {/* FOOTER */}
        <div className="p-2 shrink-0">
            <button 
                onClick={() => setIsTaskModalOpen(true)}
                className="w-full py-2 text-sm text-gray-500 hover:bg-gray-200 hover:text-gray-700 rounded-lg transition text-left px-3 flex items-center gap-2"
            >
            <span className="text-lg leading-none">+</span> Add Task
            </button>
        </div>
      </div>

      {/* MODALS */}
      <CreateTaskModal 
         isOpen={isTaskModalOpen}
         onClose={() => setIsTaskModalOpen(false)}
         onSuccess={refreshBoard}
         boardId={boardId}
         projectCollaborators={project.collaborators}
      />

      <TaskDetailModal 
        isOpen={!!selectedTaskId}
        taskId={selectedTaskId}
        onClose={() => setSelectedTaskId(null)}
        onUpdate={refreshBoard}
        projectCollaborators={project.collaborators}
      />

      <EditBoardModal 
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        board={board}
        onUpdate={refreshBoard}
        onDelete={onBoardDeleted}
      />
    </div>
  );
}