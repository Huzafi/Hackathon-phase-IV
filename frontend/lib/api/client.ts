/**
 * Centralized API client with automatic JWT injection
 */

/** const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'; */



import { getToken, clearAuth } from '../auth/token';
import { createApiError } from '@/types/errors';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'https://khann4-todo-phaseiii.hf.space';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

interface RequestOptions {
  method?: HttpMethod;
  body?: any;
  headers?: Record<string, string>;
  requiresAuth?: boolean;
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', body, headers = {}, requiresAuth = true } = options;

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (requiresAuth) {
    const token = getToken();
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  const config: RequestInit = {
    method,
    headers: requestHeaders,
  };

  if (body && method !== 'GET') {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // 🔐 Handle unauthorized
    if (response.status === 401) {
      clearAuth();
      if (typeof window !== 'undefined') {
        window.location.href = '/signin';
      }
      throw createApiError({
        message: 'Unauthorized. Please sign in again.',
        status: 401,
      });
    }

    // ✅ FIX: Handle 204 No Content (DELETE case)
    if (response.status === 204) {
      return undefined as T;
    }

    // Parse response
    let data: any;
    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      throw createApiError({
        message:
          data?.detail ||
          data?.message ||
          `Request failed with status ${response.status}`,
        status: response.status,
        detail:
          typeof data === 'string' ? data : JSON.stringify(data),
      });
    }

    return data as T;
  } catch (error: any) {
    if (error?.status) {
      throw error;
    }

    throw createApiError({
      message: 'Network error. Please check your connection.',
      status: 0,
      detail: error instanceof Error ? error.message : String(error),
    });
  }
}

/**
 * Convenience methods
 */
export const api = {
  get: <T>(endpoint: string, requiresAuth = true) =>
    apiRequest<T>(endpoint, { method: 'GET', requiresAuth }),

  post: <T>(endpoint: string, body?: any, requiresAuth = true) =>
    apiRequest<T>(endpoint, { method: 'POST', body, requiresAuth }),

  put: <T>(endpoint: string, body?: any, requiresAuth = true) =>
    apiRequest<T>(endpoint, { method: 'PUT', body, requiresAuth }),

  delete: <T>(endpoint: string, requiresAuth = true) =>
    apiRequest<T>(endpoint, { method: 'DELETE', requiresAuth }),

  patch: <T>(endpoint: string, body?: any, requiresAuth = true) =>
    apiRequest<T>(endpoint, { method: 'PATCH', body, requiresAuth }),
};
