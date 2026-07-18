<script>
	import { onMount, tick } from 'svelte';
	import { renderPattern, fitToView, getLayerColor } from '$lib/canvas.js';

	let pattern = null;
	let canvas;
	let ctx;
	let view = { width: 0, height: 0, scale: 1, offsetX: 0, offsetY: 0 };
	let isPanning = false;
	let panStart = { x: 0, y: 0 };
	let selectedPanel = null;
	let visibleLayers = new Set();

	onMount(async () => {
		const stored = sessionStorage.getItem('zervi-pattern');
		if (stored) {
			try {
				pattern = JSON.parse(stored);
				initLayers();
				await tick();
				initCanvas();
			} catch (e) {
				console.error('Failed to parse pattern:', e);
			}
		}
	});

	function initLayers() {
		if (pattern && pattern.layers) {
			visibleLayers = new Set(pattern.layers);
		}
	}

	function initCanvas() {
		if (!canvas) return;
		canvas.width = canvas.offsetWidth;
		canvas.height = canvas.offsetHeight;
		ctx = canvas.getContext('2d');
		view.width = canvas.width;
		view.height = canvas.height;
		fitView();
		render();
	}

	function fitView() {
		if (!pattern) return;
		const { scale, offsetX, offsetY } = fitToView(pattern, view.width, view.height);
		view.scale = scale;
		view.offsetX = offsetX;
		view.offsetY = offsetY;
	}

	function render() {
		if (!ctx || !pattern) return;
		renderPattern(ctx, pattern, view);
	}

	function onWheel(e) {
		e.preventDefault();
		const zoom = e.deltaY < 0 ? 1.1 : 0.9;
		const rect = canvas.getBoundingClientRect();
		const mx = e.clientX - rect.left;
		const my = e.clientY - rect.top;

		// World coords before zoom (accounting for Y-flip)
		const wx = (mx - view.offsetX) / view.scale;
		const wy = (view.offsetY + view.height - my) / view.scale;

		view.scale *= zoom;
		view.offsetX = mx - wx * view.scale;
		view.offsetY = my - (view.height - wy * view.scale);
		render();
	}

	function onMouseDown(e) {
		isPanning = true;
		panStart = { x: e.clientX, y: e.clientY };
		canvas.style.cursor = 'grabbing';
	}

	function onMouseMove(e) {
		if (!isPanning) return;
		view.offsetX += e.clientX - panStart.x;
		view.offsetY += e.clientY - panStart.y;
		panStart = { x: e.clientX, y: e.clientY };
		render();
	}

	function onMouseUp() {
		isPanning = false;
		canvas.style.cursor = 'grab';
	}

	function toggleLayer(layer) {
		if (visibleLayers.has(layer)) {
			visibleLayers.delete(layer);
		} else {
			visibleLayers.add(layer);
		}
		visibleLayers = visibleLayers;
		render();
	}

	function selectPanel(panel) {
		selectedPanel = panel;
	}
</script>

<div class="h-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-primary)] overflow-hidden">
	<!-- Toolbar -->
	<div class="flex items-center gap-4 px-4 py-2 bg-[var(--bg-secondary)] border-b border-[var(--border-color)]">
		<a href="/" class="text-sm text-[var(--accent)] hover:underline">← Back</a>
		<div class="h-4 w-px bg-[var(--border-color)]"></div>
		<button on:click={fitView} class="text-sm px-3 py-1 rounded bg-[var(--bg-elevated)] hover:bg-[var(--border-color)]">Fit View</button>
		<div class="flex-1"></div>
		<span class="text-sm text-[var(--text-secondary)]">{pattern?.filename || 'No pattern loaded'}</span>
	</div>

	{#if pattern}
		<div class="flex flex-1 overflow-hidden">
			<!-- Left Sidebar -->
			<div class="w-64 bg-[var(--bg-secondary)] border-r border-[var(--border-color)] overflow-y-auto p-3 space-y-4">
				<div>
					<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">Layers</h3>
					<div class="space-y-1">
						{#each pattern.layers as layer}
							<label class="flex items-center gap-2 text-sm cursor-pointer hover:bg-[var(--bg-elevated)] rounded px-2 py-1">
								<input type="checkbox" checked={visibleLayers.has(layer)} on:change={() => toggleLayer(layer)} />
								<span style="color:{getLayerColor(layer)}">{layer}</span>
							</label>
						{/each}
					</div>
				</div>

				<div>
					<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">Panels ({pattern.panels?.length || 0})</h3>
					<div class="space-y-1 max-h-96 overflow-y-auto">
						{#each pattern.panels as panel}
							<button
								on:click={() => selectPanel(panel)}
								class="w-full text-left text-sm px-2 py-1 rounded hover:bg-[var(--bg-elevated)] {selectedPanel?.id === panel.id ? 'bg-[var(--accent)] text-white' : ''}"
							>
								{panel.labels.length > 0 ? panel.labels[0] : panel.id}
							</button>
						{/each}
					</div>
				</div>
			</div>

			<!-- Canvas -->
			<div class="flex-1 relative bg-[#0a0a0a]">
				<canvas
					bind:this={canvas}
					on:wheel={onWheel}
					on:mousedown={onMouseDown}
					on:mousemove={onMouseMove}
					on:mouseup={onMouseUp}
					on:mouseleave={onMouseUp}
					class="w-full h-full cursor-grab"
				></canvas>
			</div>

			<!-- Right Sidebar -->
			<div class="w-80 bg-[var(--bg-secondary)] border-l border-[var(--border-color)] overflow-y-auto p-3 space-y-4">
				{#if selectedPanel}
					<div>
						<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">Selected Panel</h3>
						<div class="text-sm space-y-1">
							<div><span class="text-[var(--text-secondary)]">ID:</span> {selectedPanel.id}</div>
							{#if selectedPanel.labels.length > 0}
								<div><span class="text-[var(--text-secondary)]">Name:</span> {selectedPanel.labels[0]}</div>
							{/if}
							<div><span class="text-[var(--text-secondary)]">Area:</span> {selectedPanel.area_mm2} mm²</div>
							<div><span class="text-[var(--text-secondary)]">Cut Length:</span> {selectedPanel.cut_length_mm} mm</div>
						</div>
					</div>
				{/if}

				<div>
					<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">Holes ({pattern.holes?.length || 0})</h3>
					<div class="text-sm space-y-1 max-h-48 overflow-y-auto">
						{#each pattern.holes as hole}
							<div class="px-2 py-1 rounded bg-[var(--bg-elevated)]">
								<span class="text-[var(--success)]">{hole.classification}</span>
								<span class="text-[var(--text-secondary)]"> r={hole.radius_mm}mm</span>
							</div>
						{/each}
					</div>
				</div>

				<div>
					<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">Labels ({pattern.labels?.length || 0})</h3>
					<div class="text-sm space-y-1 max-h-96 overflow-y-auto">
						{#each pattern.labels as label}
							<div class="px-2 py-1 rounded bg-[var(--bg-elevated)]">
								<span style="color:{getLayerColor(label.layer)}">{label.text}</span>
							</div>
						{/each}
					</div>
				</div>
			</div>
		</div>
	{:else}
		<div class="flex-1 flex items-center justify-center">
			<div class="text-center space-y-4">
				<div class="text-6xl">📐</div>
				<p class="text-[var(--text-secondary)]">No pattern loaded. Upload a DXF file first.</p>
				<a href="/" class="text-[var(--accent)] hover:underline">Go to Upload</a>
			</div>
		</div>
	{/if}
</div>
