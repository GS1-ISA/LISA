'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { apiClient } from '@/lib/api';
import { ResearchResponse } from '@/types/api';
import { DocumentTextIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const researchSchema = z.object({
  query: z.string().min(10, 'Query must be at least 10 characters long'),
});

type ResearchForm = z.infer<typeof researchSchema>;

export default function ResearchPage() {
  const [results, setResults] = useState<ResearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ResearchForm>({
    resolver: zodResolver(researchSchema),
  });

  const researchMutation = useMutation({
    mutationFn: (query: string) => apiClient.research(query),
    onSuccess: (data) => {
      setResults(data);
      toast.success('Research completed successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Research failed');
    },
  });

  const onSubmit = async (data: ResearchForm) => {
    setIsLoading(true);
    try {
      await researchMutation.mutateAsync(data.query);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = () => {
    if (!results) return;

    const blob = new Blob([results.result_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-${results.query.replace(/\s+/g, '-').toLowerCase()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Report exported successfully!');
  };

  return (
    <MainLayout>
      <div className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="md:flex md:items-center md:justify-between">
            <div className="min-w-0 flex-1">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:truncate sm:text-3xl sm:tracking-tight">
                Research Interface
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Submit research queries to our AI-powered research system
              </p>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Query Form */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
                  Submit Research Query
                </h3>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div>
                    <label htmlFor="query" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Research Query
                    </label>
                    <textarea
                      {...register('query')}
                      id="query"
                      rows={6}
                      className="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Enter your research question here. Be specific and detailed for better results..."
                    />
                    {errors.query && (
                      <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                        {errors.query.message}
                      </p>
                    )}
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={isLoading || researchMutation.isPending}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <PaperAirplaneIcon className="h-4 w-4 mr-2" />
                      {isLoading || researchMutation.isPending ? 'Researching...' : 'Submit Query'}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Results */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                    Research Results
                  </h3>
                  {results && (
                    <button
                      onClick={handleExport}
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                    >
                      <DocumentTextIcon className="h-4 w-4 mr-1" />
                      Export
                    </button>
                  )}
                </div>

                {results ? (
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        Query
                      </h4>
                      <p className="mt-1 text-sm text-gray-900 dark:text-white">
                        {results.query}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                        Results
                      </h4>
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-4 max-h-96 overflow-y-auto">
                        <pre className="text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                          {results.result_markdown}
                        </pre>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                      No results yet
                    </h3>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      Submit a research query to see results here.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Recent Queries */}
          <div className="mt-8">
            <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                  Recent Queries
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                  Your previous research queries and their status.
                </p>
              </div>
              <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                {/* Placeholder for recent queries - would be populated from API */}
                <li className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                          <DocumentTextIcon className="h-4 w-4 text-green-600" />
                        </div>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          Analysis of regulatory compliance frameworks
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Completed 2 hours ago
                        </p>
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}