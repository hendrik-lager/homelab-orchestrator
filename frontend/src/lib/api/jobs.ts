import { apiFetch } from './client';

export interface ScheduledJob {
  id: number;
  name: string;
  job_type: string;
  host_id: number | null;
  cron_expression: string | null;
  enabled: boolean;
  last_run: string | null;
  last_result: string | null;
  next_run: string | null;
}

export async function getJobs(): Promise<ScheduledJob[]> {
  return apiFetch<ScheduledJob[]>('/jobs');
}

export async function createJob(data: Partial<ScheduledJob>): Promise<ScheduledJob> {
  return apiFetch<ScheduledJob>('/jobs', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateJob(id: number, data: Partial<ScheduledJob>): Promise<ScheduledJob> {
  return apiFetch<ScheduledJob>(`/jobs/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteJob(id: number): Promise<void> {
  return apiFetch<void>(`/jobs/${id}`, { method: 'DELETE' });
}
