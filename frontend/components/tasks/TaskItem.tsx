'use client';

import { useState } from 'react';
import { Task } from '@/lib/types';
import Link from 'next/link';

interface TaskItemProps {
  task: Task;
  onUpdate: (taskId: string, updates: Partial<Task>) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const handleToggleComplete = async () => {
    setIsToggling(true);
    try {
      await onUpdate(task.id, { completed: !task.completed });
    } catch (error) {
      console.error('Failed to toggle task:', error);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } catch (error) {
      console.error('Failed to delete task:', error);
      setIsDeleting(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6 border-l-4 border-blue-600 transition-colors">
      <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
        <div className="flex items-start gap-3 sm:gap-4 flex-1 w-full">
          {/* Checkbox - touch-friendly on mobile */}
          <button
            onClick={handleToggleComplete}
            disabled={isToggling}
            className="mt-1 flex-shrink-0 touch-manipulation"
            aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            <div className={`w-6 h-6 sm:w-6 sm:h-6 rounded border-2 flex items-center justify-center transition-colors ${
              task.completed
                ? 'bg-green-500 border-green-500'
                : 'border-gray-300 dark:border-gray-600 hover:border-green-500'
            } ${isToggling ? 'opacity-50' : ''}`}>
              {task.completed && (
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </button>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            <h3 className={`text-base sm:text-lg font-semibold mb-1 break-words ${task.completed ? 'line-through' : ''}`} style={{ color: task.completed ? '#6b7280' : undefined }} className={`text-base sm:text-lg font-semibold mb-1 break-words ${task.completed ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'}`}>
              {task.title}
            </h3>
            {task.description && (
              <p className={`text-sm break-words ${task.completed ? 'text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-300'}`}>
                {task.description}
              </p>
            )}
            <p className="text-xs mt-2 text-gray-500 dark:text-gray-400">
              Created {new Date(task.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Action Buttons - stack on mobile, inline on desktop */}
        <div className="flex items-center gap-2 w-full sm:w-auto sm:flex-shrink-0">
          <Link
            href={`/dashboard/tasks/${task.id}`}
            className="flex-1 sm:flex-none text-center px-4 py-2 sm:px-3 sm:py-2 text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors touch-manipulation min-h-[44px] sm:min-h-0 flex items-center justify-center"
          >
            Edit
          </Link>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="flex-1 sm:flex-none px-4 py-2 sm:px-3 sm:py-2 text-sm bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors disabled:opacity-50 touch-manipulation min-h-[44px] sm:min-h-0"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}
