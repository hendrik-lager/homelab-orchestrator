<script lang="ts">
  import { onMount } from 'svelte';
  import { getServices, deleteService, type Service } from '$lib/api/services';
  import { getHosts, type Host } from '$lib/api/hosts';
  import ServiceCard from '$lib/components/dashboard/ServiceCard.svelte';

  let services = $state<Service[]>([]);
  let hosts = $state<Host[]>([]);
  let loading = $state(true);

  const hostMap = $derived(new Map(hosts.map(h => [h.id, h])));

  const groupedByHost = $derived(() => {
    const groups = new Map<number, { host: Host | undefined; services: Service[] }>();
    for (const service of services) {
      if (!groups.has(service.host_id)) {
        groups.set(service.host_id, { host: hostMap.get(service.host_id), services: [] });
      }
      groups.get(service.host_id)!.services.push(service);
    }
    return [...groups.values()].sort((a, b) => {
      const nameA = a.host?.name ?? '';
      const nameB = b.host?.name ?? '';
      return nameA.localeCompare(nameB);
    });
  });

  async function load() {
    loading = true;
    [hosts, services] = await Promise.all([getHosts(), getServices()]);
    loading = false;
  }

  async function handleDelete(id: number) {
    if (confirm('Service wirklich löschen?')) {
      await deleteService(id);
      await load();
    }
  }

  onMount(load);
</script>

<div class="mb-6">
  <h1 class="text-2xl font-bold">Services</h1>
</div>

{#if loading}
  <div class="flex justify-center py-8">Laden...</div>
{:else if services.length === 0}
  <p class="text-gray-500 text-center py-8">Keine Services gefunden</p>
{:else}
  {#each groupedByHost() as group}
    <div class="mb-8">
      <h2 class="text-lg font-semibold text-gray-300 mb-3 flex items-center gap-2">
        <span class="text-gray-500">/</span>
        {group.host?.name ?? `Host #${group.services[0].host_id}`}
        <span class="text-sm font-normal text-gray-500">({group.services.length})</span>
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each group.services as service}
          <div class="relative">
            <ServiceCard {service} />
            <button
              class="absolute top-2 right-2 text-red-400 hover:text-red-300 text-xs"
              onclick={() => handleDelete(service.id)}
            >
              Löschen
            </button>
          </div>
        {/each}
      </div>
    </div>
  {/each}
{/if}
