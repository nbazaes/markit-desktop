<script lang="ts">
  import { onMount } from 'svelte';
  import Toolbar from '$lib/components/Toolbar.svelte';
  import FilePanel from '$lib/components/FilePanel.svelte';
  import PreviewPanel from '$lib/components/PreviewPanel.svelte';
  import StatusBar from '$lib/components/StatusBar.svelte';
  import { settings, loadSettings } from '$lib/stores/settings';
  import { setupConversionListener } from '$lib/stores/conversion';

  onMount(async () => {
    await loadSettings();
    await setupConversionListener();
  });

  $: document.documentElement.setAttribute('data-theme', $settings.dark_mode ? 'dark' : 'light');
</script>

<div class="flex flex-col h-screen bg-bg-deep text-text-primary overflow-hidden">
  <Toolbar />
  <div class="flex flex-1 overflow-hidden">
    <div class="w-80 border-r border-border flex-shrink-0">
      <FilePanel />
    </div>
    <div class="flex-1">
      <PreviewPanel />
    </div>
  </div>
  <StatusBar />
</div>
