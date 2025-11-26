// src/components/modals/CreatePageModal.tsx
import { useState } from 'react';
import { pageService } from '../../api/services';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  projectId: string; // Нам треба знати, куди додавати сторінку
}

export default function CreatePageModal({ isOpen, onClose, onSuccess, projectId }: Props) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      await pageService.create(projectId, { name, description });
      setName('');
      setDescription('');
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      setError('Failed to create page');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-xl font-bold text-[#1B5448] mb-4 font-['Montserrat']">New Page</h2>
        
        {error && <div className="mb-4 p-2 bg-red-50 text-red-600 text-sm rounded">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input required className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none"
              value={name} onChange={e => setName(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none resize-none h-24"
              value={description} onChange={e => setDescription(e.target.value)} />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
            <button type="submit" disabled={isSubmitting} className="px-4 py-2 bg-[#1B5448] text-white rounded-lg hover:opacity-90 font-medium disabled:opacity-50">
              {isSubmitting ? 'Creating...' : 'Create Page'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}