import { getServices, type Service } from '$lib/api/services';

let services = $state<Service[]>([]);
let loading = $state(false);
let error = $state<string | null>(null);

export const servicesStore = {
  get services() { return services; },
  get loading() { return loading; },
  get error() { return error; },

  async load() {
    loading = true;
    error = null;
    try {
      services = await getServices();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load services';
    } finally {
      loading = false;
    }
  },
};
