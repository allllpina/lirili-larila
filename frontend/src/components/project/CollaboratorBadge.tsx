import { useEffect, useState } from 'react';
import { authService } from '../../api/services';
import type { Collaborator, User } from '../../types';

export default function CollaboratorBadge({ collab }: { collab: Collaborator }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Отримуємо дані про користувача по ID [cite: 85]
    authService.getUserById(collab.usr_id)
      .then(res => setUser(res.data))
      .catch(err => console.error(`Failed to load user ${collab.usr_id}`, err));
  }, [collab.usr_id]);

  if (!user) return <div className="h-8 w-8 bg-gray-200 rounded-full animate-pulse" />;

  const initials = user.username.slice(0, 2).toUpperCase();

  return (
    <div className="flex items-center gap-2 bg-white/50 p-1.5 rounded-full border border-gray-200/60 shadow-sm" title={`Role: ${collab.role}, Rate: $${collab.salary}/h`}>
      <div className="h-6 w-6 rounded-full bg-[#1B5448] text-white flex items-center justify-center text-[10px] font-bold border border-white shadow-sm shrink-0">
        {initials}
      </div>
      <div className="flex flex-col leading-none pr-1">
         <span className="text-xs font-semibold text-gray-700 truncate max-w-[80px]">{user.username}</span>
         <span className="text-[9px] text-gray-500">{collab.role}</span>
      </div>
    </div>
  );
}