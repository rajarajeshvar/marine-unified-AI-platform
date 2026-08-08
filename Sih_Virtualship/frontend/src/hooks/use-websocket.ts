import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  url?: string;
  reconnectAttempts?: number;
  reconnectInterval?: number; // base interval in ms
  heartbeatInterval?: number; // ms to expect server message
}

export function useWebSocket<T>(options: UseWebSocketOptions = {}) {
  const {
    url = process.env.NEXT_PUBLIC_WS_URL || 'ws://127.0.0.1:8000/ws',
    reconnectAttempts = 10,
    reconnectInterval = 2000,
    heartbeatInterval = 15000,
  } = options;

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastMessage, setLastMessage] = useState<T | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef<number>(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimerRef = useRef<NodeJS.Timeout | null>(null);

  const resetHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearTimeout(heartbeatTimerRef.current);
    }
    
    // Setup a watchdog. If no message received within heartbeatInterval, assume connection lost
    heartbeatTimerRef.current = setTimeout(() => {
      console.warn('WebSocket watchdog timed out. Closing connection to trigger reconnect.');
      if (wsRef.current) {
        wsRef.current.close();
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  const connect = useCallback(() => {
    // Prevent duplicate connection attempts
    if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
      return;
    }

    // Cancel existing reconnect timers
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }

    try {
      console.log(`Connecting to WebSocket: ${url}`);
      const socket = new WebSocket(url);
      wsRef.current = socket;

      socket.onopen = () => {
        console.log('WebSocket connection successfully established.');
        setIsConnected(true);
        reconnectCountRef.current = 0; // reset attempts
        resetHeartbeat();
      };

      socket.onmessage = (event) => {
        resetHeartbeat();
        try {
          const parsed = JSON.parse(event.data);
          setLastMessage(parsed);
        } catch (err) {
          console.error('Failed to parse WebSocket message data:', err);
        }
      };

      socket.onclose = (event) => {
        setIsConnected(false);
        if (heartbeatTimerRef.current) clearTimeout(heartbeatTimerRef.current);
        
        // Trigger reconnect unless closed intentionally
        if (reconnectCountRef.current < reconnectAttempts) {
          const delay = reconnectInterval * Math.pow(1.5, reconnectCountRef.current);
          console.warn(`WebSocket closed: ${event.reason || 'No reason'}. Reconnecting in ${delay.toFixed(0)}ms... (Attempt ${reconnectCountRef.current + 1}/${reconnectAttempts})`);
          
          reconnectTimerRef.current = setTimeout(() => {
            reconnectCountRef.current += 1;
            connect();
          }, delay);
        } else {
          console.error('WebSocket connection failed: Max reconnect attempts reached.');
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket encountered an error:', error);
        // Onerror triggers close, which will trigger the reconnect logic
      };

    } catch (err) {
      console.error('Failed to construct WebSocket client:', err);
    }
  }, [url, reconnectAttempts, reconnectInterval, resetHeartbeat]);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    if (heartbeatTimerRef.current) clearTimeout(heartbeatTimerRef.current);
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    reconnect: connect,
    disconnect,
  };
}
