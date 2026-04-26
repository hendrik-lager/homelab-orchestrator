import { apiFetch } from './client';

export interface Alert {
  id: number;
  host_id: number | null;
  service_id: number | null;
  alert_type: string;
  severity: string;
  title: string;
  body: string | null;
  status: string;
  fired_at: string;
  resolved_at: string | null;
  notification_sent: boolean;
}

export interface AlertRule {
  id: number;
  name: string;
  rule_type: string;
  host_id: number | null;
  threshold_value: number | null;
  enabled: boolean;
  notify_email: boolean;
  created_at: string;
}

export async function getAlerts(): Promise<Alert[]> {
  return apiFetch<Alert[]>('/alerts');
}

export async function createAlertRule(data: Partial<AlertRule>): Promise<AlertRule> {
  return apiFetch<AlertRule>('/alerts/rules', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getAlertRules(): Promise<AlertRule[]> {
  return apiFetch<AlertRule[]>('/alerts/rules');
}

export async function resolveAlert(id: number): Promise<void> {
  return apiFetch<void>(`/alerts/${id}`, { method: 'DELETE' });
}
