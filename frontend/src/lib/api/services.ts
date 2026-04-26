import { apiFetch } from './client';

export interface Service {
  id: number;
  host_id: number;
  name: string;
  service_type: string;
  external_id: string | null;
  image: string | null;
  status: string;
  started_at: string | null;
  last_checked: string | null;
  labels: string | null;
}

export async function getServices(): Promise<Service[]> {
  return apiFetch<Service[]>('/services');
}

export async function getService(id: number): Promise<Service> {
  return apiFetch<Service>(`/services/${id}`);
}

export async function createService(data: Partial<Service>): Promise<Service> {
  return apiFetch<Service>('/services', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateService(id: number, data: Partial<Service>): Promise<Service> {
  return apiFetch<Service>(`/services/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteService(id: number): Promise<void> {
  return apiFetch<void>(`/services/${id}`, { method: 'DELETE' });
}
