<script lang="ts">
  import { fileCount, completedCount } from '$lib/stores/files';
  import { isConverting, progressPercent, statusMessage } from '$lib/stores/conversion';
</script>

<div class="flex items-center gap-4 px-4 h-8 bg-bg-surface border-t border-border text-xs text-text-muted">
  <span>{$statusMessage}</span>

  {#if $fileCount > 0}
    <span>{$fileCount} file{$fileCount !== 1 ? 's' : ''}</span>
    {#if $isConverting}
      <span>· {$completedCount} / {$fileCount} converted</span>
    {/if}
  {/if}

  <div class="flex-1"></div>

  {#if $isConverting}
    <div class="w-40 h-1.5 bg-bg-raised rounded-full overflow-hidden">
      <div
        class="h-full bg-accent rounded-full transition-all duration-300"
        style="width: {$progressPercent}%"
      ></div>
    </div>
    <span>{$progressPercent}%</span>
  {/if}
</div>
