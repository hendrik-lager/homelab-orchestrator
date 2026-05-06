import { apiFetch } from './client';

export interface UpdateRecord {
  id: number;
  host_id: number;
  service_id: number | null;
  update_type: string;
  package_name: string | null;
  current_version: string | null;
  available_version: string | null;
  is_security: boolean;
  status: string;
  detected_at: string;
  applied_at: string | null;
  notes: string | null;
}

export interface AutoUpdateSettings {
  enabled: boolean;
  security_only: boolean;
  cron_expression: string;
}

export async function getUpdates(params?: {
  status?: string;
  update_type?: string;
  is_security?: boolean;
}): Promise<UpdateRecord[]> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.update_type) searchParams.set('update_type', params.update_type);
  if (params?.is_security !== undefined) searchParams.set('is_security', String(params.is_security));
  const query = searchParams.toString();
  return apiFetch<UpdateRecord[]>(`/updates${query ? `?${query}` : ''}`);
}

export async function applyUpdate(id: number): Promise<{ ok: boolean; output: string }> {
  return apiFetch(`/updates/${id}/apply`, { method: 'POST' });
}

export async function applyAllPending(securityOnly = false): Promise<{ results: { id: number; ok: boolean; output: string }[] }> {
  return apiFetch(`/auto-update/apply?security_only=${securityOnly}`, { method: 'POST' });
}

export async function setUpdateStatus(id: number, status: string): Promise<void> {
  return apiFetch<void>(`/updates/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export async function getAutoUpdateSettings(): Promise<AutoUpdateSettings> {
  return apiFetch<AutoUpdateSettings>('/auto-update/settings');
}

export async function saveAutoUpdateSettings(data: AutoUpdateSettings): Promise<void> {
  return apiFetch<void>('/auto-update/settings', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
