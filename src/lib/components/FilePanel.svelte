<script lang="ts">
  let dropActive = $state(false);

  async function browseFiles() {
    // TODO: Implement with @tauri-apps/plugin-dialog
    console.log("Browse files");
  }
</script>

<div class="flex flex-col h-full bg-bg-deep">
  <div class="flex items-center justify-between px-4 py-3 bg-bg-surface border-b border-border">
    <span class="text-xs font-semibold text-text-muted tracking-wider">FILES</span>
    <div class="flex items-center gap-2">
      <button
        class="w-7 h-7 flex items-center justify-center rounded-lg border border-border
               text-text-muted hover:bg-bg-raised hover:text-text-primary transition-colors text-lg font-bold"
        onclick={browseFiles}>+</button>
    </div>
  </div>

  <div
    class="flex-1 overflow-y-auto"
    class:drop-zone-active={dropActive}
    ondragover={(e) => { e.preventDefault(); dropActive = true; }}
    ondragleave={() => dropActive = false}
    ondrop={(e) => { e.preventDefault(); dropActive = false; }}>

    <div class="flex items-center justify-center h-full text-text-dim text-sm text-center px-6 leading-relaxed">
      Drop files or folders here<br>or click + to browse
    </div>
  </div>
</div>

<style>
  .drop-zone-active {
    @apply bg-accent-dim/20 border-2 border-dashed border-accent rounded-lg m-2;
  }
</style>
