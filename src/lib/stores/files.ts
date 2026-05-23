import { writable, derived } from 'svelte/store';

export interface FileItem {
  id: string;
  path: string;
  name: string;
  size: number;
  status: 'pending' | 'converting' | 'completed' | 'error';
  error?: string;
  markdown?: string;
  outputPath?: string;
}

export const files = writable<FileItem[]>([]);

export const selectedFileId = writable<string | null>(null);

export const selectedFile = derived(
  [files, selectedFileId],
  ([$files, $selectedFileId]) => {
    if (!$selectedFileId) return null;
    return $files.find(f => f.id === $selectedFileId) || null;
  }
);

export const fileCount = derived(files, ($files) => $files.length);

export const completedCount = derived(
  files,
  ($files) => $files.filter(f => f.status === 'completed').length
);

export const hasFiles = derived(files, ($files) => $files.length > 0);

export const hasCompletedFiles = derived(
  files,
  ($files) => $files.some(f => f.status === 'completed')
);

export function addFiles(newFiles: FileItem[]) {
  files.update(current => [...current, ...newFiles]);
}

export function removeFile(id: string) {
  files.update(current => current.filter(f => f.id !== id));
  selectedFileId.update(current => current === id ? null : current);
}

export function clearFiles() {
  files.set([]);
  selectedFileId.set(null);
}

export function updateFileStatus(
  id: string,
  status: FileItem['status'],
  data?: { error?: string; markdown?: string; outputPath?: string }
) {
  files.update(current =>
    current.map(f =>
      f.id === id
        ? { ...f, status, ...data }
        : f
    )
  );
}

export function selectFile(id: string) {
  selectedFileId.set(id);
}
