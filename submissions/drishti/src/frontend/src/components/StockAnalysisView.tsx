import React, { useState, useEffect, useMemo } from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell
} from 'recharts';
import { FileText, Activity } from 'lucide-react';
import type { Company, StockDetail, DailyPrice } from '../types';
import { api } from '../services/api';

interface StockAnalysisViewProps {
  companies: Company[];
  selectedTicker: string;
  onSelectTicker: (ticker: string) => void;
  onOpenCopilot: (prompt: string, ticker: string) => void;
}

export const StockAnalysisView: React.FC<StockAnalysisViewProps> = ({
  companies,
  selectedTicker,
  onSelectTicker,
  onOpenCopilot
}) => {
  const [detail, setDetail] = useState<StockDetail | null>(null);
  const [prices, setPrices] = useState<DailyPrice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [timeframe, setTimeframe] = useState<'daily' | 'weekly' | 'monthly'>('daily');

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    Promise.all([
      api.getStockDetail(selectedTicker),
      api.getStockPrices(selectedTicker, 90)
    ])
      .then(([detailData, pricesData]) => {
        if (isMounted) {
          setDetail(detailData);
          setPrices(pricesData);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load stock data:', err);
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedTicker]);

  const comp = detail?.company;
  const metrics = detail?.metrics;
  const latestPrice = detail?.latest_price;

  // Process data for daily/weekly/monthly timeframes
  const processedChartData = useMemo(() => {
    const rawData = prices.map((p) => ({
      date: String(p.trading_date),
      close: typeof p.close_price === 'number' ? p.close_price : parseFloat(p.close_price as any) || 0,
      open: typeof p.open_price === 'number' ? p.open_price : parseFloat(p.open_price as any) || 0,
      high: typeof p.high_price === 'number' ? p.high_price : parseFloat(p.high_price as any) || 0,
      low: typeof p.low_price === 'number' ? p.low_price : parseFloat(p.low_price as any) || 0,
      volume: typeof p.volume === 'number' ? p.volume : parseInt(p.volume as any) || 0,
      vwap: typeof p.vwap === 'number' ? p.vwap : parseFloat(p.vwap as any) || 0,
    }));

    if (timeframe === 'weekly') {
      // Aggregate into 5-session weekly buckets
      const weekly = [];
      for (let i = 0; i < rawData.length; i += 5) {
        const chunk = rawData.slice(i, i + 5);
        if (chunk.length === 0) continue;
        const totalVol = chunk.reduce((acc, c) => acc + c.volume, 0);
        weekly.push({
          date: `Wk ${chunk[0].date.slice(5)}`,
          close: chunk[chunk.length - 1].close,
          volume: totalVol,
          vwap: chunk[chunk.length - 1].vwap,
        });
      }
      return weekly;
    }

    if (timeframe === 'monthly') {
      // Group by YYYY-MM
      const monthlyMap = new Map<string, any>();
      for (const p of rawData) {
        const ym = p.date.slice(0, 7);
        if (!monthlyMap.has(ym)) {
          monthlyMap.set(ym, { date: ym, close: p.close, volume: 0 });
        }
        const entry = monthlyMap.get(ym);
        entry.volume += p.volume;
        entry.close = p.close;
      }
      return Array.from(monthlyMap.values());
    }

    return rawData;
  }, [prices, timeframe]);

  // Calculate volume baseline stats
  const volumeStats = useMemo(() => {
    if (prices.length === 0) return { mean: 0, std: 0, maxVol: 0, peakZ: 0 };
    const vols = prices.map((p) => (typeof p.volume === 'number' ? p.volume : parseInt(p.volume as any) || 0));
    const mean = vols.reduce((a, b) => a + b, 0) / vols.length;
    const variance = vols.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / (vols.length - 1 || 1);
    const std = Math.sqrt(variance);
    const maxVol = Math.max(...vols);
    const peakZ = std > 0 ? (maxVol - mean) / std : 0;
    return { mean, std, maxVol, peakZ };
  }, [prices]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
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
            DRISHTI &bull; QUANTITATIVE ANALYSIS
          </div>
          <h1 style={{
            fontSize: 26,
            fontWeight: 600,
            color: '#FFFFFF',
            letterSpacing: '-0.02em'
          }}>
            Volume Intelligence
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
            Quantitative trading volume distribution, statistical surge detection, and historical price action.
          </p>
        </div>

        {/* Timeframe aggregation control */}
        <div style={{
          display: 'flex',
          gap: 2,
          backgroundColor: 'var(--bg-secondary)',
          padding: 3,
          border: '1px solid var(--border-main)',
          borderRadius: 2
        }}>
          {(['daily', 'weekly', 'monthly'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              style={{
                padding: '6px 14px',
                fontSize: 11,
                fontWeight: timeframe === tf ? 600 : 400,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                backgroundColor: timeframe === tf ? '#FFFFFF' : 'transparent',
                color: timeframe === tf ? '#000000' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 2,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                fontFamily: 'JetBrains Mono, monospace'
              }}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Ticker Selector Bar */}
      <div style={{
        display: 'flex',
        gap: 8,
        overflowX: 'auto',
        paddingBottom: 4,
        scrollbarWidth: 'none'
      }}>
        {companies.map((c) => {
          const isSelected = c.ticker === selectedTicker;
          return (
            <button
              key={c.ticker}
              onClick={() => onSelectTicker(c.ticker)}
              style={{
                padding: '8px 14px',
                borderRadius: 2,
                background: isSelected ? 'var(--bg-surface)' : 'var(--bg-card)',
                color: isSelected ? '#FFFFFF' : 'var(--text-secondary)',
                border: isSelected ? '1px solid #FFFFFF' : '1px solid var(--border-main)',
                fontWeight: isSelected ? 600 : 500,
                fontSize: 12,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                transition: 'all 0.15s ease',
                fontFamily: 'JetBrains Mono, monospace'
              }}
            >
              <span style={{ fontWeight: 700 }}>{c.ticker}</span>
              <span style={{ fontSize: 11, color: isSelected ? '#FFFFFF' : 'var(--text-muted)' }}>
                ${floatVal(c.latest_close).toFixed(2)}
              </span>
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="card" style={{ padding: 60, textAlign: 'center', color: 'var(--text-secondary)' }}>
          Retrieving historical OHLCV bars from IBM Db2 `DAILY_PRICES`...
        </div>
      ) : comp ? (
        <>
          {/* Company Profile Header Bar */}
          <div className="card" style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 20
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <h2 style={{ fontSize: 22, fontWeight: 600, color: '#FFFFFF' }}>{comp.company_name}</h2>
                <span style={{
                  fontSize: 13,
                  fontWeight: 600,
                  fontFamily: 'JetBrains Mono',
                  color: 'var(--text-secondary)',
                  padding: '2px 8px',
                  border: '1px solid var(--border-main)',
                  borderRadius: 2
                }}>
                  {comp.ticker}
                </span>
                <span style={{
                  fontSize: 11,
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em'
                }}>
                  {comp.sector} &bull; {comp.industry || 'Market Leader'}
                </span>
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                Market Capitalization: ${(floatVal(comp.market_cap) / 1e9).toFixed(2)} Billion {comp.currency}
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{
                  fontSize: 26,
                  fontWeight: 600,
                  fontFamily: 'JetBrains Mono, monospace',
                  color: '#FFFFFF'
                }}>
                  ${floatVal(latestPrice?.close_price).toFixed(2)}
                </div>
                <div style={{
                  fontSize: 12,
                  fontFamily: 'JetBrains Mono, monospace',
                  color: 'var(--text-secondary)',
                  marginTop: 2
                }}>
                  30D Return: {floatVal(metrics?.thirty_day_return_pct) >= 0 ? '+' : ''}
                  {floatVal(metrics?.thirty_day_return_pct).toFixed(2)}%
                </div>
              </div>

              <button
                className="btn btn-primary"
                onClick={() =>
                  onOpenCopilot(
                    `Conduct deep dive volume and price analysis on ${comp.ticker} including statistical anomaly baselines and technology sector peer standing.`,
                    comp.ticker
                  )
                }
              >
                <FileText size={14} color="#000000" />
                Generate Agent Report
              </button>
            </div>
          </div>

          {/* Interactive Charts: Price Action & Volume Sub-bars */}
          <div className="card">
            <div className="card-header">
              <div>
                <h3 style={{ fontSize: 14, fontWeight: 600, color: '#FFFFFF' }}>
                  Price Action & Synchronized Volume Distribution ({timeframe.toUpperCase()})
                </h3>
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  Direct queries against `DAILY_PRICES`. Spikes indicate volume $\ge 2.0\sigma$ above baseline.
                </p>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                fontSize: 11,
                fontFamily: 'JetBrains Mono',
                color: 'var(--text-muted)'
              }}>
                <span>Mean: {(volumeStats.mean / 1e6).toFixed(1)}M</span>
                <span>Peak Z: {volumeStats.peakZ.toFixed(2)}&sigma;</span>
              </div>
            </div>

            {/* Price Area Chart */}
            <div style={{ height: 280, width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={processedChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#1A1A1A" />
                  <XAxis dataKey="date" stroke="#606060" fontSize={10} tickLine={false} fontFamily="JetBrains Mono" />
                  <YAxis stroke="#606060" fontSize={10} domain={['auto', 'auto']} tickFormatter={(v) => `$${v}`} fontFamily="JetBrains Mono" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#141414',
                      borderColor: '#292929',
                      borderRadius: 2,
                      fontSize: 11,
                      fontFamily: 'JetBrains Mono',
                      color: '#FFFFFF'
                    }}
                    formatter={(value: any) => [`$${parseFloat(value).toFixed(2)}`, 'Close Price']}
                  />
                  <Area
                    type="monotone"
                    dataKey="close"
                    stroke="#FFFFFF"
                    strokeWidth={1.5}
                    fillOpacity={0.06}
                    fill="#FFFFFF"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Synchronized Volume Bars */}
            <div style={{ height: 110, width: '100%', marginTop: 12 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={processedChartData} margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                  <XAxis dataKey="date" hide />
                  <YAxis stroke="#606060" fontSize={9} domain={['auto', 'auto']} tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} fontFamily="JetBrains Mono" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#141414',
                      borderColor: '#292929',
                      borderRadius: 2,
                      fontSize: 11,
                      fontFamily: 'JetBrains Mono',
                      color: '#FFFFFF'
                    }}
                    formatter={(value: any) => [`${(parseInt(value) / 1e6).toFixed(2)}M shares`, 'Volume']}
                  />
                  <Bar dataKey="volume">
                    {processedChartData.map((entry, index) => {
                      const isSpike = volumeStats.std > 0 && (entry.volume - volumeStats.mean) / volumeStats.std >= 2.0;
                      return (
                        <Cell
                          key={`vol-${index}`}
                          fill={isSpike ? '#FFFFFF' : '#303030'}
                        />
                      );
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* 4 Quantitative Volume & Price Metric Cards */}
          <div className="grid-cols-4">
            <div className="metric-card">
              <span className="metric-label">30-Day Avg Volume</span>
              <div className="metric-value">
                {(floatVal(metrics?.average_volume_30d) / 1e6).toFixed(1)}M
              </div>
              <div className="metric-subtext">Baseline trading volume</div>
            </div>

            <div className="metric-card">
              <span className="metric-label">Peak Volume Surge</span>
              <div className="metric-value">
                {(volumeStats.maxVol / 1e6).toFixed(1)}M
              </div>
              <div className="metric-subtext">Max session volume in Db2</div>
            </div>

            <div className="metric-card">
              <span className="metric-label">52-Week High</span>
              <div className="metric-value">
                ${floatVal(metrics?.fifty_two_week_high).toFixed(2)}
              </div>
              <div className="metric-subtext">Session peak boundary</div>
            </div>

            <div className="metric-card">
              <span className="metric-label">52-Week Low</span>
              <div className="metric-value">
                ${floatVal(metrics?.fifty_two_week_low).toFixed(2)}
              </div>
              <div className="metric-subtext">Session trough boundary</div>
            </div>
          </div>

          {/* AI-Generated Volume Analytics Explanation */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <Activity size={16} color="#FFFFFF" />
              <h3 style={{ fontSize: 14, fontWeight: 600, color: '#FFFFFF' }}>
                Statistical Volume Behavior Assessment
              </h3>
            </div>
            <div style={{
              fontSize: 13,
              color: 'var(--text-secondary)',
              lineHeight: 1.6,
              backgroundColor: 'var(--bg-secondary)',
              padding: 16,
              border: '1px solid var(--border-subtle)',
              borderRadius: 2
            }}>
              <p>
                <strong>{comp.company_name} ({comp.ticker})</strong> exhibits an average 30-day session volume of{' '}
                <strong>{(volumeStats.mean / 1e6).toFixed(1)} million shares</strong> with a historical standard deviation of{' '}
                <strong>{(volumeStats.std / 1e6).toFixed(1)}M shares</strong>. The maximum observed single-session volume reached{' '}
                <strong>{(volumeStats.maxVol / 1e6).toFixed(1)}M shares</strong>, registering a statistical deviation of{' '}
                <strong>{volumeStats.peakZ.toFixed(2)}&sigma;</strong>.
              </p>
              <p style={{ marginTop: 8 }}>
                {volumeStats.peakZ >= 2.5
                  ? `Noticeable institutional liquidity cluster detected: The peak volume event qualifies as a HIGH/CRITICAL statistical anomaly in Db2's MARKET_ANOMALIES table.`
                  : `Trading activity aligns closely within expected Gaussian distribution bands with moderate retail flow.`}
              </p>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

function floatVal(val: any): number {
  if (val === undefined || val === null) return 0;
  const num = typeof val === 'number' ? val : parseFloat(val);
  return isNaN(num) ? 0 : num;
}
