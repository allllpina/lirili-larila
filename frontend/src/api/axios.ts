// src/api/axios.ts
import axios from 'axios';

const url = import.meta.env.VITE_API_BASE_URL || 'http://localhost:1313';
// Базовий URL твого Nginx Gateway [cite: 5]
export const api = axios.create({
  baseURL: url, 
  headers: {
    'Content-Type': 'application/json',
  },
});

// Автоматично додаємо токен до кожного запиту [cite: 68]
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});