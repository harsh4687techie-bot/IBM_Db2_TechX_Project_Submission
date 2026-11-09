import type {
  Company,
  StockDetail,
  DailyPrice,
  Anomaly,
  AnomalySummary,
  SectorOverview,
  AgentQueryResponse,
  ReportItem,
  HealthStatus
} from '../types';

const API_BASE = 'http://127.0.0.1:8000/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP Error ${res.status}`);
    }
    return (await res.json()) as T;
  } catch (error: any) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Health
  getHealth: () => request<HealthStatus>('/health'),

  // Stocks
  getStocks: () => request<Company[]>('/stocks'),
  getStockDetail: (ticker: string) => request<StockDetail>(`/stocks/${ticker}`),
  getStockPrices: (ticker: string, limit: number = 90) =>
    request<DailyPrice[]>(`/stocks/${ticker}/prices?limit=${limit}`),

  // Anomalies
  getAnomalies: (params?: { severity?: string; anomaly_type?: string; limit?: number }) => {
    const search = new URLSearchParams();
    if (params?.severity) search.append('severity', params.severity);
    if (params?.anomaly_type) search.append('anomaly_type', params.anomaly_type);
    if (params?.limit) search.append('limit', params.limit.toString());
    const qs = search.toString();
    return request<Anomaly[]>(`/anomalies${qs ? `?${qs}` : ''}`);
  },
  getAnomalySummary: () => request<AnomalySummary>('/anomalies/summary'),
  triggerAnomalyScan: () =>
    request<{ status: string; new_anomalies_identified: number }>('/anomalies/scan', {
      method: 'POST'
    }),

  // Sectors
  getSectors: () => request<SectorOverview[]>('/sectors'),
  getSectorStocks: (sector: string) => request<Company[]>(`/sectors/${sector}/stocks`),

  // Multi-Agent Copilot
  askAgent: (prompt: string, targetTicker?: string) =>
    request<AgentQueryResponse>('/agents/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, target_ticker: targetTicker })
    }),
  getRecentAuditLogs: (limit: number = 20) => request<any[]>(`/agents/audit?limit=${limit}`),

  // Reports
  getReports: () => request<ReportItem[]>('/reports'),
  getReportDetail: (uuid: string) => request<any>(`/reports/${uuid}`),
  getReportPdfUrl: (uuid: string) => `${API_BASE}/reports/${uuid}/pdf`,
  getReportExcelUrl: (uuid: string) => `${API_BASE}/reports/${uuid}/excel`,

  // Ingestion
  seedSampleData: () =>
    request<any>('/ingestion/seed-sample', {
      method: 'POST'
    }),
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any>('/ingestion/upload', {
      method: 'POST',
      body: formData
    });
  }
};
