import { writable, derived } from 'svelte/store';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { files, updateFileStatus } from './files';

export interface ConversionProgress {
  eventType: string;
  file?: string;
  index?: number;
  total?: number;
  markdown?: string;
  outputPath?: string;
  error?: string;
  success?: number;
  failed?: number;
}

export const isConverting = writable(false);
export const currentProgress = writable<ConversionProgress | null>(null);

export const progressPercent = derived(
  currentProgress,
  ($progress) => {
    if (!$progress || !$progress.total) return 0;
    const completed = ($progress.success || 0) + ($progress.failed || 0);
    return Math.round((completed / $progress.total) * 100);
  }
);

export const statusMessage = derived(
  [isConverting, currentProgress],
  ([$isConverting, $progress]) => {
    if (!$isConverting) return 'Ready';
    if (!$progress) return 'Starting...';
    
    switch ($progress.eventType) {
      case 'started':
        return `Converting ${$progress.index! + 1} of ${$progress.total}...`;
      case 'complete':
        return `Completed: ${$progress.success} succeeded, ${$progress.failed} failed`;
      default:
        return 'Processing...';
    }
  }
);

// Listen for conversion progress events from Rust backend
export async function setupConversionListener() {
  await listen<ConversionProgress>('conversion-progress', (event) => {
    const progress = event.payload;
    currentProgress.set(progress);

    if (progress.file) {
      const fileId = progress.file;
      
      switch (progress.eventType) {
        case 'started':
          updateFileStatus(fileId, 'converting');
          break;
        case 'finished':
          updateFileStatus(fileId, 'completed', {
            markdown: progress.markdown,
            outputPath: progress.outputPath
          });
          break;
        case 'error':
          updateFileStatus(fileId, 'error', {
            error: progress.error
          });
          break;
      }
    }

    if (progress.eventType === 'complete') {
      isConverting.set(false);
    }
  });
}

export async function startConversion(outputDir?: string) {
  isConverting.set(true);
  currentProgress.set(null);

  try {
    // Get all pending files
    const filesStore = files;
    let pendingFiles: { id: string; path: string }[] = [];
    
    filesStore.subscribe(value => {
      pendingFiles = value
        .filter(f => f.status === 'pending' || f.status === 'error')
        .map(f => ({ id: f.id, path: f.path }));
    })();

    if (pendingFiles.length === 0) {
      isConverting.set(false);
      return;
    }

    const filePaths = pendingFiles.map(f => f.path);

    await invoke('convert_files', {
      files: filePaths,
      outputDir: outputDir || null,
      useOcr: false,
      extractImages: true
    });
  } catch (error) {
    console.error('Conversion failed:', error);
    isConverting.set(false);
  }
}

export function resetProgress() {
  currentProgress.set(null);
  isConverting.set(false);
}
