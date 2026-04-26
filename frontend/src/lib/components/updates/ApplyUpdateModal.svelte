<script lang="ts">
  import Modal from '$lib/components/ui/Modal.svelte';
  import type { UpdateRecord } from '$lib/api/updates';

  interface Props {
    open: boolean;
    update: UpdateRecord | null;
    onclose: () => void;
    onApply: (id: number) => void;
  }

  let { open, update, onclose, onApply }: Props = $props();
</script>

<Modal {open} title="Update anwenden" {onclose}>
  {#if update}
    <div class="space-y-4">
      <p class="text-gray-300">
        Möchten Sie das Update für <span class="font-mono text-white">{update.package_name}</span> anwenden?
      </p>
      <p class="text-sm text-gray-500">
        Version: {update.current_version ?? '?'} → {update.available_version ?? '?'}
      </p>
      <div class="flex justify-end gap-2">
        <button class="px-4 py-2 rounded bg-gray-700 text-gray-300 hover:bg-gray-600" onclick={onclose}>
          Abbrechen
        </button>
        <button class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-500" onclick={() => onApply(update.id)}>
          Anwenden
        </button>
      </div>
    </div>
  {/if}
</Modal>
