import React, { useState, useEffect } from 'react';
import { DataImporter } from '../components/DataImporter';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface ImportStats {
  total_tasks: number;
  imported_from_csv: number;
  awaiting_customer_assignment: number;
}

export const DataImport: React.FC = () => {
  const [stats, setStats] = useState<ImportStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/import/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Data Import</h1>
          <p className="text-gray-600 mt-2">
            Import customer data from CSV files and automatically create data quality tasks
          </p>
        </div>

        {/* Stats */}
        {stats && !loading && (
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-3xl font-bold text-blue-600">{stats.total_tasks}</div>
              <div className="text-sm text-gray-600">Total Tasks</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-3xl font-bold text-green-600">{stats.imported_from_csv}</div>
              <div className="text-sm text-gray-600">From CSV Import</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-3xl font-bold text-orange-600">
                {stats.awaiting_customer_assignment}
              </div>
              <div className="text-sm text-gray-600">Awaiting Customer Assignment</div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-2 gap-6">
          {/* Importer */}
          <div>
            <DataImporter />
          </div>

          {/* Info */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">How It Works</h3>
              <ol className="space-y-3 text-sm text-gray-600">
                <li className="flex gap-3">
                  <span className="font-bold text-blue-600">1</span>
                  <span>Download the CSV template from the import panel</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-blue-600">2</span>
                  <span>Fill in your sales data with products, vendors, amounts, and dates</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-blue-600">3</span>
                  <span>Upload the CSV file to create data quality tasks</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-blue-600">4</span>
                  <span>Validate and correct the data in the Data Quality section</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-blue-600">5</span>
                  <span>Link tasks to customers and convert to contracts/opportunities</span>
                </li>
              </ol>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">CSV Format</h3>
              <div className="bg-gray-50 p-3 rounded text-xs font-mono overflow-x-auto mb-4">
                customer_name,product,vendor,amount,sale_date,contract_expiry,source_document
              </div>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-900">customer_name</span>
                  <p className="text-gray-600">Customer name (required)</p>
                </div>
                <div>
                  <span className="font-medium text-gray-900">product</span>
                  <p className="text-gray-600">Product/license name (required)</p>
                </div>
                <div>
                  <span className="font-medium text-gray-900">vendor</span>
                  <p className="text-gray-600">Vendor/manufacturer</p>
                </div>
                <div>
                  <span className="font-medium text-gray-900">amount</span>
                  <p className="text-gray-600">Sale amount in €</p>
                </div>
                <div>
                  <span className="font-medium text-gray-900">sale_date</span>
                  <p className="text-gray-600">Date in format YYYY-MM-DD</p>
                </div>
                <div>
                  <span className="font-medium text-gray-900">contract_expiry</span>
                  <p className="text-gray-600">Expiry date in format YYYY-MM-DD (optional)</p>
                </div>
                <div>
                  <span className="font-medium text-gray-900">source_document</span>
                  <p className="text-gray-600">Document reference (invoice, PO, etc.)</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
