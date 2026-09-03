import { useEffect, useRef, useState, useCallback } from 'react';

export function useWebSocket(url, onMessage) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('[WS] Connected to notification feed');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (onMessage) {
            onMessage(data);
          }
        } catch (e) {
          console.error('[WS] Failed to parse message JSON', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('[WS] Connection closed. Reconnecting in 3s...');
        setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.error('[WS] Connection error', err);
        ws.close();
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('[WS] Initialization failed', err);
      setTimeout(connect, 3000);
    }
  }, [url, onMessage]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected };
}
