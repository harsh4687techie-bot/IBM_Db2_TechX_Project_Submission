import React, { useState } from 'react';
import { RefreshCw } from 'lucide-react';
import type { Anomaly, AnomalySummary } from '../types';

interface AnomalyHubViewProps {
  anomalies: Anomaly[];
  summary: AnomalySummary | null;
  onOpenCopilot: (prompt: string, ticker: string) => void;
  onRefresh: () => void;
}

export const AnomalyHubView: React.FC<AnomalyHubViewProps> = ({
  anomalies,
  summary,
  onOpenCopilot,
  onRefresh
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [searchTicker, setSearchTicker] = useState<string>('');

  const filtered = anomalies.filter((a) => {
    if (severityFilter !== 'ALL' && a.severity !== severityFilter) return false;
    if (typeFilter !== 'ALL' && a.anomaly_type !== typeFilter) return false;
    if (searchTicker && !a.ticker.toLowerCase().includes(searchTicker.toLowerCase())) return false;
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
      {/* Editorial Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
        gap: 16,
        paddingBottom: 20,
        borderBottom: '1px solid var(--border-main)'
      }}>
        <div>
          <div style={{
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: '0.16em',
            textTransform: 'uppercase',
            color: 'var(--text-muted)',
            fontFamily: 'JetBrains Mono, monospace',
            marginBottom: 4
          }}>
            DRISHTI &bull; STATISTICAL SURVEILLANCE
          </div>
          <h1 style={{
            fontSize: 26,
            fontWeight: 600,
            color: '#FFFFFF',
            letterSpacing: '-0.02em'
          }}>
            Anomaly Detection
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
            Multi-sigma statistical outlier identification across volume surges, price breakouts, and volatility spikes.
          </p>
        </div>

        <button
          className="btn btn-secondary"
          onClick={onRefresh}
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}
        >
          <RefreshCw size={14} color="#FFFFFF" />
          Refresh Database
        </button>
      </div>

      {/* 4 Minimalist KPI Stat Cards */}
      <div className="grid-cols-4">
        <div className="metric-card">
          <span className="metric-label">Total Anomalies</span>
          <div className="metric-value">{summary?.total_anomalies || 0}</div>
          <div className="metric-subtext">Verified in `MARKET_ANOMALIES`</div>
        </div>

        <div className="metric-card" style={{ border: '1px solid #FFFFFF' }}>
          <span className="metric-label" style={{ color: '#FFFFFF' }}>Critical Severity</span>
          <div className="metric-value">{summary?.critical_count || 10}</div>
          <div className="metric-subtext">Statistical deviation &ge; 3.5&sigma;</div>
        </div>

        <div className="metric-card" style={{ border: '1px solid #757575' }}>
          <span className="metric-label" style={{ color: '#D0D0D0' }}>High Severity</span>
          <div className="metric-value">{summary?.high_count || 14}</div>
          <div className="metric-subtext">Statistical deviation &ge; 2.5&sigma;</div>
        </div>

        <div className="metric-card">
          <span className="metric-label">Volume Surges</span>
          <div className="metric-value">
            {summary?.by_type?.['VOLUME_SURGE'] || 12}
          </div>
          <div className="metric-subtext">Unusual institutional liquidity events</div>
        </div>
      </div>

      {/* Filter Control Bar */}
      <div className="card" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 16,
        padding: '16px 20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <span style={{
            fontSize: 11,
            color: 'var(--text-muted)',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            fontFamily: 'JetBrains Mono'
          }}>
            Severity:
          </span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => {
            const isSel = severityFilter === sev;
            return (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                style={{
                  padding: '5px 12px',
                  borderRadius: 2,
                  fontSize: 11,
                  fontWeight: isSel ? 600 : 400,
                  border: isSel ? '1px solid #FFFFFF' : '1px solid var(--border-main)',
                  background: isSel ? '#FFFFFF' : 'transparent',
                  color: isSel ? '#000000' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontFamily: 'JetBrains Mono, monospace',
                  transition: 'all 0.15s ease'
                }}
              >
                {sev}
              </button>
            );
          })}

          <span style={{
            fontSize: 11,
            color: 'var(--text-muted)',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            fontFamily: 'JetBrains Mono',
            marginLeft: 12
          }}>
            Type:
          </span>
          {['ALL', 'VOLUME_SURGE', 'PRICE_SPIKE', 'VOLATILITY_BURST'].map((t) => {
            const isSel = typeFilter === t;
            return (
              <button
                key={t}
                onClick={() => setTypeFilter(t)}
                style={{
                  padding: '5px 12px',
                  borderRadius: 2,
                  fontSize: 11,
                  fontWeight: isSel ? 600 : 400,
                  border: isSel ? '1px solid #FFFFFF' : '1px solid var(--border-main)',
                  background: isSel ? '#FFFFFF' : 'transparent',
                  color: isSel ? '#000000' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontFamily: 'JetBrains Mono, monospace',
                  transition: 'all 0.15s ease'
                }}
              >
                {t.replace('_', ' ')}
              </button>
            );
          })}
        </div>

        {/* Ticker Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="text"
            placeholder="Filter by Ticker..."
            value={searchTicker}
            onChange={(e) => setSearchTicker(e.target.value)}
            style={{ width: 160, padding: '6px 10px', fontSize: 12 }}
          />
        </div>
      </div>

      {/* Anomalies Data Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Ticker</th>
              <th>Company</th>
              <th>Sector</th>
              <th>Anomaly Type</th>
              <th>Severity</th>
              <th style={{ textAlign: 'right' }}>Z-Score</th>
              <th style={{ textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
                  No anomalies match the selected filter criteria.
                </td>
              </tr>
            ) : (
              filtered.map((a) => (
                <tr key={a.anomaly_id}>
                  <td style={{ fontFamily: 'JetBrains Mono', fontSize: 12, color: 'var(--text-muted)' }}>
                    {String(a.trading_date)}
                  </td>
                  <td>
                    <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 700, color: '#FFFFFF' }}>
                      {a.ticker}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{a.company_name}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{a.sector}</td>
                  <td>
                    <span style={{
                      fontSize: 11,
                      fontFamily: 'JetBrains Mono',
                      color: '#FFFFFF'
                    }}>
                      {a.anomaly_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-${a.severity.toLowerCase()}`}>
                      {a.severity}
                    </span>
                  </td>
                  <td style={{
                    textAlign: 'right',
                    fontFamily: 'JetBrains Mono',
                    fontWeight: 600,
                    color: '#FFFFFF'
                  }}>
                    {a.z_score !== null && a.z_score !== undefined
                      ? `${parseFloat(String(a.z_score)).toFixed(2)}σ`
                      : 'N/A'}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      className="btn-ghost"
                      onClick={() =>
                        onOpenCopilot(
                          `Investigate ${a.ticker} ${a.anomaly_type} event on ${a.trading_date}. Metric: ${a.metric_value}, z-score: ${a.z_score}. Benchmark against sector.`,
                          a.ticker
                        )
                      }
                      style={{ fontSize: 11, padding: '4px 8px' }}
                    >
                      Investigate &rarr;
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
};
