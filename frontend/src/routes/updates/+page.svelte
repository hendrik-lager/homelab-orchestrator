<script lang="ts">
  import { onMount } from 'svelte';
  import { getUpdates, applyUpdate, applyAllPending, setUpdateStatus, type UpdateRecord } from '$lib/api/updates';
  import UpdateTable from '$lib/components/updates/UpdateTable.svelte';

  let updates = $state<UpdateRecord[]>([]);
  let filter = $state({ status: 'pending', is_security: null as boolean | null });
  let installing = $state(new Set<number>());
  let applyingAll = $state(false);
  let errorMsg = $state<string | null>(null);

  async function load() {
    const params: any = { status: filter.status };
    if (filter.is_security !== null) params.is_security = filter.is_security;
    updates = await getUpdates(params);
  }

  async function handleIgnore(id: number) {
    await setUpdateStatus(id, 'ignored');
    await load();
  }

  async function handleInstall(id: number) {
    errorMsg = null;
    installing = new Set([...installing, id]);
    try {
      await applyUpdate(id);
      await load();
    } catch (err) {
      errorMsg = err instanceof Error ? err.message : String(err);
    } finally {
      installing = new Set([...installing].filter(i => i !== id));
    }
  }

  async function handleInstallAll() {
    errorMsg = null;
    applyingAll = true;
    try {
      const { results } = await applyAllPending(filter.is_security === true);
      const failed = results.filter(r => !r.ok);
      if (failed.length > 0) {
        errorMsg = `${failed.length} Update(s) fehlgeschlagen`;
      }
      await load();
    } catch (err) {
      errorMsg = err instanceof Error ? err.message : String(err);
    } finally {
      applyingAll = false;
    }
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
    <button
      class="px-3 py-1 rounded text-sm bg-blue-700 hover:bg-blue-600 text-white disabled:opacity-40"
      onclick={handleInstallAll}
      disabled={applyingAll || updates.length === 0}
    >
      {applyingAll ? 'Installiere…' : 'Alle installieren'}
    </button>
  </div>
</div>

{#if errorMsg}
  <div class="mb-4 p-3 bg-red-900/40 border border-red-700 rounded text-red-300 text-sm">
    {errorMsg}
  </div>
{/if}

<UpdateTable {updates} onIgnore={handleIgnore} onInstall={handleInstall} {installing} />
