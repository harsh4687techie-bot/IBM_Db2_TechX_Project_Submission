import React, { useState } from 'react';
import { Upload, CheckCircle2, AlertCircle, FileSpreadsheet, Database } from 'lucide-react';
import { api } from '../services/api';

interface IngestionViewProps {
  onDataIngested: () => void;
}

export const IngestionView: React.FC<IngestionViewProps> = ({ onDataIngested }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [seeding, setSeeding] = useState<boolean>(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await api.uploadFile(file);
      setResult(res);
      onDataIngested();
    } catch (err: any) {
      setError(err.message || 'File validation or ingestion failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    setError(null);
    try {
      const res = await api.seedSampleData();
      setResult(res);
      onDataIngested();
    } catch (err: any) {
      setError(err.message || 'Sample data seeding failed.');
    } finally {
      setSeeding(false);
    }
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
            DRISHTI &bull; DATA INGESTION ENGINE
          </div>
          <h1 style={{
            fontSize: 26,
            fontWeight: 600,
            color: '#FFFFFF',
            letterSpacing: '-0.02em'
          }}>
            Data Ingestion & Integrity Portal
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
            Bulk upload CSV and XLSX market series with automated schema validation, range checks, and idempotent MERGE insertion.
          </p>
        </div>

        <button
          className="btn btn-secondary"
          onClick={handleSeed}
          disabled={seeding}
          style={{ opacity: seeding ? 0.6 : 1 }}
        >
          <Database size={14} color="#FFFFFF" />
          {seeding ? 'Seeding Db2...' : 'Seed Baseline Benchmark Data'}
        </button>
      </div>

      {/* Upload Drop Zone & Controls */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        <div style={{
          border: '1px dashed var(--border-main)',
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: 2,
          padding: '48px 24px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 12,
          transition: 'border-color 0.15s ease'
        }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 2,
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-main)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Upload size={20} color="#FFFFFF" />
          </div>

          <div>
            <div style={{ fontSize: 14, fontWeight: 500, color: '#FFFFFF' }}>
              Select or Drag CSV / XLSX Financial Dataset
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
              Required columns: ticker, trading_date, open_price, high_price, low_price, close_price, volume
            </div>
          </div>

          <label
            className="btn btn-secondary"
            style={{ marginTop: 8, cursor: 'pointer' }}
          >
            Browse Files
            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </label>

          {file && (
            <div style={{
              marginTop: 12,
              padding: '8px 16px',
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-main)',
              borderRadius: 2,
              fontSize: 12,
              fontFamily: 'JetBrains Mono',
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}>
              <FileSpreadsheet size={14} color="#FFFFFF" />
              <span>{file.name}</span>
              <span style={{ color: 'var(--text-muted)' }}>({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={!file || uploading}
            style={{ opacity: !file || uploading ? 0.5 : 1, minWidth: 160 }}
          >
            {uploading ? 'Validating & Ingesting...' : 'Upload & Commit to Db2'}
          </button>
        </div>
      </div>

      {/* Validation Result Feedback */}
      {result && (
        <div className="card" style={{ border: '1px solid #FFFFFF' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <CheckCircle2 size={16} color="#FFFFFF" />
            <h3 style={{ fontSize: 14, fontWeight: 600, color: '#FFFFFF' }}>
              Ingestion Succeeded & Synchronized
            </h3>
          </div>

          <div className="grid-cols-4" style={{ marginTop: 12 }}>
            <div className="metric-card">
              <span className="metric-label">New Companies Created</span>
              <div className="metric-value">{result.new_companies_created || 0}</div>
            </div>
            <div className="metric-card">
              <span className="metric-label">Price Bars Inserted</span>
              <div className="metric-value">{result.prices_inserted || 0}</div>
            </div>
            <div className="metric-card">
              <span className="metric-label">Existing Bars Updated</span>
              <div className="metric-value">{result.prices_updated || 0}</div>
            </div>
            <div className="metric-card">
              <span className="metric-label">Anomalies Detected</span>
              <div className="metric-value">{result.anomalies_detected || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* Validation Error Feedback */}
      {error && (
        <div className="card" style={{ border: '1px solid #757575' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertCircle size={16} color="#FFFFFF" />
            <h3 style={{ fontSize: 14, fontWeight: 600, color: '#FFFFFF' }}>
              Validation Rejected
            </h3>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 8 }}>
            {error}
          </p>
        </div>
      )}
    </div>
  );
};
