import { apiFetch } from '$lib/api/client';
import type { Alert, AlertRule } from '$lib/api/alerts';

let alerts = $state<Alert[]>([]);
let rules = $state<AlertRule[]>([]);
let loading = $state(false);
let error = $state<string | null>(null);

export const alertsStore = {
  get alerts() { return alerts; },
  get rules() { return rules; },
  get loading() { return loading; },
  get error() { return error; },

  async loadAlerts() {
    loading = true;
    error = null;
    try {
      alerts = await apiFetch<Alert[]>('/alerts');
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load alerts';
    } finally {
      loading = false;
    }
  },

  async loadRules() {
    try {
      rules = await apiFetch<AlertRule[]>('/alerts/rules');
    } catch (e) {
      console.error('Failed to load alert rules:', e);
    }
  },
};
