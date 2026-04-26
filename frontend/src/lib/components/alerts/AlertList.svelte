<script lang="ts">
  import type { Alert } from '$lib/api/alerts';
  import Badge from '$lib/components/ui/Badge.svelte';

  interface Props {
    alerts: Alert[];
    onResolve: (id: number) => void;
  }

  let { alerts, onResolve }: Props = $props();

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleString();
  }
</script>

<div class="space-y-3">
  {#each alerts as alert}
    <div class="bg-gray-800 rounded-lg p-4 flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <Badge variant={alert.severity === 'critical' ? 'danger' : alert.severity === 'high' ? 'warning' : 'default'}>
            {alert.severity}
          </Badge>
          <Badge>{alert.alert_type}</Badge>
        </div>
        <h4 class="font-medium text-white">{alert.title}</h4>
        {#if alert.body}
          <p class="text-sm text-gray-400 mt-1">{alert.body}</p>
        {/if}
        <p class="text-xs text-gray-500 mt-2">Ausgelöst: {formatDate(alert.fired_at)}</p>
      </div>
      {#if alert.status === 'firing'}
        <button class="text-sm px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-gray-300" onclick={() => onResolve(alert.id)}>
          Auflösen
        </button>
      {/if}
    </div>
  {/each}
  {#if alerts.length === 0}
    <div class="text-center text-gray-500 py-8">Keine Alerts</div>
  {/if}
</div>
