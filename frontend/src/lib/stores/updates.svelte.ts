import { getUpdates, type UpdateRecord } from '$lib/api/updates';

let updates = $state<UpdateRecord[]>([]);
let loading = $state(false);
let error = $state<string | null>(null);

export const updatesStore = {
  get updates() { return updates; },
  get loading() { return loading; },
  get error() { return error; },

  async load(params?: { status?: string; is_security?: boolean }) {
    loading = true;
    error = null;
    try {
      updates = await getUpdates(params);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load updates';
    } finally {
      loading = false;
    }
  },
};
