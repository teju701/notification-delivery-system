import React, { useState, useEffect, useCallback } from 'react';
import { Zap, Send, RefreshCw, Key } from 'lucide-react';
import { useWebSocket } from './hooks/useWebSocket';
import MetricsBar from './components/MetricsBar';
import NotificationTable from './components/NotificationTable';
import SendNotificationModal from './components/SendNotificationModal';

const API_BASE_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws/notifications';

export default function App() {
  const [apiKey, setApiKey] = useState(localStorage.getItem('NDS_API_KEY') || 'nds_demo_key_12345');
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  // Save API key locally
  const handleApiKeyChange = (val) => {
    setApiKey(val);
    localStorage.setItem('NDS_API_KEY', val);
  };

  // Handle incoming real-time WebSocket events
  const handleWsMessage = useCallback((event) => {
    if (event.type === 'NOTIFICATION_STATUS_UPDATE') {
      setNotifications((prev) => {
        const index = prev.findIndex((n) => n.id === event.notification_id);
        if (index !== -1) {
          const updated = [...prev];
          updated[index] = {
            ...updated[index],
            status: event.status,
            attempt_count: event.attempt_count,
            updated_at: event.updated_at
          };
          return updated;
        } else {
          // New notification pushed via WebSocket
          return [
            {
              id: event.notification_id,
              tenant_id: event.tenant_id,
              recipient: event.recipient,
              channel: event.channel,
              status: event.status,
              attempt_count: event.attempt_count,
              max_attempts: 3,
              idempotency_key: 'realtime-push',
              created_at: event.created_at,
              updated_at: event.updated_at,
              delivery_attempts: []
            },
            ...prev
          ];
        }
      });
    }
  }, []);

  const { isConnected } = useWebSocket(WS_URL, handleWsMessage);

  // Fetch initial notifications list for tenant
  const fetchNotifications = useCallback(async () => {
    if (!apiKey) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/notifications`, {
        headers: { 'X-API-Key': apiKey }
      });
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.items || []);
      }
    } catch (e) {
      console.error('Failed to fetch notifications list', e);
    } finally {
      setLoading(false);
    }
  }, [apiKey]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  // Dispatch new notification request via API
  const handleSendNotification = async (payload) => {
    const res = await fetch(`${API_BASE_URL}/api/v1/notifications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey
      },
      body: JSON.stringify(payload)
    });

    if (res.status === 429) {
      const retryAfter = res.headers.get('Retry-After') || '1';
      throw new Error(`HTTP 429 Too Many Requests (Token Bucket Rate Limit Exceeded). Retry after ${retryAfter}s`);
    }

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Failed to dispatch request');
    }

    const data = await res.json();
    
    // Optimistic UI update or refresh
    fetchNotifications();
    return data;
  };

  return (
    <div className="container">
      <header>
        <div className="logo-group">
          <div className="logo-icon">
            <Zap size={22} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
              Notification Engine
            </h1>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Async • Idempotent • Rate Limited
            </span>
          </div>
        </div>

        <div className="header-actions">
          <div className="ws-status-pill">
            <div className={`ws-dot ${isConnected ? 'connected' : 'disconnected'}`} />
            {isConnected ? 'Live WebSocket Connected' : 'Reconnecting...'}
          </div>

          <div className="api-key-input-group">
            <Key size={15} color="var(--text-muted)" style={{ marginRight: '0.4rem' }} />
            <input
              type="password"
              placeholder="X-API-Key"
              value={apiKey}
              onChange={(e) => handleApiKeyChange(e.target.value)}
            />
          </div>

          <button className="btn-primary" onClick={() => setModalOpen(true)}>
            <Send size={16} />
            Send Test Notification
          </button>
        </div>
      </header>

      <MetricsBar notifications={notifications} />

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Real-time Delivery Pipeline</h2>
          <button
            onClick={fetchNotifications}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.85rem' }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>

        <NotificationTable notifications={notifications} />
      </div>

      <SendNotificationModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSend={handleSendNotification}
      />
    </div>
  );
}
