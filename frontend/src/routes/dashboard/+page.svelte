<script lang="ts">
  import { onMount } from 'svelte';
  import { apiFetch } from '$lib/api/client';
  import SummaryBar from '$lib/components/dashboard/SummaryBar.svelte';
  import HostCard from '$lib/components/dashboard/HostCard.svelte';
  import type { DashboardSummary } from '$lib/api/dashboard';
  import type { Host } from '$lib/api/hosts';

  let summary = $state<DashboardSummary | null>(null);
  let hosts = $state<Host[]>([]);

  onMount(async () => {
    [summary, hosts] = await Promise.all([
      apiFetch<DashboardSummary>('/dashboard/summary'),
      apiFetch<Host[]>('/hosts'),
    ]);
  });
</script>

<h1 class="text-2xl font-bold mb-6">Dashboard</h1>

{#if summary}
  <SummaryBar {summary} />
{/if}

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {#each hosts as host}
    <HostCard {host} />
  {/each}
</div>
