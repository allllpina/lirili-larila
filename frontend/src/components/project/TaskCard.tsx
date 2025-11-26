import { useEffect, useState } from 'react';
import { taskService } from '../../api/services';
import type { Task } from '../../types';

export default function TaskCard({ taskId }: { taskId: string }) {
  const [task, setTask] = useState<Task | null>(null);

  useEffect(() => {
    taskService.getOne(taskId)
      .then(res => setTask(res.data))
      .catch(err => console.error(err));
  }, [taskId]);

  if (!task) return <div className="h-20 bg-gray-100 rounded-lg animate-pulse mb-2" />;

  const priorityColors = {
    high: 'bg-red-50 text-red-700 border-red-100',
    medium: 'bg-yellow-50 text-yellow-700 border-yellow-100',
    low: 'bg-green-50 text-green-700 border-green-100',
    None: 'bg-gray-50 text-gray-600 border-gray-100'
  };

  return (
    <div className="bg-white p-3 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer mb-2 group relative">
      <div className="flex justify-between items-start gap-2">
        <h4 className="text-sm font-medium text-gray-800 leading-tight break-words">{task.name}</h4>
      </div>

      {/* Description Preview */}
      {task.description && (
          <p className="text-[10px] text-gray-400 mt-1 line-clamp-2">{task.description}</p>
      )}
      
      {/* Custom Fields Display */}
      {task.custom_fields && task.custom_fields.length > 0 && (
          <div className="mt-2 space-y-1">
              {task.custom_fields.map((field, idx) => {
                  if (field.type === 'deadline_date') {
                      const date = new Date(field.date).toLocaleDateString();
                      return <div key={idx} className={`text-[10px] flex items-center gap-1 ${field.is_expired ? 'text-red-500 font-bold' : 'text-gray-500'}`}>🕒 {date}</div>
                  }
                  if (field.type === 'checkbox') {
                      return <div key={idx} className="text-[10px] flex items-center gap-1 text-gray-600">
                          <input type="checkbox" checked={field.checked} readOnly className="h-3 w-3" /> {field.text}
                      </div>
                  }
                  return null;
              })}
          </div>
      )}

      {/* Collaborators Count */}
      {task.collaborators.length > 0 && (
          <div className="flex -space-x-1 mt-2">
              {task.collaborators.map((c, i) => (
                  <div key={i} className="h-4 w-4 rounded-full bg-gray-300 border border-white flex items-center justify-center text-[8px]" title={`ID: ${c.usr_id}`}>
                      {c.usr_id}
                  </div>
              ))}
          </div>
      )}

      {/* Footer: Priority & Cost */}
      <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-50">
        <span className={`text-[10px] px-2 py-0.5 rounded border font-medium ${priorityColors[task.priority] || priorityColors.None}`}>
          {task.priority}
        </span>
        {task.cost > 0 && (
           <span className="text-[10px] font-bold text-green-600 bg-green-50 px-1 rounded">${task.cost}</span>
        )}
      </div>
    </div>
  );
}