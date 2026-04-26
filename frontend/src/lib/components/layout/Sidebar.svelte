<script lang="ts">
</script>

<nav class="w-56 bg-gray-900 border-r border-gray-800 flex flex-col">
  <div class="p-4 border-b border-gray-800">
    <span class="font-bold text-white text-lg">HomeLab</span>
  </div>
  <ul class="flex-1 p-2 space-y-1">
    {#each [
      { href: '/dashboard', label: 'Dashboard' },
      { href: '/hosts', label: 'Hosts' },
      { href: '/services', label: 'Services' },
      { href: '/updates', label: 'Updates' },
      { href: '/alerts', label: 'Alerts' },
      { href: '/settings', label: 'Einstellungen' },
    ] as item}
      <li>
        <a
          href={item.href}
          class="block px-3 py-2 rounded text-gray-300 hover:bg-gray-800 hover:text-white transition text-sm"
        >
          {item.label}
        </a>
      </li>
    {/each}
  </ul>
</nav>
