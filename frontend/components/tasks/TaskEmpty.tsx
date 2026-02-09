'use client';

import Link from 'next/link';

export default function TaskEmpty() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center transition-colors">
      <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
        <svg className="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <h3 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">
        No Tasks Yet
      </h3>
      <p className="mb-6 text-gray-600 dark:text-gray-400">
        Get started by creating your first task!
      </p>
      <Link
        href="/dashboard/tasks/new"
        className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
      >
        Create Your First Task
      </Link>
    </div>
  );
}
