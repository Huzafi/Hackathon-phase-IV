'use client';

/**
 * ChatMessage component - displays individual chat messages
 */

import { Message } from '@/types/chat';
import { formatDistanceToNow } from 'date-fns';
import { User, Bot, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [showToolCalls, setShowToolCalls] = useState(false);
  const isUser = message.role === 'user';

  const formattedTime = formatDistanceToNow(new Date(message.created_at), {
    addSuffix: true,
  });

  return (
    <div
      className={`flex gap-3 mb-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Timestamp */}
        <p
          className={`text-xs text-gray-500 dark:text-gray-400 mt-1 ${
            isUser ? 'text-right' : 'text-left'
          }`}
        >
          {formattedTime}
        </p>

        {/* Tool Calls (if present) */}
        {message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-2">
            <button
              onClick={() => setShowToolCalls(!showToolCalls)}
              className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
            >
              {showToolCalls ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
              <span>
                {message.tool_calls.length} tool call
                {message.tool_calls.length > 1 ? 's' : ''}
              </span>
            </button>

            {showToolCalls && (
              <div className="mt-2 space-y-2">
                {message.tool_calls.map((toolCall) => (
                  <div
                    key={toolCall.id}
                    className="bg-gray-50 dark:bg-gray-900 rounded p-2 text-xs"
                  >
                    <div className="font-semibold text-gray-700 dark:text-gray-300 mb-1">
                      {toolCall.name}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400">
                      <div className="mb-1">
                        <span className="font-medium">Arguments:</span>
                        <pre className="mt-1 overflow-x-auto">
                          {JSON.stringify(toolCall.arguments, null, 2)}
                        </pre>
                      </div>
                      {toolCall.result && (
                        <div>
                          <span className="font-medium">Result:</span>
                          <pre className="mt-1 overflow-x-auto">
                            {JSON.stringify(toolCall.result, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
