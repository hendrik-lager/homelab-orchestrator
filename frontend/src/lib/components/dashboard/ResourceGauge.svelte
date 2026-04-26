<script lang="ts">
  interface Props {
    label: string;
    value: number;
    max: number;
    unit?: string;
  }

  let { label, value, max, unit = '%' }: Props = $props();

  const percentage = $derived(max > 0 ? Math.min(100, (value / max) * 100) : 0);
  const color = $derived(
    percentage > 90 ? 'bg-red-500' :
    percentage > 70 ? 'bg-yellow-500' :
    'bg-green-500'
  );
</script>

<div class="bg-gray-800 rounded-lg p-4">
  <div class="flex justify-between items-center mb-2">
    <span class="text-sm text-gray-400">{label}</span>
    <span class="text-sm font-medium text-white">{value.toFixed(1)}{unit}</span>
  </div>
  <div class="h-2 bg-gray-700 rounded-full overflow-hidden">
    <div class="h-full {color} transition-all" style="width: {percentage}%"></div>
  </div>
</div>
