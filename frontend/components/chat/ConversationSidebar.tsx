'use client';

/**
 * ConversationSidebar component - lists user's conversations
 */

import { useState } from 'react';
import { Conversation } from '@/types/chat';
import { formatDistanceToNow } from 'date-fns';
import {
  MessageSquare,
  Plus,
  Trash2,
  X,
  Menu,
  ChevronLeft,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface ConversationSidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (conversationId: string) => void;
  isLoading?: boolean;
  isMobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  isLoading = false,
  isMobileOpen = false,
  onMobileClose,
}: ConversationSidebarProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Defensive check: ensure conversations is always an array
  const safeConversations = Array.isArray(conversations) ? conversations : [];

  const handleDelete = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();

    if (deletingId === conversationId) {
      // Confirm delete
      onDeleteConversation(conversationId);
      setDeletingId(null);
    } else {
      // First click - show confirmation
      setDeletingId(conversationId);
      // Auto-cancel after 3 seconds
      setTimeout(() => setDeletingId(null), 3000);
    }
  };

  const handleSelectConversation = (conversationId: string) => {
    onSelectConversation(conversationId);
    if (onMobileClose) {
      onMobileClose();
    }
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onMobileClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed lg:relative inset-y-0 left-0 z-50 lg:z-0
          w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700
          flex flex-col
          transform transition-transform duration-300 ease-in-out
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Conversations
            </h2>
            {onMobileClose && (
              <button
                onClick={onMobileClose}
                className="lg:hidden p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                aria-label="Close sidebar"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
          <Button
            onClick={onNewConversation}
            fullWidth
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Conversation
          </Button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              Loading conversations...
            </div>
          ) : safeConversations.length === 0 ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Start a new conversation to get started</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {safeConversations.map((conversation) => {
                const isActive = conversation.id === activeConversationId;
                const isDeleting = deletingId === conversation.id;

                return (
                  <div
                    key={conversation.id}
                    onClick={() => handleSelectConversation(conversation.id)}
                    className={`
                      p-4 cursor-pointer transition-colors
                      ${
                        isActive
                          ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-600'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-800 border-l-4 border-transparent'
                      }
                    `}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {conversation.title || 'New Conversation'}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {formatDistanceToNow(new Date(conversation.updated_at), {
                            addSuffix: true,
                          })}
                        </p>
                        {conversation.message_count !== undefined && (
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            {conversation.message_count} message
                            {conversation.message_count !== 1 ? 's' : ''}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={(e) => handleDelete(conversation.id, e)}
                        className={`
                          p-1 rounded transition-colors flex-shrink-0
                          ${
                            isDeleting
                              ? 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-400'
                              : 'hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-400 dark:text-gray-500'
                          }
                        `}
                        aria-label={isDeleting ? 'Click again to confirm delete' : 'Delete conversation'}
                        title={isDeleting ? 'Click again to confirm' : 'Delete'}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    {isDeleting && (
                      <p className="text-xs text-red-600 dark:text-red-400 mt-2">
                        Click again to confirm delete
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
