<script lang="ts">
  import type { Host } from '$lib/api/hosts';
  import StatusDot from '$lib/components/ui/StatusDot.svelte';

  interface Props {
    host: Host;
  }

  let { host }: Props = $props();

  const status = $derived(host.last_seen ? 'up' : host.last_error ? 'down' : 'unknown');
</script>

<a href="/hosts/{host.id}" class="block bg-gray-800 rounded-lg p-5 hover:bg-gray-700 transition">
  <div class="flex items-center justify-between mb-2">
    <span class="font-semibold text-white">{host.name}</span>
    <span class="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">{host.host_type}</span>
  </div>
  <div class="text-sm text-gray-400">{host.address}</div>
  <div class="mt-2 flex items-center gap-2">
    <StatusDot {status} />
    <span class="text-xs text-gray-500">
      {host.last_seen ? 'Erreichbar' : host.last_error || 'Unbekannt'}
    </span>
  </div>
</a>
