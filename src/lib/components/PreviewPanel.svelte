<script lang="ts">
  import { marked } from 'marked';
  import hljs from 'highlight.js';
  import { selectedFile } from '$lib/stores/files';

  let activeTab: 'preview' | 'source' = 'preview';

  marked.setOptions({
    gfm: true,
    breaks: true
  });

  const renderer = new marked.Renderer();
  renderer.code = function({ text, lang }: { text: string; lang?: string }) {
    let highlighted: string;
    if (lang && hljs.getLanguage(lang)) {
      try {
        highlighted = hljs.highlight(text, { language: lang }).value;
      } catch {
        highlighted = hljs.highlightAuto(text).value;
      }
    } else {
      highlighted = hljs.highlightAuto(text).value;
    }
    return `<pre><code class="hljs language-${lang || ''}">${highlighted}</code></pre>`;
  };

  marked.use({ renderer });

  $: markdown = $selectedFile?.markdown || '';
  $: renderedHtml = markdown ? marked(markdown) : '';
</script>

<div class="flex flex-col h-full bg-bg-deep">
  <div class="flex bg-bg-surface border-b border-border px-1 pt-2">
    <button
      class="px-5 py-2 rounded-t-lg text-sm font-medium transition-colors
             {activeTab === 'preview' ? 'text-text-primary bg-bg-deep' : 'text-text-muted hover:bg-bg-raised'}"
      on:click={() => activeTab = 'preview'}
    >
      Preview
    </button>
    <button
      class="px-5 py-2 rounded-t-lg text-sm font-medium transition-colors
             {activeTab === 'source' ? 'text-text-primary bg-bg-deep' : 'text-text-muted hover:bg-bg-raised'}"
      on:click={() => activeTab = 'source'}
    >
      Source
    </button>
  </div>

  <div class="flex-1 overflow-auto">
    {#if !$selectedFile}
      <div class="flex items-center justify-center h-full text-text-dim text-sm">
        Select a file to preview
      </div>
    {:else if !$selectedFile.markdown}
      <div class="flex items-center justify-center h-full text-text-dim text-sm">
        {#if $selectedFile.status === 'converting'}
          Converting...
        {:else if $selectedFile.status === 'error'}
          Conversion failed: {$selectedFile.error}
        {:else}
          No content to preview
        {/if}
      </div>
    {:else if activeTab === 'preview'}
      <div class="prose prose-invert max-w-none p-6">
        {@html renderedHtml}
      </div>
    {:else}
      <pre class="p-6 text-sm font-mono text-text-secondary whitespace-pre-wrap break-words">{markdown}</pre>
    {/if}
  </div>
</div>

<style>
  :global(.prose) {
    color: var(--color-text-primary);
  }
  :global(.prose h1),
  :global(.prose h2),
  :global(.prose h3),
  :global(.prose h4),
  :global(.prose h5),
  :global(.prose h6) {
    color: var(--color-text-primary);
    border-bottom-color: var(--color-border);
  }
  :global(.prose a) {
    color: var(--color-accent);
  }
  :global(.prose code) {
    color: var(--color-accent);
    background-color: var(--color-bg-raised);
    padding: 0.2em 0.4em;
    border-radius: 0.25rem;
  }
  :global(.prose pre) {
    background-color: var(--color-bg-raised);
    border: 1px solid var(--color-border);
  }
  :global(.prose pre code) {
    background-color: transparent;
    padding: 0;
  }
  :global(.prose blockquote) {
    border-left-color: var(--color-accent);
    color: var(--color-text-secondary);
  }
  :global(.prose table) {
    border-color: var(--color-border);
  }
  :global(.prose th),
  :global(.prose td) {
    border-color: var(--color-border);
  }
  :global(.prose th) {
    background-color: var(--color-bg-raised);
  }
</style>
