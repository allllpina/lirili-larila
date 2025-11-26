import { useState, useEffect } from 'react';
import { boardService } from '../../api/services';
import type { Board } from '../../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  board: Board;
  onUpdate: () => void; // Оновити дані дошки (якщо змінили назву)
  onDelete: () => void; // Оновити сторінку (якщо видалили дошку)
}

export default function EditBoardModal({ isOpen, onClose, board, onUpdate, onDelete }: Props) {
  const [name, setName] = useState(board.name);
  const [description, setDescription] = useState(board.description || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Скидаємо форму при відкритті
  useEffect(() => {
    if (isOpen) {
        setName(board.name);
        setDescription(board.description || '');
        setIsDeleting(false);
    }
  }, [isOpen, board]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await boardService.update(board._id, { name, description });
      onUpdate();
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to update board');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
        await boardService.delete(board._id);
        onDelete(); // Викликаємо оновлення батьківської сторінки
        onClose();
    } catch (e) {
        alert('Failed to delete board');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-[#1B5448] font-['Montserrat']">Edit List</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">List Name</label>
            <input 
              required 
              className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none"
              value={name} 
              onChange={e => setName(e.target.value)} 
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea 
              className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none resize-none h-20 text-sm"
              value={description} 
              onChange={e => setDescription(e.target.value)} 
            />
          </div>

          <div className="border-t pt-4 flex justify-between items-center">
            {/* DELETE BUTTON WITH CONFIRMATION */}
            {isDeleting ? (
                <div className="flex items-center gap-2 bg-red-50 px-2 py-1 rounded border border-red-100">
                    <span className="text-xs text-red-600 font-bold">Sure?</span>
                    <button type="button" onClick={handleDelete} className="text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700 font-bold">Yes</button>
                    <button type="button" onClick={() => setIsDeleting(false)} className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded hover:bg-gray-300">No</button>
                </div>
            ) : (
                <button 
                    type="button" 
                    onClick={() => setIsDeleting(true)}
                    className="text-sm text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50 transition"
                >
                    Delete List
                </button>
            )}

            <div className="flex gap-2">
                <button type="button" onClick={onClose} className="px-3 py-1.5 text-gray-600 hover:bg-gray-100 rounded-lg text-sm">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="px-3 py-1.5 bg-[#1B5448] text-white rounded-lg hover:opacity-90 font-medium text-sm disabled:opacity-50">
                    Save
                </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}