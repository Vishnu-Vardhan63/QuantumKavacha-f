import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  HelpCircle,
  FileText,
  Clock,
  ArrowLeft,
  Download,
  AlertCircle
} from 'lucide-react';
import { translations } from '../i18n/translations';

export default function EvidenceResultView({ result, onReset, lang }) {
  const t = translations[lang] || translations.en;

  const getVerdictBadge = (verdict) => {
    switch (verdict) {
      case 'SAFE':
        return {
          color: '#10B981',
          bg: 'rgba(16, 185, 129, 0.1)',
          border: 'rgba(16, 185, 129, 0.3)',
          icon: ShieldCheck,
          text: t.verdict_safe
        };
      case 'SUSPICIOUS':
        return {
          color: '#F59E0B',
          bg: 'rgba(245, 158, 11, 0.1)',
          border: 'rgba(245, 158, 11, 0.3)',
          icon: AlertTriangle,
          text: t.verdict_suspicious
        };
      case 'MALICIOUS':
        return {
          color: '#EF4444',
          bg: 'rgba(239, 68, 68, 0.1)',
          border: 'rgba(239, 68, 68, 0.3)',
          icon: ShieldAlert,
          text: t.verdict_malicious
        };
      default:
        return {
          color: '#6B7280',
          bg: 'rgba(107, 114, 128, 0.1)',
          border: 'rgba(107, 114, 128, 0.3)',
          icon: HelpCircle,
          text: t.verdict_inconclusive
        };
    }
  };

  const badge = getVerdictBadge(result.final_verdict);
  const VerdictIcon = badge.icon;

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', paddingBottom: '3rem' }}>
      {/* Back action */}
      <button 
        onClick={onReset}
        className="btn-secondary"
        style={{ marginBottom: '1.5rem', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
      >
        <ArrowLeft size={15} /> Back to Overview
      </button>

      {/* Top Banner Card */}
      <div className="qk-panel" style={{ padding: '2rem', marginBottom: '2rem', borderLeft: `6px solid ${badge.color}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <span className="mono-badge" style={{ background: '#1E293B', color: 'var(--accent-cyan)' }}>
                {result.case_id}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Clock size={13} /> {new Date(result.created_at).toLocaleString()}
              </span>
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              {result.summary}
            </h2>
            <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block' }}>Evidence Type</span>
                <strong style={{ fontSize: '0.95rem' }}>{result.evidence_type}</strong>
              </div>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block' }}>Payment Settlement Status</span>
                <span className="mono-badge" style={{ background: '#1E293B', color: result.payment_status === 'VERIFIED' ? '#10B981' : '#F59E0B' }}>
                  {result.payment_status}
                </span>
              </div>
              {result.risk_score !== null && (
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block' }}>Calculated Risk Score</span>
                  <strong style={{ fontSize: '1.1rem', color: badge.color }}>{result.risk_score} / 100</strong>
                </div>
              )}
            </div>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: badge.bg,
            border: `1px solid ${badge.border}`,
            padding: '0.6rem 1.25rem',
            borderRadius: '8px',
            color: badge.color,
            fontWeight: 700,
            fontSize: '1rem'
          }}>
            <VerdictIcon size={20} />
            {badge.text}
          </div>
        </div>
      </div>

      {/* Grid: Findings & Recommended Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Evidence Findings */}
        <div className="qk-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={18} color="var(--accent-cyan)" />
            Evidence Findings ({result.evidence_findings.length})
          </h3>
          {result.evidence_findings.length === 0 ? (
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              No anomalous or deceptive findings identified in automated inspections.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {result.evidence_findings.map((f, idx) => (
                <div key={idx} style={{
                  background: 'var(--surface-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  padding: '1rem'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{f.title}</span>
                    <span className="mono-badge" style={{ 
                      background: f.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : f.severity === 'HIGH' ? 'rgba(245, 158, 11, 0.2)' : '#1E293B',
                      color: f.severity === 'CRITICAL' ? '#EF4444' : f.severity === 'HIGH' ? '#F59E0B' : 'var(--text-secondary)'
                    }}>
                      {f.severity}
                    </span>
                  </div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                    {f.description}
                  </p>
                  {f.evidence_excerpt && (
                    <div style={{
                      background: '#0B1320',
                      padding: '0.4rem 0.6rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--accent-cyan)',
                      overflowX: 'auto'
                    }}>
                      {f.evidence_excerpt}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Next Actions & Limitations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="qk-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem' }}>
              Recommended Next Actions
            </h3>
            <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-crisp-white)', fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {result.recommended_actions.map((act, idx) => (
                <li key={idx}>{act}</li>
              ))}
            </ul>
          </div>

          <div className="qk-panel" style={{ padding: '1.5rem', background: '#0F1A28' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)' }}>
              <AlertCircle size={15} /> Platform Limitations & Disclaimers
            </h4>
            <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {result.limitations.map((lim, idx) => (
                <li key={idx}>{lim}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
