'use client';

import { useEffect, useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import { ComplianceItem } from '@/types/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function CompliancePage() {
  const [complianceData, setComplianceData] = useState<ComplianceItem[]>([]);

  // Mock data - in real app, this would come from API
  useEffect(() => {
    const mockData: ComplianceItem[] = [
      { id: '1', title: 'GDPR Compliance', status: 'compliant', category: 'Privacy', last_updated: '2024-01-15' },
      { id: '2', title: 'ISO 27001', status: 'compliant', category: 'Security', last_updated: '2024-01-10' },
      { id: '3', title: 'SOX Compliance', status: 'non-compliant', category: 'Financial', last_updated: '2024-01-12' },
      { id: '4', title: 'HIPAA', status: 'pending', category: 'Healthcare', last_updated: '2024-01-08' },
      { id: '5', title: 'PCI DSS', status: 'compliant', category: 'Payment', last_updated: '2024-01-14' },
    ];
    setComplianceData(mockData);
  }, []);

  const complianceStats = {
    compliant: complianceData.filter(item => item.status === 'compliant').length,
    nonCompliant: complianceData.filter(item => item.status === 'non-compliant').length,
    pending: complianceData.filter(item => item.status === 'pending').length,
  };

  const barData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Compliance Score',
        data: [85, 88, 92, 89, 94, 96],
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
    ],
  };

  const doughnutData = {
    labels: ['Compliant', 'Non-Compliant', 'Pending'],
    datasets: [
      {
        data: [complianceStats.compliant, complianceStats.nonCompliant, complianceStats.pending],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(251, 191, 36, 0.8)',
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(239, 68, 68)',
          'rgb(251, 191, 36)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const lineData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Risk Score',
        data: [65, 59, 80, 81],
        fill: false,
        borderColor: 'rgb(239, 68, 68)',
        tension: 0.1,
      },
    ],
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'text-green-600 bg-green-100';
      case 'non-compliant':
        return 'text-red-600 bg-red-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <MainLayout>
      <div className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="md:flex md:items-center md:justify-between">
            <div className="min-w-0 flex-1">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:truncate sm:text-3xl sm:tracking-tight">
                Compliance Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Monitor compliance status and risk assessments
              </p>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Compliance Overview
              </h3>
              <div className="h-64">
                <Doughnut data={doughnutData} options={{ maintainAspectRatio: false }} />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Compliance Trend
              </h3>
              <div className="h-64">
                <Bar data={barData} options={{ maintainAspectRatio: false }} />
              </div>
            </div>
          </div>

          <div className="mt-8 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Risk Assessment Trend
            </h3>
            <div className="h-64">
              <Line data={lineData} options={{ maintainAspectRatio: false }} />
            </div>
          </div>

          {/* Compliance Items Table */}
          <div className="mt-8">
            <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                  Compliance Items
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                  Detailed status of all compliance requirements.
                </p>
              </div>
              <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                {complianceData.map((item) => (
                  <li key={item.id} className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                            {item.status.replace('-', ' ')}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {item.title}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {item.category} • Last updated {item.last_updated}
                          </div>
                        </div>
                      </div>
                      <div className="ml-2 flex-shrink-0 flex">
                        <button className="text-sm text-primary hover:text-primary/80">
                          View Details
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}