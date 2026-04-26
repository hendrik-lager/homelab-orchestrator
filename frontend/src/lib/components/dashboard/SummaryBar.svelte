<script lang="ts">
  interface Props {
    summary: {
      hosts_total: number;
      services_running: number;
      services_down: number;
      pending_updates: number;
      security_updates: number;
      active_alerts: number;
    };
  }

  let { summary }: Props = $props();
</script>

<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
  <div class="bg-gray-800 rounded-lg p-4">
    <div class="text-3xl font-bold text-white">{summary.hosts_total}</div>
    <div class="text-gray-400 text-sm">Hosts</div>
  </div>
  <div class="bg-gray-800 rounded-lg p-4">
    <div class="text-3xl font-bold text-green-400">{summary.services_running}</div>
    <div class="text-gray-400 text-sm">Services aktiv</div>
  </div>
  <div class="bg-gray-800 rounded-lg p-4">
    <div class="text-3xl font-bold text-red-400">{summary.services_down}</div>
    <div class="text-gray-400 text-sm">Services down</div>
  </div>
  <div class="bg-gray-800 rounded-lg p-4">
    <div class="text-3xl font-bold text-yellow-400">{summary.pending_updates}</div>
    <div class="text-gray-400 text-sm">Updates verfügbar</div>
  </div>
  <div class="bg-gray-800 rounded-lg p-4">
    <div class="text-3xl font-bold text-red-500">{summary.security_updates}</div>
    <div class="text-gray-400 text-sm">Security Updates</div>
  </div>
  <div class="bg-gray-800 rounded-lg p-4">
    <div class="text-3xl font-bold text-orange-400">{summary.active_alerts}</div>
    <div class="text-gray-400 text-sm">Aktive Alerts</div>
  </div>
</div>
