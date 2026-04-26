import { apiFetch } from './client';

export interface DashboardSummary {
  hosts_total: number;
  services_running: number;
  services_down: number;
  pending_updates: number;
  security_updates: number;
  active_alerts: number;
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>('/dashboard/summary');
}
