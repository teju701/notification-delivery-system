import React, { useState } from 'react';
import { Copy, Check, Terminal, Code2 } from 'lucide-react';

export default function CodePlayground({ apiKey }) {
  const [activeTab, setActiveTab] = useState('curl');
  const [copied, setCopied] = useState(false);

  const activeKey = apiKey || 'nds_live_YOUR_GENERATED_API_KEY';

  const SNIPPETS = {
    curl: `curl -X POST http://localhost:8000/api/v1/notifications \\
  -H "X-API-Key: ${activeKey}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "idempotency_key": "order-10293-receipt",
    "channel": "email",
    "recipient": "user@example.com",
    "template_id": "shipping_confirmation",
    "payload": {
      "order_id": "10293",
      "carrier": "FedEx",
      "tracking_code": "9876543210"
    }
  }'`,

    js: `// Node.js / JavaScript Fetch Integration
const response = await fetch('http://localhost:8000/api/v1/notifications', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': '${activeKey}'
  },
  body: JSON.stringify({
    idempotency_key: 'order-10293-receipt',
    channel: 'email',
    recipient: 'user@example.com',
    template_id: 'shipping_confirmation',
    payload: {
      order_id: '10293',
      carrier: 'FedEx'
    }
  })
});

const data = await response.json();
console.log('Queued Notification ID:', data.id);`,

    python: `# Python Requests Integration
import requests

url = "http://localhost:8000/api/v1/notifications"
headers = {
    "X-API-Key": "${activeKey}",
    "Content-Type": "application/json"
}
payload = {
    "idempotency_key": "order-10293-receipt",
    "channel": "email",
    "recipient": "user@example.com",
    "template_id": "shipping_confirmation",
    "payload": {
        "order_id": "10293",
        "carrier": "FedEx"
    }
}

response = requests.post(url, headers=headers, json=payload)
print("HTTP Status:", response.status_code) # 202 Accepted
print("Response:", response.json())`
  };

  const copyCode = () => {
    navigator.clipboard.writeText(SNIPPETS[activeTab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #1e293b', overflow: 'hidden', boxShadow: '0 15px 30px rgba(15, 23, 42, 0.15)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1e293b', padding: '0.65rem 1.25rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setActiveTab('curl')}
            style={{
              background: activeTab === 'curl' ? '#0f172a' : 'transparent',
              color: activeTab === 'curl' ? '#38bdf8' : '#94a3b8',
              border: 'none',
              borderRadius: '6px',
              padding: '0.35rem 0.75rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            cURL
          </button>
          <button
            onClick={() => setActiveTab('js')}
            style={{
              background: activeTab === 'js' ? '#0f172a' : 'transparent',
              color: activeTab === 'js' ? '#facc15' : '#94a3b8',
              border: 'none',
              borderRadius: '6px',
              padding: '0.35rem 0.75rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            JavaScript / Node
          </button>
          <button
            onClick={() => setActiveTab('python')}
            style={{
              background: activeTab === 'python' ? '#0f172a' : 'transparent',
              color: activeTab === 'python' ? '#38bdf8' : '#94a3b8',
              border: 'none',
              borderRadius: '6px',
              padding: '0.35rem 0.75rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Python
          </button>
        </div>

        <button
          onClick={copyCode}
          style={{
            background: 'rgba(255, 255, 255, 0.08)',
            color: '#f8fafc',
            border: 'none',
            borderRadius: '6px',
            padding: '0.35rem 0.75rem',
            fontSize: '0.78rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            cursor: 'pointer'
          }}
        >
          {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
          {copied ? 'Copied' : 'Copy Code'}
        </button>
      </div>

      <pre style={{ padding: '1.25rem 1.5rem', overflowX: 'auto', margin: 0, fontFamily: 'var(--font-mono)', fontSize: '0.83rem', color: '#e2e8f0', lineHeight: 1.6 }}>
        <code>{SNIPPETS[activeTab]}</code>
      </pre>
    </div>
  );
}
