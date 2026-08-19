import React, { useState, useEffect } from 'react';
import { dataQualityAPI } from '../services/api';

interface Task {
  id: number;
  customer_id: number;
  task_type: string;
  extracted_customer: string;
  corrected_customer?: string;
  extracted_product?: string;
  corrected_product?: string;
  amount?: number;
  sale_date?: string;
  status: string;
  created_at: string;
  source_document?: string;
}

interface DataQualityTaskListProps {
  onSelectTask?: (task: Task) => void;
  status?: string;
}

export const DataQualityTaskList: React.FC<DataQualityTaskListProps> = ({ onSelectTask, status }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [selectedStatus, setSelectedStatus] = useState(status || 'to_validate');
  const [skip, setSkip] = useState(0);
  const limit = 20;

  useEffect(() => {
    loadTasks();
    loadStats();
  }, [selectedStatus, skip]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await dataQualityAPI.getTasks(selectedStatus, undefined, skip, limit);
      setTasks(response.data.tasks);
    } catch (error) {
      console.error('Error loading tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await dataQualityAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'to_validate':
        return 'bg-yellow-100 text-yellow-800';
      case 'validated':
        return 'bg-green-100 text-green-800';
      case 'doubtful':
        return 'bg-orange-100 text-orange-800';
      case 'discarded':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="w-full">
      {/* Stats Header */}
      {stats && (
        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-gray-600">Total Tasks</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">{stats.to_validate}</div>
            <div className="text-sm text-gray-600">To Validate</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{stats.validated}</div>
            <div className="text-sm text-gray-600">Validated</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{stats.doubtful}</div>
            <div className="text-sm text-gray-600">Doubtful</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{stats.validation_rate}%</div>
            <div className="text-sm text-gray-600">Validation Rate</div>
          </div>
        </div>
      )}

      {/* Status Filter */}
      <div className="mb-4 flex gap-2 border-b">
        {['to_validate', 'validated', 'doubtful', 'discarded'].map((s) => (
          <button
            key={s}
            onClick={() => {
              setSelectedStatus(s);
              setSkip(0);
            }}
            className={`px-4 py-2 font-medium ${
              selectedStatus === s
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {s === 'to_validate'
              ? 'To Validate'
              : s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="space-y-2">
        {loading ? (
          <div className="text-center py-8">Loading tasks...</div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No tasks found</div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              onClick={() => onSelectTask?.(task)}
              className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">
                    {task.corrected_customer || task.extracted_customer}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Product: {task.corrected_product || task.extracted_product || '—'}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    Created: {new Date(task.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div className="text-right">
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                      task.status
                    )}`}
                  >
                    {task.status === 'to_validate' ? 'To Validate' : task.status}
                  </span>
                  {task.amount && (
                    <div className="text-lg font-semibold text-gray-900 mt-2">
                      €{task.amount.toLocaleString()}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      <div className="mt-4 flex justify-between items-center">
        <button
          disabled={skip === 0}
          onClick={() => setSkip(Math.max(0, skip - limit))}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Previous
        </button>
        <span className="text-gray-600">
          Showing {skip + 1} to {skip + tasks.length}
        </span>
        <button
          disabled={tasks.length < limit}
          onClick={() => setSkip(skip + limit)}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
};
