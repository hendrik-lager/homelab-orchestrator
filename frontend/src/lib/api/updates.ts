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

export async function setUpdateStatus(id: number, status: string): Promise<void> {
  return apiFetch<void>(`/updates/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}
