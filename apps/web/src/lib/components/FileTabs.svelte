<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let files = [];

	function selectFile(file) {
		dispatch('select', file);
	}

	function closeFile(file) {
		dispatch('close', file);
	}

	function newFile() {
		dispatch('new');
	}
</script>

<div class="flex items-center gap-1 px-2 py-1 bg-[var(--bg-secondary)] border-b border-[var(--border-color)] overflow-x-auto">
	{#each files as file}
		<button
			on:click={() => selectFile(file)}
			class="flex items-center gap-2 px-3 py-1.5 text-sm rounded-t border-b-2 {file.active ? 'bg-[var(--bg-primary)] border-[var(--accent)] text-[var(--text-primary)]' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}"
		>
			<span>{file.name}</span>
			{#if file.dirty}
				<span class="text-[var(--warning)]">•</span>
			{/if}
			<span
				on:click|stopPropagation={() => closeFile(file)}
				class="ml-1 text-[var(--text-secondary)] hover:text-[var(--error)] cursor-pointer"
			>
				×
			</span>
		</button>
	{/each}

	<button
		on:click={newFile}
		class="px-2 py-1.5 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
		title="New Pattern"
	>
		+
	</button>
</div>
