<script lang="ts">
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import Topbar from '$lib/components/layout/Topbar.svelte';
  import { wsStore } from '$lib/stores/websocket.svelte';
  import { onMount } from 'svelte';

  onMount(() => wsStore.connect());
</script>

<div class="flex h-screen bg-gray-950">
  <Sidebar />
  <div class="flex flex-col flex-1 overflow-hidden">
    <Topbar />
    <main class="flex-1 overflow-auto p-6">
      <slot />
    </main>
  </div>
</div>
