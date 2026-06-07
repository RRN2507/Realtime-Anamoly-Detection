import { useState, useEffect } from 'react';
import { getMetrics } from '../api/client';

export const useMetrics = (interval = 2000) => {
  const [metrics, setMetrics] = useState({ throughput: 0, latency_ms: 0 });
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await getMetrics();
        setMetrics(data);
        setHistory(prev => [...prev.slice(-19), {
          time: new Date().toLocaleTimeString(),
          value: data.throughput
        }]);
      } catch (err) {
        console.error('Failed to fetch metrics:', err);
      }
    };

    fetchMetrics();
    const id = setInterval(fetchMetrics, interval);
    return () => clearInterval(id);
  }, [interval]);

  return { metrics, history };
};
