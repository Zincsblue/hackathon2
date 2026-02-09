'use client';

import { useState, FormEvent } from 'react';
import { Task } from '@/lib/types';
import { useRouter } from 'next/navigation';

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: { title: string; description?: string; completed?: boolean }) => Promise<void>;
  submitLabel?: string;
}

export default function TaskForm({ task, onSubmit, submitLabel = 'Save Task' }: TaskFormProps) {
  const router = useRouter();
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [completed, setCompleted] = useState(task?.completed || false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (title.length > 200) {
      setError('Title must be 200 characters or less');
      return;
    }

    if (description.length > 1000) {
      setError('Description must be 1000 characters or less');
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        completed: task ? completed : undefined,
      });
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to save task');
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Title Field */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-200">
          Title *
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="Enter task title"
          maxLength={200}
          required
          disabled={isSubmitting}
        />
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{title.length}/200 characters</p>
      </div>

      {/* Description Field */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-200">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="Enter task description (optional)"
          rows={4}
          maxLength={1000}
          disabled={isSubmitting}
        />
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{description.length}/1000 characters</p>
      </div>

      {/* Completed Checkbox (only for edit) */}
      {task && (
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="completed"
            checked={completed}
            onChange={(e) => setCompleted(e.target.checked)}
            className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
            disabled={isSubmitting}
          />
          <label htmlFor="completed" className="text-sm font-medium text-gray-900 dark:text-gray-200">
            Mark as completed
          </label>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>
        <button
          type="button"
          onClick={() => router.push('/dashboard')}
          disabled={isSubmitting}
          className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium disabled:opacity-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
