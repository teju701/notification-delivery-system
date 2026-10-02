import React from 'react';
import { Zap, ShieldCheck, Cpu, RefreshCw, AlertTriangle, Radio, ArrowRight, Key, LayoutDashboard, Terminal } from 'lucide-react';
import CodePlayground from './CodePlayground';

export default function LandingPage({ onGoToDashboard, onOpenKeyModal, apiKey }) {
  return (
    <div>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '3.5rem 1rem 3rem 1rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: '#ecfdf5', color: '#059669', padding: '0.4rem 1rem', borderRadius: '9999px', border: '1px solid #6ee7b7', fontSize: '0.82rem', fontWeight: 600, marginBottom: '1.5rem' }}>
          <Zap size={15} /> Asynchronous • Fault-Tolerant • Distributed Architecture
        </div>

        <h1 style={{ fontSize: '2.75rem', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.2, color: 'var(--text-primary)', maxWidth: '840px', margin: '0 auto 1.25rem auto' }}>
          Reliable Notification Delivery Engine for Production Applications
        </h1>

        <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', maxWidth: '680px', margin: '0 auto 2.25rem auto', lineHeight: 1.6 }}>
          Decouple your application from third-party email latency. Queue requests instantly, enforce per-tenant rate limits, retry transient failures with backoff, and guarantee zero double-sends.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <button className="btn-primary" style={{ padding: '0.85rem 1.75rem', fontSize: '1rem', borderRadius: '12px' }} onClick={onGoToDashboard}>
            <LayoutDashboard size={18} /> Open Live Dashboard
          </button>
          <button className="btn-secondary" style={{ padding: '0.85rem 1.75rem', fontSize: '1rem', borderRadius: '12px', background: '#ffffff', color: 'var(--text-primary)', border: '1px solid var(--bg-card-border)', boxShadow: '0 2px 5px rgba(0,0,0,0.04)' }} onClick={onOpenKeyModal}>
            <Key size={18} color="var(--primary-accent)" /> Generate API Key
          </button>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section style={{ marginBottom: '3.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)' }}>Engineered for System Resilience</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '0.3rem' }}>Core backend patterns preventing system crashes and double sends</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {/* Card 1 */}
          <div className="card" style={{ margin: 0 }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: '#e0f2fe', color: '#0284c7', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <Zap size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Decoupled Async Queueing</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Accepts notification requests instantly with <code>HTTP 202 Accepted</code> in ~15ms. Pushes jobs onto Redis Streams so your callers never wait on email network latency.
            </p>
          </div>

          {/* Card 2 */}
          <div className="card" style={{ margin: 0 }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: '#ecfdf5', color: '#059669', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <ShieldCheck size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Idempotency & Zero Double-Sends</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Guaranteed at the database level using a PostgreSQL unique index on <code>(tenant_id, key)</code>. Duplicate requests return HTTP 200 without sending extra emails.
            </p>
          </div>

          {/* Card 3 */}
          <div className="card" style={{ margin: 0 }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: '#f0fdf4', color: '#16a34a', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <Cpu size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Token Bucket Rate Limiting</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Concurrency-safe Redis Lua script enforcing 2 dimensions: per-tenant fairness (preventing spam) and global provider compliance (preventing email API bans).
            </p>
          </div>

          {/* Card 4 */}
          <div className="card" style={{ margin: 0 }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: '#fffbeb', color: '#d97706', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <RefreshCw size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Exponential Backoff Retries</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Failed attempts delay re-enqueuing by <code>2^attempt</code> seconds (2s, 4s, 8s) in a Redis Sorted Set scheduler, avoiding thundering herd crashes.
            </p>
          </div>

          {/* Card 5 */}
          <div className="card" style={{ margin: 0 }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: '#fff1f2', color: '#e11d48', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <AlertTriangle size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Dead-Letter Queue (DLQ)</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Jobs exceeding maximum attempts (3) transition to <code>failed</code> and park in a separate DLQ stream for isolation, alerting, and manual inspection.
            </p>
          </div>

          {/* Card 6 */}
          <div className="card" style={{ margin: 0 }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: '#f5f3ff', color: '#7c3aed', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <Radio size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>WebSocket Real-Time Feed</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Worker updates publish to Redis Pub/Sub, which FastAPI streams live over WebSockets to your browser screen without heavy HTTP polling overhead.
            </p>
          </div>
        </div>
      </section>

      {/* Code Playground Section */}
      <section style={{ marginBottom: '3.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>Quick Integration Code Snippets</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>Copy and paste this snippet directly into your backend code</p>
        </div>

        <CodePlayground apiKey={apiKey} />
      </section>
    </div>
  );
}
