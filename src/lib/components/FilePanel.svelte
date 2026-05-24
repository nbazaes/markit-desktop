<script lang="ts">
  import { open } from '@tauri-apps/plugin-dialog';
  import { files, addFiles, removeFile, clearFiles, selectFile, selectedFileId, type FileItem } from '$lib/stores/files';
  import { isConverting } from '$lib/stores/conversion';

  let dragOver = false;

  function generateId(): string {
    return Math.random().toString(36).substring(2, 15);
  }

  async function handleFileSelect() {
    try {
      const selected = await open({
        multiple: true,
        filters: [{
          name: 'Supported Files',
          extensions: [
            'pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv',
            'pptx', 'ppt', 'html', 'htm', 'xml', 'json',
            'txt', 'md', 'epub', 'jpg', 'jpeg', 'png',
            'gif', 'bmp', 'tiff', 'tif', 'mp3', 'wav',
            'm4a', 'flac', 'ogg', 'msg', 'ipynb', 'zip', 'rss'
          ]
        }]
      });

      if (selected) {
        const newFiles: FileItem[] = (Array.isArray(selected) ? selected : [selected]).map(path => ({
          id: generateId(),
          path,
          name: path.split('/').pop() || path,
          size: 0, // TODO: Get actual file size
          status: 'pending'
        }));
        addFiles(newFiles);
      }
    } catch (error) {
      console.error('Failed to select files:', error);
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragOver = true;
  }

  function handleDragLeave() {
    dragOver = false;
  }

  async function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragOver = false;

    // Tauri v2 drag-drop handling
    // Note: In Tauri v2, dropped files come through a different mechanism
    // This is a placeholder for the actual implementation
    console.log('Drop event received');
  }

  function handleFileClick(id: string) {
    selectFile(id);
  }

  function handleRemove(e: Event, id: string) {
    e.stopPropagation();
    removeFile(id);
  }

  function getStatusIcon(status: FileItem['status']): string {
    switch (status) {
      case 'pending': return '○';
      case 'converting': return '⟳';
      case 'completed': return '✓';
      case 'warning': return '⚠';
      case 'error': return '✗';
      default: return '○';
    }
  }

  function getStatusColor(status: FileItem['status']): string {
    switch (status) {
      case 'pending': return 'text-text-muted';
      case 'converting': return 'text-warning animate-spin';
      case 'completed': return 'text-success';
      case 'warning': return 'text-warning';
      case 'error': return 'text-error';
      default: return 'text-text-muted';
    }
  }
</script>

<div
  class="flex flex-col h-full bg-bg-deep"
  role="region"
  aria-label="File drop zone"
  on:dragover={handleDragOver}
  on:dragleave={handleDragLeave}
  on:drop={handleDrop}
>
  <div class="flex items-center justify-between px-4 py-3 bg-bg-surface border-b border-border">
    <span class="text-xs font-semibold text-text-muted tracking-wider">FILES</span>
    <div class="flex items-center gap-2">
      {#if $files.length > 0}
        <span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-bg-raised text-text-muted">
          {$files.length}
        </span>
      {/if}
      <button
        class="w-7 h-7 flex items-center justify-center rounded-lg border border-border
               text-text-muted hover:bg-bg-raised hover:text-text-primary transition-colors text-lg font-bold"
        on:click={handleFileSelect}
        disabled={$isConverting}
      >
        +
      </button>
    </div>
  </div>

  <div class="flex-1 overflow-y-auto p-2">
    {#if $files.length === 0}
      <div class="flex items-center justify-center h-full text-text-dim text-sm text-center px-6 leading-relaxed">
        {#if dragOver}
          <span class="text-accent">Drop files here</span>
        {:else}
          Drop files or folders here<br>or click + to browse
        {/if}
      </div>
    {:else}
      <div class="space-y-1">
        {#each $files as file (file.id)}
          <div
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors cursor-pointer
                   {$selectedFileId === file.id ? 'bg-bg-raised border border-accent' : 'hover:bg-bg-surface border border-transparent'}"
            role="button"
            tabindex="0"
            on:click={() => handleFileClick(file.id)}
            on:keypress={(e) => { if (e.key === 'Enter' || e.key === ' ') handleFileClick(file.id); }}
          >
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-text-primary truncate">
                {file.name}
              </div>
              {#if file.error}
                <div class="text-xs {file.status === 'warning' ? 'text-warning' : 'text-error'} truncate mt-0.5">
                  {file.error}
                </div>
              {/if}
            </div>
            <div class="flex items-center gap-2">
              <span class="text-lg {getStatusColor(file.status)}">
                {getStatusIcon(file.status)}
              </span>
              {#if !$isConverting}
                <button
                  class="text-text-dim hover:text-error transition-colors"
                  on:click={(e) => { e.stopPropagation(); handleRemove(e, file.id); }}
                  aria-label="Remove file"
                >
                  ×
                </button>
              {/if}
            </div>
          </div>
        {/each}
      </div>

      {#if !$isConverting && $files.length > 0}
        <button
          class="w-full mt-4 px-3 py-2 text-sm text-text-muted hover:text-error transition-colors"
          on:click={clearFiles}
        >
          Clear All
        </button>
      {/if}
    {/if}
  </div>
</div>

<style>
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>
