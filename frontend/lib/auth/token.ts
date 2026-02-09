/**
 * Token storage utilities for JWT authentication
 */

import Cookies from 'js-cookie';

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

/**
 * Store JWT token in cookie + localStorage
 */
export function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    // Cookie (for middleware)
    Cookies.set(TOKEN_KEY, token, {
      expires: 7,
      sameSite: 'lax',
    });

    // localStorage (for client usage)
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * Retrieve JWT token (cookie first, fallback localStorage)
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return Cookies.get(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Remove JWT token from everywhere
 */
export function removeToken(): void {
  if (typeof window !== 'undefined') {
    Cookies.remove(TOKEN_KEY);
    localStorage.removeItem(TOKEN_KEY);
  }
}

/**
 * Store user data in localStorage
 */
export function setUser(user: any): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

/**
 * Retrieve user data from localStorage
 */
export function getUser(): any | null {
  if (typeof window !== 'undefined') {
    const userData = localStorage.getItem(USER_KEY);
    if (userData) {
      try {
        return JSON.parse(userData);
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * Remove user data
 */
export function removeUser(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * Clear all auth data
 */
export function clearAuth(): void {
  removeToken();
  removeUser();
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

