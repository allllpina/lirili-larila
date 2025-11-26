// src/components/modals/TaskDetailModal.tsx
import { useEffect, useState, useMemo } from 'react';
import { taskService } from '../../api/services';
import type { Task, CustomField, Collaborator } from '../../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  taskId: string | null;
  onUpdate: () => void;
  projectCollaborators: Collaborator[];
}

export default function TaskDetailModal({ isOpen, onClose, taskId, onUpdate, projectCollaborators }: Props) {
  const [task, setTask] = useState<Task | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // --- СТАНИ РЕДАГУВАННЯ ---
  const [editName, setEditName] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editStatus, setEditStatus] = useState<string>('');
  const [editPriority, setEditPriority] = useState<string>('');
  const [editCustomFields, setEditCustomFields] = useState<CustomField[]>([]);
  const [editTags, setEditTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [editCollabIds, setEditCollabIds] = useState<number[]>([]);
  const [editTimeToComplete, setEditTimeToComplete] = useState<string>('');

  useEffect(() => {
    if (isOpen && taskId) {
      loadTask();
      setIsEditing(false);
      setIsDeleting(false);
    }
  }, [isOpen, taskId]);

  const loadTask = async () => {
    if (!taskId) return;
    setIsLoading(true);
    try {
        const { data } = await taskService.getOne(taskId);
        setTask(data);
        setEditName(data.name);
        setEditDesc(data.description);
        setEditStatus(data.status);
        setEditPriority(data.priority);
        setEditTags(data.tags || []);
        setEditCollabIds(data.collaborators.map(c => c.usr_id));
        setEditTimeToComplete(data.time_to_complete ? String(data.time_to_complete) : '');
        setEditCustomFields(JSON.parse(JSON.stringify(data.custom_fields)));
    } catch (e) {
        console.error(e);
    } finally {
        setIsLoading(false);
    }
  };

  const isChanged = useMemo(() => {
    if (!task) return false;
    if (editName !== task.name) return true;
    if (editDesc !== task.description) return true;
    if (editStatus !== task.status) return true;
    if (editPriority !== task.priority) return true;
    const originalTime = task.time_to_complete ? String(task.time_to_complete) : '';
    if (editStatus === 'complete' && editTimeToComplete !== originalTime) return true;
    if (JSON.stringify(editTags.sort()) !== JSON.stringify(task.tags.sort())) return true;
    const originalCollabs = task.collaborators.map(c => c.usr_id).sort();
    if (JSON.stringify(editCollabIds.sort()) !== JSON.stringify(originalCollabs)) return true;
    if (JSON.stringify(editCustomFields) !== JSON.stringify(task.custom_fields)) return true;
    return false;
  }, [task, editName, editDesc, editStatus, editPriority, editTags, editCollabIds, editCustomFields, editTimeToComplete]);

  // --- HELPERS ---
  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!editTags.includes(tagInput.trim())) setEditTags([...editTags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const toggleCollaborator = (usr_id: number) => {
    if (editCollabIds.includes(usr_id)) setEditCollabIds(editCollabIds.filter(id => id !== usr_id));
    else setEditCollabIds([...editCollabIds, usr_id]);
  };

  const handleDelete = async () => {
    if (!task) return;
    try {
        await taskService.delete(task._id);
        onUpdate();
        onClose();
    } catch (e) {
        alert('Failed to delete');
    }
  };

  // --- CUSTOM FIELDS LOGIC ---
  const updateEditFieldState = (index: number, updatedField: CustomField) => {
    const newFields = [...editCustomFields];
    newFields[index] = updatedField;
    setEditCustomFields(newFields);
  };

  // 👇 ФУНКЦІЯ ВИДАЛЕННЯ КАСТОМНОГО ПОЛЯ
  const removeEditField = (index: number) => {
    setEditCustomFields(editCustomFields.filter((_, i) => i !== index));
  };

  const toggleCheckboxViewMode = async (idx: number) => {
     if (!task) return;
     const newFields = JSON.parse(JSON.stringify(task.custom_fields));
     const field = newFields[idx];
     if (field.type === 'checkbox') {
         field.checked = !field.checked;
         setTask({ ...task, custom_fields: newFields }); 
         try { await taskService.update(task._id, { custom_fields: newFields }); onUpdate(); } 
         catch (error) { loadTask(); }
     }
  };

  const updateFieldLive = async (idx: number, updatedFieldData: Partial<CustomField>) => {
     if (!task) return;
     const newFields = JSON.parse(JSON.stringify(task.custom_fields));
     Object.assign(newFields[idx], updatedFieldData);
     setTask({ ...task, custom_fields: newFields }); 
     await taskService.update(task._id, { custom_fields: newFields });
     onUpdate();
  };

  const handleSave = async () => {
    if (!task) return;
    const finalCollaborators = projectCollaborators.filter(c => editCollabIds.includes(c.usr_id));
    try {
        await taskService.update(task._id, {
            name: editName,
            description: editDesc,
            status: editStatus as any,
            priority: editPriority as any,
            custom_fields: editCustomFields,
            tags: editTags,
            collaborators: finalCollaborators,
            time_to_complete: editStatus === 'complete' ? Number(editTimeToComplete) : undefined
        });
        setIsEditing(false);
        loadTask();
        onUpdate();
    } catch (e) {
        alert('Failed to update task');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose}></div>
      
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-3xl min-h-[50vh] max-h-[90vh] flex flex-col overflow-hidden transition-all">
        
        {/* HEADER */}
        <div className="flex justify-between items-center p-4 border-b bg-gray-50">
            <div className="flex gap-2 items-center">
                <span className={`text-xs px-2 py-1 rounded border font-bold uppercase tracking-wider
                    ${task?.status === 'complete' ? 'bg-green-100 text-green-700 border-green-200' : 
                      task?.status === 'in progress' ? 'bg-blue-100 text-blue-700 border-blue-200' : 
                      'bg-gray-200 text-gray-700 border-gray-300'}`}>
                    {task?.status}
                </span>
            </div>
            
            <div className="flex gap-3 items-center">
                {isDeleting ? (
                    <div className="flex items-center gap-2 animate-fade-in bg-red-50 px-2 py-1 rounded border border-red-100">
                        <span className="text-xs text-red-600 font-bold">Are you sure?</span>
                        <button onClick={handleDelete} className="text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700 font-bold">Yes</button>
                        <button onClick={() => setIsDeleting(false)} className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded hover:bg-gray-300">No</button>
                    </div>
                ) : (
                    !isEditing ? (
                        <>
                            <button onClick={() => setIsEditing(true)} className="px-4 py-1.5 bg-gray-100 border border-gray-300 text-gray-700 font-bold rounded-lg border-b-4 hover:bg-gray-200 active:border-b-2 active:translate-y-[2px] transition-all text-sm">
                                Edit Task
                            </button>
                            <button onClick={() => setIsDeleting(true)} className="px-4 py-1.5 bg-red-50 border border-red-200 text-red-600 font-bold rounded-lg border-b-4 hover:bg-red-100 active:border-b-2 active:translate-y-[2px] transition-all text-sm">
                                Delete
                            </button>
                        </>
                    ) : (
                        <>
                            <button onClick={() => { setIsEditing(false); loadTask(); }} className="px-4 py-1.5 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium transition">
                                Cancel
                            </button>
                            <button onClick={handleSave} disabled={!isChanged} className={`px-4 py-1.5 font-bold rounded-lg border-b-4 transition-all text-sm ${isChanged ? 'bg-[#1B5448] text-white border-[#143d34] hover:bg-[#154238] active:border-b-0 active:translate-y-[4px]' : 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed'}`}>
                                Save Changes
                            </button>
                        </>
                    )
                )}
                <div className="w-px h-6 bg-gray-300 mx-1 self-center"></div>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-600 px-2 text-xl font-bold">✕</button>
            </div>
        </div>

        {/* CONTENT */}
        <div className="p-8 overflow-y-auto flex-1 custom-scrollbar">
            {isLoading || !task ? (
                <div className="flex justify-center py-10"><div className="animate-spin h-8 w-8 border-2 border-[#1B5448] rounded-full border-t-transparent"></div></div>
            ) : isEditing ? (
                // --- EDIT MODE ---
                <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="col-span-2">
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Title</label>
                            <input className="w-full border p-2 rounded focus:ring-[#1B5448] outline-none font-bold text-gray-800" value={editName} onChange={e => setEditName(e.target.value)} />
                        </div>
                        <div>
                             <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Status</label>
                             <select className="border p-2 rounded w-full bg-white" value={editStatus} onChange={e => setEditStatus(e.target.value)}>
                                 <option value="not done">Not Done</option>
                                 <option value="in progress">In Progress</option>
                                 <option value="complete">Complete</option>
                             </select>
                        </div>
                        <div>
                             <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Priority</label>
                             <select className="border p-2 rounded w-full bg-white" value={editPriority} onChange={e => setEditPriority(e.target.value)}>
                                 <option value="None">None</option>
                                 <option value="low">Low</option>
                                 <option value="medium">Medium</option>
                                 <option value="high">High</option>
                             </select>
                        </div>
                        {editStatus === 'complete' && (
                            <div className="col-span-2 bg-green-50 p-3 rounded border border-green-200 animate-fade-in">
                                <label className="block text-xs font-bold text-green-800 uppercase mb-1">Time Spent (Hours) *</label>
                                <input type="number" min="0" placeholder="e.g. 5.5" className="w-full border p-2 rounded focus:ring-green-600 outline-none font-medium" value={editTimeToComplete} onChange={e => setEditTimeToComplete(e.target.value)} />
                            </div>
                        )}
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Description</label>
                        <textarea className="w-full border p-2 rounded focus:ring-[#1B5448] outline-none h-32 text-sm" value={editDesc} onChange={e => setEditDesc(e.target.value)} />
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Tags</label>
                        <div className="flex flex-wrap gap-2 mb-2">
                            {editTags.map(tag => (
                                <span key={tag} className="bg-blue-50 text-blue-600 px-2 py-1 rounded text-xs flex items-center gap-1">
                                    {tag}
                                    <button onClick={() => setEditTags(editTags.filter(t => t !== tag))} className="hover:text-red-500">×</button>
                                </span>
                            ))}
                        </div>
                        <input className="w-full border p-2 rounded focus:ring-[#1B5448] outline-none text-sm" placeholder="Add tag..." value={tagInput} onChange={e => setTagInput(e.target.value)} onKeyDown={handleAddTag} />
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Collaborators</label>
                        <div className="flex flex-wrap gap-2">
                             {projectCollaborators.length === 0 && <span className="text-sm text-gray-400">No members in project</span>}
                             {projectCollaborators.map(c => (
                                <button key={c.usr_id} onClick={() => toggleCollaborator(c.usr_id)} className={`px-3 py-1.5 rounded text-xs font-medium border transition ${editCollabIds.includes(c.usr_id) ? 'bg-[#1B5448] text-white border-[#1B5448]' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'}`}>
                                    ID: {c.usr_id} ({c.role})
                                </button>
                             ))}
                        </div>
                    </div>
                    
                    {editCustomFields.length > 0 && (
                        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                            <h3 className="text-xs font-bold text-gray-500 uppercase mb-3">Custom Fields Data</h3>
                            <div className="space-y-3">
                                {editCustomFields.map((field, idx) => (
                                    <div key={idx} className="bg-white p-3 rounded border border-gray-200 shadow-sm relative group">
                                        
                                        {/* 👇 КНОПКА ВИДАЛЕННЯ ПОЛЯ */}
                                        <button 
                                            onClick={() => removeEditField(idx)}
                                            className="absolute top-2 right-2 text-gray-400 hover:text-red-500 transition z-10 p-1"
                                            title="Remove field"
                                        >
                                            ✕
                                        </button>

                                        {field.type === 'text' && (
                                            <input className="w-full border-b outline-none py-1 text-sm pr-6" value={field.text} onChange={(e) => updateEditFieldState(idx, { ...field, text: e.target.value })} placeholder="Text value" />
                                        )}
                                        {field.type === 'checkbox' && (
                                            <div className="flex items-center gap-3 pr-6">
                                                <input type="checkbox" checked={field.checked} onChange={(e) => updateEditFieldState(idx, { ...field, checked: e.target.checked })} className="h-4 w-4 accent-[#1B5448]" />
                                                <input className="flex-1 border-b outline-none py-1 text-sm" value={field.text} onChange={(e) => updateEditFieldState(idx, { ...field, text: e.target.value })} />
                                            </div>
                                        )}
                                        {field.type === 'deadline_date' && (
                                            <input type="date" className="w-full border rounded p-1 text-sm pr-6" value={field.date ? field.date.split('T')[0] : ''} 
                                                onChange={(e) => updateEditFieldState(idx, { ...field, date: e.target.value ? new Date(e.target.value).toISOString() : field.date })} />
                                        )}
                                        {field.type === 'dropdown' && (
                                            <select className="w-full border rounded p-1 text-sm bg-white pr-6" value={field.index_of_selected} 
                                                onChange={(e) => updateEditFieldState(idx, { ...field, index_of_selected: Number(e.target.value) })}>
                                                {field.elements.map((el, i) => <option key={i} value={i}>{el}</option>)}
                                            </select>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                // --- VIEW MODE ---
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="md:col-span-2 space-y-6">
                        <h1 className="text-2xl font-bold text-gray-900 font-['Montserrat']">{task.name}</h1>
                        <div>
                            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">Description</h3>
                            <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                                {task.description || <span className="text-gray-400 italic">No description provided.</span>}
                            </p>
                        </div>
                        
                        {task.tags && task.tags.length > 0 && (
                             <div>
                                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">Tags</h3>
                                <div className="flex flex-wrap gap-2">
                                    {task.tags.map(tag => (
                                        <span key={tag} className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs border border-blue-100">#{tag}</span>
                                    ))}
                                </div>
                             </div>
                        )}

                         {task.custom_fields.length > 0 && (
                             <div>
                                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">Details</h3>
                                <div className="space-y-2">
                                    {task.custom_fields.map((field, idx) => (
                                        <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
                                            {field.type === 'checkbox' && (
                                                <label className="flex items-center gap-3 cursor-pointer w-full select-none">
                                                    <input type="checkbox" checked={field.checked} onChange={() => toggleCheckboxViewMode(idx)} className="h-5 w-5 accent-[#1B5448]" />
                                                    <span className={`text-sm ${field.checked ? 'line-through text-gray-400' : 'text-gray-700 font-medium'}`}>{field.text}</span>
                                                </label>
                                            )}
                                            {field.type === 'text' && (
                                                <div className="w-full">
                                                    <span className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Text Note</span>
                                                    <div className="text-sm text-gray-800 bg-white p-2 rounded border border-gray-200">{field.text}</div>
                                                </div>
                                            )}
                                            {field.type === 'deadline_date' && (
                                                <div className="w-full">
                                                     <span className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Deadline</span>
                                                     <div className={`text-sm font-medium ${field.is_expired ? 'text-red-600' : 'text-gray-700'}`}>🗓 {new Date(field.date).toLocaleDateString()} {field.is_expired && " (Expired)"}</div>
                                                </div>
                                            )}
                                            {field.type === 'dropdown' && (
                                                <div className="w-full">
                                                     <span className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Select Option</span>
                                                     <select className="w-full border-gray-300 rounded-md text-sm shadow-sm py-1.5" value={field.index_of_selected} onChange={(e) => updateFieldLive(idx, { index_of_selected: Number(e.target.value) })}>
                                                         {field.elements.map((el, i) => <option key={i} value={i}>{el}</option>)}
                                                     </select>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                             </div>
                        )}
                    </div>
                    
                    <div className="space-y-6">
                         <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                             <h3 className="text-xs font-bold text-gray-500 uppercase mb-3">Properties</h3>
                             <div className="space-y-3 text-sm">
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-500">Priority</span>
                                    <span className={`font-medium px-2 py-0.5 rounded text-xs uppercase
                                        ${task.priority === 'high' ? 'bg-red-100 text-red-700' : 
                                          task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                          'bg-green-100 text-green-700'}`}>
                                        {task.priority}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-500">Cost</span>
                                    <span className="font-medium text-green-700">${task.cost}</span>
                                </div>
                                {task.time_to_complete && (
                                     <div className="flex justify-between">
                                        <span className="text-gray-500">Time Spent</span>
                                        <span className="font-medium text-gray-800">{task.time_to_complete}h</span>
                                    </div>
                                )}
                                <div className="flex justify-between">
                                    <span className="text-gray-500">ID</span>
                                    <span className="font-mono text-xs text-gray-400">{task._id.slice(-4)}</span>
                                </div>
                             </div>
                         </div>
                         <div>
                            <h3 className="text-xs font-bold text-gray-500 uppercase mb-3">Collaborators</h3>
                            <div className="flex flex-wrap gap-2">
                                {task.collaborators.length > 0 ? (
                                    task.collaborators.map(c => (
                                        <div key={c.usr_id} className="text-xs bg-white text-gray-700 px-2 py-1 rounded border shadow-sm flex items-center gap-1">
                                            <span className="w-4 h-4 rounded-full bg-gray-200 flex items-center justify-center text-[8px] font-bold">
                                                {c.usr_id}
                                            </span>
                                            {c.role}
                                        </div>
                                    ))
                                ) : (
                                    <span className="text-sm text-gray-400 italic">Unassigned</span>
                                )}
                            </div>
                        </div>
                     </div>
                </div>
            )}
        </div>
      </div>
    </div>
  );
}