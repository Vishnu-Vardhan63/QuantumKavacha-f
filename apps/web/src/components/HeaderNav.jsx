import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Search, 
  Bell, 
  Globe, 
  ChevronDown,
  LayoutDashboard,
  FileSearch,
  FolderGit2,
  Radar,
  Atom,
  FileText,
  Settings,
  Cpu
} from 'lucide-react';
import { translations } from '../i18n/translations';

export default function HeaderNav({ activePage, setActivePage, lang, setLang }) {
  const t = translations[lang] || translations.en;
  const [analystMenuOpen, setAnalystMenuOpen] = useState(false);

  const navItems = [
    { id: 'overview', label: t.nav_overview, icon: LayoutDashboard },
    { id: 'analyze', label: t.nav_analyze, icon: FileSearch },
    { id: 'investigations', label: t.nav_investigations, icon: FolderGit2 },
    { id: 'threat_intel', label: t.nav_threat_intel, icon: Radar },
    { id: 'research_lab', label: t.nav_research_lab, icon: Atom },
    { id: 'reports', label: t.nav_reports, icon: FileText },
    { id: 'settings', label: t.nav_settings, icon: Settings },
  ];

  return (
    <header style={{ borderBottom: '1px solid var(--border-subtle)', background: 'var(--panel-graphite)' }}>
      {/* Top Header Row */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0.75rem 2rem',
        borderBottom: '1px solid #162438'
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', cursor: 'pointer' }} onClick={() => setActivePage('overview')}>
          <div style={{
            background: 'rgba(40, 185, 245, 0.1)',
            padding: '0.4rem',
            borderRadius: '8px',
            border: '1px solid rgba(40, 185, 245, 0.3)',
            display: 'flex'
          }}>
            <ShieldCheck size={24} color="#28B9F5" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.01em', color: 'var(--text-crisp-white)' }}>
              QUANTUM KAVACHA
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 500 }}>
              {t.brand_subtitle}
            </div>
          </div>
        </div>

        {/* Global Search & Profile Tools */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            background: 'var(--surface-secondary)',
            borderRadius: '6px',
            padding: '0.35rem 0.75rem',
            border: '1px solid var(--border-subtle)',
            gap: '0.5rem',
            width: '260px'
          }}>
            <Search size={15} color="var(--text-muted)" />
            <input 
              type="text" 
              placeholder="Search Case ID, URL, Payee..."
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

          {/* Language Toggle */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'var(--surface-secondary)', padding: '0.35rem 0.65rem', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
            <Globe size={14} color="var(--accent-cyan)" />
            <select 
              value={lang} 
              onChange={(e) => setLang(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-crisp-white)',
                fontSize: '0.8rem',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="en" style={{ background: '#111D2D' }}>English</option>
              <option value="hi" style={{ background: '#111D2D' }}>हिंदी (Hindi)</option>
            </select>
          </div>

          {/* User Profile */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: '0.5rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: '#20334C',
              border: '1px solid var(--accent-cyan)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 600,
              fontSize: '0.8rem',
              color: 'var(--accent-cyan)'
            }}>
              VK
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Horizontal Navigation Row */}
      <nav style={{
        display: 'flex',
        alignItems: 'center',
        padding: '0 2rem',
        gap: '1.5rem',
        overflowX: 'auto'
      }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'transparent',
                border: 'none',
                color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.875rem',
                padding: '0.75rem 0',
                borderBottom: isActive ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                cursor: 'pointer',
                transition: 'color 0.15s, border-bottom 0.15s',
                whiteSpace: 'nowrap'
              }}
            >
              <Icon size={16} />
              {item.label}
            </button>
          );
        })}

        {/* Advanced Analyst Tools Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setAnalystMenuOpen(!analystMenuOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: 'transparent',
              border: 'none',
              color: ['graph', 'agent', 'simulation', 'health'].includes(activePage) ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              fontWeight: 500,
              fontSize: '0.875rem',
              padding: '0.75rem 0',
              cursor: 'pointer'
            }}
          >
            <Cpu size={16} />
            {t.nav_analyst_tools}
            <ChevronDown size={14} />
          </button>

          {analystMenuOpen && (
            <div style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              background: 'var(--panel-graphite)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '0.5rem',
              minWidth: '220px',
              boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
              zIndex: 100
            }}>
              <div 
                style={{ padding: '0.5rem 0.75rem', fontSize: '0.85rem', cursor: 'pointer', borderRadius: '4px', color: 'var(--text-crisp-white)' }}
                onClick={() => { setActivePage('graph'); setAnalystMenuOpen(false); }}
              >
                Fraud Relationship Graph
              </div>
              <div 
                style={{ padding: '0.5rem 0.75rem', fontSize: '0.85rem', cursor: 'pointer', borderRadius: '4px', color: 'var(--text-crisp-white)' }}
                onClick={() => { setActivePage('agent'); setAnalystMenuOpen(false); }}
              >
                Autonomous Agent Workspace
              </div>
              <div 
                style={{ padding: '0.5rem 0.75rem', fontSize: '0.85rem', cursor: 'pointer', borderRadius: '4px', color: 'var(--text-crisp-white)' }}
                onClick={() => { setActivePage('simulation'); setAnalystMenuOpen(false); }}
              >
                Attack Simulation Lab
              </div>
              <div 
                style={{ padding: '0.5rem 0.75rem', fontSize: '0.85rem', cursor: 'pointer', borderRadius: '4px', color: 'var(--text-crisp-white)' }}
                onClick={() => { setActivePage('health'); setAnalystMenuOpen(false); }}
              >
                System Health & Audit
              </div>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
