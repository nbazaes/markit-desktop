<script lang="ts">
  let activeTab = $state<"preview" | "source">("preview");
</script>

<div class="flex flex-col h-full bg-bg-deep">
  <div class="flex bg-bg-surface border-b border-border px-1 pt-2">
    <button
      class="px-5 py-2 rounded-t-lg text-sm font-medium transition-colors"
      class:text-text-primary={activeTab === "preview"}
      class:text-text-muted={activeTab !== "preview"}
      class:bg-bg-deep={activeTab === "preview"}
      class:hover:bg-bg-raised={activeTab !== "preview"}
      onclick={() => activeTab = "preview"}>Preview</button>
    <button
      class="px-5 py-2 rounded-t-lg text-sm font-medium transition-colors"
      class:text-text-primary={activeTab === "source"}
      class:text-text-muted={activeTab !== "source"}
      class:bg-bg-deep={activeTab === "source"}
      class:hover:bg-bg-raised={activeTab !== "source"}
      onclick={() => activeTab = "source"}>Source</button>
  </div>

  <div class="flex-1 overflow-auto p-8">
    {#if activeTab === "preview"}
      <div class="text-text-muted text-center">
        No file selected
      </div>
    {:else}
      <pre class="text-sm font-mono text-text-secondary whitespace-pre-wrap break-words"></pre>
    {/if}
  </div>
</div>
