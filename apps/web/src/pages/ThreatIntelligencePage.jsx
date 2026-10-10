import React, { useState, useEffect } from 'react';
import { Radar, AlertCircle, Shield, ExternalLink } from 'lucide-react';

export default function ThreatIntelligencePage() {
  const [indicators, setIndicators] = useState([]);

  useEffect(() => {
    fetch('/api/threat-intel/indicators')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setIndicators(data);
      })
      .catch(() => {});
  }, []);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.25rem' }}>Threat Intelligence</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Real-time indicators of compromise (IoCs), phishing hosts, and known payment scam vectors.
        </p>
      </div>

      <div className="qk-panel" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ background: '#0F1A28', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '0.85rem 1.25rem' }}>Indicator</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Type</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Category</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Severity</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Status</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>First Seen</th>
            </tr>
          </thead>
          <tbody>
            {indicators.map((ioc, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.85rem 1.25rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
                  {ioc.indicator}
                </td>
                <td style={{ padding: '0.85rem 1.25rem' }}>{ioc.type}</td>
                <td style={{ padding: '0.85rem 1.25rem', color: 'var(--text-secondary)' }}>{ioc.category}</td>
                <td style={{ padding: '0.85rem 1.25rem' }}>
                  <span className="mono-badge" style={{
                    background: ioc.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: ioc.severity === 'CRITICAL' ? '#EF4444' : '#F59E0B'
                  }}>
                    {ioc.severity}
                  </span>
                </td>
                <td style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>{ioc.status}</td>
                <td style={{ padding: '0.85rem 1.25rem', color: 'var(--text-muted)' }}>
                  {new Date(ioc.first_seen).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
