import React, { useState, useEffect } from 'react';
import { FileText, Download, Clock, Shield, Search } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function ReportsPage({ lang }) {
  const [cases, setCases] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetch('/api/investigations')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setCases(data);
      })
      .catch(() => {});
  }, []);

  const handleDownload = (caseId) => {
    window.open(`/api/investigations/${caseId}/report`, '_blank');
  };

  const filtered = cases.filter(c =>
    c.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.summary.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.25rem' }}>Forensic Reports</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Download verified, audit-ready investigation summaries and compliance documentation.
          </p>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          background: 'var(--surface-secondary)',
          borderRadius: '6px',
          padding: '0.4rem 0.75rem',
          border: '1px solid var(--border-subtle)',
          gap: '0.5rem',
          width: '280px'
        }}>
          <Search size={15} color="var(--text-muted)" />
          <input 
            type="text" 
            placeholder="Search report by Case ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-crisp-white)',
              fontSize: '0.85rem',
              width: '100%'
            }}
          />
        </div>
      </div>

      <div className="qk-panel" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ background: '#0F1A28', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '0.85rem 1.25rem' }}>Case ID</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Created Timestamp</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Classification</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Verdict</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Summary</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Export Format</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                  No investigation reports available yet. Submit evidence on the Overview page to generate reports.
                </td>
              </tr>
            ) : (
              filtered.map((c, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '0.85rem 1.25rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
                    {c.case_id}
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem', color: 'var(--text-secondary)' }}>
                    {new Date(c.created_at).toLocaleString()}
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem' }}>{c.evidence_type}</td>
                  <td style={{ padding: '0.85rem 1.25rem' }}>
                    <span className="mono-badge" style={{
                      background: c.final_verdict === 'MALICIOUS' ? 'rgba(239, 68, 68, 0.2)' : c.final_verdict === 'SAFE' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                      color: c.final_verdict === 'MALICIOUS' ? '#EF4444' : c.final_verdict === 'SAFE' ? '#10B981' : '#F59E0B'
                    }}>
                      {c.final_verdict}
                    </span>
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem', color: 'var(--text-secondary)' }}>
                    {c.summary}
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem' }}>
                    <button 
                      onClick={() => handleDownload(c.case_id)}
                      className="btn-primary"
                      style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
                    >
                      <Download size={13} /> Export Report (.md)
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
