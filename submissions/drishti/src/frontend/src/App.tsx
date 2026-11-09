import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { DashboardView } from './components/DashboardView';
import { StockAnalysisView } from './components/StockAnalysisView';
import { AnomalyHubView } from './components/AnomalyHubView';
import { SectorIntelligenceView } from './components/SectorIntelligenceView';
import { AgentCopilotView } from './components/AgentCopilotView';
import { IngestionView } from './components/IngestionView';
import { ReportsHistoryView } from './components/ReportsHistoryView';
import { SettingsView } from './components/SettingsView';
import type { Company, AnomalySummary, Anomaly, SectorOverview, HealthStatus } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const tabParam = params.get('tab') || window.location.hash.replace('#', '');
      if (tabParam && ['dashboard', 'stocks', 'anomalies', 'sectors', 'copilot', 'reports', 'ingestion', 'settings'].includes(tabParam)) {
        return tabParam;
      }
    }
    return 'dashboard';
  });
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [anomalySummary, setAnomalySummary] = useState<AnomalySummary | null>(null);
  const [recentAnomalies, setRecentAnomalies] = useState<Anomaly[]>([]);
  const [sectors, setSectors] = useState<SectorOverview[]>([]);
  const [selectedStock, setSelectedStock] = useState<string>('AAPL');
  const [copilotPrompt, setCopilotPrompt] = useState<string>('');
  const [copilotTicker, setCopilotTicker] = useState<string>('');
  const [scanning, setScanning] = useState<boolean>(false);

  const loadData = async () => {
    try {
      const [h, comps, anomSum, anoms, secs] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getStocks().catch(() => []),
        api.getAnomalySummary().catch(() => null),
        api.getAnomalies({ limit: 40 }).catch(() => []),
        api.getSectors().catch(() => [])
      ]);

      setHealth(h);
      setCompanies(comps);
      setAnomalySummary(anomSum);
      setRecentAnomalies(anoms);
      setSectors(secs);

      if (comps.length > 0 && !comps.some((c) => c.ticker === selectedStock)) {
        setSelectedStock(comps[0].ticker);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    }
  };

  useEffect(() => {
    loadData();
    // Periodic health ping every 30s
    const timer = setInterval(() => {
      api.getHealth().then(setHealth).catch(() => {});
    }, 30000);
    return () => clearInterval(timer);
  }, []);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      url.searchParams.set('tab', tab);
      window.history.replaceState(null, '', url.toString());
    }
  };

  const handleSelectStock = (ticker: string) => {
    setSelectedStock(ticker);
    handleTabChange('stocks');
  };

  const handleOpenCopilotWithPrompt = (prompt: string, ticker?: string) => {
    setCopilotPrompt(prompt);
    if (ticker) setCopilotTicker(ticker);
    handleTabChange('copilot');
  };

  const handleTriggerScan = async () => {
    setScanning(true);
    try {
      await api.triggerAnomalyScan();
      await loadData();
    } catch (err) {
      console.error('Scan error:', err);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="app-container">
      <Header activeTab={activeTab} setActiveTab={handleTabChange} health={health} />

      <main className="content-wrapper">
        {activeTab === 'dashboard' && (
          <DashboardView
            companies={companies}
            anomalySummary={anomalySummary}
            recentAnomalies={recentAnomalies}
            sectors={sectors}
            onSelectStock={handleSelectStock}
            onOpenCopilotWithPrompt={handleOpenCopilotWithPrompt}
            onTriggerScan={handleTriggerScan}
            scanning={scanning}
          />
        )}

        {activeTab === 'stocks' && (
          <StockAnalysisView
            companies={companies}
            selectedTicker={selectedStock}
            onSelectTicker={setSelectedStock}
            onOpenCopilot={handleOpenCopilotWithPrompt}
          />
        )}

        {activeTab === 'anomalies' && (
          <AnomalyHubView
            anomalies={recentAnomalies}
            summary={anomalySummary}
            onOpenCopilot={handleOpenCopilotWithPrompt}
            onRefresh={loadData}
          />
        )}

        {activeTab === 'sectors' && (
          <SectorIntelligenceView
            sectors={sectors}
            companies={companies}
            onSelectStock={handleSelectStock}
            onOpenCopilot={(p) => handleOpenCopilotWithPrompt(p)}
          />
        )}

        {activeTab === 'copilot' && (
          <AgentCopilotView
            initialPrompt={copilotPrompt}
            initialTicker={copilotTicker}
          />
        )}

        {activeTab === 'reports' && (
          <ReportsHistoryView />
        )}

        {activeTab === 'ingestion' && (
          <IngestionView onDataIngested={loadData} />
        )}

        {activeTab === 'settings' && (
          <SettingsView health={health} onRefreshHealth={loadData} />
        )}
      </main>

      <footer style={{
        marginTop: 'auto',
        borderTop: '1px solid var(--border-main)',
        padding: '20px 32px',
        fontSize: 11,
        color: 'var(--text-muted)',
        backgroundColor: 'var(--bg-secondary)',
        fontFamily: 'Inter, sans-serif'
      }}>
        <div style={{ maxWidth: 1440, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontWeight: 700, letterSpacing: '0.12em', color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>DRISHTI</span>
            <span>&bull;</span>
            <span>See Beyond Data.</span>
            <span>&bull;</span>
            <span>IBM Db2 + Agentic AI Platform</span>
          </div>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--text-muted)' }}>
            IBM Db2 Community Edition &bull; FastAPI &bull; React 19 &bull; Vite &bull; Recharts
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
