import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { projectService, authService } from '../api/services';
import type { ProjectCostEvaluation } from '../types';

// Компонент для відображення імені юзера замість ID
const UserNameDisplay = ({ userId }: { userId: number }) => {
    const [username, setUsername] = useState(`User ${userId}`);
    useEffect(() => {
        authService.getUserById(userId).then(res => setUsername(res.data.username)).catch(() => {});
    }, [userId]);
    return <span className="font-medium text-gray-700">{username}</span>;
};

export default function ProjectFinance() {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<ProjectCostEvaluation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      projectService.getCostEvaluation(projectId)
        .then(res => setData(res.data))
        .catch(err => console.error("Failed to load finance", err))
        .finally(() => setIsLoading(false));
    }
  }, [projectId]);

  if (isLoading) return <div className="flex h-full items-center justify-center text-[#1B5448]">Calculating Finances...</div>;
  if (!data) return <div className="p-8 text-center text-gray-500">No financial data available.</div>;

  // Готуємо дані для діаграми (Витрати по сторінках)
  const chartData = data.per_page.map(page => ({
    name: page.name,
    value: page.overall
  })).filter(item => item.value > 0); // Прибираємо пусті, щоб не псувати графік

  // Кольори для діаграми (відтінки зеленого та додаткові)
  const COLORS = ['#1B5448', '#2C7A6A', '#4db6ac', '#80cbc4', '#FFBB28', '#FF8042'];

  return (
    <div className="h-full overflow-y-auto custom-scrollbar bg-[#F9FAFB] p-8">
      <h1 className="text-2xl font-bold text-gray-800 font-['Montserrat'] mb-6">Financial Overview</h1>

      {/* TOP SECTION: SUMMARY & CHART */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Summary Card */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-center items-center">
            <h3 className="text-gray-500 uppercase tracking-wider text-sm font-bold mb-2">Total Project Cost</h3>
            <span className="text-5xl font-bold text-[#1B5448]">${data.overall}</span>
            <p className="text-gray-400 text-sm mt-2">Based on tasks completion</p>
        </div>

        {/* Chart Card */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col">
            <h3 className="text-gray-800 font-bold mb-4">Cost Distribution (Per Page)</h3>
            <div className="h-64 w-full">
                {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60} // Робить "кільце" (Donut)
                                outerRadius={80}
                                fill="#8884d8"
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {chartData.map((_, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value) => `$${value}`} />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full flex items-center justify-center text-gray-400 text-sm italic">
                        Not enough data to display chart.
                    </div>
                )}
            </div>
        </div>
      </div>

      {/* BOTTOM SECTION: DETAILED BREAKDOWN */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b bg-gray-50">
              <h3 className="font-bold text-gray-700">Detailed Breakdown</h3>
          </div>
          
          <div className="p-4 space-y-6">
              {data.per_page.map(page => (
                  <div key={page.page_id} className="border border-gray-100 rounded-lg overflow-hidden">
                      {/* Page Header */}
                      <div className="bg-gray-50 p-3 flex justify-between items-center border-b border-gray-100">
                          <div className="flex items-center gap-2">
                              <span className="text-xl">📄</span>
                              <span className="font-bold text-gray-800">{page.name}</span>
                          </div>
                          <span className="font-bold text-[#1B5448]">${page.overall}</span>
                      </div>

                      {/* Boards */}
                      <div className="p-3 space-y-4">
                          {page.per_board.map(board => (
                              <div key={board.board_id} className="pl-4 border-l-2 border-gray-200">
                                  <div className="flex justify-between items-center mb-2">
                                      <h4 className="font-semibold text-gray-700 text-sm">{board.name} (List)</h4>
                                      <span className="text-sm text-gray-500">${board.overall}</span>
                                  </div>

                                  {/* Tasks */}
                                  <div className="space-y-2">
                                      {board.per_task.map(task => (
                                          <div key={task.task_id} className="bg-gray-50 p-2 rounded text-sm">
                                              <div className="flex justify-between items-center mb-1">
                                                  <span className="font-medium text-gray-800">{task.name}</span>
                                                  <span className="font-bold text-green-700 text-xs">${task.total_cost}</span>
                                              </div>
                                              
                                              {/* User Breakdown */}
                                              {task.cost_breakdown.length > 0 && (
                                                  <div className="mt-1 pl-2 text-xs text-gray-500 space-y-0.5">
                                                      {task.cost_breakdown.map((userCost, idx) => (
                                                          <div key={idx} className="flex justify-between border-b border-gray-200 last:border-0 pb-0.5">
                                                              <span>
                                                                  <UserNameDisplay userId={userCost.usr_id} /> 
                                                                  <span className="ml-1">({userCost.hours_worked}h × ${userCost.hourly_rate})</span>
                                                              </span>
                                                              <span>${userCost.total_pay}</span>
                                                          </div>
                                                      ))}
                                                  </div>
                                              )}
                                          </div>
                                      ))}
                                      {board.per_task.length === 0 && <div className="text-xs text-gray-400 italic">No tasks with cost data</div>}
                                  </div>
                              </div>
                          ))}
                          {page.per_board.length === 0 && <div className="text-sm text-gray-400 italic">No boards</div>}
                      </div>
                  </div>
              ))}
              {data.per_page.length === 0 && <div className="text-center text-gray-500">No pages found.</div>}
          </div>
      </div>
    </div>
  );
}