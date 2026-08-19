import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Data Quality endpoints
export const dataQualityAPI = {
  getTasks: (status?: string, customerId?: number, skip = 0, limit = 20) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (customerId) params.append('customer_id', customerId.toString());
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return apiClient.get(`/data-quality/tasks?${params}`);
  },

  getTask: (taskId: number) =>
    apiClient.get(`/data-quality/tasks/${taskId}`),

  createTask: (data: any) =>
    apiClient.post(`/data-quality/tasks`, data),

  updateTask: (taskId: number, data: any) =>
    apiClient.put(`/data-quality/tasks/${taskId}`, data),

  getStats: () =>
    apiClient.get('/data-quality/dashboard/stats'),
};

// Customers endpoints
export const customersAPI = {
  list: (skip = 0, limit = 20, search?: string) => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (search) params.append('search', search);
    return apiClient.get(`/customers?${params}`);
  },

  get: (id: number) =>
    apiClient.get(`/customers/${id}`),

  create: (data: any) =>
    apiClient.post(`/customers`, data),
};

// Services endpoints
export const servicesAPI = {
  list: (categoryId?: number, skip = 0, limit = 20) => {
    const params = new URLSearchParams();
    if (categoryId) params.append('category_id', categoryId.toString());
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return apiClient.get(`/services?${params}`);
  },

  get: (id: number) =>
    apiClient.get(`/services/${id}`),

  listCategories: () =>
    apiClient.get('/services/categories/list'),
};

// Opportunities endpoints
export const opportunitiesAPI = {
  list: (customerId?: number, status?: string, skip = 0, limit = 20) => {
    const params = new URLSearchParams();
    if (customerId) params.append('customer_id', customerId.toString());
    if (status) params.append('status', status);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return apiClient.get(`/opportunities?${params}`);
  },

  get: (id: number) =>
    apiClient.get(`/opportunities/${id}`),

  create: (data: any) =>
    apiClient.post(`/opportunities`, data),

  updateStatus: (id: number, status: string, notes?: string) =>
    apiClient.put(`/opportunities/${id}`, { status, notes }),
};

// Conversion Engine endpoints
export const conversionAPI = {
  listRules: (skip = 0, limit = 20) => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return apiClient.get(`/conversion/rules?${params}`);
  },

  getRule: (id: number) =>
    apiClient.get(`/conversion/rules/${id}`),

  createRule: (data: any) =>
    apiClient.post(`/conversion/rules`, data),

  runEngine: (customerId?: number) => {
    const params = new URLSearchParams();
    if (customerId) params.append('customer_id', customerId.toString());
    return apiClient.post(`/conversion/run?${params}`);
  },

  getStats: () =>
    apiClient.get('/conversion/stats'),

  getLogs: (skip = 0, limit = 20, customerId?: number) => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (customerId) params.append('customer_id', customerId.toString());
    return apiClient.get(`/conversion/logs?${params}`);
  },
};

export default apiClient;
