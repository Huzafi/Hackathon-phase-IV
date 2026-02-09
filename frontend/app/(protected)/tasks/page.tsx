'use client';

/**
 * Tasks page with AI Chat Interface - manage tasks through natural language conversation
 */

import { useState, useEffect } from 'react';
import { getTasks } from '@/lib/api/tasks';
import {
  sendMessage,
  getConversations,
  getConversation,
  deleteConversation,
} from '@/lib/api/chat';
import { Task } from '@/types/entities';
import { Conversation, Message } from '@/types/chat';
import { TaskList } from '@/components/tasks/TaskList';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { ConversationSidebar } from '@/components/chat/ConversationSidebar';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Button } from '@/components/ui/Button';
import { Menu, X, ListTodo, RefreshCw } from 'lucide-react';

export default function TasksPage() {
  // Task state
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [tasksError, setTasksError] = useState<string | null>(null);

  // Conversation state
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  // UI state
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isTaskPanelOpen, setIsTaskPanelOpen] = useState(false);

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      const fetchedTasks = await getTasks();
      setTasks(fetchedTasks);
      setTasksError(null);
    } catch (err: any) {
      setTasksError(err.message || 'Failed to load tasks');
    }
  };

  // Fetch conversations
  const fetchConversations = async () => {
    setIsLoadingConversations(true);
    try {
      const fetchedConversations = await getConversations();

      // Defensive check: ensure we always set an array
      if (Array.isArray(fetchedConversations)) {
        setConversations(fetchedConversations);
      } else {
        console.warn('getConversations did not return an array:', fetchedConversations);
        setConversations([]);
      }
    } catch (err: any) {
      console.error('Failed to load conversations:', err);
      // On error, ensure conversations is still an array
      setConversations([]);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  // Fetch conversation messages
  const fetchConversationMessages = async (conversationId: string) => {
    setIsLoadingMessages(true);
    setChatError(null);
    try {
      const conversation = await getConversation(conversationId);
      setMessages(conversation.messages);
      setActiveConversationId(conversationId);
    } catch (err: any) {
      setChatError(err.message || 'Failed to load conversation');
    } finally {
      setIsLoadingMessages(false);
    }
  };

  // Initial load
  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoadingTasks(true);
      await Promise.all([fetchTasks(), fetchConversations()]);
      setIsLoadingTasks(false);
    };
    loadInitialData();
  }, []);

  // Handle send message
  const handleSendMessage = async (message: string) => {
    setIsSendingMessage(true);
    setChatError(null);

    try {
      const response = await sendMessage(message, activeConversationId || undefined);

      // Add user message
      const userMessage: Message = {
        id: Date.now(), // Temporary ID
        conversation_id: response.conversation_id,
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      };

      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now() + 1, // Temporary ID
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.message,
        tool_calls: response.tool_calls,
        created_at: response.created_at,
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);

      // Update active conversation ID if it's a new conversation
      if (!activeConversationId) {
        setActiveConversationId(response.conversation_id);
      }

      // Refresh conversations list and tasks
      await Promise.all([fetchConversations(), fetchTasks()]);
    } catch (err: any) {
      setChatError(err.message || 'Failed to send message');
    } finally {
      setIsSendingMessage(false);
    }
  };

  // Handle select conversation
  const handleSelectConversation = (conversationId: string) => {
    if (conversationId !== activeConversationId) {
      fetchConversationMessages(conversationId);
    }
  };

  // Handle new conversation
  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
    setChatError(null);
  };

  // Handle delete conversation
  const handleDeleteConversation = async (conversationId: string) => {
    try {
      await deleteConversation(conversationId);

      // If deleted conversation was active, clear it
      if (conversationId === activeConversationId) {
        handleNewConversation();
      }

      // Refresh conversations list
      await fetchConversations();
    } catch (err: any) {
      console.error('Failed to delete conversation:', err);
    }
  };

  // Handle refresh tasks
  const handleRefreshTasks = () => {
    fetchTasks();
  };

  // Initial loading state
  if (isLoadingTasks && conversations.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col lg:flex-row overflow-hidden">
      {/* Mobile Header */}
      <div className="lg:hidden flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
        <button
          onClick={() => setIsSidebarOpen(true)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
          aria-label="Open conversations"
        >
          <Menu className="w-6 h-6" />
        </button>
        <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
          AI Task Assistant
        </h1>
        <button
          onClick={() => setIsTaskPanelOpen(true)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
          aria-label="View tasks"
        >
          <ListTodo className="w-6 h-6" />
        </button>
      </div>

      {/* Conversation Sidebar */}
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        isLoading={isLoadingConversations}
        isMobileOpen={isSidebarOpen}
        onMobileClose={() => setIsSidebarOpen(false)}
      />

      {/* Chat Window (Center) */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Desktop Header */}
        <div className="hidden lg:flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              AI Task Assistant
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Manage your tasks through natural language conversation
            </p>
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <ChatWindow
            conversationId={activeConversationId}
            messages={messages}
            isLoading={isLoadingMessages}
            error={chatError}
            onSendMessage={handleSendMessage}
            isSending={isSendingMessage}
          />
        </div>
      </div>

      {/* Task Panel (Right Side) */}
      <div
        className={`
          fixed lg:relative inset-y-0 right-0 z-50 lg:z-0
          w-80 xl:w-96 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700
          flex flex-col
          transform transition-transform duration-300 ease-in-out
          ${isTaskPanelOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Task Panel Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <ListTodo className="w-5 h-5" />
              Your Tasks
            </h2>
            <div className="flex items-center gap-2">
              <button
                onClick={handleRefreshTasks}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                aria-label="Refresh tasks"
                title="Refresh tasks"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsTaskPanelOpen(false)}
                className="lg:hidden p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                aria-label="Close task panel"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
          </p>
        </div>

        {/* Task List */}
        <div className="flex-1 overflow-y-auto p-4">
          {tasksError ? (
            <ErrorMessage>{tasksError}</ErrorMessage>
          ) : tasks.length === 0 ? (
            <div className="text-center py-8">
              <ListTodo className="w-12 h-12 mx-auto text-gray-400 dark:text-gray-600 mb-3" />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                No tasks yet
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                Ask the AI to create tasks for you
              </p>
            </div>
          ) : (
            <TaskList tasks={tasks} onTasksChange={fetchTasks} />
          )}
        </div>
      </div>

      {/* Mobile Task Panel Overlay */}
      {isTaskPanelOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsTaskPanelOpen(false)}
        />
      )}
    </div>
  );
}
