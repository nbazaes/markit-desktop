<script lang="ts">
  import Toolbar from "./lib/components/Toolbar.svelte";
  import FilePanel from "./lib/components/FilePanel.svelte";
  import PreviewPanel from "./lib/components/PreviewPanel.svelte";
  import StatusBar from "./lib/components/StatusBar.svelte";

  let darkMode = $state(true);

  $effect(() => {
    document.documentElement.setAttribute("data-theme", darkMode ? "dark" : "light");
  });
</script>

<div class="flex flex-col h-screen bg-bg-deep text-text-primary overflow-hidden">
  <Toolbar {darkMode} onToggle={() => darkMode = !darkMode} />
  <div class="flex flex-1 overflow-hidden">
    <FilePanel class="w-80 border-r border-border flex-shrink-0" />
    <PreviewPanel class="flex-1" />
  </div>
  <StatusBar class="h-8 border-t border-border bg-bg-surface" />
</div>
