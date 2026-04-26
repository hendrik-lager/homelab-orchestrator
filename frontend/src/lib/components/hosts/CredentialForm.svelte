<script lang="ts">
  interface Props {
    credType?: string;
    onsubmit: (data: { cred_type: string; value: string; username?: string }) => void;
  }

  let { credType = 'api_token', onsubmit }: Props = $props();

  let cred_type = $state(credType);
  let username = $state('');
  let value = $state('');

  function handleSubmit() {
    onsubmit({
      cred_type,
      value,
      username: username || undefined,
    });
  }
</script>

<form class="space-y-4" onsubmit|preventDefault={handleSubmit}>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Typ</label>
    <select bind:value={cred_type} class="w-full bg-gray-700 rounded px-3 py-2 text-white">
      <option value="api_token">API Token</option>
      <option value="ssh_key">SSH Key</option>
      <option value="ssh_password">SSH Password</option>
      <option value="bearer_token">Bearer Token</option>
    </select>
  </div>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Benutzername (optional)</label>
    <input type="text" bind:value={username} class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
  </div>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Wert</label>
    <textarea bind:value={value} rows="4" class="w-full bg-gray-700 rounded px-3 py-2 text-white font-mono text-sm"></textarea>
  </div>
  <button type="submit" class="w-full bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-500">
    Speichern
  </button>
</form>
