import React from 'react';
import { Database, Shield } from 'lucide-react';
import type { HealthStatus } from '../types';
import { DrishtiLogo } from './DrishtiLogo';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: HealthStatus | null;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, health }) => {
  const tabs = [
    { id: 'dashboard', label: 'Market Overview' },
    { id: 'stocks', label: 'Volume Intelligence' },
    { id: 'anomalies', label: 'Anomaly Detection' },
    { id: 'sectors', label: 'Sector Intelligence' },
    { id: 'copilot', label: 'AI Copilot' },
    { id: 'reports', label: 'Reports & History' },
    { id: 'ingestion', label: 'Data Ingestion' },
    { id: 'settings', label: 'Settings & Db2 Status' },
  ];

  const dbOnline = health?.database?.status === 'healthy';
  const latency = health?.database?.latency_ms;

  return (
    <header style={{
      backgroundColor: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-main)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      {/* Top Bar: Brand Identity & Live Institutional Health */}
      <div style={{
        maxWidth: 1440,
        margin: '0 auto',
        padding: '12px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16,
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        {/* Brand identity */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <DrishtiLogo variant="horizontal" size={32} />
        </div>

        {/* Live System Governance Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* IBM Db2 Verified Connection Pill */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            backgroundColor: 'var(--bg-card)',
            padding: '5px 12px',
            borderRadius: 2,
            border: '1px solid var(--border-main)',
            fontSize: 11,
            fontFamily: 'JetBrains Mono, monospace'
          }}>
            <Database size={13} color={dbOnline ? '#FFFFFF' : '#707070'} />
            <span style={{ color: 'var(--text-secondary)' }}>IBM Db2:</span>
            <span style={{
              fontWeight: 600,
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              gap: 5
            }}>
              <span style={{
                width: 5,
                height: 5,
                borderRadius: '50%',
                backgroundColor: dbOnline ? '#FFFFFF' : '#707070',
                display: 'inline-block'
              }} />
              {dbOnline ? 'ONLINE' : 'CONNECTING'}
            </span>
            {latency !== undefined && (
              <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>
                {latency}ms
              </span>
            )}
          </div>

          {/* Zero-Hallucination Governance Tag */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-main)',
            padding: '5px 10px',
            borderRadius: 2,
            fontSize: 10,
            color: 'var(--text-secondary)',
            fontFamily: 'JetBrains Mono, monospace',
            textTransform: 'uppercase',
            letterSpacing: '0.08em'
          }}>
            <Shield size={12} color="#FFFFFF" />
            <span>Db2 Grounded</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs Bar */}
      <div style={{
        maxWidth: 1440,
        margin: '0 auto',
        padding: '0 32px',
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        overflowX: 'auto',
        scrollbarWidth: 'none'
      }}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '11px 16px',
                fontSize: 12,
                fontWeight: isActive ? 600 : 400,
                color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: isActive ? '2px solid #FFFFFF' : '2px solid transparent',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
                letterSpacing: '0.01em',
                fontFamily: 'Inter, sans-serif'
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = '#FFFFFF';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </header>
  );
};
