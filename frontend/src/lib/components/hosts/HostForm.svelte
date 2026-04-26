<script lang="ts">
  import type { Host } from '$lib/api/hosts';

  interface Props {
    host?: Partial<Host>;
    onsubmit: (data: any) => void;
  }

  let { host = {}, onsubmit }: Props = $props();

  let name = $state(host.name || '');
  let host_type = $state(host.host_type || 'ssh');
  let address = $state(host.address || '');
  let port = $state(host.port || 22);
  let cred_type = $state('api_token');
  let username = $state('');
  let credential_value = $state('');

  function handleSubmit() {
    onsubmit({
      name,
      host_type,
      address,
      port: port || null,
      cred_type,
      username: username || null,
      credential_value,
    });
  }
</script>

<form class="space-y-4" onsubmit|preventDefault={handleSubmit}>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Name</label>
    <input type="text" bind:value={name} class="w-full bg-gray-700 rounded px-3 py-2 text-white" required />
  </div>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Typ</label>
    <select bind:value={host_type} class="w-full bg-gray-700 rounded px-3 py-2 text-white">
      <option value="ssh">SSH</option>
      <option value="proxmox">Proxmox</option>
      <option value="docker">Docker</option>
      <option value="homeassistant">Home Assistant</option>
    </select>
  </div>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Adresse</label>
    <input type="text" bind:value={address} class="w-full bg-gray-700 rounded px-3 py-2 text-white" required />
  </div>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Port</label>
    <input type="number" bind:value={port} class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
  </div>
  <div>
    <label class="block text-sm text-gray-400 mb-1">Credential Typ</label>
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
    <label class="block text-sm text-gray-400 mb-1">Credential Wert</label>
    <input type="password" bind:value={credential_value} class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
  </div>
  <button type="submit" class="w-full bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-500">
    {host.id ? 'Aktualisieren' : 'Erstellen'}
  </button>
</form>
