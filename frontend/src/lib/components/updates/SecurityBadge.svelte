<script lang="ts">
  interface Props {
    isSecurity: boolean;
  }

  let { isSecurity }: Props = $props();
</script>

{#if isSecurity}
  <span class="px-2 py-0.5 rounded text-xs bg-red-900 text-red-300 font-semibold">SECURITY</span>
{/if}
