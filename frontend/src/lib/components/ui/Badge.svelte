<script lang="ts">
  interface Props {
    variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
    size?: 'sm' | 'md';
  }

  let { variant = 'default', size = 'sm' }: Props = $props();
</script>

<span class="inline-flex items-center rounded {size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'} {variant === 'default' ? 'bg-gray-700 text-gray-300' : ''} {variant === 'success' ? 'bg-green-900 text-green-300' : ''} {variant === 'warning' ? 'bg-yellow-900 text-yellow-300' : ''} {variant === 'danger' ? 'bg-red-900 text-red-300' : ''} {variant === 'info' ? 'bg-blue-900 text-blue-300' : ''}">
  <slot />
</span>
