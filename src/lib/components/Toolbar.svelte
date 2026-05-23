<script lang="ts">
  let { darkMode, onToggle }: { darkMode: boolean; onToggle: () => void } = $props();
</script>

<div class="flex items-center gap-3 px-4 py-2.5 bg-bg-surface border-b border-border">
  <button
    class="px-5 py-1.5 rounded-lg bg-accent text-white font-semibold text-sm
           hover:bg-accent-hover active:bg-accent-pressed disabled:opacity-40
           disabled:cursor-not-allowed transition-colors"
    disabled>
    Convert All
  </button>

  <div class="w-px h-6 bg-border"></div>

  <button class="toolbar-btn" disabled>Copy</button>
  <button class="toolbar-btn" disabled>Save</button>

  <div class="flex-1"></div>

  <button class="toolbar-btn text-text-muted" disabled>Clear</button>

  <div class="w-px h-6 bg-border"></div>

  <button class="toolbar-btn text-text-muted text-xs" disabled>
    Output folder...
  </button>

  <button class="toolbar-btn text-xs" onclick={onToggle}>
    {darkMode ? "☀️" : "🌙"}
  </button>
</div>

<style>
  .toolbar-btn {
    @apply px-3.5 py-1.5 rounded-lg text-sm font-medium text-text-secondary
           hover:bg-bg-raised hover:text-text-primary active:bg-bg-surface
           disabled:opacity-30 disabled:cursor-not-allowed transition-colors
           border border-transparent;
  }
</style>
