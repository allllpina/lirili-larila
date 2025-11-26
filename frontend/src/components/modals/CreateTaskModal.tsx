// src/components/modals/CreateTaskModal.tsx
import { useState } from 'react';
import { taskService } from '../../api/services';
import type { Collaborator, CustomField } from '../../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  boardId: string;
  projectCollaborators: Collaborator[]; // Список всіх доступних у проекті
}

export default function CreateTaskModal({ isOpen, onClose, onSuccess, boardId, projectCollaborators }: Props) {
  // Базові поля
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low'|'medium'|'high'|'None'>('None');
  
  // Теги
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  
  // Колаборатори
  const [selectedCollabIds, setSelectedCollabIds] = useState<number[]>([]);

  // Кастомні поля
  const [customFields, setCustomFields] = useState<CustomField[]>([]);
  const [newFieldType, setNewFieldType] = useState<string>('text'); // Тип поля, що додається
  
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  // --- ЛОГІКА ТЕГІВ ---
  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagInput.trim())) setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  // --- ЛОГІКА КОЛАБОРАТОРІВ ---
  const toggleCollaborator = (usr_id: number) => {
    if (selectedCollabIds.includes(usr_id)) {
      setSelectedCollabIds(selectedCollabIds.filter(id => id !== usr_id));
    } else {
      setSelectedCollabIds([...selectedCollabIds, usr_id]);
    }
  };

  // --- ЛОГІКА КАСТОМНИХ ПОЛІВ ---
  const addCustomField = () => {
    let newField: CustomField;

    switch (newFieldType) {
        case 'text':
            newField = { type: 'text', text: '' }; // text - це назва поля чи значення? Зазвичай при створенні ми задаємо значення. 
            // Але згідно твого JSON, custom_fields містять значення. 
            // Припустимо, що користувач вводить значення відразу.
            break;
        case 'checkbox':
            newField = { type: 'checkbox', checked: false, text: 'New Checkbox' };
            break;
        case 'deadline_date':
            newField = { type: 'deadline_date', date: new Date().toISOString(), is_expired: false };
            break;
        case 'dropdown':
            newField = { type: 'dropdown', elements: ['Option 1', 'Option 2'], index_of_selected: 0 };
            break;
        default: return;
    }
    setCustomFields([...customFields, newField]);
  };

  const updateCustomField = (index: number, updatedField: CustomField) => {
      const newFields = [...customFields];
      newFields[index] = updatedField;
      setCustomFields(newFields);
  };

  const removeCustomField = (index: number) => {
      setCustomFields(customFields.filter((_, i) => i !== index));
  };

  // --- SUBMIT ---
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Формуємо список об'єктів Collaborator на основі вибраних ID
    const finalCollaborators = projectCollaborators.filter(c => selectedCollabIds.includes(c.usr_id));

    try {
      await taskService.create(boardId, {
        name,
        description,
        priority,
        status: 'not done',
        tags,
        collaborators: finalCollaborators,
        custom_fields: customFields
      });
      
      // Reset
      setName(''); setDescription(''); setPriority('None'); setTags([]); setSelectedCollabIds([]); setCustomFields([]);
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto custom-scrollbar">
        <h2 className="text-xl font-bold text-[#1B5448] mb-4 font-['Montserrat']">New Task</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name & Desc */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Task Name</label>
            <input required className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none"
              value={name} onChange={e => setName(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none resize-none h-20"
              value={description} onChange={e => setDescription(e.target.value)} />
          </div>

          <div className="grid grid-cols-2 gap-4">
             {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Priority</label>
              <select className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none bg-white"
                value={priority} onChange={e => setPriority(e.target.value as any)}>
                <option value="None">None</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            
             {/* Tags */}
            <div>
                <label className="block text-sm font-medium text-gray-700">Tags</label>
                <input className="w-full px-3 py-2 border rounded-lg focus:ring-[#1B5448] outline-none"
                  placeholder="Type & Enter" value={tagInput} onChange={e => setTagInput(e.target.value)} onKeyDown={handleAddTag} />
                 <div className="flex flex-wrap gap-1 mt-1">
                  {tags.map(tag => (
                    <span key={tag} className="bg-blue-50 text-blue-600 px-1 rounded text-xs cursor-pointer" onClick={() => setTags(tags.filter(t => t !== tag))}>#{tag}</span>
                  ))}
                </div>
            </div>
          </div>

          {/* COLLABORATORS SELECTOR */}
          <div className="border-t pt-3">
             <label className="block text-sm font-medium text-gray-700 mb-2">Assign Team Members</label>
             <div className="flex flex-wrap gap-2">
                {projectCollaborators.length === 0 && <span className="text-xs text-gray-400">No members in project</span>}
                
                {projectCollaborators.map(c => (
                    <button
                        type="button"
                        key={c.usr_id}
                        onClick={() => toggleCollaborator(c.usr_id)}
                        className={`px-3 py-1 rounded-full text-xs font-medium border transition ${
                            selectedCollabIds.includes(c.usr_id) 
                            ? 'bg-[#1B5448] text-white border-[#1B5448]' 
                            : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                        }`}
                    >
                        User ID: {c.usr_id} ({c.role})
                    </button>
                ))}
             </div>
          </div>

          {/* CUSTOM FIELDS BUILDER */}
          <div className="border-t pt-3 bg-gray-50 p-3 rounded-lg">
             <div className="flex justify-between items-center mb-2">
                 <label className="text-sm font-bold text-gray-700">Custom Fields</label>
                 <div className="flex gap-2">
                     <select 
                        className="text-xs border rounded p-1"
                        value={newFieldType}
                        onChange={(e) => setNewFieldType(e.target.value)}
                     >
                         <option value="text">Text</option>
                         <option value="checkbox">Checkbox</option>
                         <option value="deadline_date">Deadline</option>
                         <option value="dropdown">Dropdown</option>
                     </select>
                     <button type="button" onClick={addCustomField} className="text-xs bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded">
                         + Add Field
                     </button>
                 </div>
             </div>
             
             <div className="space-y-2">
                 {customFields.map((field, idx) => (
                     <div key={idx} className="flex items-center gap-2 bg-white p-2 rounded border border-gray-200">
                         {/* Рендеримо інпут в залежності від типу, щоб заповнити значення */}
                         
                         {field.type === 'text' && (
                             <input 
                                className="flex-1 text-sm border-b outline-none" 
                                placeholder="Text value"
                                value={field.text}
                                onChange={(e) => updateCustomField(idx, { ...field, text: e.target.value })}
                             />
                         )}

                         {field.type === 'checkbox' && (
                             <div className="flex items-center gap-2 flex-1">
                                 <input 
                                    type="checkbox" 
                                    checked={field.checked} 
                                    onChange={(e) => updateCustomField(idx, { ...field, checked: e.target.checked })}
                                 />
                                 <input 
                                    className="text-sm border-b outline-none flex-1"
                                    placeholder="Label text"
                                    value={field.text}
                                    onChange={(e) => updateCustomField(idx, { ...field, text: e.target.value })}
                                 />
                             </div>
                         )}

                         {field.type === 'deadline_date' && (
                             <input 
                                type="date"
                                className="flex-1 text-sm"
                                value={field.date.split('T')[0]}
                                onChange={(e) => updateCustomField(idx, { ...field, date: new Date(e.target.value).toISOString() })}
                             />
                         )}

                         {field.type === 'dropdown' && (
                             <div className="flex-1">
                                 <input 
                                    className="w-full text-xs border-b mb-1"
                                    placeholder="Options (comma separated)"
                                    value={field.elements.join(',')}
                                    onChange={(e) => updateCustomField(idx, { ...field, elements: e.target.value.split(',') })}
                                 />
                                 <select className="w-full text-xs bg-gray-50">
                                     {field.elements.map((el, i) => <option key={i}>{el}</option>)}
                                 </select>
                             </div>
                         )}

                         <button type="button" onClick={() => removeCustomField(idx)} className="text-red-500 hover:text-red-700 text-xs px-2">✕</button>
                     </div>
                 ))}
             </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
            <button type="submit" disabled={isSubmitting} className="px-4 py-2 bg-[#1B5448] text-white rounded-lg hover:opacity-90 font-medium disabled:opacity-50">Create Task</button>
          </div>
        </form>
      </div>
    </div>
  );
}