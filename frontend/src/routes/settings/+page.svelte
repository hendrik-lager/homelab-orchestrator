<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getTaskStatus, type TaskStatus } from '$lib/api/jobs';
  import { apiFetch } from '$lib/api/client';
  import { getAutoUpdateSettings, saveAutoUpdateSettings, type AutoUpdateSettings } from '$lib/api/updates';
  import Badge from '$lib/components/ui/Badge.svelte';

  let tasks = $state<TaskStatus[]>([]);
  let loading = $state(true);
  let triggering = $state<string | null>(null);
  let triggerError = $state<string | null>(null);
  let refreshInterval: ReturnType<typeof setInterval>;

  let autoUpdate = $state<AutoUpdateSettings>({ enabled: false, security_only: true, cron_expression: '0 3 * * *' });
  let autoUpdateSaving = $state(false);
  let autoUpdateMsg = $state<{ ok: boolean; text: string } | null>(null);

  async function loadTasks() {
    try {
      tasks = await getTaskStatus();
    } catch {
      // silently ignore – backend may not be running during dev
    } finally {
      loading = false;
    }
  }

  async function triggerJob(jobId: string) {
    triggering = jobId;
    triggerError = null;
    try {
      await apiFetch(`/jobs/trigger/${jobId}`, { method: 'POST' });
      await loadTasks();
    } catch (err) {
      triggerError = err instanceof Error ? err.message : String(err);
    } finally {
      triggering = null;
    }
  }

  async function loadAutoUpdateSettings() {
    try {
      autoUpdate = await getAutoUpdateSettings();
    } catch { /* ignore */ }
  }

  async function handleSaveAutoUpdate() {
    autoUpdateSaving = true;
    autoUpdateMsg = null;
    try {
      await saveAutoUpdateSettings(autoUpdate);
      autoUpdateMsg = { ok: true, text: 'Gespeichert' };
    } catch (err) {
      autoUpdateMsg = { ok: false, text: err instanceof Error ? err.message : String(err) };
    } finally {
      autoUpdateSaving = false;
    }
  }

  onMount(() => {
    loadTasks();
    loadAutoUpdateSettings();
    refreshInterval = setInterval(loadTasks, 15_000);
  });

  onDestroy(() => clearInterval(refreshInterval));

  function formatDate(iso: string | null): string {
    if (!iso) return '—';
    return new Intl.DateTimeFormat('de-DE', {
      dateStyle: 'short',
      timeStyle: 'medium',
    }).format(new Date(iso));
  }
</script>

<div class="max-w-4xl space-y-6">
  <h1 class="text-2xl font-bold">Einstellungen</h1>

  <!-- Task Status -->
  <div class="bg-gray-800 rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold">Geplante Tasks</h2>
      <button
        onclick={loadTasks}
        class="text-xs text-gray-400 hover:text-white px-2 py-1 rounded bg-gray-700 hover:bg-gray-600 transition-colors"
      >
        Aktualisieren
      </button>
    </div>

    {#if loading}
      <p class="text-gray-400 text-sm">Lade Tasks…</p>
    {:else if tasks.length === 0}
      <p class="text-gray-400 text-sm">Keine Tasks gefunden.</p>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-gray-400 border-b border-gray-700">
              <th class="pb-2 pr-4 font-medium">Task</th>
              <th class="pb-2 pr-4 font-medium">Status</th>
              <th class="pb-2 pr-4 font-medium">Letzter Run</th>
              <th class="pb-2 pr-4 font-medium">Nächster Run</th>
              <th class="pb-2 font-medium"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700/50">
            {#each tasks as task}
              <tr>
                <td class="py-3 pr-4 font-medium text-white">{task.label}</td>
                <td class="py-3 pr-4">
                  {#if task.last_result === 'ok'}
                    <Badge variant="success">OK</Badge>
                  {:else if task.last_result === 'error'}
                    <Badge variant="danger">Fehler</Badge>
                  {:else}
                    <Badge variant="default">Noch nicht gelaufen</Badge>
                  {/if}
                </td>
                <td class="py-3 pr-4">
                  <span class="text-gray-300">{formatDate(task.last_run)}</span>
                  {#if task.last_result === 'error' && task.last_error}
                    <p class="text-red-400 text-xs mt-0.5 max-w-xs truncate" title={task.last_error}>
                      {task.last_error}
                    </p>
                  {/if}
                </td>
                <td class="py-3 pr-4 text-gray-300">{formatDate(task.next_run)}</td>
                <td class="py-3 text-right">
                  <button
                    onclick={() => triggerJob(task.id)}
                    disabled={triggering === task.id}
                    class="text-xs px-2 py-1 rounded bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white transition-colors disabled:opacity-40"
                  >
                    {triggering === task.id ? '…' : 'Jetzt ausführen'}
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      {#if triggerError}
        <div class="mt-3 p-3 bg-red-900/40 border border-red-700 rounded text-red-300 text-xs font-mono break-all">
          {triggerError}
        </div>
      {/if}

      <p class="text-xs text-gray-500 mt-3">Wird alle 15 Sekunden automatisch aktualisiert.</p>
    {/if}
  </div>

  <!-- Auto-Install -->
  <div class="bg-gray-800 rounded-lg p-6">
    <h2 class="text-lg font-semibold mb-1">Auto-Install</h2>
    <p class="text-gray-400 text-sm mb-4">
      Updates automatisch nach Zeitplan installieren. Für Proxmox-Hosts werden SSH-Credentials (private_key + username) benötigt.
    </p>
    <div class="space-y-4">
      <label class="flex items-center gap-3 cursor-pointer">
        <input
          type="checkbox"
          class="w-4 h-4 accent-blue-500"
          bind:checked={autoUpdate.enabled}
        />
        <span class="text-sm text-gray-300">Auto-Install aktiviert</span>
      </label>
      <label class="flex items-center gap-3 cursor-pointer">
        <input
          type="checkbox"
          class="w-4 h-4 accent-blue-500"
          bind:checked={autoUpdate.security_only}
        />
        <span class="text-sm text-gray-300">Nur Security-Updates</span>
      </label>
      <div>
        <label class="block text-sm text-gray-400 mb-1">
          Cron-Ausdruck
          <span class="text-gray-500 ml-1">(min std tag monat wochentag)</span>
        </label>
        <input
          type="text"
          class="w-full bg-gray-700 rounded px-3 py-2 text-white font-mono"
          placeholder="0 3 * * *"
          bind:value={autoUpdate.cron_expression}
        />
        <p class="text-xs text-gray-500 mt-1">
          Beispiele: täglich 3 Uhr → <code class="font-mono">0 3 * * *</code> &nbsp;|&nbsp;
          Mo–Fr 2 Uhr → <code class="font-mono">0 2 * * 1-5</code> &nbsp;|&nbsp;
          sonntags 4 Uhr → <code class="font-mono">0 4 * * 0</code>
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500 disabled:opacity-40"
          onclick={handleSaveAutoUpdate}
          disabled={autoUpdateSaving}
        >
          {autoUpdateSaving ? 'Speichern…' : 'Einstellungen speichern'}
        </button>
        {#if autoUpdateMsg}
          <span class="text-sm {autoUpdateMsg.ok ? 'text-green-400' : 'text-red-400'}">
            {autoUpdateMsg.text}
          </span>
        {/if}
      </div>
    </div>
  </div>

  <!-- SMTP -->
  <div class="bg-gray-800 rounded-lg p-6">
    <h2 class="text-lg font-semibold mb-4">SMTP / E-Mail Benachrichtigungen</h2>
    <p class="text-gray-400 text-sm mb-4">
      Konfigurieren Sie die SMTP-Einstellungen für E-Mail-Benachrichtigungen bei Alerts.
    </p>
    <div class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-1">SMTP Host</label>
        <input type="text" placeholder="smtp.example.com" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">Port</label>
          <input type="number" placeholder="587" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Benutzer</label>
          <input type="text" placeholder="user@example.com" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
        </div>
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-1">Passwort</label>
        <input type="password" placeholder="********" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-1">Von E-Mail</label>
        <input type="email" placeholder="homelab@example.com" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-1">An E-Mail (kommagetrennt)</label>
        <input type="text" placeholder="admin@example.com" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
      </div>
      <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500">
        Einstellungen speichern
      </button>
    </div>
  </div>

  <!-- Intervalle -->
  <div class="bg-gray-800 rounded-lg p-6">
    <h2 class="text-lg font-semibold mb-4">Intervalle</h2>
    <div class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-1">Health Check Intervall (Sekunden)</label>
        <input type="number" value="60" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-1">Update Scan Intervall (Sekunden)</label>
        <input type="number" value="3600" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-1">Metrik Sammel Intervall (Sekunden)</label>
        <input type="number" value="60" class="w-full bg-gray-700 rounded px-3 py-2 text-white" />
      </div>
      <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500">
        Einstellungen speichern
      </button>
    </div>
  </div>
</div>
