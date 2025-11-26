// src/api/services.ts
import { api } from './axios';
import type { LoginRequest, RegisterRequest, User, Project, Collaborator, CustomField, Page, Board, Task, ProjectCostEvaluation } from '../types';
const url = import.meta.env.VITE_API_BASE_URL || 'http://localhost:1313';

export const authService = {
  // Реєстрація повертає рядок (токен) [cite: 37]
  register: async (data: RegisterRequest) => {
    return api.post<string>('/auth/register', data);
  },

  // Логін повертає рядок (токен) 
  login: async (data: LoginRequest) => {
    return api.post<string>('/auth/token', data);
  },

  // Отримання поточного юзера [cite: 64]
  me: async () => {
    return api.get<User>('/auth/get_current_user');
  },

  getUserById: async (id: number) => {
    return api.get<User>(`/auth/get_user_by_id`, {
      params: { user_id: id }
    });
  },
  
  // Посилання для Google Login (для кнопки) [cite: 60]
  googleLoginUrl: `${url}/auth/google/login`
};

export const projectService = {
  getAll: async () => {
    return api.get<Project[]>('/lirililarila/projects/my_projects');
  },

  getOne: async (id: string) => {
    return api.get<Project>(`/lirililarila/projects/get_project/${id}`);
  },

  create: async (data: { 
    name: string; 
    description: string; 
    admin_id: number;
    collaborators: Collaborator[]; 
  }) => {
    return api.post<Project>('/lirililarila/projects/create_project', data);
  },

  update: async (projectId: string, data: {
    name?: string;
    description?: string;
    collaborators?: Collaborator[];
  }) => {
    return api.put<Project>('/lirililarila/projects/edit_project', data, {
      params: {project_id: projectId}
    });
  },

  delete: async (projectId: string) => {
    return api.delete<{ deleted_project: string;  deleted_pages: number; deleted_boards: number; deleted_tasks: number }>(`/lirililarila/projects/delete_project/${projectId}`);
  },

  getCostEvaluation: async (projectId: string) => {
    return api.get<ProjectCostEvaluation>(`/lirililarila/projects/get_cost_evaluation/${projectId}`);
  }
};

// --- PAGE SERVICE ---
export const pageService = {
  // [POST] /lirililarila/pages/create_page?project_id=... [cite: 365-378]
  create: async (projectId: string, data: { name: string; description: string }) => {
    return api.post<Page>('/lirililarila/pages/create_page', data, {
      params: { project_id: projectId }
    });
  },

  // [GET] /lirililarila/pages/get_page/{page_id} [cite: 391-396]
  getOne: async (id: string) => {
    return api.get<Page>(`/lirililarila/pages/get_page/${id}`);
  },

  update: async (pageId: string, data: {name?: string; description?: string}) => {
    return api.put<Page>('/lirililarila/pages/edit_page', data, {
      params: { page_id: pageId }
    });
  },

  delete: async (pageId: string) => {
    return api.delete<{ deleted_page: string;  deleted_boards: number; deleted_tasks: number}>(`/lirililarila/pages/delete_page/${pageId}`);
  }
};

// --- BOARD SERVICE ---
export const boardService = {
  // [POST] /lirililarila/boards/create_board?page_id=... [cite: 266-279]
  create: async (pageId: string, data: { name: string; description: string }) => {
    return api.post<Board>('/lirililarila/boards/create_board', data, {
      params: { page_id: pageId }
    });
  },

  // [GET] /lirililarila/boards/get_board/{board_id} [cite: 293-298]
  getOne: async (id: string) => {
    return api.get<Board>(`/lirililarila/boards/get_board/${id}`);
  },

  update: async (boardId: string, data: {name?: string; description?: string}) => {
    return api.put<Board>('/lirililarila/boards/edit_board', data, {params: {board_id: boardId}});
  },
  delete: async (boardId: string) => {
    return api.delete<{deled_board: string; deleted_tasks: number}>(`/lirililarila/boards/delete_board/${boardId}`);
  }
};

// --- TASK SERVICE ---
export const taskService = {
  // [POST] /lirililarila/tasks/create_task?board_id=... [cite: 122-140]
  create: async (boardId: string, data: {
    name: string;
    description: string;
    priority: 'low' | 'medium' | 'high' | 'None';
    status: 'complete' | 'in progress' | 'not done';
    tags: string[];
    collaborators: Collaborator[];
    custom_fields: CustomField[];
  }) => {
    return api.post<Task>('/lirililarila/tasks/create_task', data, {
      params: { board_id: boardId }
    });
  },

  // [GET] /lirililarila/tasks/get_task/{task_id} [cite: 159-164]
  getOne: async (id: string) => {
    return api.get<Task>(`/lirililarila/tasks/get_task/${id}`);
  },

  update: async (taskId: string, data: any) => {
    return api.put<Task>('/lirililarila/tasks/edit_task', data, {params: {task_id: taskId}});
  },

  delete: async (taskId: string) => {
    return api.delete<{deleted_task: string}>(`/lirililarila/tasks/delete_task/${taskId}`);
  },

  move: async (data: {taskId: string; boardGiverId: string; boardReceiverId: string}) => {
    return api.put<{status: string}>('/lirililarila/tasks/move_task', data);
  }
};