import { useState, useEffect } from 'react';
import { pageService } from '../../api/services';
import type { Page } from '../../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  page: Page;
  onUpdate: () => void; // Оновити заголовок на сторінці
  onDelete: () => void; // Навігація після видалення
}

export default function EditPageModal({ isOpen, onClose, page, onUpdate, onDelete }: Props) {
  const [name, setName] = useState(page.name);
  const [description, setDescription] = useState(page.description || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (isOpen) {
        setName(page.name);
        setDescription(page.description || '');
        setIsDeleting(false);
    }
  }, [isOpen, page]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await pageService.update(page._id, { name, description });
      onUpdate();
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to update page');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
        await pageService.delete(page._id);
        onDelete();
        onClose();
    } catch (e) {
        alert('Failed to delete page');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-[#1B5448] font-['Montserrat']">Edit Page</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Page Name</label>
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
              className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none resize-none h-24 text-sm"
              value={description} 
              onChange={e => setDescription(e.target.value)} 
            />
          </div>

          <div className="border-t pt-4 flex justify-between items-center">
            {/* DELETE SECTION */}
            {isDeleting ? (
                <div className="flex items-center gap-2 bg-red-50 px-2 py-1 rounded border border-red-100 animate-fade-in">
                    <span className="text-xs text-red-600 font-bold">Delete page?</span>
                    <button type="button" onClick={handleDelete} className="text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700 font-bold">Yes</button>
                    <button type="button" onClick={() => setIsDeleting(false)} className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded hover:bg-gray-300">No</button>
                </div>
            ) : (
                <button 
                    type="button" 
                    onClick={() => setIsDeleting(true)}
                    className="text-sm text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50 transition border border-transparent hover:border-red-100"
                >
                    Delete Page
                </button>
            )}

            <div className="flex gap-2">
                <button type="button" onClick={onClose} className="px-3 py-1.5 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="px-3 py-1.5 bg-[#1B5448] text-white rounded-lg hover:opacity-90 font-medium text-sm disabled:opacity-50">
                    Save Changes
                </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}