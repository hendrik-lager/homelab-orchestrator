<script lang="ts">
  import { onMount } from 'svelte';
  import { getServices, deleteService, type Service } from '$lib/api/services';
  import ServiceCard from '$lib/components/dashboard/ServiceCard.svelte';

  let services = $state<Service[]>([]);
  let loading = $state(true);

  async function load() {
    loading = true;
    services = await getServices();
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
{:else}
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each services as service}
      <div class="relative">
        <ServiceCard {service} />
        <button
          class="absolute top-2 right-2 text-red-400 hover:text-red-300 text-xs"
          onclick={() => handleDelete(service.id)}
        >
          Löschen
        </button>
      </div>
    {:else}
      <p class="text-gray-500 col-span-full text-center py-8">Keine Services gefunden</p>
    {/each}
  </div>
{/if}
