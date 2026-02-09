/**
 * Authentication API functions
 */

import { api } from './client';
import { SignupRequest, SigninRequest, AuthResponse } from '@/types/api';
import { User } from '@/types/entities';

/**
 * Sign up a new user
 */
export async function signup(data: SignupRequest): Promise<AuthResponse> {
  const response = await api.post<any>('/api/auth/signup', data, false);
  // Map backend fields to frontend format
  return {
    access_token: response.access_token,
    token_type: response.token_type,
    user: {
      id: String(response.user.id),
      email: response.user.email,
      created_at: response.user.created_at
    }
  };
}

/**
 * Sign in an existing user
 */
export async function signin(data: SigninRequest): Promise<AuthResponse> {
  const response = await api.post<any>('/api/auth/signin', data, false);
  // Map backend fields to frontend format
  return {
    access_token: response.access_token,
    token_type: response.token_type,
    user: {
      id: String(response.user.id),
      email: response.user.email,
      created_at: response.user.created_at
    }
  };
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
  const response = await api.get<any>('/api/auth/me', true);
  // Map backend fields to frontend format
  return {
    id: String(response.id),
    email: response.email,
    created_at: response.created_at
  };
}

/**
 * Verify JWT token is valid
 */
export async function verifyToken(): Promise<boolean> {
  try {
    await getCurrentUser();
    return true;
  } catch {
    return false;
  }
}
