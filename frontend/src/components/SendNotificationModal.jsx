import React, { useState } from 'react';
import { Send, X, AlertTriangle } from 'lucide-react';

export default function SendNotificationModal({ isOpen, onClose, onSend }) {
  const [recipient, setRecipient] = useState('user@example.com');
  const [channel, setChannel] = useState('email');
  const [templateId, setTemplateId] = useState('welcome_email');
  const [idempotencyKey, setIdempotencyKey] = useState(`test-key-${Math.floor(Math.random() * 10000)}`);
  const [simulateFail, setSimulateFail] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload = {
      idempotency_key: idempotencyKey,
      channel,
      recipient: simulateFail ? 'fail-user@example.com' : recipient,
      template_id: templateId,
      payload: {
        timestamp: new Date().toISOString(),
        simulate_fail: simulateFail,
      },
    };

    try {
      await onSend(payload);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to dispatch notification request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Simulate Notification Dispatch</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div style={{ padding: '0.75rem 1rem', background: 'var(--status-failed-bg)', border: '1px solid var(--status-failed)', borderRadius: '8px', color: 'var(--status-failed)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Recipient Email</label>
            <input
              type="text"
              className="form-input"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Channel</label>
            <select className="form-input" value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="email">Email</option>
              <option value="sms">SMS (Future Channel)</option>
              <option value="push">Push (Future Channel)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Template ID</label>
            <input
              type="text"
              className="form-input"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Idempotency Key</label>
            <input
              type="text"
              className="form-input"
              value={idempotencyKey}
              onChange={(e) => setIdempotencyKey(e.target.value)}
              required
            />
            <button
              type="button"
              onClick={() => setIdempotencyKey(`test-key-${Math.floor(Math.random() * 10000)}`)}
              style={{ background: 'none', border: 'none', color: 'var(--primary-accent)', fontSize: '0.75rem', cursor: 'pointer', marginTop: '0.25rem' }}
            >
              Generate New Key
            </button>
          </div>

          <div className="form-group" style={{ background: 'rgba(245, 158, 11, 0.08)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', margin: 0 }}>
              <input
                type="checkbox"
                checked={simulateFail}
                onChange={(e) => setSimulateFail(e.target.checked)}
              />
              <span style={{ fontSize: '0.85rem', color: 'var(--status-retrying)', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <AlertTriangle size={15} /> Simulate Delivery Failure (Test Exponential Backoff & DLQ)
              </span>
            </label>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              <Send size={16} />
              {loading ? 'Dispatching...' : 'Dispatch Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
