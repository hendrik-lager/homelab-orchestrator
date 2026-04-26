<script lang="ts">
  interface Props {
    status: 'up' | 'down' | 'degraded' | 'unknown';
    size?: 'sm' | 'md';
  }

  let { status, size = 'sm' }: Props = $props();
</script>

<span class="inline-block rounded-full {size === 'sm' ? 'w-2 h-2' : 'w-3 h-3'} {status === 'up' ? 'bg-green-500' : ''} {status === 'down' ? 'bg-red-500' : ''} {status === 'degraded' ? 'bg-yellow-500' : ''} {status === 'unknown' ? 'bg-gray-500' : ''}"></span>
