<script lang="ts">
  import { onMount } from 'svelte';
  import { getHosts, createHost, deleteHost, type Host } from '$lib/api/hosts';
  import Modal from '$lib/components/ui/Modal.svelte';
  import HostForm from '$lib/components/hosts/HostForm.svelte';

  let hosts = $state<Host[]>([]);
  let loading = $state(true);
  let showModal = $state(false);

  async function load() {
    loading = true;
    hosts = await getHosts();
    loading = false;
  }

  async function handleCreate(data: any) {
    await createHost(data);
    showModal = false;
    await load();
  }

  async function handleDelete(id: number) {
    if (confirm('Host wirklich löschen?')) {
      await deleteHost(id);
      await load();
    }
  }

  onMount(load);
</script>

<div class="flex items-center justify-between mb-6">
  <h1 class="text-2xl font-bold">Hosts</h1>
  <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500" onclick={() => showModal = true}>
    + Host hinzufügen
  </button>
</div>

{#if loading}
  <div class="flex justify-center py-8">Laden...</div>
{:else}
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each hosts as host}
      <div class="bg-gray-800 rounded-lg p-5">
        <div class="flex items-center justify-between mb-2">
          <a href="/hosts/{host.id}" class="font-semibold text-white hover:text-blue-400">{host.name}</a>
          <button class="text-red-400 hover:text-red-300 text-sm" onclick={() => handleDelete(host.id)}>Löschen</button>
        </div>
        <div class="text-sm text-gray-400 mb-2">{host.address}:{host.port || 'default'}</div>
        <span class="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">{host.host_type}</span>
        <div class="mt-3 text-xs text-gray-500">
          {host.last_seen ? `Zuletzt gesehen: ${new Date(host.last_seen).toLocaleString()}` : 'Nie gesehen'}
        </div>
      </div>
    {/each}
  </div>
{/if}

<Modal open={showModal} title="Host erstellen" onclose={() => showModal = false}>
  <HostForm onsubmit={handleCreate} />
</Modal>
