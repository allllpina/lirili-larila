// src/components/modals/CreateBoardModal.tsx
import { useState } from 'react';
import { boardService } from '../../api/services';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  pageId: string;
}

export default function CreateBoardModal({ isOpen, onClose, onSuccess, pageId }: Props) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await boardService.create(pageId, { name, description });
      setName('');
      setDescription('');
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to create board');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-xl font-bold text-[#1B5448] mb-4 font-['Montserrat']">New Board List</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">List Name</label>
            <input required placeholder="e.g. To Do" className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none"
              value={name} onChange={e => setName(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description (Optional)</label>
            <textarea 
              placeholder="What is this list for?" 
              className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none resize-none h-16 text-sm"
              value={description} 
              onChange={e => setDescription(e.target.value)} 
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
            <button type="submit" disabled={isSubmitting} className="px-4 py-2 bg-[#1B5448] text-white rounded-lg hover:opacity-90 font-medium disabled:opacity-50">Create</button>
          </div>
        </form>
      </div>
    </div>
  );
}