import { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface ExtractResult {
  task_id: number;
  extracted: {
    customer_name: string | null;
    product_name: string | null;
    vendor_name: string | null;
    amount: number | null;
    sale_date: string | null;
    contract_expiry_date: string | null;
    notes: string | null;
  };
  usage: {
    input_tokens: number;
    output_tokens: number;
    cost_usd: number;
  };
}

export const AITextExtractor: React.FC = () => {
  const [text, setText] = useState('');
  const [sourceDocument, setSourceDocument] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ExtractResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExtract = async () => {
    if (!text.trim()) {
      setError('Incolla del testo da analizzare');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/import/extract-text`, {
        text,
        source_document: sourceDocument || undefined,
      });
      setResult(response.data);
      setText('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Estrazione fallita');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Estrazione con AI</h2>
        <p className="text-gray-600">
          Incolla email, note o qualsiasi testo non strutturato: l'AI estrae cliente,
          prodotto, importo e scadenza per la validazione manuale
        </p>
      </div>

      <div className="space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={loading}
          rows={8}
          placeholder="Es: Abbiamo rinnovato la licenza Fortinet per Acme Corp, 15.000€, scadenza giugno 2026..."
          className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />

        <input
          type="text"
          value={sourceDocument}
          onChange={(e) => setSourceDocument(e.target.value)}
          disabled={loading}
          placeholder="Riferimento documento (opzionale)"
          className="w-full border border-gray-300 rounded-lg p-2 text-sm"
        />

        <button
          onClick={handleExtract}
          disabled={!text.trim() || loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {loading ? 'Estrazione in corso...' : '✨ Estrai con AI'}
        </button>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            ⚠️ {error}
          </div>
        )}

        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-3">
              ✓ Task #{result.task_id} creato — da validare
            </h3>
            <div className="space-y-1 text-sm text-green-800">
              <p><strong>Cliente:</strong> {result.extracted.customer_name || '—'}</p>
              <p><strong>Prodotto:</strong> {result.extracted.product_name || '—'}</p>
              <p><strong>Vendor:</strong> {result.extracted.vendor_name || '—'}</p>
              <p><strong>Importo:</strong> {result.extracted.amount ? `€${result.extracted.amount}` : '—'}</p>
              <p><strong>Data vendita:</strong> {result.extracted.sale_date || '—'}</p>
              <p><strong>Scadenza:</strong> {result.extracted.contract_expiry_date || '—'}</p>
            </div>
            <div className="mt-3 pt-3 border-t border-green-200 text-xs text-green-600">
              Costo: ${result.usage.cost_usd.toFixed(4)} ({result.usage.input_tokens} + {result.usage.output_tokens} token)
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
