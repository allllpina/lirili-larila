import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { pageService } from '../api/services';
import type { Page } from '../types';
import BoardColumn from '../components/project/BoardColumn';
import CreateBoardModal from '../components/modals/CreateBoardModal';

export default function PageView() {
  const { pageId } = useParams<{ pageId: string }>();
  const [page, setPage] = useState<Page | null>(null);
  const [isBoardModalOpen, setIsBoardModalOpen] = useState(false);

  const refreshPage = () => {
     if (pageId) pageService.getOne(pageId).then(res => setPage(res.data));
  };

  useEffect(() => {
    if (pageId) {
        setPage(null); // Reset перед завантаженням нової
        // Отримуємо сторінку по ID [cite: 391]
        pageService.getOne(pageId)
            .then(res => setPage(res.data))
            .catch(err => console.error(err));
    }
  }, [pageId]);

  if (!page) return <div className="flex h-full items-center justify-center text-gray-400">Loading Page...</div>;

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Page Header Info */}
      <div className="h-14 border-b border-gray-200 flex items-center justify-between px-6 bg-white shrink-0">
         <div className="flex flex-col">
            <h2 className="text-lg font-bold text-gray-800 font-['Montserrat'] leading-tight">{page.name}</h2>
            {page.description && <p className="text-xs text-gray-400">{page.description}</p>}
         </div>
         <div className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded border border-green-100">
            Total Cost: <span className="font-bold">${page.cost}</span>
         </div>
      </div>

      {/* Kanban Container (Horizontal Scroll) */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden p-4 bg-[#F9FAFB]">
        <div className="flex h-full items-start">
          {page.board_ids.map((boardId) => (
            <BoardColumn key={boardId} boardId={boardId} />
          ))}
          
          {/* Create Board Button Placeholder */}
          <div className="w-72 flex-shrink-0 mx-2">
            <button onClick={() => setIsBoardModalOpen(true)} className="w-full h-12 rounded-xl bg-white/50 border-2 border-dashed border-gray-300 text-gray-500 hover:border-[#1B5448] hover:text-[#1B5448] hover:bg-white transition flex items-center justify-center font-medium shadow-sm">
              + Add Another List
            </button>
          </div>
        </div>
      </div>

      {page && (
      <CreateBoardModal 
        isOpen={isBoardModalOpen}
        onClose={() => setIsBoardModalOpen(false)}
        onSuccess={refreshPage}
        pageId={page._id}
      />
    )}
    </div>
  );
}