import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  QrCode, 
  Receipt, 
  Link2, 
  FileCheck, 
  FolderGit2, 
  ArrowRight,
  ExternalLink,
  Clock
} from 'lucide-react';
import { translations } from '../i18n/translations';
import EvidenceSubmissionWorkspace from '../components/EvidenceSubmissionWorkspace';
import EvidenceResultView from '../components/EvidenceResultView';

export default function OverviewPage({ lang, setActivePage, activeResult, setActiveResult }) {
  const t = translations[lang] || translations.en;
  const [recentCases, setRecentCases] = useState([]);

  useEffect(() => {
    fetch('/api/investigations')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setRecentCases(data);
      })
      .catch(() => {});
  }, [activeResult]);

  if (activeResult) {
    return (
      <EvidenceResultView 
        result={activeResult} 
        onReset={() => setActiveResult(null)} 
        lang={lang} 
      />
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem 4rem 1rem' }}>
      {/* Hero Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.6rem' }}>
          {t.hero_title}
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', maxWidth: '780px' }}>
          {t.hero_subtitle}
        </p>
      </div>

      {/* 4 Primary Action Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '1.25rem',
        marginBottom: '2.5rem'
      }}>
        {[
          { title: t.action_qr_title, desc: t.action_qr_desc, icon: QrCode, type: 'QR_CODE' },
          { title: t.action_payment_title, desc: t.action_payment_desc, icon: Receipt, type: 'PAYMENT_SCREENSHOT' },
          { title: t.action_url_title, desc: t.action_url_desc, icon: Link2, type: 'URL' },
          { title: t.action_doc_title, desc: t.action_doc_desc, icon: FileCheck, type: 'GENERAL_DOCUMENT' }
        ].map((card, idx) => {
          const Icon = card.icon;
          return (
            <div 
              key={idx} 
              className="qk-panel qk-panel-interactive" 
              style={{ padding: '1.5rem', cursor: 'pointer' }}
              onClick={() => setActivePage('analyze')}
            >
              <div style={{
                background: 'rgba(40, 185, 245, 0.1)',
                width: '42px',
                height: '42px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem',
                border: '1px solid rgba(40, 185, 245, 0.25)'
              }}>
                <Icon size={22} color="var(--accent-cyan)" />
              </div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '0.4rem' }}>{card.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: '1.4' }}>{card.desc}</p>
            </div>
          );
        })}
      </div>

      {/* Evidence Submission Workspace */}
      <EvidenceSubmissionWorkspace 
        onAnalysisComplete={(res) => setActiveResult(res)} 
        lang={lang} 
      />

      {/* Recent Investigations Workspace */}
      <div className="qk-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FolderGit2 size={20} color="var(--accent-cyan)" /> Recent Investigations
          </h3>
          <button 
            onClick={() => setActivePage('investigations')} 
            style={{ background: 'transparent', border: 'none', color: 'var(--accent-cyan)', fontSize: '0.85rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
          >
            View all investigations <ArrowRight size={14} />
          </button>
        </div>

        {recentCases.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <FolderGit2 size={36} style={{ marginBottom: '0.5rem', opacity: 0.4 }} />
            <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
              {t.empty_investigations_title}
            </div>
            <div style={{ fontSize: '0.85rem' }}>
              {t.empty_investigations_desc}
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {recentCases.slice(0, 5).map((c, idx) => (
              <div 
                key={idx} 
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'var(--surface-secondary)',
                  padding: '0.85rem 1.25rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  cursor: 'pointer'
                }}
                onClick={() => {
                  fetch(`/api/investigations/${c.case_id}`)
                    .then(res => res.json())
                    .then(fullCase => setActiveResult(fullCase));
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span className="mono-badge" style={{ background: '#111D2D', color: 'var(--accent-cyan)' }}>
                    {c.case_id}
                  </span>
                  <div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{c.summary}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{c.evidence_type}</div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span className="mono-badge" style={{
                    background: c.final_verdict === 'MALICIOUS' ? 'rgba(239, 68, 68, 0.2)' : c.final_verdict === 'SAFE' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: c.final_verdict === 'MALICIOUS' ? '#EF4444' : c.final_verdict === 'SAFE' ? '#10B981' : '#F59E0B'
                  }}>
                    {c.final_verdict}
                  </span>
                  <ExternalLink size={15} color="var(--text-muted)" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
