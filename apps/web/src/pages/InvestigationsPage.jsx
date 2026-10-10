import React, { useState, useEffect } from 'react';
import { FolderGit2, Search, Filter, Clock, ExternalLink } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function InvestigationsPage({ onSelectCase, lang }) {
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

  const filtered = cases.filter(c => 
    c.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.evidence_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.25rem' }}>Investigations</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Authoritative history of digital forensics analysis and threat verdicts.
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
            placeholder="Filter by Case ID or type..."
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
              <th style={{ padding: '0.85rem 1.25rem' }}>Timestamp</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Evidence Type</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Verdict</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Risk Score</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Summary</th>
              <th style={{ padding: '0.85rem 1.25rem' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                  No investigation records found.
                </td>
              </tr>
            ) : (
              filtered.map((c, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.15s' }}>
                  <td style={{ padding: '0.85rem 1.25rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
                    {c.case_id}
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem', color: 'var(--text-secondary)' }}>
                    {new Date(c.created_at).toLocaleString()}
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem', fontWeight: 500 }}>
                    {c.evidence_type}
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem' }}>
                    <span className="mono-badge" style={{
                      background: c.final_verdict === 'MALICIOUS' ? 'rgba(239, 68, 68, 0.2)' : c.final_verdict === 'SAFE' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                      color: c.final_verdict === 'MALICIOUS' ? '#EF4444' : c.final_verdict === 'SAFE' ? '#10B981' : '#F59E0B'
                    }}>
                      {c.final_verdict}
                    </span>
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>
                    {c.risk_score !== null ? `${c.risk_score} / 100` : '—'}
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem', color: 'var(--text-secondary)', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {c.summary}
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem' }}>
                    <button 
                      onClick={() => {
                        fetch(`/api/investigations/${c.case_id}`)
                          .then(res => res.json())
                          .then(fullCase => onSelectCase(fullCase));
                      }}
                      className="btn-secondary"
                      style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                    >
                      Inspect <ExternalLink size={12} />
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
