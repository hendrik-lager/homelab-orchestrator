<script lang="ts">
  interface Props {
    open: boolean;
    title: string;
    onclose: () => void;
  }

  let { open, title, onclose }: Props = $props();
</script>

{#if open}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="fixed inset-0 bg-black/60" onclick={onclose}></div>
    <div class="relative bg-gray-800 rounded-lg shadow-xl max-w-lg w-full mx-4 p-6 z-10">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">{title}</h3>
        <button class="text-gray-400 hover:text-white" onclick={onclose}>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <slot />
    </div>
  </div>
{/if}
