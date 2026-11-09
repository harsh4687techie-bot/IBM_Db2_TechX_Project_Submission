import React, { useState, useEffect } from 'react';
import {
  FileDown,
  FileSpreadsheet
} from 'lucide-react';
import type { ReportItem } from '../types';
import { api } from '../services/api';

export const ReportsHistoryView: React.FC = () => {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedReport, setSelectedReport] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getReports()
      .then((data) => {
        if (isMounted) {
          setReports(data);
          if (data.length > 0) {
            api.getReportDetail(data[0].report_uuid).then(setSelectedReport).catch(() => {});
          }
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load reports:', err);
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleSelectReport = (uuid: string) => {
    api.getReportDetail(uuid).then(setSelectedReport).catch(console.error);
  };

  const filtered = reports.filter((r) => {
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const matchTitle = r.report_title.toLowerCase().includes(term);
      const matchTicker = (r.target_ticker || '').toLowerCase().includes(term);
      return matchTitle || matchTicker;
    }
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
            DRISHTI &bull; ARTIFACT REPOSITORY
          </div>
          <h1 style={{
            fontSize: 26,
            fontWeight: 600,
            color: '#FFFFFF',
            letterSpacing: '-0.02em'
          }}>
            Reports & Analysis History
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
            Downloadable executive intelligence briefings compiled by ReportGenerationAgent and persisted in IBM Db2 `ANALYSIS_REPORTS`.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <input
            type="text"
            placeholder="Search reports by title or ticker..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: 260, padding: '8px 12px', fontSize: 12 }}
          />
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ padding: 60, textAlign: 'center', color: 'var(--text-secondary)' }}>
          Retrieving persisted report records from IBM Db2...
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.6fr', gap: 24 }}>
          {/* Reports Catalog List */}
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border-main)' }}>
              <span style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>
                Cataloged Reports ({filtered.length})
              </span>
            </div>

            <div style={{ maxHeight: 600, overflowY: 'auto' }}>
              {filtered.map((r) => {
                const isSelected = selectedReport?.report_uuid === r.report_uuid;
                return (
                  <div
                    key={r.report_uuid}
                    onClick={() => handleSelectReport(r.report_uuid)}
                    style={{
                      padding: '16px 18px',
                      borderBottom: '1px solid var(--border-subtle)',
                      backgroundColor: isSelected ? 'var(--bg-surface)' : 'transparent',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{
                        fontFamily: 'JetBrains Mono',
                        fontSize: 12,
                        fontWeight: 700,
                        color: '#FFFFFF'
                      }}>
                        {r.target_ticker || 'MARKET'}
                      </span>
                      <span style={{ fontSize: 10, fontFamily: 'JetBrains Mono', color: 'var(--text-muted)' }}>
                        {String(r.created_at).slice(0, 10)}
                      </span>
                    </div>

                    <div style={{ fontSize: 13, fontWeight: 500, color: '#FFFFFF', marginTop: 4 }}>
                      {r.report_title}
                    </div>

                    <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                      <span style={{
                        fontSize: 10,
                        color: 'var(--text-muted)',
                        padding: '2px 6px',
                        border: '1px solid var(--border-main)',
                        borderRadius: 2,
                        fontFamily: 'JetBrains Mono'
                      }}>
                        {r.report_type}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Selected Report Inspection Pane */}
          {selectedReport ? (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
              <div className="card-header" style={{ marginBottom: 0, paddingBottom: 16 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{
                      fontFamily: 'JetBrains Mono',
                      fontSize: 13,
                      fontWeight: 700,
                      color: '#FFFFFF'
                    }}>
                      {selectedReport.target_ticker || 'MARKET'}
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>&bull; UUID: {selectedReport.report_uuid.slice(0, 8)}</span>
                  </div>
                  <h2 style={{ fontSize: 18, fontWeight: 600, color: '#FFFFFF', marginTop: 4 }}>
                    {selectedReport.report_title}
                  </h2>
                </div>

                <div style={{ display: 'flex', gap: 8 }}>
                  <a
                    href={`/api/reports/${selectedReport.report_uuid}/pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-secondary"
                    style={{ fontSize: 12, padding: '7px 12px', textDecoration: 'none' }}
                  >
                    <FileDown size={14} color="#FFFFFF" /> PDF
                  </a>
                  <a
                    href={`/api/reports/${selectedReport.report_uuid}/excel`}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-secondary"
                    style={{ fontSize: 12, padding: '7px 12px', textDecoration: 'none' }}
                  >
                    <FileSpreadsheet size={14} color="#FFFFFF" /> Excel
                  </a>
                </div>
              </div>

              {/* Report Markdown Narrative */}
              <div style={{
                backgroundColor: 'var(--bg-secondary)',
                padding: 20,
                border: '1px solid var(--border-subtle)',
                borderRadius: 2,
                fontSize: 13,
                lineHeight: 1.7,
                color: 'var(--text-secondary)',
                whiteSpace: 'pre-wrap',
                maxHeight: 480,
                overflowY: 'auto'
              }}>
                {selectedReport.summary_markdown}
              </div>
            </div>
          ) : (
            <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
              Select a report from the catalog to inspect.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
