<script lang="ts">
  import type { Service } from '$lib/api/services';
  import StatusDot from '$lib/components/ui/StatusDot.svelte';

  interface Props {
    service: Service;
  }

  let { service }: Props = $props();

  const status = $derived(
    service.status === 'running' ? 'up' :
    service.status === 'stopped' ? 'down' :
    service.status === 'error' ? 'down' :
    'unknown'
  );
</script>

<div class="bg-gray-800 rounded-lg p-4">
  <div class="flex items-center justify-between mb-2">
    <span class="font-medium text-white">{service.name}</span>
    <StatusDot {status} />
  </div>
  <div class="text-xs text-gray-400">{service.service_type}</div>
  {#if service.image}
    <div class="text-xs text-gray-500 mt-1 font-mono truncate">{service.image}</div>
  {/if}
</div>
