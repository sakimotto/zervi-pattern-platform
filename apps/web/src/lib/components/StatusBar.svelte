<script>
	export let coordinates = { x: 0, y: 0 };
	export let scale = 1;
	export let panelCount = 0;
	export let selectedPanel = null;
	export let units = 'mm';
</script>

<div class="flex items-center gap-4 px-3 py-1 bg-[var(--bg-secondary)] border-t border-[var(--border-color)] text-xs text-[var(--text-secondary)]">
	<div class="flex items-center gap-2">
		<span>Coordinates:</span>
		<span class="text-[var(--text-primary)]">
			X {coordinates.x.toFixed(1)} Y {coordinates.y.toFixed(1)} {units}
		</span>
	</div>

	<div class="h-3 w-px bg-[var(--border-color)]"></div>

	<div class="flex items-center gap-2">
		<span>Scale:</span>
		<span class="text-[var(--text-primary)]">1:{(1 / scale).toFixed(1)}</span>
	</div>

	<div class="h-3 w-px bg-[var(--border-color)]"></div>

	<div class="flex items-center gap-2">
		<span>Panels:</span>
		<span class="text-[var(--text-primary)]">{panelCount}</span>
	</div>

	{#if selectedPanel}
		<div class="h-3 w-px bg-[var(--border-color)]"></div>
		<div class="flex items-center gap-2">
			<span>Selected:</span>
			<span class="text-[var(--accent)]">
				{#if selectedPanel.length > 1}
					{selectedPanel.length} panels
				{:else}
					{selectedPanel[0]?.labels?.[0] || selectedPanel[0]?.id}
				{/if}
			</span>
		</div>
	{/if}

	<div class="flex-1"></div>

	<div class="flex items-center gap-3">
		<button class="hover:text-[var(--text-primary)]" title="Toggle Grid">▦</button>
		<button class="hover:text-[var(--text-primary)]" title="Snap">⊞</button>
		<button class="hover:text-[var(--text-primary)]" title="Ortho">⊥</button>
	</div>
</div>
