import { useState, useEffect } from 'react';

export const useAlerts = () => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/alerts`;
    
    let ws;
    const connect = () => {
      ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'anomaly') {
          setAlerts(prev => [msg.data, ...prev.slice(0, 49)]);
        }
      };

      ws.onclose = () => {
        setTimeout(connect, 3000);
      };
    };

    connect();
    return () => {
      if (ws) ws.close();
    };
  }, []);

  return alerts;
};
