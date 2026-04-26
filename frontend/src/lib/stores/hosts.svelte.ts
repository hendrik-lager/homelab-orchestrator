import { getHosts, type Host } from '$lib/api/hosts';

let hosts = $state<Host[]>([]);
let loading = $state(false);
let error = $state<string | null>(null);

export const hostsStore = {
  get hosts() { return hosts; },
  get loading() { return loading; },
  get error() { return error; },

  async load() {
    loading = true;
    error = null;
    try {
      hosts = await getHosts();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load hosts';
    } finally {
      loading = false;
    }
  },
};
