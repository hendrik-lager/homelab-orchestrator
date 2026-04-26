<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { getHost, updateHost, type Host } from '$lib/api/hosts';
  import { getServices, type Service } from '$lib/api/services';
  import HostForm from '$lib/components/hosts/HostForm.svelte';
  import ServiceCard from '$lib/components/dashboard/ServiceCard.svelte';

  let host = $state<Host | null>(null);
  let services = $state<Service[]>([]);
  let loading = $state(true);

  async function load() {
    loading = true;
    const id = Number($page.params.id);
    [host, services] = await Promise.all([
      getHost(id),
      getServices().then(all => all.filter(s => s.host_id === id)),
    ]);
    loading = false;
  }

  async function handleUpdate(data: any) {
    const id = Number($page.params.id);
    await updateHost(id, data);
    await load();
  }

  onMount(load);
</script>

{#if loading}
  <div class="flex justify-center py-8">Laden...</div>
{:else if host}
  <div class="mb-6">
    <a href="/hosts" class="text-blue-400 hover:text-blue-300 text-sm">← Zurück zu Hosts</a>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="bg-gray-800 rounded-lg p-6">
      <h2 class="text-xl font-bold mb-4">Host bearbeiten</h2>
      <HostForm {host} onsubmit={handleUpdate} />
    </div>

    <div>
      <h2 class="text-xl font-bold mb-4">Services</h2>
      <div class="space-y-3">
        {#each services as service}
          <ServiceCard {service} />
        {:else}
          <p class="text-gray-500">Keine Services gefunden</p>
        {/each}
      </div>
    </div>
  </div>
{/if}
