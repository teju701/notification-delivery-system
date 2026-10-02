import React, { useState } from 'react';
import { Key, Copy, Check, X, ShieldCheck, ArrowRight } from 'lucide-react';

export default function ApiKeyGeneratorModal({ isOpen, onClose, onKeyGenerated }) {
  const [appName, setAppName] = useState('');
  const [generatedKey, setGeneratedKey] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!appName.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('http://localhost:8000/api/v1/tenants/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: appName.trim() })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to generate API Key');
      }

      const data = await res.json();
      setGeneratedKey(data.api_key);
    } catch (err) {
      setError(err.message || 'Failed to register application');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (generatedKey) {
      navigator.clipboard.writeText(generatedKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleUseKeyInDashboard = () => {
    if (generatedKey && onKeyGenerated) {
      onKeyGenerated(generatedKey);
    }
    handleClose();
  };

  const handleClose = () => {
    setAppName('');
    setGeneratedKey(null);
    setError(null);
    setCopied(false);
    onClose();
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content" style={{ maxWidth: '540px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'var(--status-processing-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary-accent)' }}>
              <Key size={18} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {generatedKey ? 'API Key Generated!' : 'Generate Developer API Key'}
              </h2>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {generatedKey ? 'Save key securely — shown only once' : 'Creates an isolated tenant in PostgreSQL'}
              </span>
            </div>
          </div>

          <button onClick={handleClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div style={{ padding: '0.75rem 1rem', background: 'var(--status-failed-bg)', border: '1px solid var(--status-failed-border)', borderRadius: '10px', color: 'var(--status-failed)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
            {error}
          </div>
        )}

        {!generatedKey ? (
          <form onSubmit={handleGenerate}>
            <div className="form-group">
              <label>Application / Team Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Acme E-Commerce, Auth Microservice"
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                required
                autoFocus
              />
            </div>

            <div style={{ background: '#f8fafc', padding: '0.85rem 1rem', borderRadius: '10px', border: '1px solid var(--bg-card-border)', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                <ShieldCheck size={16} color="var(--primary-accent)" />
                SHA-256 Hashed Storage & 10 RPS Rate Limit automatically applied.
              </div>
            </div>

            <div className="modal-actions">
              <button type="button" className="btn-secondary" onClick={handleClose}>
                Cancel
              </button>
              <button type="submit" className="btn-primary" disabled={loading || !appName.trim()}>
                {loading ? 'Generating...' : 'Generate Secret Key'}
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div className="form-group">
              <label>Your Secret X-API-Key</label>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.3rem' }}>
                <input
                  type="text"
                  readOnly
                  className="form-input mono"
                  value={generatedKey}
                  style={{ background: '#ecfdf5', borderColor: '#6ee7b7', color: '#047857', fontWeight: 600 }}
                />
                <button
                  type="button"
                  onClick={copyToClipboard}
                  className="btn-secondary"
                  style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: copied ? '#ecfdf5' : '#f1f5f9', color: copied ? '#059669' : 'var(--text-secondary)' }}
                >
                  {copied ? <Check size={16} /> : <Copy size={16} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>

            <div style={{ padding: '0.85rem 1rem', background: '#fffbeb', border: '1px solid #fcd34d', borderRadius: '10px', color: '#b45309', fontSize: '0.82rem', marginBottom: '1.5rem' }}>
              ⚠️ Make sure to copy your key now. For security reasons, the raw key is never stored in plain text and cannot be retrieved later.
            </div>

            <div className="modal-actions">
              <button type="button" className="btn-secondary" onClick={handleClose}>
                Close
              </button>
              <button type="button" className="btn-primary" onClick={handleUseKeyInDashboard}>
                Use Key in Live Dashboard <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
