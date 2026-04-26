<script lang="ts">
  import { wsStore } from '$lib/stores/websocket.svelte';
</script>

<header class="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">
  <div class="flex items-center gap-4">
    <h2 class="text-gray-400 text-sm">HomeLab Orchestrator</h2>
  </div>
  <div class="flex items-center gap-4">
    <div class="flex items-center gap-2">
      <span class="w-2 h-2 rounded-full {wsStore.connected ? 'bg-green-500' : 'bg-red-500'}"></span>
      <span class="text-xs text-gray-400">
        {wsStore.connected ? 'Verbunden' : 'Getrennt'}
      </span>
    </div>
  </div>
</header>
