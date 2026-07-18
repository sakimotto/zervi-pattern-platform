<script>
	import { onMount, tick } from 'svelte';
	import MenuBar from '$lib/components/MenuBar.svelte';
	import RibbonTabs from '$lib/components/RibbonTabs.svelte';
	import FileTabs from '$lib/components/FileTabs.svelte';
	import StatusBar from '$lib/components/StatusBar.svelte';
	import Toolbox from '$lib/components/Toolbox.svelte';
	import BlockLibrary from '$lib/components/BlockLibrary.svelte';
	import FabricCanvas from '$lib/components/FabricCanvas.svelte';

	let pattern = null;
	let selectedObjects = [];
	let visibleLayers = new Set();
	let coordinates = { x: 0, y: 0 };

	let files = [];
	let activeFile = null;
	let showLibrary = false;
	let editingPanel = null;
	let editName = '';
	let editMode = 'select';

	let fabricCanvas;

	onMount(async () => {
		const stored = sessionStorage.getItem('zervi-pattern');
		if (stored) {
			try {
				const initialPattern = JSON.parse(stored);
				addFile(initialPattern);
				await tick();
				if (fabricCanvas && pattern) {
					fabricCanvas.loadPattern(pattern);
				}
			} catch (e) {
				console.error('Failed to parse pattern:', e);
			}
		}
	});

	function addFile(patternData) {
		const newFile = {
			name: patternData.filename || 'Untitled',
			active: true,
			dirty: false,
			pattern: patternData
		};
		files = [...files.map((f) => ({ ...f, active: false })), newFile];
		activeFile = newFile;
		pattern = patternData;
		initLayers();
		if (fabricCanvas) {
			fabricCanvas.loadPattern(pattern);
		}
	}

	function switchToFile(file) {
		files = files.map((f) => ({ ...f, active: f === file }));
		activeFile = file;
		pattern = file.pattern;
		selectedObjects = [];
		initLayers();
		if (fabricCanvas) {
			fabricCanvas.loadPattern(pattern);
		}
	}

	function closeFile(file) {
		files = files.filter((f) => f !== file);
		if (activeFile === file) {
			activeFile = files[0] || null;
			pattern = activeFile?.pattern || null;
			selectedObjects = [];
			if (pattern && fabricCanvas) {
				fabricCanvas.loadPattern(pattern);
			}
		}
	}

	function initLayers() {
		if (pattern && pattern.layers) {
			visibleLayers = new Set(pattern.layers);
		}
	}

	function handleSelectionChange(objects) {
		selectedObjects = objects;
	}

	function handleObjectModified(obj) {
		console.log('Object modified:', obj);
		if (activeFile) {
			activeFile.dirty = true;
		}
	}

	function handleMenuAction(e) {
		const action = e.detail;
		if (action === 'open') {
			document.getElementById('file-input')?.click();
		} else if (action === 'fit' && fabricCanvas) {
			fabricCanvas.zoomToFit();
		}
	}

	function handleToolboxAction(e) {
		const action = e.detail;
		if (action === 'open') {
			document.getElementById('file-input')?.click();
		} else if (action === 'library') {
			showLibrary = !showLibrary;
		} else if (action === 'fit' && fabricCanvas) {
			fabricCanvas.zoomToFit();
		}
	}

	function handleBlockInsert(e) {
		const { block, options } = e.detail;
		console.log('Insert block:', block, options);
	}

	function handleFileSelect(e) {
		switchToFile(e.detail);
	}

	function handleFileClose(e) {
		closeFile(e.detail);
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
			addFile(result);
		} catch (error) {
			console.error(error);
			alert('Upload failed');
		}
	}

	function setEditMode(mode) {
		editMode = mode;
	}

	function toggleLayer(layer) {
		if (visibleLayers.has(layer)) {
			visibleLayers.delete(layer);
		} else {
			visibleLayers.add(layer);
		}
		visibleLayers = visibleLayers;
		// TODO: Filter Fabric objects by layer
	}

	function selectPanel(panel) {
		// TODO: Select corresponding Fabric object
		console.log('Select panel:', panel);
	}

	function startEditPanel(panel) {
		editingPanel = panel;
		editName = panel.labels[0] || '';
	}

	function saveEditPanel() {
		if (!editingPanel || !activeFile) return;

		const label = pattern.labels.find((l) => l.linked_panel_id === editingPanel.id);
		if (label) {
			label.text = editName;
		}

		editingPanel.labels = [editName];
		activeFile.dirty = true;
		pattern = pattern;
		files = files;

		editingPanel = null;
		editName = '';
	}

	function cancelEditPanel() {
		editingPanel = null;
		editName = '';
	}

	async function exportSelectedPanel() {
		if (selectedObjects.length === 0) return;

		// Get selected panels from Fabric objects
		const selectedPanels = selectedObjects
			.filter((obj) => obj.data?.type === 'panel')
			.map((obj) => ({
				id: obj.data.id,
				labels: obj.data.labels,
				polygon: obj.points.map((p) => [p.x, p.y]),
				area_mm2: obj.data.area,
				cut_length_mm: obj.data.cutLength
			}));

		if (selectedPanels.length === 0) {
			alert('No panels selected');
			return;
		}

		const filename =
			selectedPanels.length === 1
				? selectedPanels[0].labels[0] || selectedPanels[0].id
				: `${selectedPanels.length}_panels`;

		try {
			const response = await fetch('/api/v1/patterns/export-panels', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					panels: selectedPanels,
					holes: pattern.holes,
					labels: pattern.labels,
					filename
				})
			});

			if (!response.ok) throw new Error('Export failed');

			const blob = await response.blob();
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `${filename}.dxf`;
			document.body.appendChild(a);
			a.click();
			a.remove();
			window.URL.revokeObjectURL(url);
		} catch (e) {
			console.error(e);
			alert('Export failed');
		}
	}

	$: filteredHoles =
		selectedObjects.length > 0
			? pattern.holes.filter((h) => selectedObjects.some((obj) => obj.data?.id === h.inside_panel_id))
			: [];

	$: filteredLabels =
		selectedObjects.length > 0
			? pattern.labels.filter((l) => selectedObjects.some((obj) => obj.data?.id === l.linked_panel_id))
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
								class="w-full text-left text-sm px-2 py-1 rounded hover:bg-[var(--bg-elevated)] {selectedObjects.some((obj) => obj.data?.id === panel.id) ? 'bg-[var(--accent)] text-white' : ''}"
							>
								{panel.labels.length > 0 ? panel.labels[0] : panel.id}
							</button>
						{/each}
					</div>
				</div>
			</div>

			<!-- Canvas -->
			<div class="flex-1 relative bg-[#0a0a0a]">
				<FabricCanvas
					bind:this={fabricCanvas}
					{pattern}
					onSelectionChange={handleSelectionChange}
					onObjectModified={handleObjectModified}
				/>
			</div>

			<!-- Right Sidebar -->
			<div class="w-80 bg-[var(--bg-secondary)] border-l border-[var(--border-color)] overflow-y-auto p-3 space-y-4">
				{#if selectedObjects.length > 0}
					<div>
						<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">Selected ({selectedObjects.length})</h3>
						<div class="text-sm space-y-1 max-h-40 overflow-y-auto">
							{#each selectedObjects as obj}
								<div class="px-2 py-1 rounded bg-[var(--bg-elevated)]">
									{obj.data?.labels?.[0] || obj.data?.id || obj.type}
								</div>
							{/each}
						</div>
					</div>

					{#if editingPanel}
						<div class="p-3 bg-[var(--bg-elevated)] rounded border border-[var(--border-color)]">
							<h4 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">Edit Panel Name</h4>
							<input
								type="text"
								bind:value={editName}
								class="w-full px-2 py-1 text-sm bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-[var(--text-primary)] mb-2"
								on:keydown={(e) => e.key === 'Enter' && saveEditPanel()}
							/>
							<div class="flex gap-2">
								<button
									on:click={saveEditPanel}
									class="px-3 py-1 text-sm bg-[var(--accent)] text-white rounded hover:opacity-90"
								>
									Save
								</button>
								<button
									on:click={cancelEditPanel}
									class="px-3 py-1 text-sm bg-[var(--border-color)] text-[var(--text-primary)] rounded hover:opacity-90"
								>
									Cancel
								</button>
							</div>
						</div>
					{/if}

					<button
						on:click={exportSelectedPanel}
						class="w-full px-3 py-2 text-sm bg-[var(--accent)] text-white rounded hover:opacity-90"
					>
						Export Selected as DXF
					</button>
				{/if}

				<div>
					<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">
						Holes ({filteredHoles.length})
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
						Labels ({filteredLabels.length})
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
		scale={1}
		panelCount={pattern?.panels?.length || 0}
		selectedPanel={selectedObjects}
	/>
</div>

<script context="module">
	export function getLayerColor(layer) {
		const l = layer.toUpperCase();
		if (l.includes('CUT')) return '#ff6b6b';
		if (l.includes('NOTCH')) return '#4ade80';
		if (l.includes('STITCH')) return '#fbbf24';
		if (l.includes('TEXT') || l.includes('PART') || l.includes('PANEL')) return '#e8eaed';
		if (l.includes('DIM')) return '#60a5fa';
		if (l.includes('HOLE')) return '#4ade80';
		return '#e8eaed';
	}
</script>
