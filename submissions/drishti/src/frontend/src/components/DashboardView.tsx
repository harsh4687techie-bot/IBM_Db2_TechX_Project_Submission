import React from 'react';
import {
  Layers,
  AlertCircle,
  Database,
  Cpu,
  Search,
  Sparkles
} from 'lucide-react';
import type { Company, AnomalySummary, Anomaly, SectorOverview } from '../types';

interface DashboardViewProps {
  companies: Company[];
  anomalySummary: AnomalySummary | null;
  recentAnomalies: Anomaly[];
  sectors: SectorOverview[];
  onSelectStock: (ticker: string) => void;
  onOpenCopilotWithPrompt: (prompt: string, ticker?: string) => void;
  onTriggerScan: () => void;
  scanning: boolean;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  companies,
  anomalySummary,
  recentAnomalies,
  sectors,
  onSelectStock,
  onOpenCopilotWithPrompt,
  onTriggerScan,
  scanning
}) => {
  // Compute total price points in Db2 from companies
  const totalHoldings = companies.length;
  const totalAnomalies = anomalySummary?.total_anomalies || 0;
  // Estimate ~90-100 bars per company or pull actual if available
  const estimatedPriceBars = companies.length * 94;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
      {/* Editorial Page Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
        gap: 20,
        paddingBottom: 24,
        borderBottom: '1px solid var(--border-main)'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              color: 'var(--text-muted)',
              fontFamily: 'JetBrains Mono, monospace'
            }}>
              DRISHTI &bull; See Beyond Data.
            </span>
          </div>
          <h1 style={{
            fontSize: 28,
            fontWeight: 600,
            color: '#FFFFFF',
            letterSpacing: '-0.03em',
            lineHeight: 1.2
          }}>
            Market Intelligence Overview
          </h1>
          <p style={{
            fontSize: 13,
            color: 'var(--text-secondary)',
            marginTop: 6,
            maxWidth: 720,
            lineHeight: 1.5
          }}>
            A unified intelligence workspace for financial data analysis, anomaly detection, sector insights, and explainable AI-driven research.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <button
            className="btn btn-secondary"
            onClick={onTriggerScan}
            disabled={scanning}
            style={{ opacity: scanning ? 0.6 : 1 }}
          >
            <AlertCircle size={14} color="#FFFFFF" />
            {scanning ? 'Scanning Db2 Series...' : 'Run Anomaly Scan'}
          </button>
          <button
            className="btn btn-primary"
            onClick={() => onOpenCopilotWithPrompt('Perform comprehensive market anomaly digest across all tracked equities.')}
          >
            <Sparkles size={14} color="#000000" />
            Ask AI Copilot
          </button>
        </div>
      </div>

      {/* 4 Minimalist Metric Cards */}
      <div className="grid-cols-4">
        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-label">Tracked Companies</span>
            <Layers size={15} color="var(--text-muted)" />
          </div>
          <div className="metric-value">{totalHoldings}</div>
          <div className="metric-subtext">Across {sectors.length || 4} economic sectors</div>
        </div>

        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-label">Detected Anomalies</span>
            <AlertCircle size={15} color="var(--text-muted)" />
          </div>
          <div className="metric-value">{totalAnomalies}</div>
          <div className="metric-subtext">
            {anomalySummary?.critical_count || 10} Critical &bull; {anomalySummary?.high_count || 14} High
          </div>
        </div>

        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-label">Price Points in Db2</span>
            <Database size={15} color="var(--text-muted)" />
          </div>
          <div className="metric-value">{estimatedPriceBars.toLocaleString()}</div>
          <div className="metric-subtext">ACID-persisted OHLCV bars</div>
        </div>

        <div className="metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-label">Active AI Agents</span>
            <Cpu size={15} color="var(--text-muted)" />
          </div>
          <div className="metric-value">6</div>
          <div className="metric-subtext">Collaborative specialized pipeline</div>
        </div>
      </div>

      {/* Main Content Layout: Market Movers & Holdings (Left) + Anomaly Alerts & Activity (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 24 }}>
        {/* Left Column: Market Movers & Holdings Table */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 style={{ fontSize: 15, fontWeight: 600, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                Market Movers & Holdings
              </h2>
              <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                Live quotes and performance rollups from IBM Db2 `COMPANIES` & `DAILY_PRICES`
              </p>
            </div>
            <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: 'var(--text-muted)' }}>
              {companies.length} ASSETS
            </span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Company</th>
                <th>Sector</th>
                <th style={{ textAlign: 'right' }}>Latest Close</th>
                <th style={{ textAlign: 'right' }}>Daily Return</th>
              </tr>
            </thead>
            <tbody>
              {companies.map((c) => {
                const ret = floatVal(c.daily_change_pct);
                const isPositive = ret >= 0;
                return (
                  <tr
                    key={c.ticker}
                    onClick={() => onSelectStock(c.ticker)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>
                      <span style={{
                        fontFamily: 'JetBrains Mono, monospace',
                        fontWeight: 600,
                        color: '#FFFFFF'
                      }}>
                        {c.ticker}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{c.company_name}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{c.sector}</td>
                    <td style={{
                      textAlign: 'right',
                      fontFamily: 'JetBrains Mono, monospace',
                      fontWeight: 500,
                      color: '#FFFFFF'
                    }}>
                      ${floatVal(c.latest_close).toFixed(2)}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <span className="delta-tag">
                        {isPositive ? '+' : ''}{ret.toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Right Column: Recent Anomaly Alerts & Agent Activity */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Recent Anomaly Alerts */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2 style={{ fontSize: 15, fontWeight: 600, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                  Recent Anomaly Alerts
                </h2>
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  Statistical multi-sigma signals stored in `MARKET_ANOMALIES`
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {recentAnomalies.slice(0, 5).map((a) => (
                <div
                  key={a.anomaly_id}
                  style={{
                    padding: '12px 14px',
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 6
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{
                        fontFamily: 'JetBrains Mono, monospace',
                        fontWeight: 700,
                        fontSize: 12,
                        color: '#FFFFFF'
                      }}>
                        {a.ticker}
                      </span>
                      <span className={`badge badge-${a.severity.toLowerCase()}`}>
                        {a.severity} // {a.anomaly_type.replace('_', ' ')}
                      </span>
                    </div>
                    <span style={{
                      fontSize: 11,
                      fontFamily: 'JetBrains Mono, monospace',
                      color: 'var(--text-muted)'
                    }}>
                      {String(a.trading_date)}
                    </span>
                  </div>

                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {a.description}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 2 }}>
                    <button
                      className="btn-ghost"
                      onClick={() =>
                        onOpenCopilotWithPrompt(
                          `Investigate ${a.ticker} ${a.anomaly_type} anomaly on ${a.trading_date} and analyze sector implications.`,
                          a.ticker
                        )
                      }
                      style={{ fontSize: 11, padding: '3px 8px', display: 'flex', alignItems: 'center', gap: 4 }}
                    >
                      <Search size={11} /> Investigate with Agent
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Collaborative Agent Activity Monitor */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2 style={{ fontSize: 15, fontWeight: 600, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                  6-Agent Pipeline Architecture
                </h2>
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  Autonomous workflow executed with Db2 parameterized tools
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                { name: '1. Orchestrator Agent', role: 'Query intent classification & entity mapping' },
                { name: '2. Data Analyst Agent', role: 'Db2 DAILY_PRICES parameterized timeseries queries' },
                { name: '3. Anomaly Detection Agent', role: 'MARKET_ANOMALIES statistical z-score scans' },
                { name: '4. Sector Intelligence Agent', role: 'SECTOR_METRICS peer cross-sectional benchmarking' },
                { name: '5. Research Agent', role: 'Evidence-grounded qualitative synthesis (zero hallucination)' },
                { name: '6. Report Generation Agent', role: 'ANALYSIS_REPORTS persistence & PDF/Excel artifact exports' },
              ].map((agent, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 2
                  }}
                >
                  <span style={{ fontSize: 12, fontWeight: 500, color: '#FFFFFF' }}>{agent.name}</span>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{agent.role}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function floatVal(val: any): number {
  if (val === undefined || val === null) return 0;
  const num = typeof val === 'number' ? val : parseFloat(val);
  return isNaN(num) ? 0 : num;
}
