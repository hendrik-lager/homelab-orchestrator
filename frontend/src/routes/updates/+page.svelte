<script lang="ts">
  import { onMount } from 'svelte';
  import { getUpdates, setUpdateStatus, type UpdateRecord } from '$lib/api/updates';
  import UpdateTable from '$lib/components/updates/UpdateTable.svelte';

  let updates = $state<UpdateRecord[]>([]);
  let filter = $state({ status: 'pending', is_security: null as boolean | null });

  async function load() {
    const params: any = { status: filter.status };
    if (filter.is_security !== null) params.is_security = filter.is_security;
    updates = await getUpdates(params);
  }

  async function handleIgnore(id: number) {
    await setUpdateStatus(id, 'ignored');
    await load();
  }

  onMount(load);
</script>

<div class="flex items-center justify-between mb-6">
  <h1 class="text-2xl font-bold">Updates</h1>
  <div class="flex gap-2">
    <button
      class="px-3 py-1 rounded text-sm {filter.is_security === true ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300'}"
      onclick={() => { filter.is_security = filter.is_security === true ? null : true; load(); }}
    >
      Nur Security
    </button>
  </div>
</div>

<UpdateTable {updates} onIgnore={handleIgnore} />
