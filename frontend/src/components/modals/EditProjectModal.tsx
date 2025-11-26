import { useState, useEffect } from 'react';
import { projectService, authService } from '../../api/services';
import type { Project, Collaborator, User } from '../../types';
import { useAuth } from '../../context/AuthContext';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  project: Project;
  onUpdate: (updatedProject: Project) => void; // <-- ЗМІНА: Приймаємо оновлений проект
  onDelete: () => void;
}

export default function EditProjectModal({ isOpen, onClose, project, onUpdate, onDelete }: Props) {
  const { user: currentUser } = useAuth();
  
  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description || '');
  const [collaborators, setCollaborators] = useState<Collaborator[]>(project.collaborators || []);
  
  // Додавання нових учасників
  const [newCollabId, setNewCollabId] = useState('');
  const [foundUser, setFoundUser] = useState<User | null>(null);
  const [newCollabRole, setNewCollabRole] = useState('');
  const [newCollabSalary, setNewCollabSalary] = useState('');
  const [userSearchError, setUserSearchError] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setName(project.name);
      setDescription(project.description || '');
      setCollaborators(project.collaborators || []);
      setNewCollabId('');
      setFoundUser(null);
      setIsDeleting(false);
    }
  }, [isOpen, project]);

  if (!isOpen) return null;

  const verifyUser = async () => {
    setUserSearchError('');
    setFoundUser(null);
    if (!newCollabId) return;

    try {
      const id = parseInt(newCollabId);
      if (isNaN(id)) { setUserSearchError("ID must be a number"); return; }
      if (currentUser?.id === id) { setUserSearchError("You are the admin."); return; }
      if (collaborators.some(c => c.usr_id === id)) { setUserSearchError("User already in team."); return; }

      const { data } = await authService.getUserById(id);
      setFoundUser(data);
    } catch (err) {
      setUserSearchError("User not found");
    }
  };

  const addCollaborator = () => {
    if (foundUser && newCollabRole && newCollabSalary) {
        const newCollab: Collaborator = {
            usr_id: foundUser.id,
            role: newCollabRole,
            salary: parseFloat(newCollabSalary) || 0
        };
        setCollaborators([...collaborators, newCollab]);
        setNewCollabId(''); setFoundUser(null); setNewCollabRole(''); setNewCollabSalary('');
    }
  };

  const removeCollaborator = (userId: number) => {
    setCollaborators(collaborators.filter(c => c.usr_id !== userId));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      // 👇 ОТРИМУЄМО ОНОВЛЕНИЙ ОБ'ЄКТ З ВІДПОВІДІ
      const { data } = await projectService.update(project._id, {
        name,
        description,
        collaborators 
      });
      
      // 👇 ВІДРАЗУ ОНОВЛЮЄМО СТАН БАТЬКА
      onUpdate(data); 
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to update project');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
        await projectService.delete(project._id);
        onDelete();
        onClose();
    } catch (e) {
        alert('Failed to delete project');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto custom-scrollbar">
        <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-[#1B5448] font-['Montserrat']">Project Settings</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
        </div>

        <form onSubmit={handleSave} className="space-y-6">
          <div className="space-y-4">
            <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Project Name</label>
                <input required className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none font-medium"
                  value={name} onChange={e => setName(e.target.value)} />
            </div>
            <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Description</label>
                <textarea className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none resize-none h-24 text-sm"
                  value={description} onChange={e => setDescription(e.target.value)} />
            </div>
          </div>

          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-sm font-bold text-gray-700 mb-3">Team Management</h3>
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200 space-y-3 mb-4">
                <div className="flex gap-2">
                    <input className="flex-1 px-3 py-2 border rounded text-sm outline-none focus:border-[#1B5448]"
                        placeholder="User ID" value={newCollabId} onChange={(e) => setNewCollabId(e.target.value)} />
                    <button type="button" onClick={verifyUser} className="bg-white border border-gray-300 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-50 font-medium">Verify</button>
                </div>
                {userSearchError && <div className="text-xs text-red-500">{userSearchError}</div>}
                {foundUser && (
                    <div className="animate-fade-in">
                        <div className="text-xs text-green-700 mb-2">Found: <b>{foundUser.username}</b></div>
                        <div className="grid grid-cols-2 gap-2 mb-2">
                            <input placeholder="Role" className="px-3 py-2 border rounded text-sm outline-none" value={newCollabRole} onChange={e => setNewCollabRole(e.target.value)} />
                            <input type="number" placeholder="Rate ($/h)" className="px-3 py-2 border rounded text-sm outline-none" value={newCollabSalary} onChange={e => setNewCollabSalary(e.target.value)} />
                        </div>
                        <button type="button" onClick={addCollaborator} disabled={!newCollabRole || !newCollabSalary} className="w-full bg-[#1B5448] text-white py-1.5 rounded text-sm disabled:opacity-50 hover:bg-[#154238]">Add to Team</button>
                    </div>
                )}
            </div>
            <div className="space-y-2">
                {collaborators.map((c, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-white p-2 rounded border border-gray-200 text-sm shadow-sm">
                        <div className="flex items-center gap-2">
                            <div className="h-6 w-6 rounded-full bg-gray-200 flex items-center justify-center text-[10px] font-bold">{c.usr_id}</div>
                            <div><span className="font-medium text-gray-800 block">{c.role}</span><span className="text-xs text-green-600">${c.salary}/h</span></div>
                        </div>
                        <button type="button" onClick={() => removeCollaborator(c.usr_id)} className="text-gray-400 hover:text-red-500 p-1 rounded transition">✕</button>
                    </div>
                ))}
                {collaborators.length === 0 && <p className="text-xs text-gray-400 italic">No team members</p>}
            </div>
          </div>

          <div className="border-t pt-4 flex justify-between items-center">
            {isDeleting ? (
                <div className="flex items-center gap-2 bg-red-50 px-2 py-1 rounded border border-red-100 animate-fade-in">
                    <span className="text-xs text-red-600 font-bold">Delete Project?</span>
                    <button type="button" onClick={handleDelete} className="text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700 font-bold">Yes</button>
                    <button type="button" onClick={() => setIsDeleting(false)} className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded hover:bg-gray-300">No</button>
                </div>
            ) : (
                <button type="button" onClick={() => setIsDeleting(true)} className="text-sm text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50 transition">Delete Project</button>
            )}
            <div className="flex gap-2">
                <button type="button" onClick={onClose} className="px-3 py-1.5 text-gray-600 hover:bg-gray-100 rounded-lg text-sm">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="px-3 py-1.5 bg-[#1B5448] text-white rounded-lg hover:opacity-90 font-medium text-sm disabled:opacity-50">Save Changes</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}