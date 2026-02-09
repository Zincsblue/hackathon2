'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import TaskForm from '@/components/tasks/TaskForm';
import { Task } from '@/lib/types';

export default function EditTaskPage() {
  const params = useParams();
  const taskId = params.id as string;
  const { accessToken } = useAuth();
  const [task, setTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (accessToken) {
      fetchTask();
    }
  }, [taskId, accessToken]);

  const fetchTask = async () => {
    if (!accessToken) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/tasks/${taskId}`, {
        credentials: 'include',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch task');
      }

      const data = await response.json();
      setTask(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load task');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (data: { title: string; description?: string; completed?: boolean }) => {
    if (!accessToken) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/tasks/${taskId}`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update task');
    }

    return response.json();
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg">
          {error || 'Task not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Edit Task</h2>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Update your task details
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 transition-colors">
        <TaskForm task={task} onSubmit={handleSubmit} submitLabel="Update Task" />
      </div>
    </div>
  );
}
