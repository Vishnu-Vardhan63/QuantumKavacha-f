import React, { useState } from 'react';
import { 
  Upload, 
  QrCode, 
  Receipt, 
  Link2, 
  FileCheck, 
  AlertTriangle,
  ArrowRight
} from 'lucide-react';
import { translations } from '../i18n/translations';

export default function EvidenceSubmissionWorkspace({ onAnalysisComplete, lang }) {
  const t = translations[lang] || translations.en;
  const [evidenceType, setEvidenceType] = useState('URL');
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    setErrorMsg(null);
    setLoading(true);

    try {
      let response;
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        response = await fetch('/api/evidence/upload', {
          method: 'POST',
          body: formData
        });
      } else if (inputText.trim()) {
        response = await fetch('/api/evidence/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            evidence_type: evidenceType,
            input_text: inputText.trim()
          })
        });
      } else {
        setErrorMsg('Please enter an indicator URL/payload or upload a document/image.');
        setLoading(false);
        return;
      }

      if (!response.ok) {
        throw new Error(`Analysis failed with HTTP status ${response.status}`);
      }

      const data = await response.json();
      onAnalysisComplete(data);
    } catch (err) {
      setErrorMsg(err.message || 'Analysis failed. Please verify API connectivity.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="qk-panel" style={{ padding: '2rem', marginBottom: '2.5rem' }}>
      <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', fontWeight: 600 }}>
        Evidence Submission Workspace
      </h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
        Submit suspicious digital payment artifacts for multi-engine verification.
      </p>

      {/* Mode Selector */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {[
          { id: 'URL', label: 'Suspicious Link / Host', icon: Link2 },
          { id: 'QR_CODE', label: 'QR Payload / UPI', icon: QrCode },
          { id: 'PAYMENT_SCREENSHOT', label: 'Payment Screenshot', icon: Receipt },
          { id: 'GENERAL_DOCUMENT', label: 'Document / Invoice', icon: FileCheck }
        ].map(tab => {
          const Icon = tab.icon;
          const active = evidenceType === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => { setEvidenceType(tab.id); setSelectedFile(null); }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.55rem 1rem',
                borderRadius: '6px',
                border: active ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                background: active ? 'rgba(40, 185, 245, 0.12)' : 'var(--surface-secondary)',
                color: active ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                fontWeight: 500,
                fontSize: '0.85rem'
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Input Dropzone / Text Form */}
      {['URL', 'QR_CODE'].includes(evidenceType) && !selectedFile ? (
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
            Enter destination URL or raw UPI payment string:
          </label>
          <input 
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={evidenceType === 'URL' ? 'e.g., https://paytm-reward-support.xyz/login' : 'e.g., upi://pay?pa=store@icici&pn=Merchant&am=100'}
            style={{
              width: '100%',
              padding: '0.75rem 1rem',
              borderRadius: '6px',
              background: 'var(--surface-secondary)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-crisp-white)',
              fontSize: '0.9rem',
              outline: 'none'
            }}
          />
        </div>
      ) : null}

      {/* File Upload Dropzone */}
      <div style={{
        border: '2px dashed var(--border-subtle)',
        borderRadius: '8px',
        padding: '2rem',
        textAlign: 'center',
        background: 'rgba(24, 38, 58, 0.4)',
        marginBottom: '1.5rem'
      }}>
        <Upload size={32} color="var(--accent-cyan)" style={{ marginBottom: '0.75rem' }} />
        <div style={{ fontSize: '0.95rem', fontWeight: 500, marginBottom: '0.35rem' }}>
          {selectedFile ? `Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)` : "Drag and drop evidence file, or browse"}
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Supported: PNG, JPG, WEBP, PDF (Max 10 MB)
        </div>
        <input 
          type="file" 
          id="evidenceFileInput" 
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <label htmlFor="evidenceFileInput" className="btn-secondary" style={{ cursor: 'pointer' }}>
          Browse Files
        </label>
        {selectedFile && (
          <button 
            onClick={() => setSelectedFile(null)} 
            style={{ background: 'transparent', border: 'none', color: '#EF4444', marginLeft: '1rem', fontSize: '0.85rem', cursor: 'pointer' }}
          >
            Remove file
          </button>
        )}
      </div>

      {errorMsg && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#EF4444', marginBottom: '1rem', fontSize: '0.85rem' }}>
          <AlertTriangle size={16} />
          {errorMsg}
        </div>
      )}

      {/* Submit Action */}
      <button 
        className="btn-primary" 
        onClick={handleAnalyze} 
        disabled={loading}
        style={{ opacity: loading ? 0.7 : 1 }}
      >
        {loading ? t.btn_analyzing : t.btn_analyze}
        {!loading && <ArrowRight size={16} />}
      </button>
    </div>
  );
}
