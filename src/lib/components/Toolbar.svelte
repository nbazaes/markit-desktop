<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import { hasFiles, hasCompletedFiles, selectedFile } from '$lib/stores/files';
  import { isConverting, startConversion } from '$lib/stores/conversion';
  import { settings, selectOutputDirectory, toggleDarkMode } from '$lib/stores/settings';

  async function handleConvert() {
    await startConversion($settings.output_directory || undefined);
  }

  async function handleCopy() {
    if (!$selectedFile?.markdown) return;
    
    try {
      await navigator.clipboard.writeText($selectedFile.markdown);
      // TODO: Show toast notification
      console.log('Copied to clipboard');
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  }

  async function handleSave() {
    if (!$selectedFile?.markdown) return;

    try {
      await invoke('save_markdown', {
        content: $selectedFile.markdown,
        defaultName: $selectedFile.name.replace(/\.[^/.]+$/, '') + '.md'
      });
    } catch (error) {
      console.error('Failed to save:', error);
    }
  }

  function getOutputDisplay(): string {
    if (!$settings.output_directory) return 'Output folder...';
    const parts = $settings.output_directory.split('/');
    return parts[parts.length - 1] || 'Output folder...';
  }
</script>

<div class="flex items-center gap-3 px-4 py-2.5 bg-bg-surface border-b border-border">
  <button
    class="px-5 py-1.5 rounded-lg bg-accent text-white font-semibold text-sm
           hover:bg-accent-hover active:bg-accent-pressed disabled:opacity-40
           disabled:cursor-not-allowed transition-colors"
    on:click={handleConvert}
    disabled={!$hasFiles || $isConverting}
  >
    Convert All
  </button>

  <div class="w-px h-6 bg-border"></div>

  <button
    class="toolbar-btn"
    on:click={handleCopy}
    disabled={!$hasCompletedFiles || !$selectedFile?.markdown}
  >
    Copy
  </button>
  
  <button
    class="toolbar-btn"
    on:click={handleSave}
    disabled={!$hasCompletedFiles || !$selectedFile?.markdown}
  >
    Save
  </button>

  <div class="flex-1"></div>

  <button
    class="toolbar-btn text-text-muted text-xs"
    on:click={selectOutputDirectory}
    disabled={$isConverting}
  >
    {getOutputDisplay()}
  </button>

  <button
    class="toolbar-btn text-xs"
    on:click={toggleDarkMode}
  >
    {$settings.dark_mode ? '☀️' : '🌙'}
  </button>
</div>

<style>
  .toolbar-btn {
    padding-left: 0.875rem;
    padding-right: 0.875rem;
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-text-secondary);
    border: 1px solid transparent;
    transition: all 0.2s;
  }
  .toolbar-btn:hover:not(:disabled) {
    background-color: var(--color-bg-raised);
    color: var(--color-text-primary);
  }
  .toolbar-btn:active:not(:disabled) {
    background-color: var(--color-bg-surface);
  }
  .toolbar-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
</style>
