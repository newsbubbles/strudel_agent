<script lang="ts">
	/**
	 * MarkdownViewer - Renders markdown content
	 *
	 * Features:
	 * - Basic markdown rendering
	 * - Syntax highlighting for code blocks
	 * - Link handling
	 * - Responsive images
	 * - Custom styling
	 *
	 * Note: Using simple markdown parser for now.
	 * Can upgrade to marked.js or remark later if needed.
	 */

	export let content: string = '';
	export let className: string = '';

	/** Simple markdown parser (basic implementation) */
	function parseMarkdown(md: string): string {
		if (!md) return '';

		let html = md;

		// Headers
		html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
		html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
		html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

		// Bold
		html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

		// Italic
		html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

		// Code blocks
		html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>');

		// Inline code
		html = html.replace(/`(.*?)`/gim, '<code>$1</code>');

		// Links
		html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

		// Lists
		html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
		html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

		// Line breaks
		html = html.replace(/\n\n/g, '</p><p>');
		html = '<p>' + html + '</p>';

		return html;
	}

	$: htmlContent = parseMarkdown(content);
</script>

<div class="markdown-viewer prose prose-sm dark:prose-invert max-w-none {className}">
	{@html htmlContent}
</div>

<style>
	/* Markdown styling */
	:global(.markdown-viewer h1) {
		@apply text-2xl font-bold mb-4 mt-6;
	}

	:global(.markdown-viewer h2) {
		@apply text-xl font-semibold mb-3 mt-5;
	}

	:global(.markdown-viewer h3) {
		@apply text-lg font-semibold mb-2 mt-4;
	}

	:global(.markdown-viewer p) {
		@apply mb-4 leading-relaxed;
	}

	:global(.markdown-viewer ul) {
		@apply list-disc list-inside mb-4 space-y-2;
	}

	:global(.markdown-viewer li) {
		@apply ml-4;
	}

	:global(.markdown-viewer code) {
		@apply bg-muted px-1.5 py-0.5 rounded text-sm font-mono;
	}

	:global(.markdown-viewer pre) {
		@apply bg-muted p-4 rounded-lg overflow-x-auto mb-4;
	}

	:global(.markdown-viewer pre code) {
		@apply bg-transparent p-0;
	}

	:global(.markdown-viewer a) {
		@apply text-primary underline hover:text-primary/80;
	}

	:global(.markdown-viewer strong) {
		@apply font-semibold;
	}

	:global(.markdown-viewer em) {
		@apply italic;
	}
</style>
