import React from 'react';
import { Clock, RefreshCw, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

const STATUS_CONFIG = {
  queued: { label: 'Queued', icon: Clock, className: 'status-queued' },
  processing: { label: 'Processing', icon: RefreshCw, className: 'status-processing' },
  delivered: { label: 'Delivered', icon: CheckCircle2, className: 'status-delivered' },
  retrying: { label: 'Retrying', icon: AlertCircle, className: 'status-retrying' },
  failed: { label: 'Failed', icon: XCircle, className: 'status-failed' },
};

export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status?.toLowerCase()] || STATUS_CONFIG.queued;
  const Icon = config.icon;

  return (
    <span className={`status-badge ${config.className}`}>
      <Icon size={13} className={status === 'processing' ? 'animate-spin' : ''} />
      {config.label}
    </span>
  );
}
