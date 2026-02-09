'use client';

/**
 * Authentication Context Provider
 */

import React, { createContext, useState, useEffect, useCallback } from 'react';
import { User } from '@/types/entities';
import { signin as apiSignin, signup as apiSignup, getCurrentUser } from '../api/auth';
import { setToken, setUser, getToken, getUser, clearAuth } from './token';

/**
 * Auth context type
 */
export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  signout: () => void;
  refreshUser: () => Promise<void>;
}

/**
 * Create auth context
 */
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Auth provider props
 */
interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * Auth provider component
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUserState] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Initialize auth state from localStorage
   */
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = getToken();
      const storedUser = getUser();

      if (storedToken && storedUser) {
        setTokenState(storedToken);
        setUserState(storedUser);

        // Verify token is still valid
        try {
          const currentUser = await getCurrentUser();
          setUserState(currentUser);
          setUser(currentUser);
        } catch {
          // Token is invalid, clear auth
          clearAuth();
          setTokenState(null);
          setUserState(null);
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, []);

  /**
   * Sign in user
   */
  const signin = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await apiSignin({ email, password });
      setToken(response.access_token);
      setUser(response.user);
      setTokenState(response.access_token);
      setUserState(response.user);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Sign up new user
   */
  const signup = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await apiSignup({ email, password });
      setToken(response.access_token);
      setUser(response.user);
      setTokenState(response.access_token);
      setUserState(response.user);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Sign out user
   */
  const signout = useCallback(() => {
    clearAuth();
    setTokenState(null);
    setUserState(null);
  }, []);

  /**
   * Refresh user data
   */
  const refreshUser = useCallback(async () => {
    if (token) {
      try {
        const currentUser = await getCurrentUser();
        setUserState(currentUser);
        setUser(currentUser);
      } catch {
        // Token is invalid, clear auth
        signout();
      }
    }
  }, [token, signout]);

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    signin,
    signup,
    signout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
