import { useEffect, useState, useRef } from 'react'; // <-- Додали useRef
import { useParams } from 'react-router-dom';
import { projectService, taskService } from '../api/services';
import type { AiEvaluationResponse, Task } from '../types';
import GeminiIcon from '../components/icons/GeminiIcon';

interface EnrichedAiTask {
  taskId: string;
  suggestedPriority: string;
  taskDetails: Task | null;
}

export default function ProjectAI() {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<AiEvaluationResponse | null>(null);
  const [enrichedTasks, setEnrichedTasks] = useState<EnrichedAiTask[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 👇 Використовуємо ref, щоб відстежувати, для якого ID ми вже зробили запит
  const loadedProjectId = useRef<string | null>(null);

  useEffect(() => {
    // Перевіряємо: якщо є ID і ми його ще НЕ завантажували
    if (projectId && loadedProjectId.current !== projectId) {
      loadedProjectId.current = projectId; // Фіксуємо, що почали завантаження
      loadData();
    }
  }, [projectId]);

  const loadData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const { data: aiData } = await projectService.getAiEvaluation(projectId);
      setData(aiData);

      const tasksPromises = aiData.prioritized_tasks.map(async (item) => {
        try {
          const { data: task } = await taskService.getOne(item.task_id);
          return {
            taskId: item.task_id,
            suggestedPriority: item.priority,
            taskDetails: task
          };
        } catch (e) {
          return {
            taskId: item.task_id,
            suggestedPriority: item.priority,
            taskDetails: null
          };
        }
      });

      const fullTasks = await Promise.all(tasksPromises);
      setEnrichedTasks(fullTasks);

    } catch (err) {
      console.error("AI Load Failed", err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return (
    <div className="flex flex-col h-full items-center justify-center text-[#1B5448] gap-4">
       <GeminiIcon className="w-12 h-12 animate-pulse" />
       <span className="font-['Montserrat'] font-medium">Generating Insights...</span>
    </div>
  );

  if (!data) return <div className="p-8 text-center text-gray-500">AI Analysis unavailable.</div>;

  return (
    <div className="h-full overflow-y-auto custom-scrollbar bg-[#F9FAFB] p-8">
      
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <GeminiIcon className="w-10 h-10" />
        <div>
            <h1 className="text-2xl font-bold text-gray-800 font-['Montserrat']">AI Evaluation</h1>
            <p className="text-sm text-gray-500">Smart insights based on project data</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT COLUMN: RECOMMENDATIONS */}
        <div className="lg:col-span-2 space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <span>✨</span> Strategic Recommendations
                </h3>
                
                <div className="space-y-4">
                    {data.recommendations.length > 0 ? (
                        data.recommendations.map((rec, idx) => (
                            <div key={idx} className="flex gap-4 p-4 bg-gradient-to-r from-blue-50 to-white rounded-lg border border-blue-100">
                                <div className="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm shrink-0">
                                    {idx + 1}
                                </div>
                                <p className="text-gray-700 text-sm leading-relaxed pt-1">
                                    {rec}
                                </p>
                            </div>
                        ))
                    ) : (
                        <p className="text-gray-400 italic">No recommendations at this time.</p>
                    )}
                </div>
            </div>
        </div>

        {/* RIGHT COLUMN: PRIORITY TASKS */}
        <div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <span>🔥</span> Priority Focus
                </h3>
                <p className="text-xs text-gray-400 mb-4">Tasks that require immediate attention according to AI analysis.</p>

                <div className="space-y-3">
                    {enrichedTasks.length > 0 ? (
                        enrichedTasks.map((item, idx) => (
                            <div key={idx} className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-[#1B5448] transition group">
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-xs font-mono text-gray-400">ID: {item.taskId.slice(-4)}</span>
                                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase
                                        ${item.suggestedPriority === 'high' ? 'bg-red-100 text-red-600' : 
                                          item.suggestedPriority === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}`}>
                                        {item.suggestedPriority}
                                    </span>
                                </div>
                                
                                {item.taskDetails ? (
                                    <>
                                        <h4 className="text-sm font-bold text-gray-800 mb-1 group-hover:text-[#1B5448] transition">
                                            {item.taskDetails.name}
                                        </h4>
                                        <div className="flex justify-between items-center mt-2">
                                            <span className="text-[10px] bg-white border px-1.5 rounded text-gray-500">
                                                {item.taskDetails.status}
                                            </span>
                                            {item.taskDetails.cost > 0 && (
                                                <span className="text-[10px] font-bold text-green-700">
                                                    ${item.taskDetails.cost}
                                                </span>
                                            )}
                                        </div>
                                    </>
                                ) : (
                                    <p className="text-sm text-gray-400 italic">Task details not found</p>
                                )}
                            </div>
                        ))
                    ) : (
                        <div className="text-center py-8 text-gray-400 text-sm">
                            No critical tasks identified.
                        </div>
                    )}
                </div>
            </div>
        </div>

      </div>
    </div>
  );
}