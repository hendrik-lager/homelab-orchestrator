<script lang="ts">
  interface Props {
    onsubmit: (data: any) => void;
  }

  let { onsubmit }: Props = $props();

  let name = $state('');
  let rule_type = $state('service_down');
  let threshold_value = $state<number | undefined>(undefined);
  let notify_email = $state(true);

  function handleSubmit() {
    onsubmit({
      name,
      rule_type,
      threshold_value,
      notify_email,
    });
  }
</script>

<form class="space-y-4" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Name</label>
    <input type="text" bind:value={name} class="w-full bg-gray-700 rounded px-3 py-2 text-white" required />
  </div>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Regel-Typ</label>
    <select bind:value={rule_type} class="w-full bg-gray-700 rounded px-3 py-2 text-white">
      <option value="service_down">Service Down</option>
      <option value="security_update">Security Update</option>
      <option value="resource_threshold">Resource Threshold</option>
    </select>
  </div>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Schwellwert (optional)</label>
    <input type="number" step="0.1" bind:value={threshold_value} class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
  </div>
  <div class="flex items-center gap-2">
    <input type="checkbox" bind:checked={notify_email} class="rounded bg-gray-700" />
    <label class="text-sm text-gray-300">Per E-Mail benachrichtigen</label>
  </div>
  <button type="submit" class="w-full bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-500">
    Regel erstellen
  </button>
</form>
