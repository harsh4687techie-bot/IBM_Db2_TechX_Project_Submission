import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell
} from 'recharts';
import { Sparkles } from 'lucide-react';
import type { SectorOverview, Company } from '../types';

interface SectorIntelligenceViewProps {
  sectors: SectorOverview[];
  companies: Company[];
  onSelectStock: (ticker: string) => void;
  onOpenCopilot: (prompt: string) => void;
}

export const SectorIntelligenceView: React.FC<SectorIntelligenceViewProps> = ({
  sectors,
  companies,
  onSelectStock,
  onOpenCopilot
}) => {
  const chartData = sectors.map((s) => ({
    name: s.sector,
    returnPct: floatVal(s.latest_avg_return_pct),
    stocks: s.stock_count,
    anomalies: s.anomaly_count
  }));

  // Monochrome shade generator for sector comparison bars
  const monochromeFills = ['#FFFFFF', '#D5D5D5', '#AAAAAA', '#808080', '#555555', '#333333'];

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
            DRISHTI &bull; CROSS-SECTIONAL BENCHMARKS
          </div>
          <h1 style={{
            fontSize: 26,
            fontWeight: 600,
            color: '#FFFFFF',
            letterSpacing: '-0.02em'
          }}>
            Sector Intelligence
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
            Aggregated sector performance rollups, peer constituent benchmarking, and anomaly distribution.
          </p>
        </div>

        <button
          className="btn btn-primary"
          onClick={() => onOpenCopilot('Compare all market sectors by performance, volume trends, and statistical anomaly clusters.')}
        >
          <Sparkles size={14} color="#000000" />
          Ask Sector Intelligence Agent
        </button>
      </div>

      {/* Sector Overview Grid */}
      <div className="grid-cols-4">
        {sectors.map((sec) => {
          const ret = floatVal(sec.latest_avg_return_pct);
          const isPositive = ret >= 0;
          return (
            <div key={sec.sector} className="metric-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="metric-label">{sec.sector}</span>
                <span className="delta-tag">
                  {isPositive ? '+' : ''}{ret.toFixed(2)}%
                </span>
              </div>
              <div className="metric-value">{sec.stock_count} Holdings</div>
              <div className="metric-subtext">
                {sec.anomaly_count} detected anomaly events
              </div>
            </div>
          );
        })}
      </div>

      {/* Cross-Sector Performance Comparison Chart */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 style={{ fontSize: 15, fontWeight: 600, color: '#FFFFFF' }}>
              Cross-Sector Average Return Performance
            </h2>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
              Dynamically aggregated from IBM Db2 `SECTOR_METRICS` across constituents
            </p>
          </div>
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1A1A1A" vertical={false} />
              <XAxis dataKey="name" stroke="#606060" fontSize={11} fontFamily="JetBrains Mono" />
              <YAxis stroke="#606060" fontSize={10} tickFormatter={(v) => `${v}%`} fontFamily="JetBrains Mono" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141414',
                  borderColor: '#292929',
                  borderRadius: 2,
                  fontSize: 11,
                  fontFamily: 'JetBrains Mono',
                  color: '#FFFFFF'
                }}
                formatter={(val: any) => [`${parseFloat(val).toFixed(2)}%`, 'Average Return']}
              />
              <Bar dataKey="returnPct">
                {chartData.map((_, index) => (
                  <Cell
                    key={`sector-cell-${index}`}
                    fill={monochromeFills[index % monochromeFills.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sector Holdings Breakdown Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-main)' }}>
          <h2 style={{ fontSize: 15, fontWeight: 600, color: '#FFFFFF' }}>
            Constituent Equities & Sector Valuations
          </h2>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
            Master listings from `COMPANIES` joined with latest session closes
          </p>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Sector</th>
              <th>Ticker</th>
              <th>Company Name</th>
              <th>Industry</th>
              <th style={{ textAlign: 'right' }}>Market Cap</th>
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
                  <td style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>{c.sector}</td>
                  <td>
                    <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 700, color: '#FFFFFF' }}>
                      {c.ticker}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{c.company_name}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{c.industry || 'N/A'}</td>
                  <td style={{ textAlign: 'right', fontFamily: 'JetBrains Mono' }}>
                    ${(floatVal(c.market_cap) / 1e9).toFixed(1)}B
                  </td>
                  <td style={{ textAlign: 'right', fontFamily: 'JetBrains Mono', fontWeight: 600 }}>
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
    </div>
  );
};

function floatVal(val: any): number {
  if (val === undefined || val === null) return 0;
  const num = typeof val === 'number' ? val : parseFloat(val);
  return isNaN(num) ? 0 : num;
}
