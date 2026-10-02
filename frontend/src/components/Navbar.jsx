import React from 'react';
import { Zap, LayoutDashboard, Home, Key, Send } from 'lucide-react';

export default function Navbar({ activeView, setActiveView, onOpenKeyModal, isConnected }) {
  return (
    <header>
      <div className="logo-group" style={{ cursor: 'pointer' }} onClick={() => setActiveView('landing')}>
        <div className="logo-icon">
          <Zap size={22} color="#fff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            Notification Engine
          </h1>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Async • Idempotent • Rate Limited
          </span>
        </div>
      </div>

      <div className="header-actions">
        {/* Navigation Tabs */}
        <div style={{ display: 'flex', background: '#ffffff', padding: '0.25rem', borderRadius: '10px', border: '1px solid var(--bg-card-border)', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
          <button
            onClick={() => setActiveView('landing')}
            style={{
              background: activeView === 'landing' ? 'var(--primary-accent)' : 'transparent',
              color: activeView === 'landing' ? '#ffffff' : 'var(--text-secondary)',
              border: 'none',
              borderRadius: '8px',
              padding: '0.45rem 0.9rem',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              transition: 'all 0.2s ease'
            }}
          >
            <Home size={15} /> Overview
          </button>
          <button
            onClick={() => setActiveView('dashboard')}
            style={{
              background: activeView === 'dashboard' ? 'var(--primary-accent)' : 'transparent',
              color: activeView === 'dashboard' ? '#ffffff' : 'var(--text-secondary)',
              border: 'none',
              borderRadius: '8px',
              padding: '0.45rem 0.9rem',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              transition: 'all 0.2s ease'
            }}
          >
            <LayoutDashboard size={15} /> Live Dashboard
          </button>
        </div>

        {/* WebSocket Status Indicator */}
        <div className="ws-status-pill">
          <div className={`ws-dot ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Live Connected' : 'Reconnecting...'}
        </div>

        {/* Generate API Key CTA */}
        <button className="btn-primary" onClick={onOpenKeyModal}>
          <Key size={16} />
          Generate API Key
        </button>
      </div>
    </header>
  );
}
