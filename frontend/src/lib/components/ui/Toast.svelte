<script lang="ts">
  interface Props {
    message: string;
    type?: 'success' | 'error' | 'info';
  }

  let { message, type = 'info' }: Props = $props();
</script>

<div class="fixed bottom-4 right-4 z-50 animate-slide-up">
  <div class="rounded-lg px-4 py-3 shadow-lg {type === 'success' ? 'bg-green-800 text-green-200' : ''} {type === 'error' ? 'bg-red-800 text-red-200' : ''} {type === 'info' ? 'bg-blue-800 text-blue-200' : ''}">
    {message}
  </div>
</div>
