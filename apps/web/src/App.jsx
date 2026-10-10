import React, { useState } from 'react';
import HeaderNav from './components/HeaderNav';
import OverviewPage from './pages/OverviewPage';
import InvestigationsPage from './pages/InvestigationsPage';
import ThreatIntelligencePage from './pages/ThreatIntelligencePage';
import ResearchLabPage from './pages/ResearchLabPage';
import ReportsPage from './pages/ReportsPage';
import EvidenceSubmissionWorkspace from './components/EvidenceSubmissionWorkspace';
import EvidenceResultView from './components/EvidenceResultView';
import './styles/globals.css';

export default function App() {
  const [activePage, setActivePage] = useState('overview');
  const [lang, setLang] = useState('en');
  const [activeResult, setActiveResult] = useState(null);

  const renderContent = () => {
    switch (activePage) {
      case 'overview':
        return (
          <OverviewPage 
            lang={lang} 
            setActivePage={setActivePage} 
            activeResult={activeResult}
            setActiveResult={setActiveResult}
          />
        );
      case 'analyze':
        return activeResult ? (
          <EvidenceResultView 
            result={activeResult} 
            onReset={() => setActiveResult(null)} 
            lang={lang} 
          />
        ) : (
          <div style={{ maxWidth: '1000px', margin: '2rem auto', padding: '0 1rem' }}>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              Analyze Evidence
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '2rem' }}>
              Unified forensic pipeline for QR codes, payment receipts, URLs, and general documents.
            </p>
            <EvidenceSubmissionWorkspace 
              onAnalysisComplete={(res) => setActiveResult(res)} 
              lang={lang} 
            />
          </div>
        );
      case 'investigations':
        return (
          <InvestigationsPage 
            lang={lang} 
            onSelectCase={(c) => {
              setActiveResult(c);
              setActivePage('analyze');
            }} 
          />
        );
      case 'threat_intel':
        return <ThreatIntelligencePage />;
      case 'research_lab':
        return <ResearchLabPage />;
      case 'reports':
        return <ReportsPage lang={lang} />;
      case 'settings':
        return (
          <div style={{ maxWidth: '800px', margin: '3rem auto', padding: '0 1rem' }}>
            <h2>Platform Settings</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', marginBottom: '2rem' }}>
              Manage session preferences, language localization, and API integrations.
            </p>
            <div className="qk-panel" style={{ padding: '1.5rem' }}>
              <div style={{ fontSize: '0.9rem', marginBottom: '0.5rem', fontWeight: 600 }}>Active Language</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{lang === 'en' ? 'English (US)' : 'Hindi (हिंदी)'}</div>
            </div>
          </div>
        );
      default:
        return (
          <div style={{ maxWidth: '1000px', margin: '3rem auto', padding: '0 1rem' }}>
            <h2>{activePage.toUpperCase()} Analyst Module</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
              Enterprise security analyst tools are isolated from standard merchant operations.
            </p>
          </div>
        );
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <HeaderNav 
        activePage={activePage} 
        setActivePage={(page) => {
          setActivePage(page);
          if (page === 'overview') setActiveResult(null);
        }} 
        lang={lang} 
        setLang={setLang} 
      />
      <main style={{ flex: 1 }}>
        {renderContent()}
      </main>
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '1.5rem 2rem',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        background: 'var(--panel-graphite)'
      }}>
        Quantum Kavacha Platform v2.0.0 &bull; Financial Fraud & Digital Forensics Intelligence &bull; Evidence Before Verdicts
      </footer>
    </div>
  );
}
