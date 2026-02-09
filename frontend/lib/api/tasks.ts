/**
 * Task API functions
 */

import { api } from './client';
import { Task } from '@/types/entities';
import { CreateTaskRequest, UpdateTaskRequest, TaskListResponse } from '@/types/api';

/**
 * Get all tasks for the authenticated user
 */
export async function getTasks(): Promise<Task[]> {
  // Backend returns array directly, not wrapped in object
  const response = await api.get<any[]>('/api/todos', true);
  // Map backend fields to frontend format
  return response.map(todo => ({
    id: String(todo.id),
    title: todo.title,
    description: todo.description || '',
    completed: todo.is_completed,
    user_id: String(todo.user_id),
    created_at: todo.created_at,
    updated_at: todo.updated_at
  }));
}

/**
 * Get a single task by ID
 */
export async function getTask(id: string): Promise<Task> {
  const todo = await api.get<any>(`/api/todos/${id}`, true);
  // Map backend fields to frontend format
  return {
    id: String(todo.id),
    title: todo.title,
    description: todo.description || '',
    completed: todo.is_completed,
    user_id: String(todo.user_id),
    created_at: todo.created_at,
    updated_at: todo.updated_at
  };
}

/**
 * Create a new task
 */
export async function createTask(data: CreateTaskRequest): Promise<Task> {
  const todo = await api.post<any>('/api/todos', data, true);
  // Map backend fields to frontend format
  return {
    id: String(todo.id),
    title: todo.title,
    description: todo.description || '',
    completed: todo.is_completed,
    user_id: String(todo.user_id),
    created_at: todo.created_at,
    updated_at: todo.updated_at
  };
}

/**
 * Update an existing task
 */
export async function updateTask(id: string, data: UpdateTaskRequest): Promise<Task> {
  // Map frontend fields to backend format
  const backendData: any = {};
  if (data.title !== undefined) backendData.title = data.title;
  if (data.description !== undefined) backendData.description = data.description;
  if (data.completed !== undefined) backendData.is_completed = data.completed;

  const todo = await api.patch<any>(`/api/todos/${id}`, backendData, true);
  // Map backend fields to frontend format
  return {
    id: String(todo.id),
    title: todo.title,
    description: todo.description || '',
    completed: todo.is_completed,
    user_id: String(todo.user_id),
    created_at: todo.created_at,
    updated_at: todo.updated_at
  };
}

/**
 * Delete a task
 */
export async function deleteTask(id: string): Promise<void> {
  return api.delete<void>(`/api/todos/${id}`, true);
}

/**
 * Toggle task completion status
 */
export async function toggleTaskCompletion(id: string, completed: boolean): Promise<Task> {
  return updateTask(id, { completed });
}
