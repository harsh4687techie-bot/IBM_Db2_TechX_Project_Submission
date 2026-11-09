import React, { useState } from 'react';
import {
  Send,
  FileDown,
  FileSpreadsheet,
  Shield,
  Bot,
  Database,
  Search,
  Layers,
  FileText,
  AlertCircle
} from 'lucide-react';
import type { AgentQueryResponse } from '../types';
import { api } from '../services/api';

interface AgentCopilotViewProps {
  initialPrompt?: string;
  initialTicker?: string;
}

export const AgentCopilotView: React.FC<AgentCopilotViewProps> = ({
  initialPrompt = '',
  initialTicker = ''
}) => {
  const [prompt, setPrompt] = useState<string>(
    initialPrompt || "Analyze NVIDIA's recent volume surge and compare performance against technology sector peers."
  );
  const [targetTicker, setTargetTicker] = useState<string>(initialTicker || 'NVDA');
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<AgentQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'narrative' | 'trace' | 'audit'>('narrative');
  const [auditLogs, setAuditLogs] = useState<any[]>([]);

  const samplePrompts = [
    { label: 'NVDA Volume Breakout', query: "Analyze NVIDIA's recent volume surge and compare against technology sector peers.", ticker: 'NVDA' },
    { label: 'AAPL Anomaly Audit', query: "Investigate Apple's latest price spikes, 52-week boundaries and moving average baseline.", ticker: 'AAPL' },
    { label: 'JPMorgan Sector Standing', query: "Evaluate JPMorgan Chase relative to broader Financials sector performance.", ticker: 'JPM' },
    { label: 'Exxon Energy Spike', query: "Perform deep-dive analysis on Exxon Mobil's recent volatility burst and crude momentum.", ticker: 'XOM' },
  ];

  const handleExecute = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.askAgent(prompt, targetTicker || undefined);
      setResponse(res);
      if (res.session_id) {
        api.getRecentAuditLogs(10).then(setAuditLogs).catch(() => {});
      }
    } catch (err: any) {
      setError(err.message || 'Multi-agent workflow execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const getAgentIcon = (agent: string) => {
    if (agent.includes('Orchestrator')) return <Bot size={14} color="#FFFFFF" />;
    if (agent.includes('DataAnalyst')) return <Database size={14} color="#D0D0D0" />;
    if (agent.includes('Anomaly')) return <AlertCircle size={14} color="#FFFFFF" />;
    if (agent.includes('Sector')) return <Layers size={14} color="#A0A0A0" />;
    if (agent.includes('Research')) return <Search size={14} color="#D0D0D0" />;
    return <FileText size={14} color="#FFFFFF" />;
  };

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
            DRISHTI &bull; AGENTIC FINANCIAL COPILOT
          </div>
          <h1 style={{
            fontSize: 26,
            fontWeight: 600,
            color: '#FFFFFF',
            letterSpacing: '-0.02em'
          }}>
            Institutional Research Terminal
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
            Direct queries dispatched to 6 autonomous agents. All findings strictly grounded in verified Db2 transactions.
          </p>
        </div>

        {/* Zero Hallucination Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-main)',
          padding: '6px 12px',
          borderRadius: 2,
          fontSize: 11,
          fontFamily: 'JetBrains Mono'
        }}>
          <Shield size={13} color="#FFFFFF" />
          <span style={{ color: '#FFFFFF', fontWeight: 600 }}>Zero Hallucination</span>
          <span style={{ color: 'var(--text-muted)' }}>&bull; ACID Grounded</span>
        </div>
      </div>

      {/* Query Dispatch Console */}
      <div className="card">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Preset Prompts */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'JetBrains Mono' }}>
              Quick Inquiries:
            </span>
            {samplePrompts.map((sp) => (
              <button
                key={sp.label}
                className="btn-ghost"
                onClick={() => {
                  setPrompt(sp.query);
                  setTargetTicker(sp.ticker);
                }}
                style={{
                  fontSize: 11,
                  padding: '4px 10px',
                  borderRadius: 2,
                  border: '1px solid var(--border-main)',
                  backgroundColor: 'var(--bg-secondary)',
                  fontFamily: 'JetBrains Mono, monospace'
                }}
              >
                {sp.label}
              </button>
            ))}
          </div>

          {/* Text Area & Input controls */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <textarea
                rows={3}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Submit an institutional inquiry: stock deep dive, volume anomaly scan, or sector benchmark..."
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-main)',
                  borderRadius: 2,
                  color: '#FFFFFF',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  resize: 'none'
                }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, width: 140 }}>
              <input
                type="text"
                placeholder="Ticker (e.g. NVDA)"
                value={targetTicker}
                onChange={(e) => setTargetTicker(e.target.value.toUpperCase())}
                style={{
                  padding: '10px 12px',
                  textAlign: 'center',
                  fontFamily: 'JetBrains Mono, monospace',
                  fontWeight: 600,
                  fontSize: 13
                }}
              />

              <button
                className="btn btn-primary"
                onClick={handleExecute}
                disabled={loading}
                style={{
                  padding: '10px 14px',
                  opacity: loading ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 6
                }}
              >
                <Send size={13} color="#000000" />
                {loading ? 'Executing...' : 'Run Pipeline'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="card" style={{ padding: 40, textAlign: 'center' }}>
          <div style={{
            display: 'inline-block',
            width: 24,
            height: 24,
            border: '2px solid #292929',
            borderTopColor: '#FFFFFF',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
            marginBottom: 12
          }} />
          <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          <div style={{ fontSize: 13, fontWeight: 500, color: '#FFFFFF' }}>
            Dispatching query across 6 autonomous AI agents...
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, fontFamily: 'JetBrains Mono' }}>
            Querying IBM Db2 &bull; Extracting z-scores &bull; Synthesizing evidence
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="card" style={{ border: '1px solid #FFFFFF', padding: 16 }}>
          <div style={{ fontSize: 13, color: '#FFFFFF', fontWeight: 600 }}>Execution Error:</div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>{error}</div>
        </div>
      )}

      {/* Response Display */}
      {response && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Navigation tab bar within response */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid var(--border-main)',
            paddingBottom: 8
          }}>
            <div style={{ display: 'flex', gap: 4 }}>
              {[
                { id: 'narrative', label: 'Executive Synthesis' },
                { id: 'trace', label: `Agent Execution Trace (${response.steps?.length || 6})` },
                { id: 'audit', label: 'Db2 Audit Logs' }
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id as any)}
                  style={{
                    padding: '8px 16px',
                    fontSize: 12,
                    fontWeight: activeTab === t.id ? 600 : 400,
                    color: activeTab === t.id ? '#FFFFFF' : 'var(--text-secondary)',
                    backgroundColor: activeTab === t.id ? 'var(--bg-surface)' : 'transparent',
                    border: activeTab === t.id ? '1px solid var(--border-main)' : '1px solid transparent',
                    borderRadius: 2,
                    cursor: 'pointer',
                    fontFamily: 'Inter, sans-serif'
                  }}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Export Actions */}
            {response.generated_report_uuid && (
              <div style={{ display: 'flex', gap: 8 }}>
                <a
                  href={`/api/reports/${response.generated_report_uuid}/pdf`}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  style={{ fontSize: 11, padding: '6px 12px', textDecoration: 'none' }}
                >
                  <FileDown size={13} /> Download PDF
                </a>
                <a
                  href={`/api/reports/${response.generated_report_uuid}/excel`}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  style={{ fontSize: 11, padding: '6px 12px', textDecoration: 'none' }}
                >
                  <FileSpreadsheet size={13} /> Download Excel
                </a>
              </div>
            )}
          </div>

          {/* Tab 1: Executive Synthesis */}
          {activeTab === 'narrative' && (
            <div className="card">
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 13,
                lineHeight: 1.7,
                color: 'var(--text-secondary)',
                whiteSpace: 'pre-wrap'
              }}>
                {response.response_markdown}
              </div>
            </div>
          )}

          {/* Tab 2: Agent Execution Trace */}
          {activeTab === 'trace' && (
            <div className="card">
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {response.steps.map((s, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: 16
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                      <div style={{
                        width: 28,
                        height: 28,
                        borderRadius: 2,
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-main)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginTop: 2
                      }}>
                        {getAgentIcon(s.agent)}
                      </div>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontSize: 13, fontWeight: 600, color: '#FFFFFF' }}>
                            {s.agent}
                          </span>
                          <span style={{
                            fontSize: 10,
                            fontFamily: 'JetBrains Mono',
                            color: 'var(--text-muted)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.08em'
                          }}>
                            {s.action}
                          </span>
                        </div>
                        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                          {s.detail}
                        </p>
                      </div>
                    </div>

                    <span style={{
                      fontSize: 11,
                      fontFamily: 'JetBrains Mono',
                      color: '#FFFFFF',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-main)',
                      padding: '2px 8px',
                      borderRadius: 2,
                      whiteSpace: 'nowrap'
                    }}>
                      {s.duration_ms}ms
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 3: Db2 Audit Logs */}
          {activeTab === 'audit' && (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Agent</th>
                    <th>Action</th>
                    <th>Status</th>
                    <th style={{ textAlign: 'right' }}>Latency</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.length === 0 ? (
                    <tr>
                      <td colSpan={5} style={{ textAlign: 'center', padding: 24, color: 'var(--text-muted)' }}>
                        Fetching recent audit trail from `AGENT_AUDIT_LOGS`...
                      </td>
                    </tr>
                  ) : (
                    auditLogs.map((log: any, i: number) => (
                      <tr key={i}>
                        <td style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-muted)' }}>
                          {String(log.created_at || '').slice(0, 19)}
                        </td>
                        <td style={{ fontWeight: 600, color: '#FFFFFF' }}>{log.agent_name}</td>
                        <td style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-secondary)' }}>
                          {log.action_type}
                        </td>
                        <td>
                          <span className="badge badge-low">{log.status}</span>
                        </td>
                        <td style={{ textAlign: 'right', fontFamily: 'JetBrains Mono', fontWeight: 600, color: '#FFFFFF' }}>
                          {log.execution_time_ms}ms
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
