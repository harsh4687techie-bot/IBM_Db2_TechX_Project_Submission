export interface Company {
  stock_id: number;
  ticker: string;
  company_name: string;
  sector: string;
  industry?: string;
  market_cap?: number;
  currency: string;
  latest_close?: number;
  daily_change_pct?: number;
  latest_volume?: number;
  latest_date?: string;
}

export interface DailyPrice {
  price_id: number;
  stock_id: number;
  trading_date: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
  vwap?: number;
  daily_return_pct?: number;
}

export interface StockMetrics {
  total_records: number;
  fifty_two_week_high?: number;
  fifty_two_week_low?: number;
  average_volume_30d?: number;
  thirty_day_return_pct?: number;
}

export interface StockDetail {
  company: Company;
  latest_price?: DailyPrice;
  metrics: StockMetrics;
}

export interface Anomaly {
  anomaly_id: number;
  stock_id: number;
  ticker: string;
  company_name: string;
  sector: string;
  trading_date: string;
  anomaly_type: 'VOLUME_SURGE' | 'PRICE_SPIKE' | 'VOLATILITY_BURST';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  metric_value?: number;
  baseline_mean?: number;
  z_score?: number;
  description: string;
  detected_by: string;
  detected_at?: string;
}

export interface AnomalySummary {
  total_anomalies: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  by_type: Record<string, number>;
}

export interface SectorOverview {
  sector: string;
  stock_count: number;
  avg_market_cap?: number;
  latest_avg_return_pct?: number;
  total_sector_volume?: number;
  anomaly_count: number;
}

export interface AgentStepTrace {
  agent: string;
  action: string;
  detail: string;
  sql_query?: string;
  duration_ms?: number;
}

export interface AgentQueryResponse {
  session_id: string;
  user_query: string;
  response_markdown: string;
  structured_findings?: any;
  steps: AgentStepTrace[];
  generated_report_uuid?: string;
}

export interface ReportItem {
  report_id: number;
  report_uuid: string;
  report_title: string;
  target_ticker?: string;
  report_type: string;
  file_path_pdf?: string;
  file_path_excel?: string;
  generated_by: string;
  created_at?: string;
}

export interface HealthStatus {
  status: string;
  platform: string;
  tagline: string;
  version: string;
  database: {
    status: string;
    latency_ms: number;
    database: string;
    dbms_name: string;
    dbms_version: string;
    server_timestamp: string;
  };
}
