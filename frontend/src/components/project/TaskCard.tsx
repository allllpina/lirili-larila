// src/components/project/TaskCard.tsx
import { useEffect, useState } from 'react';
import { Draggable } from '@hello-pangea/dnd';
import { taskService } from '../../api/services';
import type { Task } from '../../types';

interface Props {
  taskId: string;
  index: number; // <-- Важливо для DnD
  onClick: () => void;
  refreshTrigger?: number;
}

export default function TaskCard({ taskId, index, onClick, refreshTrigger = 0 }: Props) {
  const [task, setTask] = useState<Task | null>(null);

  useEffect(() => {
    loadTask();
  }, [taskId, refreshTrigger]);

  const loadTask = () => {
    taskService.getOne(taskId).then(res => setTask(res.data)).catch(console.error);
  };

  // Інтерактивне оновлення полів (Checkbox, Dropdown) прямо на картці
  const handleFieldUpdate = async (e: React.MouseEvent | React.ChangeEvent, fieldIndex: number, newValue: any) => {
    e.stopPropagation(); // Щоб не відкривалась модалка
    if (!task) return;

    const updatedFields = JSON.parse(JSON.stringify(task.custom_fields));
    const field = updatedFields[fieldIndex];

    if (field.type === 'checkbox') {
        field.checked = newValue;
    } else if (field.type === 'dropdown') {
        field.index_of_selected = Number(newValue);
    }

    // Оптимістичне оновлення
    setTask({ ...task, custom_fields: updatedFields });

    try {
        await taskService.update(task._id, { custom_fields: updatedFields });
    } catch (error) {
        console.error("Update failed", error);
        loadTask();
    }
  };

  const priorityColors = {
    high: 'bg-red-50 text-red-700 border-red-100',
    medium: 'bg-yellow-50 text-yellow-700 border-yellow-100',
    low: 'bg-green-50 text-green-700 border-green-100',
    None: 'bg-gray-50 text-gray-600 border-gray-100'
  };

  if (!task) {
      // Плейсхолдер поки вантажиться, але вже Draggable, щоб не "стрибало"
      return (
        <Draggable draggableId={taskId} index={index}>
            {(provided) => (
                <div 
                    ref={provided.innerRef} 
                    {...provided.draggableProps} 
                    {...provided.dragHandleProps}
                    className="h-20 bg-gray-100 rounded-lg animate-pulse mb-2"
                />
            )}
        </Draggable>
      );
  }

  return (
    <Draggable draggableId={taskId} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          
          // Стилі для ефекту перетягування
          style={{ 
             ...provided.draggableProps.style,
             opacity: snapshot.isDragging ? 0.9 : 1,
             transform: snapshot.isDragging ? provided.draggableProps.style?.transform : 'none'
          }}
          
          onClick={onClick}
          className={`bg-white p-3 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer mb-2 group relative
             ${snapshot.isDragging ? 'shadow-xl ring-2 ring-[#1B5448] rotate-1 z-50' : ''}
          `}
        >
          {/* ЗАГОЛОВОК */}
          <div className="flex justify-between items-start gap-2 mb-2">
            <h4 className="text-sm font-medium text-gray-800 leading-tight break-words">{task.name}</h4>
          </div>

          {/* ОПИС (preview) */}
          {task.description && (
              <p className="text-[10px] text-gray-400 mb-2 line-clamp-2">{task.description}</p>
          )}
          
          {/* ТЕГИ */}
          {task.tags && task.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-2">
                  {task.tags.map((tag, idx) => (
                      <span key={idx} className="bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded text-[9px] border border-blue-100">#{tag}</span>
                  ))}
              </div>
          )}
          
          {/* КАСТОМНІ ПОЛЯ */}
          {task.custom_fields && task.custom_fields.length > 0 && (
              <div className="space-y-1.5 border-t border-gray-50 pt-2 mb-2">
                  {task.custom_fields.map((field, idx) => {
                      
                      // 1. DEADLINE
                      if (field.type === 'deadline_date') {
                          const date = new Date(field.date).toLocaleDateString();
                          return (
                            <div key={idx} className={`text-[10px] flex items-center gap-1 ${field.is_expired ? 'text-red-500 font-bold' : 'text-gray-500'}`}>
                                🕒 {date}
                            </div>
                          );
                      }
                      
                      // 2. CHECKBOX
                      if (field.type === 'checkbox') {
                          return (
                            <div key={idx} className="text-[10px] flex items-center gap-1.5 text-gray-600 z-10" onClick={(e) => e.stopPropagation()}>
                                <input 
                                    type="checkbox" 
                                    checked={field.checked} 
                                    onChange={(e) => handleFieldUpdate(e, idx, e.target.checked)}
                                    className="h-3 w-3 cursor-pointer accent-[#1B5448]" 
                                /> 
                                <span className={`truncate ${field.checked ? 'line-through text-gray-400' : ''}`}>{field.text}</span>
                            </div>
                          );
                      }

                      // 3. DROPDOWN
                      if (field.type === 'dropdown') {
                          return (
                            <div key={idx} className="z-10" onClick={(e) => e.stopPropagation()}>
                                <select
                                    className="w-full text-[10px] border border-gray-200 rounded px-1 py-0.5 bg-gray-50 text-gray-700 focus:ring-1 focus:ring-[#1B5448] outline-none cursor-pointer hover:bg-gray-100"
                                    value={field.index_of_selected}
                                    onChange={(e) => handleFieldUpdate(e, idx, e.target.value)}
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    {field.elements.map((option, optIdx) => (
                                        <option key={optIdx} value={optIdx}>{option}</option>
                                    ))}
                                </select>
                            </div>
                          );
                      }

                      // 4. TEXT
                      if (field.type === 'text' && field.text) {
                          return (
                              <div key={idx} className="text-[10px] text-gray-500 flex items-start gap-1">
                                  <span>📝</span>
                                  <span className="truncate">{field.text}</span>
                              </div>
                          );
                      }

                      return null;
                  })}
              </div>
          )}

          {/* УЧАСНИКИ (Collaborators) */}
          {task.collaborators.length > 0 && (
              <div className="flex -space-x-1 mb-2">
                  {task.collaborators.map((c, i) => (
                      <div key={i} className="h-4 w-4 rounded-full bg-gray-300 border border-white flex items-center justify-center text-[8px] font-mono text-gray-600" title={`ID: ${c.usr_id}`}>
                          {c.usr_id}
                      </div>
                  ))}
              </div>
          )}

          {/* ФУТЕР (Пріоритет і Ціна) */}
          <div className="flex items-center justify-between pt-2 border-t border-gray-50">
            <span className={`text-[10px] px-2 py-0.5 rounded border font-medium ${priorityColors[task.priority as keyof typeof priorityColors] || priorityColors.None}`}>
              {task.priority}
            </span>
            {task.cost > 0 && (
               <span className="text-[10px] font-bold text-green-600 bg-green-50 px-1 rounded">${task.cost}</span>
            )}
          </div>
        </div>
      )}
    </Draggable>
  );
}