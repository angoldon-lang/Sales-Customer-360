import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface ImportResult {
  created_tasks: number;
  total_rows_processed: number;
  errors: string[];
}

export const DataImporter: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid CSV file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('No file selected');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/import/csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
      setFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = () => {
    const csv = `customer_name,product,vendor,amount,sale_date,contract_expiry,source_document
Acme Corp,Fortinet Firewall,Fortinet,15000,2023-06-15,2026-06-15,Invoice-001
Tech Solutions,Microsoft 365,Microsoft,8500,2023-09-20,2025-09-20,Invoice-002`;

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'import_template.csv';
    a.click();
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Import Data</h2>
        <p className="text-gray-600">Upload CSV file to create data quality tasks</p>
      </div>

      <div className="space-y-4">
        {/* Template Download */}
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <p className="text-sm text-gray-700 mb-3">
            Download the CSV template to see the expected format:
          </p>
          <button
            onClick={downloadTemplate}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm"
          >
            📥 Download Template
          </button>
        </div>

        {/* File Upload */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={loading}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
          {file && (
            <p className="mt-2 text-sm text-green-600 font-medium">✓ {file.name} selected</p>
          )}
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {loading ? 'Uploading...' : 'Upload CSV'}
        </button>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            ⚠️ {error}
          </div>
        )}

        {/* Success Result */}
        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-3">✓ Import Successful</h3>
            <div className="space-y-2 text-sm text-green-700">
              <p>
                <strong>Created Tasks:</strong> {result.created_tasks}
              </p>
              <p>
                <strong>Rows Processed:</strong> {result.total_rows_processed}
              </p>
              {result.errors.length > 0 && (
                <div className="mt-3 pt-3 border-t border-green-200">
                  <p className="font-medium text-yellow-700 mb-2">Errors ({result.errors.length}):</p>
                  <ul className="space-y-1 text-yellow-600 text-xs">
                    {result.errors.slice(0, 5).map((err, idx) => (
                      <li key={idx}>• {err}</li>
                    ))}
                    {result.errors.length > 5 && (
                      <li>... and {result.errors.length - 5} more</li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* CSV Format Guide */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm font-medium text-gray-900 mb-2">CSV Format:</p>
          <div className="text-xs text-gray-600 font-mono bg-white p-2 rounded border overflow-x-auto">
            customer_name, product, vendor, amount, sale_date, contract_expiry, source_document
          </div>
          <ul className="mt-2 text-xs text-gray-600 space-y-1">
            <li>• <strong>customer_name</strong>: Required</li>
            <li>• <strong>product</strong>: Required</li>
            <li>• <strong>sale_date</strong>: Format YYYY-MM-DD</li>
            <li>• <strong>contract_expiry</strong>: Format YYYY-MM-DD (optional)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
