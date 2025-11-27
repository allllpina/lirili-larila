// src/types/index.ts

// --- Auth Types ---
export interface User {
  id: number;
  username: string;
  email: string;
}

export interface Collaborator {
  usr_id: number;
  role: string;
  salary: number;
}

export interface LoginRequest {
  login: string; // Email або Username
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface DeadlineField {
  type: 'deadline_date';
  date: string;       // ISO Date string
  is_expired: boolean;
}

export interface CheckboxField {
  type: 'checkbox';
  checked: boolean;
  text: string;
}

export interface TextField {
  type: 'text';
  text: string;
}

export interface DropdownField {
  type: 'dropdown';
  elements: string[];
  index_of_selected: number;
}

// Об'єднуємо всі можливі варіанти в один тип
export type CustomField = DeadlineField | CheckboxField | TextField | DropdownField;

// --- Project Types ---
// Згідно з документацією, проекти повертають ID сторінок, а не об'єкти [cite: 487]
export interface Project {
  _id: string;
  admin_id: number;
  name: string;
  description: string;
  cost: number;
  page_ids: string[]; 
  collaborators: Collaborator[];
}

export interface Page {
  _id: string;
  project_id: string;
  name: string;
  description: string;
  cost: number;
  board_ids: string[]
}

export interface Board {
  _id: string;
  project_id: string;
  page_id: string;
  name: string;
  description: string;
  cost: number;
  task_ids: string[];
}

export interface Task {
  _id: string;
  project_id: string;
  board_id: string;
  name: string;
  description: string;
  collaborators: Collaborator[];
  
  // Використовуємо літерали для суворої типізації згідно з документацією [cite: 134, 135]
  priority: 'low' | 'medium' | 'high' | 'None'; 
  status: 'complete' | 'in progress' | 'not done';
  
  tags: string[];
  
  // Ось тут наш складний масив
  custom_fields: CustomField[]; 
  
  time_to_complete: number | null;
  cost: number;
}

// --- FINANCE TYPES ---
export interface CostBreakdownUser {
  usr_id: number;
  hourly_rate: number;
  hours_worked: number;
  total_pay: number;
}

export interface TaskCost {
  task_id: string;
  name: string;
  total_cost: number;
  cost_breakdown: CostBreakdownUser[];
}

export interface BoardCost {
  board_id: string;
  name: string;
  overall: number;
  per_task: TaskCost[];
}

export interface PageCost {
  page_id: string;
  name: string;
  overall: number;
  per_board: BoardCost[];
}

export interface ProjectCostEvaluation {
  project_id: string;
  project_name: string;
  overall: number;
  per_page: PageCost[];
}

export interface AiPrioritizedTask {
  task_id: string;
  priority: 'low' | 'medium' | 'high' | 'None';  
}

export interface AiEvaluationResponse {
  prioritized_tasks: AiPrioritizedTask[];
  recommendations: string[];
}