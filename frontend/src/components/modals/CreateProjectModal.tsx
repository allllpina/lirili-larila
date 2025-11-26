// src/components/modals/CreateProjectModal.tsx
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { projectService, authService } from '../../api/services';
import type { Collaborator, User } from '../../types';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateProjectModal({ isOpen, onClose, onSuccess }: CreateProjectModalProps) {
  const { user } = useAuth();
  
  // Дані проекту
  const [formData, setFormData] = useState({ name: '', description: '' });
  
  // Список вже доданих колабораторів
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);
  
  // Стан для форми додавання нового колаборатора
  const [newCollabId, setNewCollabId] = useState('');
  const [foundUser, setFoundUser] = useState<User | null>(null); // Знайдений юзер
  const [newCollabRole, setNewCollabRole] = useState('');
  const [newCollabSalary, setNewCollabSalary] = useState('');
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [userSearchError, setUserSearchError] = useState(''); // Помилка пошуку юзера

  if (!isOpen) return null;

  // 1. Пошук юзера за ID
  const verifyUser = async () => {
    setUserSearchError('');
    setFoundUser(null);
    
    if (!newCollabId) return;

    try {
      // Конвертуємо в число
      const id = parseInt(newCollabId);
      if (isNaN(id)) {
          setUserSearchError("ID must be a number");
          return;
      }
      
      // Самого себе додавати не можна (опціонально)
      if (user?.id === id) {
          setUserSearchError("You are the admin, no need to add yourself.");
          return;
      }

      // Перевіряємо, чи вже додали цього юзера
      if (collaborators.some(c => c.usr_id === id)) {
          setUserSearchError("User already added.");
          return;
      }

      const { data } = await authService.getUserById(id);
      setFoundUser(data); // Юзер знайдений!
    } catch (err) {
      setUserSearchError("User not found (check ID)");
    }
  };

  // 2. Додавання у тимчасовий список
  const addCollaborator = () => {
    if (foundUser && newCollabRole && newCollabSalary) {
        const newCollab: Collaborator = {
            usr_id: foundUser.id,
            role: newCollabRole,
            salary: parseFloat(newCollabSalary) || 0
        };
        
        setCollaborators([...collaborators, newCollab]);
        
        // Скидаємо поля пошуку
        setNewCollabId('');
        setFoundUser(null);
        setNewCollabRole('');
        setNewCollabSalary('');
    }
  };

  // 3. Видалення зі списку
  const removeCollaborator = (userId: number) => {
    setCollaborators(collaborators.filter(c => c.usr_id !== userId));
  };

  // 4. Створення проекту
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    if (!user?.id) {
        setError("Please relogin.");
        setIsSubmitting(false);
        return;
    }

    try {
      await projectService.create({
        name: formData.name,
        description: formData.description,
        admin_id: user.id,
        collaborators: collaborators // Відправляємо масив
      });

      // Очистка
      setFormData({ name: '', description: '' });
      setCollaborators([]);
      setNewCollabId('');
      setFoundUser(null);
      
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error(err);
      setError('Failed to create project.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>

      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-[#1B5448] mb-4 font-['Montserrat']">New Project</h2>
        
        {error && <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Основні поля */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Project Name</label>
            <input
              required
              className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none resize-none h-20"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
          </div>

          <div className="border-t border-gray-200 my-4 pt-4">
            <h3 className="text-md font-bold text-gray-700 mb-2">Add Team (Optional)</h3>
            
            {/* Блок додавання колаборатора */}
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200 space-y-3">
                {/* 1. Пошук ID */}
                <div className="flex gap-2">
                    <input 
                        type="text" 
                        placeholder="User ID (e.g. 5)"
                        className="flex-1 px-3 py-2 border rounded text-sm"
                        value={newCollabId}
                        onChange={(e) => setNewCollabId(e.target.value)}
                    />
                    <button 
                        type="button"
                        onClick={verifyUser}
                        className="bg-gray-200 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-300 transition"
                    >
                        Verify
                    </button>
                </div>
                {userSearchError && <div className="text-xs text-red-500">{userSearchError}</div>}

                {/* 2. Якщо юзер знайдений - показуємо поля Ролі і ЗП */}
                {foundUser && (
                    <div className="animate-fade-in">
                        <div className="text-sm text-green-700 mb-2 flex items-center gap-2">
                            ✅ Found: <span className="font-bold">{foundUser.username}</span> ({foundUser.email})
                        </div>
                        <div className="grid grid-cols-2 gap-2 mb-2">
                            <input 
                                placeholder="Role (e.g. Developer)"
                                className="px-3 py-2 border rounded text-sm"
                                value={newCollabRole}
                                onChange={e => setNewCollabRole(e.target.value)}
                            />
                            <input 
                                type="number"
                                placeholder="Hourly Rate ($)"
                                className="px-3 py-2 border rounded text-sm"
                                value={newCollabSalary}
                                onChange={e => setNewCollabSalary(e.target.value)}
                            />
                        </div>
                        <button 
                            type="button"
                            onClick={addCollaborator}
                            disabled={!newCollabRole || !newCollabSalary}
                            className="w-full bg-[#1B5448] text-white py-1.5 rounded text-sm disabled:opacity-50 hover:bg-[#154238]"
                        >
                            Add to List
                        </button>
                    </div>
                )}
            </div>

            {/* Список доданих */}
            {collaborators.length > 0 && (
                <div className="mt-4 space-y-2">
                    <p className="text-xs font-semibold text-gray-500 uppercase">Team Members:</p>
                    {collaborators.map(c => (
                        <div key={c.usr_id} className="flex justify-between items-center bg-blue-50 p-2 rounded border border-blue-100 text-sm">
                            <div>
                                <span className="font-bold text-gray-800">ID: {c.usr_id}</span>
                                <span className="mx-2 text-gray-400">|</span>
                                <span className="text-gray-600">{c.role}</span>
                                <span className="mx-2 text-gray-400">|</span>
                                <span className="text-green-600 font-medium">${c.salary}/hr</span>
                            </div>
                            <button 
                                type="button" 
                                onClick={() => removeCollaborator(c.usr_id)}
                                className="text-red-500 hover:text-red-700 px-2"
                            >
                                ✕
                            </button>
                        </div>
                    ))}
                </div>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-[#1B5448] text-white rounded-lg hover:opacity-90 font-medium"
            >
              {isSubmitting ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}