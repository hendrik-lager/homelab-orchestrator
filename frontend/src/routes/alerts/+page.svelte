<script lang="ts">
  import { onMount } from 'svelte';
  import { getAlerts, resolveAlert, createAlertRule, getAlertRules, type Alert, type AlertRule } from '$lib/api/alerts';
  import AlertList from '$lib/components/alerts/AlertList.svelte';
  import AlertRuleForm from '$lib/components/alerts/AlertRuleForm.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';

  let alerts = $state<Alert[]>([]);
  let rules = $state<AlertRule[]>([]);
  let loading = $state(true);
  let showRuleModal = $state(false);

  async function load() {
    loading = true;
    [alerts, rules] = await Promise.all([getAlerts(), getAlertRules()]);
    loading = false;
  }

  async function handleResolve(id: number) {
    await resolveAlert(id);
    await load();
  }

  async function handleCreateRule(data: any) {
    await createAlertRule(data);
    showRuleModal = false;
    await load();
  }

  onMount(load);
</script>

<div class="flex items-center justify-between mb-6">
  <h1 class="text-2xl font-bold">Alerts</h1>
  <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500" onclick={() => showRuleModal = true}>
    + Regel erstellen
  </button>
</div>

{#if loading}
  <div class="flex justify-center py-8">Laden...</div>
{:else}
  <div class="space-y-6">
    <div>
      <h2 class="text-lg font-semibold mb-3">Aktive Alerts</h2>
      <AlertList alerts={alerts.filter(a => a.status === 'firing')} onResolve={handleResolve} />
    </div>

    {#if alerts.some(a => a.status === 'resolved')}
      <div>
        <h2 class="text-lg font-semibold mb-3 text-gray-400">Aufgelöste Alerts</h2>
        <AlertList alerts={alerts.filter(a => a.status === 'resolved')} onResolve={handleResolve} />
      </div>
    {/if}

    <div>
      <h2 class="text-lg font-semibold mb-3">Alert-Regeln</h2>
      <div class="space-y-2">
        {#each rules as rule}
          <div class="bg-gray-800 rounded-lg p-4 flex items-center justify-between">
            <div>
              <span class="font-medium text-white">{rule.name}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-700 text-gray-300 ml-2">{rule.rule_type}</span>
            </div>
            <span class="text-xs text-gray-500">{rule.enabled ? 'Aktiv' : 'Deaktiviert'}</span>
          </div>
        {:else}
          <p class="text-gray-500">Keine Regeln definiert</p>
        {/each}
      </div>
    </div>
  </div>
{/if}

<Modal open={showRuleModal} title="Alert-Regel erstellen" onclose={() => showRuleModal = false}>
  <AlertRuleForm onsubmit={handleCreateRule} />
</Modal>
