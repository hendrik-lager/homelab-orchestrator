import { apiFetch } from './client';

export interface Host {
  id: number;
  name: string;
  host_type: string;
  address: string;
  port: number | null;
  node_name: string | null;
  enabled: boolean;
  last_seen: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
  // Credential metadata (returned by GET /hosts/{id}, never contains secrets)
  cred_type?: string;
  username?: string;
  token_id?: string;
  has_secret?: boolean;
}

export async function getHosts(): Promise<Host[]> {
  return apiFetch<Host[]>('/hosts');
}

export async function getHost(id: number): Promise<Host> {
  return apiFetch<Host>(`/hosts/${id}`);
}

export async function createHost(data: Partial<Host> & { credential_value?: string; cred_type?: string }): Promise<Host> {
  return apiFetch<Host>('/hosts', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateHost(id: number, data: Partial<Host>): Promise<Host> {
  return apiFetch<Host>(`/hosts/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteHost(id: number): Promise<void> {
  return apiFetch<void>(`/hosts/${id}`, { method: 'DELETE' });
}
