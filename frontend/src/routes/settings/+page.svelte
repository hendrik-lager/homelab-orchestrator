<script lang="ts">
</script>

<div class="max-w-2xl">
  <h1 class="text-2xl font-bold mb-6">Einstellungen</h1>

  <div class="bg-gray-800 rounded-lg p-6 mb-6">
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
