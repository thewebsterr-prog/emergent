import axios from 'axios';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Products
export const getProducts = async (params?: {
  category?: string;
  search?: string;
  minPrice?: number;
  maxPrice?: number;
  sort?: string;
}) => {
  const response = await api.get('/products', { params });
  return response.data;
};

export const getProduct = async (id: string) => {
  const response = await api.get(`/products/${id}`);
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get('/categories');
  return response.data;
};

// Reviews
export const getReviews = async (productId: string) => {
  const response = await api.get(`/reviews/${productId}`);
  return response.data;
};

export const createReview = async (data: {
  productId: string;
  rating: number;
  comment: string;
}) => {
  const response = await api.post('/reviews', data);
  return response.data;
};

// Cart
export const getCart = async () => {
  const response = await api.get('/cart');
  return response.data;
};

export const addToCart = async (productId: string, quantity: number = 1) => {
  const response = await api.post('/cart/add', { productId, quantity });
  return response.data;
};

export const updateCartItem = async (productId: string, quantity: number) => {
  const response = await api.post('/cart/update', { productId, quantity });
  return response.data;
};

export const removeFromCart = async (productId: string) => {
  const response = await api.delete(`/cart/remove/${productId}`);
  return response.data;
};

export const clearCart = async () => {
  const response = await api.delete('/cart/clear');
  return response.data;
};

// Orders
export const createOrder = async (data: {
  items: any[];
  total: number;
  shippingAddress: any;
}) => {
  const response = await api.post('/orders', data);
  return response.data;
};

export const getOrders = async () => {
  const response = await api.get('/orders');
  return response.data;
};

export const getOrder = async (id: string) => {
  const response = await api.get(`/orders/${id}`);
  return response.data;
};

// Initialize mock data
export const initMockData = async () => {
  const response = await api.post('/init-data');
  return response.data;
};

export default api;