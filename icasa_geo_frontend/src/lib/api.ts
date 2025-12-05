import axios from 'axios';
import { Category, Document, ApiResponse } from '@/types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API de Categorías
export const categoriesApi = {
  getAll: () => api.get<ApiResponse<Category>>('/knowledge/categories/'),
  getTree: () => api.get<Category[]>('/knowledge/categories/tree/'),
  getBySlug: (slug: string) => api.get<Category>(`/knowledge/categories/${slug}/`),
  create: (data: Partial<Category>) => api.post<Category>('/knowledge/categories/', data),
  update: (slug: string, data: Partial<Category>) => api.put<Category>(`/knowledge/categories/${slug}/`, data),
  delete: (slug: string) => api.delete(`/knowledge/categories/${slug}/`),
};

// API de Documentos
export const documentsApi = {
  getAll: (params?: { category?: string; search?: string }) => 
    api.get<ApiResponse<Document>>('/knowledge/documents/', { params }),
  getBySlug: (slug: string) => api.get<Document>(`/knowledge/documents/${slug}/`),
  create: (data: Partial<Document>) => api.post<Document>('/knowledge/documents/', data),
  update: (slug: string, data: Partial<Document>) => api.put<Document>(`/knowledge/documents/${slug}/`, data),
  delete: (slug: string) => api.delete(`/knowledge/documents/${slug}/`),
  approve: (slug: string) => api.post(`/knowledge/documents/${slug}/approve/`),
  reject: (slug: string, reason: string) => api.post(`/knowledge/documents/${slug}/reject/`, { reason }),
};

export default api;