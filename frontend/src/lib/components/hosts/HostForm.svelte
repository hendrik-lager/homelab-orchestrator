<script lang="ts">
  import type { Host } from '$lib/api/hosts';

  interface Props {
    host?: Partial<Host>;
    onsubmit: (data: any) => void;
  }

  let { host = {}, onsubmit }: Props = $props();

  const isEditing = $derived(!!host.id);

  const CRED_DEFAULTS: Record<string, string> = {
    ssh: 'ssh_key',
    proxmox: 'api_token',
    docker: 'api_token',
    homeassistant: 'bearer_token',
  };
  const PORT_DEFAULTS: Record<string, number> = {
    ssh: 22,
    proxmox: 8006,
    docker: 2375,
    homeassistant: 8123,
  };

  let name = $state(host.name || '');
  let host_type = $state(host.host_type || 'ssh');
  let address = $state(host.address || '');
  let port = $state(host.port || PORT_DEFAULTS[host_type] || 22);
  let cred_type = $state(host.cred_type || (host.host_type ? (CRED_DEFAULTS[host.host_type] || 'api_token') : 'ssh_key'));
  let username = $state(host.username || '');
  let credential_value = $state('');
  let proxmox_token_id = $state(host.token_id || '');
  let proxmox_token_secret = $state('');
  let proxmox_node_name = $state(host.node_name || 'pve');

  $effect(() => {
    if (!host.id) {
      cred_type = CRED_DEFAULTS[host_type] || 'api_token';
      port = PORT_DEFAULTS[host_type] || 22;
    }
  });

  function handleSubmit() {
    if (host_type === 'proxmox') {
      const payload: any = {
        name,
        host_type,
        address,
        port: port || null,
        node_name: proxmox_node_name || 'pve',
        token_id: proxmox_token_id || undefined,
      };
      if (proxmox_token_secret) payload.token_secret = proxmox_token_secret;
      onsubmit(payload);
    } else {
      const payload: any = {
        name,
        host_type,
        address,
        port: port || null,
        cred_type,
        username: username || null,
      };
      if (credential_value) payload.credential_value = credential_value;
      onsubmit(payload);
    }
  }
</script>

<form class="space-y-4" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
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
  {#if host_type === 'proxmox'}
    <div>
      <label class="block text-sm text-gray-400 mb-1">Node Name <span class="text-gray-500">(Standard: pve)</span></label>
      <input type="text" bind:value={proxmox_node_name} placeholder="pve" class="w-full bg-gray-700 rounded px-3 py-2 text-white font-mono" />
    </div>
    <div>
      <label class="block text-sm text-gray-400 mb-1">Token ID <span class="text-gray-500">(z.B. user@pam!token-name)</span></label>
      <input type="text" bind:value={proxmox_token_id} class="w-full bg-gray-700 rounded px-3 py-2 text-white font-mono" required={!isEditing} />
    </div>
    <div>
      <label class="block text-sm text-gray-400 mb-1">
        Token Secret <span class="text-gray-500">(UUID)</span>
        {#if isEditing && host.has_secret}
          <span class="ml-2 text-xs text-green-400">&#10003; gespeichert</span>
        {/if}
      </label>
      <input
        type="password"
        bind:value={proxmox_token_secret}
        placeholder={isEditing && host.has_secret ? 'Leer lassen, um das bestehende Secret zu behalten' : ''}
        class="w-full bg-gray-700 rounded px-3 py-2 text-white font-mono placeholder:text-gray-500"
        required={!isEditing}
      />
    </div>
  {:else}
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
      <label class="block text-sm text-gray-400 mb-1">
        Credential Wert
        {#if isEditing && host.has_secret}
          <span class="ml-2 text-xs text-green-400">&#10003; gespeichert</span>
        {/if}
      </label>
      <input
        type="password"
        bind:value={credential_value}
        placeholder={isEditing && host.has_secret ? 'Leer lassen, um das bestehende Secret zu behalten' : ''}
        class="w-full bg-gray-700 rounded px-3 py-2 text-white placeholder:text-gray-500"
        required={!isEditing}
      />
    </div>
  {/if}
  <button type="submit" class="w-full bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-500">
    {host.id ? 'Aktualisieren' : 'Erstellen'}
  </button>
</form>
