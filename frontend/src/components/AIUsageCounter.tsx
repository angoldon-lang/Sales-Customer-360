import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface UsageBucket {
  cost_usd: number;
  requests: number;
  input_tokens: number;
  output_tokens: number;
}

interface UsageStats {
  today: UsageBucket;
  this_month: UsageBucket;
  all_time: UsageBucket;
}

const POLL_INTERVAL_MS = 10000;

export const AIUsageCounter: React.FC = () => {
  const [stats, setStats] = useState<UsageStats | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const response = await axios.get(`${API_URL}/import/ai-usage/stats`);
        if (!cancelled) {
          setStats(response.data);
          setError(false);
        }
      } catch {
        if (!cancelled) setError(true);
      }
    };

    load();
    const interval = setInterval(load, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  if (error) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-500">
        Costi AI non disponibili
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-500">
        Caricamento costi AI...
      </div>
    );
  }

  const formatCost = (value: number) =>
    value < 0.01 && value > 0 ? '<$0.01' : `$${value.toFixed(2)}`;

  return (
    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-900">💰 Costo Estrazione AI</h3>
        <span className="text-xs text-gray-400">aggiornato ogni 10s</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <div className="text-xl font-bold text-blue-600">{formatCost(stats.today.cost_usd)}</div>
          <div className="text-xs text-gray-500">Oggi ({stats.today.requests} richieste)</div>
        </div>
        <div>
          <div className="text-xl font-bold text-blue-600">{formatCost(stats.this_month.cost_usd)}</div>
          <div className="text-xs text-gray-500">Questo mese ({stats.this_month.requests} richieste)</div>
        </div>
        <div>
          <div className="text-xl font-bold text-gray-700">{formatCost(stats.all_time.cost_usd)}</div>
          <div className="text-xs text-gray-500">Totale ({stats.all_time.requests} richieste)</div>
        </div>
      </div>
    </div>
  );
};
