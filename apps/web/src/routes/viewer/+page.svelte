<script>
	import { onMount, tick } from 'svelte';
	import { renderPattern, fitToView, getLayerColor, pointInPolygon } from '$lib/canvas.js';
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
	let isSelecting = false;
	let isTouchPanning = false;
	let touchDistance = 0;
	let touchCenter = { x: 0, y: 0 };
	let panStart = { x: 0, y: 0 };
	let selectStart = { x: 0, y: 0 };
	let selectEnd = { x: 0, y: 0 };
	let selectedPanels = [];
	let visibleLayers = new Set();
	let coordinates = { x: 0, y: 0 };

	let files = [];
	let activeFile = null;
	let showLibrary = false;
	let editingPanel = null;

	// CAD editing modes
	let editMode = 'select'; // select, move, draw-line, add-notch
	let movingPanel = null;
	let moveOffset = { x: 0, y: 0 };
	let drawLineStart = null;
	let editName = '';

	onMount(async () => {
		const stored = sessionStorage.getItem('zervi-pattern');
		if (stored) {
			try {
				const initialPattern = JSON.parse(stored);
				addFile(initialPattern);
				await tick();
				initCanvas();
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
		fitView();
	}

	function switchToFile(file) {
		files = files.map((f) => ({ ...f, active: f === file }));
		activeFile = file;
		pattern = file.pattern;
		selectedPanels = [];
		initLayers();
		fitView();
		render();
	}

	function closeFile(file) {
		files = files.filter((f) => f !== file);
		if (activeFile === file) {
			activeFile = files[0] || null;
			pattern = activeFile?.pattern || null;
			selectedPanels = [];
			if (pattern) {
				initLayers();
				fitView();
				render();
			}
		}
	}

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
		renderPattern(ctx, pattern, view, visibleLayers, selectedPanels.map((p) => p.id));

		// Draw rubber band selection rectangle
		if (isSelecting) {
			const minX = Math.min(selectStart.x, selectEnd.x);
			const maxX = Math.max(selectStart.x, selectEnd.x);
			const minY = Math.min(selectStart.y, selectEnd.y);
			const maxY = Math.max(selectStart.y, selectEnd.y);

			ctx.save();
			ctx.strokeStyle = '#4f8cff';
			ctx.fillStyle = 'rgba(79, 140, 255, 0.1)';
			ctx.lineWidth = 1;
			ctx.setLineDash([5, 5]);
			ctx.fillRect(minX, minY, maxX - minX, maxY - minY);
			ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
			ctx.restore();
		}

		// Draw line preview when in draw-line mode
		if (editMode === 'draw-line' && drawLineStart) {
			const worldX = coordinates.x;
			const worldY = coordinates.y;

			// Convert to screen coordinates
			const sx = drawLineStart.x * view.scale + view.offsetX;
			const sy = view.height - (drawLineStart.y * view.scale + view.offsetY);
			const ex = worldX * view.scale + view.offsetX;
			const ey = view.height - (worldY * view.scale + view.offsetY);

			ctx.save();
			ctx.strokeStyle = '#4ade80';
			ctx.lineWidth = 2;
			ctx.setLineDash([5, 5]);
			ctx.beginPath();
			ctx.moveTo(sx, sy);
			ctx.lineTo(ex, ey);
			ctx.stroke();
			ctx.restore();
		}
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
		const rect = canvas.getBoundingClientRect();
		const mx = e.clientX - rect.left;
		const my = e.clientY - rect.top;
		const worldX = (mx - view.offsetX) / view.scale;
		const worldY = (view.offsetY + view.height - my) / view.scale;

		if (e.button === 0) {
			if (editMode === 'move' && selectedPanels.length > 0) {
				// Start moving selected panels
				movingPanel = selectedPanels[0];
				moveOffset = { x: worldX - movingPanel.centroid[0], y: worldY - movingPanel.centroid[1] };
				return;
			}

			if (editMode === 'draw-line') {
				if (!drawLineStart) {
					drawLineStart = { x: worldX, y: worldY };
				} else {
					// Finish line
					pattern.entities = pattern.entities || [];
					pattern.entities.push({
						type: 'LINE',
						layer: 'CUT',
						geometry: {
							start: [drawLineStart.x, drawLineStart.y],
							end: [worldX, worldY]
						}
					});
					drawLineStart = null;
					render();
				}
				return;
			}

			if (editMode === 'add-notch') {
				// Add a notch at click position
				pattern.holes.push({
					center: [worldX, worldY],
					radius_mm: 13,
					diameter_mm: 26,
					classification: 'notch',
					layer: 'NOTCH',
					inside_panel_id: null
				});
				render();
				return;
			}

			// Default: select mode
			const clickedPanel = pattern.panels.find((panel) => pointInPolygon([worldX, worldY], panel.polygon));

			if (clickedPanel) {
				if (e.ctrlKey || e.metaKey) {
					if (selectedPanels.find((p) => p.id === clickedPanel.id)) {
						selectedPanels = selectedPanels.filter((p) => p.id !== clickedPanel.id);
					} else {
						selectedPanels = [...selectedPanels, clickedPanel];
					}
				} else {
					selectedPanels = [clickedPanel];
				}
				render();
				return;
			}

			// No panel clicked: start rubber band selection
			isSelecting = true;
			selectStart = { x: mx, y: my };
			selectEnd = { x: mx, y: my };
		} else if (e.button === 1 || e.button === 2) {
			// Middle or right click: pan
			isPanning = true;
			panStart = { x: e.clientX, y: e.clientY };
			canvas.style.cursor = 'grabbing';
		}
	}

	function onMouseMove(e) {
		const rect = canvas.getBoundingClientRect();
		const mx = e.clientX - rect.left;
		const my = e.clientY - rect.top;

		if (!isPanning && !isSelecting && !movingPanel) {
			// Update coordinates
			coordinates = {
				x: (mx - view.offsetX) / view.scale,
				y: (view.offsetY + view.height - my) / view.scale
			};
			return;
		}

		if (isSelecting) {
			selectEnd = { x: mx, y: my };
			render();
			return;
		}

		if (movingPanel) {
			const worldX = (mx - view.offsetX) / view.scale;
			const worldY = (view.offsetY + view.height - my) / view.scale;
			const dx = worldX - moveOffset.x - movingPanel.centroid[0];
			const dy = worldY - moveOffset.y - movingPanel.centroid[1];

			// Move all selected panels
			for (const panel of selectedPanels) {
				for (const pt of panel.polygon) {
					pt[0] += dx;
					pt[1] += dy;
				}
				panel.centroid[0] += dx;
				panel.centroid[1] += dy;
			}

			// Update move offset for next frame
			moveOffset = { x: worldX - movingPanel.centroid[0], y: worldY - movingPanel.centroid[1] };
			render();
			return;
		}

		if (isPanning) {
			view.offsetX += e.clientX - panStart.x;
			view.offsetY += e.clientY - panStart.y;
			panStart = { x: e.clientX, y: e.clientY };
			render();
		}
	}

	function onMouseUp(e) {
		if (movingPanel) {
			movingPanel = null;
			render();
			return;
		}

		if (isSelecting) {
			// Finish rubber band selection
			const minX = Math.min(selectStart.x, selectEnd.x);
			const maxX = Math.max(selectStart.x, selectEnd.x);
			const minY = Math.min(selectStart.y, selectEnd.y);
			const maxY = Math.max(selectStart.y, selectEnd.y);

			// Convert to world coordinates
			const worldMinX = (minX - view.offsetX) / view.scale;
			const worldMaxX = (maxX - view.offsetX) / view.scale;
			const worldMinY = (view.offsetY + view.height - maxY) / view.scale;
			const worldMaxY = (view.offsetY + view.height - minY) / view.scale;

			// Select panels whose centroid is inside the rubber band
			const newSelection = pattern.panels.filter((panel) => {
				const cx = panel.centroid[0];
				const cy = panel.centroid[1];
				return cx >= worldMinX && cx <= worldMaxX && cy >= worldMinY && cy <= worldMaxY;
			});

			if (e.ctrlKey || e.metaKey) {
				// Add to selection
				const newIds = new Set([...selectedPanels.map((p) => p.id), ...newSelection.map((p) => p.id)]);
				selectedPanels = pattern.panels.filter((p) => newIds.has(p.id));
			} else {
				selectedPanels = newSelection;
			}

			isSelecting = false;
			render();
			return;
		}

		isPanning = false;
		canvas.style.cursor = 'grab';
	}

	// Touch handlers
	function onTouchStart(e) {
		e.preventDefault();
		if (e.touches.length === 1) {
			// Single touch: could be select or pan
			const rect = canvas.getBoundingClientRect();
			const mx = e.touches[0].clientX - rect.left;
			const my = e.touches[0].clientY - rect.top;
			const worldX = (mx - view.offsetX) / view.scale;
			const worldY = (view.offsetY + view.height - my) / view.scale;

			const clickedPanel = pattern.panels.find((panel) => pointInPolygon([worldX, worldY], panel.polygon));

			if (clickedPanel) {
				selectedPanels = [clickedPanel];
				render();
			} else {
				// Start rubber band
				isSelecting = true;
				selectStart = { x: mx, y: my };
				selectEnd = { x: mx, y: my };
			}
		} else if (e.touches.length === 2) {
			// Two fingers: pinch to zoom
			isTouchPanning = true;
			const dx = e.touches[0].clientX - e.touches[1].clientX;
			const dy = e.touches[0].clientY - e.touches[1].clientY;
			touchDistance = Math.sqrt(dx * dx + dy * dy);
			touchCenter = {
				x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
				y: (e.touches[0].clientY + e.touches[1].clientY) / 2
			};
		}
	}

	function onTouchMove(e) {
		e.preventDefault();
		if (isSelecting && e.touches.length === 1) {
			const rect = canvas.getBoundingClientRect();
			selectEnd = {
				x: e.touches[0].clientX - rect.left,
				y: e.touches[0].clientY - rect.top
			};
			render();
		} else if (isTouchPanning && e.touches.length === 2) {
			const dx = e.touches[0].clientX - e.touches[1].clientX;
			const dy = e.touches[0].clientY - e.touches[1].clientY;
			const newDistance = Math.sqrt(dx * dx + dy * dy);
			const newCenter = {
				x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
				y: (e.touches[0].clientY + e.touches[1].clientY) / 2
			};

			// Zoom based on pinch distance change
			if (touchDistance > 0) {
				const zoom = newDistance / touchDistance;
				const rect = canvas.getBoundingClientRect();
				const mx = newCenter.x - rect.left;
				const my = newCenter.y - rect.top;

				const wx = (mx - view.offsetX) / view.scale;
				const wy = (view.offsetY + view.height - my) / view.scale;

				view.scale *= zoom;
				view.offsetX = mx - wx * view.scale;
				view.offsetY = my - (view.height - wy * view.scale);
			}

			// Pan based on center movement
			view.offsetX += newCenter.x - touchCenter.x;
			view.offsetY += newCenter.y - touchCenter.y;

			touchDistance = newDistance;
			touchCenter = newCenter;
			render();
		}
	}

	function onTouchEnd(e) {
		if (isSelecting) {
			isSelecting = false;
			render();
		}
		if (isTouchPanning) {
			isTouchPanning = false;
		}
	}

	function setEditMode(mode) {
		editMode = mode;
		movingPanel = null;
		drawLineStart = null;
		canvas.style.cursor = mode === 'select' ? 'default' : mode === 'move' ? 'move' : 'crosshair';
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
		// Toggle selection when clicking panel in sidebar
		if (selectedPanels.find((p) => p.id === panel.id)) {
			selectedPanels = selectedPanels.filter((p) => p.id !== panel.id);
		} else {
			selectedPanels = [...selectedPanels, panel];
		}
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
			render();
		} catch (error) {
			console.error(error);
			alert('Upload failed');
		}
	}

	function startEditPanel(panel) {
		editingPanel = panel;
		editName = panel.labels[0] || '';
	}

	function saveEditPanel() {
		if (!editingPanel || !activeFile) return;

		// Update the label in the pattern
		const label = pattern.labels.find((l) => l.linked_panel_id === editingPanel.id);
		if (label) {
			label.text = editName;
		}

		// Update panel labels array
		editingPanel.labels = [editName];

		// Mark file as dirty
		activeFile.dirty = true;

		// Force Svelte reactivity so the left panel list updates
		pattern = pattern;
		files = files;

		editingPanel = null;
		editName = '';
		render();
	}

	function cancelEditPanel() {
		editingPanel = null;
		editName = '';
	}

	async function exportSelectedPanel() {
		if (selectedPanels.length === 0) return;

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

	async function applySeamAllowance() {
		if (selectedPanels.length === 0) return;

		const distance = prompt('Seam allowance (mm):', '10');
		if (!distance || isNaN(parseFloat(distance))) return;

		try {
			const response = await fetch('/api/v1/patterns/seam-allowance', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					panels: selectedPanels,
					distance_mm: parseFloat(distance)
				})
			});

			if (!response.ok) throw new Error('Seam allowance failed');

			const result = await response.json();
			// Update panels with new geometry
			for (const updatedPanel of result.panels) {
				const idx = pattern.panels.findIndex((p) => p.id === updatedPanel.id);
				if (idx >= 0) {
					pattern.panels[idx] = updatedPanel;
				}
			}
			pattern = pattern;
			render();
		} catch (e) {
			console.error(e);
			alert('Seam allowance failed');
		}
	}

	$: filteredHoles =
		selectedPanels.length > 0
			? pattern.holes.filter((h) => selectedPanels.some((p) => p.id === h.inside_panel_id))
			: [];

	$: filteredLabels =
		selectedPanels.length > 0
			? pattern.labels.filter((l) => selectedPanels.some((p) => p.id === l.linked_panel_id))
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
								class="w-full text-left text-sm px-2 py-1 rounded hover:bg-[var(--bg-elevated)] {selectedPanels.some((p) => p.id === panel.id) ? 'bg-[var(--accent)] text-white' : ''}"
							>
								{panel.labels.length > 0 ? panel.labels[0] : panel.id}
							</button>
						{/each}
					</div>
				</div>
			</div>

			<!-- Canvas -->
			<div class="flex-1 relative bg-[#0a0a0a]">
				<!-- Edit Mode Toolbar -->
				<div class="absolute top-2 left-2 z-10 flex gap-1 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded p-1">
					<button
						on:click={() => setEditMode('select')}
						class="px-2 py-1 text-sm rounded {editMode === 'select' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]'}"
						title="Select"
					>
						⬚ Select
					</button>
					<button
						on:click={() => setEditMode('move')}
						class="px-2 py-1 text-sm rounded {editMode === 'move' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]'}"
						title="Move Panels"
					>
						✥ Move
					</button>
					<button
						on:click={() => setEditMode('draw-line')}
						class="px-2 py-1 text-sm rounded {editMode === 'draw-line' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]'}"
						title="Draw Line"
					>
						╱ Line
					</button>
					<button
						on:click={() => setEditMode('add-notch')}
						class="px-2 py-1 text-sm rounded {editMode === 'add-notch' ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]'}"
						title="Add Notch"
					>
						◉ Notch
					</button>
				</div>

				<canvas
					bind:this={canvas}
					on:wheel={onWheel}
					on:mousedown={onMouseDown}
					on:mousemove={onMouseMove}
					on:mouseup={onMouseUp}
					on:mouseleave={onMouseUp}
					on:touchstart={onTouchStart}
					on:touchmove={onTouchMove}
					on:touchend={onTouchEnd}
					class="w-full h-full cursor-grab"
				></canvas>
			</div>

			<!-- Right Sidebar -->
			<div class="w-80 bg-[var(--bg-secondary)] border-l border-[var(--border-color)] overflow-y-auto p-3 space-y-4">
				{#if selectedPanels.length > 0}
					<div>
						<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">Selected Panels ({selectedPanels.length})</h3>
						<div class="text-sm space-y-1 max-h-40 overflow-y-auto">
							{#each selectedPanels as panel}
								<div class="px-2 py-1 rounded bg-[var(--bg-elevated)] flex items-center justify-between">
									<span>{panel.labels.length > 0 ? panel.labels[0] : panel.id}</span>
									<button
										on:click={() => startEditPanel(panel)}
										class="text-xs text-[var(--accent)] hover:underline"
									>
										Edit
									</button>
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
						Export {selectedPanels.length > 1 ? `${selectedPanels.length} Panels` : 'Selected Panel'} as DXF
					</button>

					<button
						on:click={applySeamAllowance}
						class="w-full px-3 py-2 text-sm bg-[var(--success)] text-white rounded hover:opacity-90"
					>
						Apply Seam Allowance
					</button>
				{/if}

				<div>
					<h3 class="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">
						Holes ({selectedPanels.length > 0 ? filteredHoles.length : 0})
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
						Labels ({selectedPanels.length > 0 ? filteredLabels.length : 0})
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
		selectedPanel={selectedPanels}
	/>
</div>
