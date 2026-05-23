import { writable } from 'svelte/store';
import { invoke } from '@tauri-apps/api/core';

export interface AppSettings {
  output_directory: string | null;
  dark_mode: boolean;
  use_ocr: boolean;
  extract_images: boolean;
}

const defaultSettings: AppSettings = {
  output_directory: null,
  dark_mode: true,
  use_ocr: false,
  extract_images: true
};

export const settings = writable<AppSettings>(defaultSettings);

export async function loadSettings() {
  try {
    const loaded = await invoke<AppSettings>('get_settings');
    settings.set(loaded);
  } catch (error) {
    console.error('Failed to load settings:', error);
  }
}

export async function saveSettings(newSettings: AppSettings) {
  try {
    await invoke('set_settings', { newSettings });
    settings.set(newSettings);
  } catch (error) {
    console.error('Failed to save settings:', error);
  }
}

export async function selectOutputDirectory() {
  try {
    const dir = await invoke<string | null>('select_output_dir');
    if (dir) {
      settings.update(current => {
        const updated = { ...current, output_directory: dir };
        saveSettings(updated);
        return updated;
      });
    }
  } catch (error) {
    console.error('Failed to select output directory:', error);
  }
}

export function toggleDarkMode() {
  settings.update(current => {
    const updated = { ...current, dark_mode: !current.dark_mode };
    saveSettings(updated);
    return updated;
  });
}
