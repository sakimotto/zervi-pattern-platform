<script>
	import { onMount, tick } from 'svelte';
	import { renderPattern, fitToView, getLayerColor } from '$lib/canvas.js';
	import MenuBar from '$lib/components/MenuBar.svelte';
	import RibbonTabs from '$lib/components/RibbonTabs.svelte';
	import FileTabs from '$lib/components/FileTabs.svelte';
	import StatusBar from '$lib/components/StatusBar.svelte';
	import Toolbox from '$lib/components/Toolbox.svelte';
	import BlockLibrary from '$lib/components/BlockLibrary.svelte';

	let pattern = null;
	let canvas;
	let ctx;
	let view = { width: 0, height: 0, scale: 1, offsetX: 0, offsetY: 0 };
	let isPanning = false;
	let panStart = { x: 0, y: 0 };
	let selectedPanel = null;
	let visibleLayers = new Set();
	let coordinates = { x: 0, y: 0 };

	let files = [];
	let activeFile = null;
	let showLibrary = false;

	onMount(async () => {
		const stored = sessionStorage.getItem('zervi-pattern');
		if (stored) {
			try {
				pattern = JSON.parse(stored);
				files = [
					{
						name: pattern.filename || 'Untitled',
						active: true,
						dirty: false,
						pattern
					}
				];
				activeFile = files[0];
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
		renderPattern(ctx, pattern, view, visibleLayers, selectedPanel?.id);
	}

	function onWheel(e) {
		e.preventDefault();
		const zoom = e.deltaY < 0 ? 1.1 : 0.9;
		const rect = canvas.getBoundingClientRect();
		const mx = e.clientX - rect.left;
		const my = e.clientY - rect.top;

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
		if (!isPanning) {
			// Update coordinates
			const rect = canvas.getBoundingClientRect();
			const mx = e.clientX - rect.left;
			const my = e.clientY - rect.top;
			coordinates = {
				x: (mx - view.offsetX) / view.scale,
				y: (view.offsetY + view.height - my) / view.scale
			};
			return;
		}
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
		render();
	}

	function handleMenuAction(e) {
		const action = e.detail;
		console.log('Menu action:', action);
		if (action === 'fit') fitView();
		if (action === 'open') {
			document.getElementById('file-input')?.click();
		}
	}

	function handleToolboxAction(e) {
		const action = e.detail;
		if (action === 'open') {
			document.getElementById('file-input')?.click();
		} else if (action === 'library') {
			showLibrary = !showLibrary;
		}
	}

	function handleBlockInsert(e) {
		const { block, options } = e.detail;
		console.log('Insert block:', block, options);
		// TODO: Implement block insertion into canvas
		alert(`Insert ${block.name} (scale=${options.scale}, angle=${options.angle})`);
	}

	function handleFileSelect(e) {
		const file = e.detail;
		activeFile = file;
		pattern = file.pattern;
		initLayers();
		fitView();
		render();
	}

	function handleFileClose(e) {
		const file = e.detail;
		files = files.filter((f) => f !== file);
		if (activeFile === file) {
			activeFile = files[0] || null;
			pattern = activeFile?.pattern || null;
			if (pattern) {
				initLayers();
				fitView();
				render();
			}
		}
	}

	function handleNewFile() {
		document.getElementById('file-input')?.click();
	}

	async function handleUpload(event) {
		const file = event.target.files[0];
		if (!file) return;

		const formData = new FormData();
		formData.append('file', file);

		try {
			const response = await fetch('/api/v1/patterns/ingest', {
				method: 'POST',
				body: formData
			});
			const result = await response.json();
			const newFile = {
				name: result.filename || 'Untitled',
				active: true,
				dirty: false,
				pattern: result
			};
			files = [...files.map((f) => ({ ...f, active: false })), newFile];
			activeFile = newFile;
			pattern = result;
			initLayers();
			fitView();
			render();
		} catch (error) {
			console.error(error);
			alert('Upload failed');
		}
	}

	$: filteredHoles = selectedPanel
		? pattern.holes.filter((h) => h.inside_panel_id === selectedPanel.id)
		: [];

	$: filteredLabels = selectedPanel
		? pattern.labels.filter((l) => l.linked_panel_id === selectedPanel.id)
		: [];
</script>

<svelte:head>
	<title>Zervi Pattern Platform</title>
</svelte:head>

<input type="file" id="file-input" accept=".dxf" class="hidden" on:change={handleUpload} />

<div class="h-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-primary)] overflow-hidden">
	<MenuBar on:action={handleMenuAction} />
	<RibbonTabs on:action={handleMenuAction} />
	<FileTabs
		{files}
		on:select={handleFileSelect}
		on:close={handleFileClose}
		on:new={handleNewFile}
	/>

	{#if pattern}
		<div class="flex flex-1 overflow-hidden">
			<!-- Toolbox -->
			<Toolbox on:action={handleToolboxAction} />

			<!-- Block Library -->
			{#if showLibrary}
				<div class="w-80 border-r border-[var(--border-color)]">
					<BlockLibrary on:insert={handleBlockInsert} />
				</div>
			{/if}

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
					<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">
						Holes ({selectedPanel ? filteredHoles.length : 0})
					</h3>
					<div class="text-sm space-y-1 max-h-48 overflow-y-auto">
						{#each filteredHoles as hole}
							<div class="px-2 py-1 rounded bg-[var(--bg-elevated)]">
								<span class="text-[var(--success)]">{hole.classification}</span>
								<span class="text-[var(--text-secondary)]"> r={hole.radius_mm}mm</span>
							</div>
						{/each}
					</div>
				</div>

				<div>
					<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">
						Labels ({selectedPanel ? filteredLabels.length : 0})
					</h3>
					<div class="text-sm space-y-1 max-h-96 overflow-y-auto">
						{#each filteredLabels as label}
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
				<button
					on:click={handleNewFile}
					class="px-4 py-2 rounded bg-[var(--accent)] text-white hover:opacity-90"
				>
					Upload DXF
				</button>
			</div>
		</div>
	{/if}

	<StatusBar
		{coordinates}
		scale={view.scale}
		panelCount={pattern?.panels?.length || 0}
		{selectedPanel}
	/>
</div>
