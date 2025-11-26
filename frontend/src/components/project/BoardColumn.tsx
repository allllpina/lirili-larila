// src/components/project/BoardColumn.tsx
import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { boardService } from '../../api/services';
import type { Board } from '../../types';
import TaskCard from './TaskCard';
import CreateTaskModal from '../modals/CreateTaskModal';
import type { ProjectContextType } from '../../pages/ProjectView';

export default function BoardColumn({ boardId }: { boardId: string }) {
  const [board, setBoard] = useState<Board | null>(null);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  
  const { project } = useOutletContext<ProjectContextType>();

  // Функція оновлення дошки після створення задачі
  const refreshBoard = () => {
    boardService.getOne(boardId).then(res => setBoard(res.data));
  };

  useEffect(() => {
    refreshBoard();
  }, [boardId]);

  if (!board) return <div className="w-72 h-[500px] bg-gray-100 rounded-xl animate-pulse mx-2 shrink-0" />;

  return (
    // 1. Зовнішній контейнер: обмежуємо максимальну висоту (max-h-full)
    <div className="w-72 flex-shrink-0 flex flex-col max-h-full mx-2">
      
      {/* 2. Внутрішній контейнер (Сіра картка): 
          Додаємо 'overflow-hidden', щоб контент не вилазив за заокруглення,
          і 'flex flex-col', щоб правильно розподілити простір.
      */}
      <div className="bg-[#F4F5F7] rounded-xl flex flex-col max-h-full border border-gray-200/60 shadow-sm overflow-hidden">
        
        {/* Header (Фіксований) */}
        <div className="p-3 shrink-0">
          <div className="flex justify-between items-center">
            <h3 className="font-bold text-gray-700 text-sm font-['Montserrat'] truncate">{board.name}</h3>
            <span className="bg-gray-200 text-gray-600 text-[10px] px-2 py-0.5 rounded-full font-bold">
                {board.task_ids.length}
            </span>
          </div>
          {board.description && (
            <p className="text-[10px] text-gray-400 mt-1 line-clamp-2" title={board.description}>
                {board.description}
            </p>
          )}
        </div>

        {/* 3. Список задач (Скрол):
            'flex-1' - займає весь доступний простір, що залишився.
            'overflow-y-auto' - вмикає вертикальний скрол, якщо задач багато.
            'min-h-0' - критичний фікс для Flexbox, щоб скрол працював у вкладених контейнерах.
        */}
        <div className="flex-1 overflow-y-auto min-h-0 px-2 pb-2 space-y-2 custom-scrollbar">
          {board.task_ids.map((taskId) => (
            <TaskCard key={taskId} taskId={taskId} />
          ))}
        </div>

        {/* Footer: Кнопка додавання (Фіксована знизу) */}
        <div className="p-2 shrink-0">
            <button 
            onClick={() => setIsTaskModalOpen(true)}
            className="w-full py-2 text-sm text-gray-500 hover:bg-gray-200 hover:text-gray-700 rounded-lg transition text-left px-3 flex items-center gap-2"
            >
            <span className="text-lg leading-none">+</span> Add Task
            </button>
        </div>
      </div>

      <CreateTaskModal 
         isOpen={isTaskModalOpen}
         onClose={() => setIsTaskModalOpen(false)}
         onSuccess={refreshBoard}
         boardId={boardId}
         projectCollaborators={project.collaborators}
      />
    </div>
  );
}