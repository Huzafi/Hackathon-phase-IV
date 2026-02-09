/**
 * Chat API functions for AI agent interaction
 */

import { api } from './client';
import {
  ChatResponse,
  Conversation,
  ConversationDetail,
  ConversationListResponse,
  SendMessageRequest,
} from '@/types/chat';

/**
 * Send a message to the AI agent
 * Creates a new conversation if conversation_id is not provided
 */
export async function sendMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const payload: SendMessageRequest = {
    message,
  };

  if (conversationId) {
    payload.conversation_id = conversationId;
  }

  return api.post<ChatResponse>('/api/chat', payload, true);
}

/**
 * Get all conversations for the authenticated user
 * Backend returns ConversationListResponse with pagination metadata
 */
export async function getConversations(): Promise<Conversation[]> {
  const response = await api.get<ConversationListResponse>('/api/conversations', true);

  // Extract conversations array from response object
  // Add defensive check to ensure we always return an array
  if (response && Array.isArray(response.conversations)) {
    return response.conversations;
  }

  // Fallback: if response is already an array (shouldn't happen but defensive)
  if (Array.isArray(response)) {
    return response;
  }

  // Last resort: return empty array
  console.warn('Unexpected conversations response format:', response);
  return [];
}

/**
 * Get a single conversation with all messages
 */
export async function getConversation(
  conversationId: string
): Promise<ConversationDetail> {
  return api.get<ConversationDetail>(
    `/api/conversations/${conversationId}`,
    true
  );
}

/**
 * Delete a conversation
 */
export async function deleteConversation(conversationId: string): Promise<void> {
  return api.delete<void>(`/api/conversations/${conversationId}`, true);
}
