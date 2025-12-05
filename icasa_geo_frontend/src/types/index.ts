// Tipos para ICASA-GEO

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  is_active: boolean;
  children: Category[];
}

export interface Document {
  id: number;
  title: string;
  slug: string;
  category: Category;
  content: string;
  summary: string;
  tags: string[];
  document_code: string;
  effective_date: string | null;
  version: number;
  status: 'draft' | 'review' | 'approved' | 'rejected';
  status_display: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
}

export interface DashboardStats {
  total_documents: number;
  pending_approval: number;
  total_categories: number;
  recent_activity: number;
}

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}