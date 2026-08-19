import React, { useState } from 'react';
import { dataQualityAPI } from '../services/api';

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
}

interface DataQualityTaskValidatorProps {
  task: Task | null;
  onSave?: () => void;
  onClose?: () => void;
}

export const DataQualityTaskValidator: React.FC<DataQualityTaskValidatorProps> = ({
  task,
  onSave,
  onClose,
}) => {
  const [formData, setFormData] = useState<Partial<Task>>(task || {});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  if (!task) {
    return null;
  }

  const handleChange = (field: string, value: any) => {
    setFormData({
      ...formData,
      [field]: value,
    });
  };

  const handleStatusChange = async (newStatus: string) => {
    setLoading(true);
    try {
      await dataQualityAPI.updateTask(task.id, {
        status: newStatus,
        corrected_customer: formData.corrected_customer || task.extracted_customer,
        corrected_product: formData.corrected_product || task.extracted_product,
        corrected_vendor: formData.corrected_vendor || task.extracted_vendor,
        validation_notes: formData.validation_notes,
        sales_notes: formData.sales_notes,
      });

      setMessage(`Task updated successfully`);
      setTimeout(() => {
        setMessage('');
        onSave?.();
      }, 1500);
    } catch (error) {
      setMessage('Error saving task');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Validate Task #{task.id}</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-2xl"
        >
          ×
        </button>
      </div>

      {message && (
        <div className="mb-4 p-3 bg-green-100 text-green-800 rounded">
          {message}
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        {/* Customer */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Customer (Extracted)
          </label>
          <div className="p-3 bg-gray-50 rounded text-gray-900">{task.extracted_customer}</div>
          <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">
            Customer (Corrected)
          </label>
          <input
            type="text"
            value={formData.corrected_customer || task.extracted_customer}
            onChange={(e) => handleChange('corrected_customer', e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Product */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product (Extracted)
          </label>
          <div className="p-3 bg-gray-50 rounded text-gray-900">
            {task.extracted_product || '—'}
          </div>
          <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">
            Product (Corrected)
          </label>
          <input
            type="text"
            value={formData.corrected_product || task.extracted_product || ''}
            onChange={(e) => handleChange('corrected_product', e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Vendor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Vendor (Extracted)
          </label>
          <div className="p-3 bg-gray-50 rounded text-gray-900">
            {task.extracted_vendor || '—'}
          </div>
          <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">
            Vendor (Corrected)
          </label>
          <input
            type="text"
            value={formData.corrected_vendor || task.extracted_vendor || ''}
            onChange={(e) => handleChange('corrected_vendor', e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Amount */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Amount (€)
          </label>
          <div className="p-3 bg-gray-50 rounded text-gray-900">
            {task.amount ? `€${task.amount.toLocaleString()}` : '—'}
          </div>
        </div>

        {/* Sale Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sale Date
          </label>
          <div className="p-3 bg-gray-50 rounded text-gray-900">
            {task.sale_date ? new Date(task.sale_date).toLocaleDateString() : '—'}
          </div>
        </div>

        {/* Contract Expiry */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Contract Expiry
          </label>
          <div className="p-3 bg-gray-50 rounded text-gray-900">
            {task.contract_expiry_date
              ? new Date(task.contract_expiry_date).toLocaleDateString()
              : '—'}
          </div>
        </div>
      </div>

      {/* Notes */}
      <div className="mt-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Validation Notes
        </label>
        <textarea
          value={formData.validation_notes || ''}
          onChange={(e) => handleChange('validation_notes', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Add notes about the validation"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">
          Sales Notes
        </label>
        <textarea
          value={formData.sales_notes || ''}
          onChange={(e) => handleChange('sales_notes', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Sales feedback"
        />
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex gap-3 justify-end">
        <button
          onClick={() => handleStatusChange('discarded')}
          disabled={loading}
          className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 disabled:opacity-50"
        >
          Discard
        </button>
        <button
          onClick={() => handleStatusChange('doubtful')}
          disabled={loading}
          className="px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 disabled:opacity-50"
        >
          Mark Doubtful
        </button>
        <button
          onClick={() => handleStatusChange('validated')}
          disabled={loading}
          className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 disabled:opacity-50 font-medium"
        >
          Validate
        </button>
      </div>
    </div>
  );
};
