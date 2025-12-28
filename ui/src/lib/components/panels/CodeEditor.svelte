<script lang="ts">
	/**
	 * CodeEditor - CodeMirror-based code editor
	 *
	 * Features:
	 * - JavaScript syntax highlighting
	 * - Line numbers
	 * - Auto-indentation
	 * - Vim mode (optional)
	 * - Dark theme
	 */

	import { onMount, onDestroy, createEventDispatcher } from 'svelte';
	import { EditorView, basicSetup } from 'codemirror';
	import { javascript } from '@codemirror/lang-javascript';
	import { oneDark } from '@codemirror/theme-one-dark';

	export let value: string = '';
	export let readonly: boolean = false;
	export let placeholder: string = '// Write your Strudel code here...';

	const dispatch = createEventDispatcher<{ change: string }>();

	let editorElement: HTMLDivElement;
	let editorView: EditorView | null = null;

	onMount(() => {
		const extensions = [
			basicSetup,
			javascript(),
			oneDark,
			EditorView.editable.of(!readonly),
			EditorView.updateListener.of((update) => {
				if (update.docChanged) {
					const newValue = update.state.doc.toString();
					dispatch('change', newValue);
				}
			})
		];

		// Add placeholder if empty
		if (placeholder && !value) {
			extensions.push(
				EditorView.contentAttributes.of({
					'data-placeholder': placeholder
				})
			);
		}

		editorView = new EditorView({
			doc: value,
			extensions,
			parent: editorElement
		});
	});

	onDestroy(() => {
		if (editorView) {
			editorView.destroy();
			editorView = null;
		}
	});

	// Update editor when value prop changes externally
	$: if (editorView && value !== editorView.state.doc.toString()) {
		editorView.dispatch({
			changes: {
				from: 0,
				to: editorView.state.doc.length,
				insert: value
			}
		});
	}
</script>

<div bind:this={editorElement} class="h-full w-full overflow-hidden" />

<style>
	/* CodeMirror base styling */
	:global(.cm-editor) {
		height: 100%;
		font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
		font-size: 14px;
	}

	:global(.cm-scroller) {
		overflow: auto;
	}

	/* Placeholder styling */
	:global(.cm-content[data-placeholder]:empty::before) {
		content: attr(data-placeholder);
		color: #6b7280;
		opacity: 0.5;
		position: absolute;
		pointer-events: none;
	}

	/* Ensure proper sizing */
	:global(.cm-editor .cm-scroller) {
		height: 100%;
	}
</style>
