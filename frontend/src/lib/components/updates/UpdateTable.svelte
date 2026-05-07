<script lang="ts">
  import type { UpdateRecord } from '$lib/api/updates';
  import SecurityBadge from './SecurityBadge.svelte';

  interface Props {
    updates: UpdateRecord[];
    onIgnore: (id: number) => void;
    onInstall: (id: number) => void;
    installing?: Set<number>;
  }

  let { updates, onIgnore, onInstall, installing = new Set() }: Props = $props();

  function displayName(upd: UpdateRecord): string {
    if (upd.update_type === 'homeassistant' && upd.notes) return upd.notes;
    return upd.package_name ?? '-';
  }
</script>

<div class="bg-gray-800 rounded-lg overflow-hidden">
  <table class="w-full text-sm">
    <thead class="bg-gray-700">
      <tr>
        <th class="text-left p-3 text-gray-300">Host</th>
        <th class="text-left p-3 text-gray-300">Paket / Name</th>
        <th class="text-left p-3 text-gray-300">Typ</th>
        <th class="text-left p-3 text-gray-300">Version</th>
        <th class="text-left p-3 text-gray-300">Security</th>
        <th class="text-left p-3 text-gray-300">Aktion</th>
      </tr>
    </thead>
    <tbody>
      {#each updates as upd}
        <tr class="border-t border-gray-700 hover:bg-gray-750">
          <td class="p-3 text-gray-300">{upd.host_name ?? upd.host_id}</td>
          <td class="p-3 text-white font-mono">{displayName(upd)}</td>
          <td class="p-3">
            <span class="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">{upd.update_type}</span>
          </td>
          <td class="p-3 text-gray-400 font-mono text-xs">
            {upd.current_version ?? '?'} → {upd.available_version ?? '?'}
          </td>
          <td class="p-3">
            <SecurityBadge isSecurity={upd.is_security} />
          </td>
          <td class="p-3 flex gap-1">
            <button
              class="text-xs px-2 py-1 rounded bg-blue-700 hover:bg-blue-600 text-white disabled:opacity-40"
              onclick={() => onInstall(upd.id)}
              disabled={installing.has(upd.id)}
            >
              {installing.has(upd.id) ? '…' : 'Installieren'}
            </button>
            <button
              class="text-xs px-2 py-1 rounded bg-gray-700 hover:bg-gray-600 text-gray-300"
              onclick={() => onIgnore(upd.id)}
            >
              Ignorieren
            </button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
  {#if updates.length === 0}
    <div class="p-8 text-center text-gray-500">Keine Updates gefunden</div>
  {/if}
</div>
