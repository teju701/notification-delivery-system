import React from 'react';

export default function MetricsBar({ notifications }) {
  const counts = notifications.reduce(
    (acc, item) => {
      const s = item.status?.toLowerCase();
      if (acc[s] !== undefined) acc[s]++;
      return acc;
    },
    { queued: 0, processing: 0, delivered: 0, retrying: 0, failed: 0 }
  );

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <span className="metric-title">Total Requests</span>
        <span className="metric-value">{notifications.length}</span>
      </div>
      <div className="metric-card" style={{ borderLeft: '4px solid var(--status-delivered)' }}>
        <span className="metric-title" style={{ color: 'var(--status-delivered)' }}>Delivered</span>
        <span className="metric-value" style={{ color: 'var(--status-delivered)' }}>{counts.delivered}</span>
      </div>
      <div className="metric-card" style={{ borderLeft: '4px solid var(--status-retrying)' }}>
        <span className="metric-title" style={{ color: 'var(--status-retrying)' }}>Retrying</span>
        <span className="metric-value" style={{ color: 'var(--status-retrying)' }}>{counts.retrying}</span>
      </div>
      <div className="metric-card" style={{ borderLeft: '4px solid var(--status-failed)' }}>
        <span className="metric-title" style={{ color: 'var(--status-failed)' }}>Failed (DLQ)</span>
        <span className="metric-value" style={{ color: 'var(--status-failed)' }}>{counts.failed}</span>
      </div>
      <div className="metric-card" style={{ borderLeft: '4px solid var(--status-processing)' }}>
        <span className="metric-title" style={{ color: 'var(--status-processing)' }}>Queued / In-Flight</span>
        <span className="metric-value" style={{ color: 'var(--status-processing)' }}>{counts.queued + counts.processing}</span>
      </div>
    </div>
  );
}
