import React, { useState } from 'react';
import StatusBadge from './StatusBadge';
import { ChevronDown, ChevronRight, History } from 'lucide-react';

export default function NotificationTable({ notifications, onSelectNotification }) {
  const [expandedId, setExpandedId] = useState(null);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (!notifications.length) {
    return (
      <div style={{ textAlign: 'center', padding: '3.5rem 1rem', color: 'var(--text-muted)' }}>
        No notification requests recorded yet. Click <strong style={{ color: 'var(--primary-accent)' }}>"Send Test Notification"</strong> above to dispatch one!
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead>
          <tr>
            <th style={{ width: '40px' }}></th>
            <th>Notification ID</th>
            <th>Recipient</th>
            <th>Channel</th>
            <th>Status</th>
            <th>Attempts</th>
            <th>Idempotency Key</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {notifications.map((item) => {
            const isExpanded = expandedId === item.id;
            const hasAttempts = item.delivery_attempts && item.delivery_attempts.length > 0;

            return (
              <React.Fragment key={item.id}>
                <tr onClick={() => hasAttempts && toggleExpand(item.id)} style={{ cursor: hasAttempts ? 'pointer' : 'default' }}>
                  <td>
                    {hasAttempts && (
                      isExpanded ? <ChevronDown size={16} color="var(--primary-accent)" /> : <ChevronRight size={16} color="var(--text-muted)" />
                    )}
                  </td>
                  <td className="mono">{item.id.slice(0, 8)}...</td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{item.recipient}</td>
                  <td className="mono" style={{ textTransform: 'uppercase' }}>{item.channel}</td>
                  <td>
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="mono">{item.attempt_count} / {item.max_attempts}</td>
                  <td className="mono" style={{ color: 'var(--text-muted)' }}>{item.idempotency_key}</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {new Date(item.created_at).toLocaleTimeString()}
                  </td>
                </tr>

                {isExpanded && hasAttempts && (
                  <tr>
                    <td colSpan="8" style={{ background: '#f8fafc', padding: '1.25rem 1.5rem', borderLeft: '3px solid var(--primary-accent)', borderRadius: '0 0 10px 10px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem', fontSize: '0.85rem', color: 'var(--primary-accent)', fontWeight: 600 }}>
                        <History size={16} /> Audit Trail & Delivery Attempts ({item.delivery_attempts.length})
                      </div>
                      <table style={{ margin: 0, background: '#ffffff', borderRadius: '10px', border: '1px solid var(--bg-card-border)', overflow: 'hidden' }}>
                        <thead>
                          <tr>
                            <th>Attempt #</th>
                            <th>Status</th>
                            <th>Error Message</th>
                            <th>Timestamp</th>
                          </tr>
                        </thead>
                        <tbody>
                          {item.delivery_attempts.map((attempt) => (
                            <tr key={attempt.id || attempt.attempt_number}>
                              <td className="mono">Attempt #{attempt.attempt_number}</td>
                              <td>
                                <StatusBadge status={attempt.status} />
                              </td>
                              <td style={{ color: attempt.error_message ? 'var(--status-failed)' : 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                                {attempt.error_message || 'None (Successful)'}
                              </td>
                              <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                {new Date(attempt.attempted_at).toLocaleString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
