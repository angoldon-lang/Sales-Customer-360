import React, { useState } from 'react';
import { DataQualityTaskList } from '../components/DataQualityTaskList';
import { DataQualityTaskValidator } from '../components/DataQualityTaskValidator';

interface Task {
  id: number;
  customer_id: number;
  task_type: string;
  extracted_customer: string;
  corrected_customer?: string;
  extracted_product?: string;
  corrected_product?: string;
  extracted_vendor?: string;
  corrected_vendor?: string;
  amount?: number;
  sale_date?: string;
  contract_expiry_date?: string;
  status: string;
  validation_notes?: string;
  sales_notes?: string;
  created_at: string;
  source_document?: string;
}

export const DataQuality: React.FC = () => {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTaskSaved = () => {
    setRefreshKey((prev) => prev + 1);
    setSelectedTask(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Data Quality</h1>
          <p className="text-gray-600 mt-2">
            Validate and correct imported customer data before integration
          </p>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Task List */}
          <div className="col-span-2 bg-white rounded-lg shadow">
            <div className="p-6">
              <DataQualityTaskList
                key={refreshKey}
                onSelectTask={(task) => {
                  setSelectedTask(task as Task);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
              />
            </div>
          </div>

          {/* Task Validator */}
          <div className="col-span-1">
            {selectedTask ? (
              <DataQualityTaskValidator
                task={selectedTask}
                onSave={handleTaskSaved}
                onClose={() => setSelectedTask(null)}
              />
            ) : (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-center text-gray-500">
                  <div className="text-4xl mb-4">📋</div>
                  <p>Select a task to validate</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
