'use client';

import { useAuth } from '@/contexts/AuthContext';
import TaskForm from '@/components/tasks/TaskForm';

export default function NewTaskPage() {
  const { accessToken } = useAuth();

  const handleSubmit = async (data: { title: string; description?: string }) => {
    if (!accessToken) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/tasks`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create task');
    }

    return response.json();
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Create New Task</h2>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Add a new task to your todo list
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 transition-colors">
        <TaskForm onSubmit={handleSubmit} submitLabel="Create Task" />
      </div>
    </div>
  );
}
