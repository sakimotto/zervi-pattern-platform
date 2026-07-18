<script>
	import { onMount, onDestroy } from 'svelte';
	import { fabric } from 'fabric';

	export let pattern = null;
	export let onSelectionChange = () => {};
	export let onObjectModified = () => {};

	let canvasEl;
	let canvas;
	let isPanning = false;
	let panStart = { x: 0, y: 0 };

	onMount(() => {
		canvas = new fabric.Canvas(canvasEl, {
			selection: true,
			preserveObjectStacking: true,
			backgroundColor: '#0a0a0a'
		});

		// Handle selection changes
		canvas.on('selection:created', (e) => {
			onSelectionChange(e.selected || []);
		});
		canvas.on('selection:updated', (e) => {
			onSelectionChange(e.selected || []);
		});
		canvas.on('selection:cleared', () => {
			onSelectionChange([]);
		});

		// Handle object modifications
		canvas.on('object:modified', (e) => {
			onObjectModified(e.target);
		});

		// Zoom with mouse wheel
		canvas.on('mouse:wheel', (opt) => {
			const delta = opt.e.deltaY;
			let zoom = canvas.getZoom();
			zoom *= 0.999 ** delta;
			if (zoom > 20) zoom = 20;
			if (zoom < 0.01) zoom = 0.01;
			canvas.zoomToPoint({ x: opt.e.offsetX, y: opt.e.offsetY }, zoom);
			opt.e.preventDefault();
			opt.e.stopPropagation();
		});

		// Pan with middle/right mouse or space+drag
		canvas.on('mouse:down', (opt) => {
			const evt = opt.e;
			if (evt.button === 1 || evt.button === 2 || evt.altKey) {
				isPanning = true;
				panStart = { x: evt.clientX, y: evt.clientY };
				canvas.selection = false;
			}
		});

		canvas.on('mouse:move', (opt) => {
			if (isPanning) {
				const evt = opt.e;
				const vpt = canvas.viewportTransform;
				vpt[4] += evt.clientX - panStart.x;
				vpt[5] += evt.clientY - panStart.y;
				canvas.requestRenderAll();
				panStart = { x: evt.clientX, y: evt.clientY };
			}
		});

		canvas.on('mouse:up', () => {
			isPanning = false;
			canvas.selection = true;
		});

		resizeCanvas();
		window.addEventListener('resize', resizeCanvas);

		if (pattern) {
			loadPattern(pattern);
		}
	});

	onDestroy(() => {
		window.removeEventListener('resize', resizeCanvas);
		if (canvas) {
			canvas.dispose();
		}
	});

	function resizeCanvas() {
		if (!canvas) return;
		const parent = canvasEl.parentElement;
		canvas.setWidth(parent.clientWidth);
		canvas.setHeight(parent.clientHeight);
		canvas.renderAll();
	}

	export function loadPattern(patternData) {
		if (!canvas) return;
		canvas.clear();

		// Set background
		canvas.backgroundColor = '#0a0a0a';

		// Load panels as Fabric polygons
		if (patternData.panels) {
			for (const panel of patternData.panels) {
				const points = panel.polygon.map((p) => ({ x: p[0], y: p[1] }));
				const poly = new fabric.Polygon(points, {
					fill: 'rgba(79, 140, 255, 0.08)',
					stroke: '#4f8cff',
					strokeWidth: 1.5,
					selectable: true,
					hasControls: true,
					hasBorders: true,
					lockRotation: true,
					data: {
						id: panel.id,
						type: 'panel',
						labels: panel.labels,
						area: panel.area_mm2,
						cutLength: panel.cut_length_mm
					}
				});
				canvas.add(poly);
			}
		}

		// Load holes as Fabric circles
		if (patternData.holes) {
			for (const hole of patternData.holes) {
				const circle = new fabric.Circle({
					left: hole.center[0] - hole.radius_mm,
					top: hole.center[1] - hole.radius_mm,
					radius: hole.radius_mm,
					fill: 'transparent',
					stroke: hole.classification === 'notch' ? '#4ade80' : '#fbbf24',
					strokeWidth: 2,
					selectable: true,
					data: {
						id: `hole-${hole.center[0]}-${hole.center[1]}`,
						type: 'hole',
						classification: hole.classification,
						radius: hole.radius_mm
					}
				});
				canvas.add(circle);
			}
		}

		// Load labels as Fabric text
		if (patternData.labels) {
			for (const label of patternData.labels) {
				const text = new fabric.Text(label.text, {
					left: label.position[0],
					top: label.position[1],
					fontSize: label.height || 10,
					fill: '#e8eaed',
					selectable: true,
					data: {
						id: `label-${label.text}-${label.position[0]}`,
						type: 'label',
						layer: label.layer
					}
				});
				canvas.add(text);
			}
		}

		// Fit to view
		zoomToFit();
	}

	export function zoomToFit() {
		if (!canvas) return;
		const objects = canvas.getObjects();
		if (objects.length === 0) return;

		const group = new fabric.Group(objects, { canvas });
		const groupWidth = group.width || 1;
		const groupHeight = group.height || 1;
		const canvasWidth = canvas.getWidth();
		const canvasHeight = canvas.getHeight();

		const scaleX = canvasWidth / groupWidth;
		const scaleY = canvasHeight / groupHeight;
		const scale = Math.min(scaleX, scaleY) * 0.9;

		canvas.setZoom(scale);
		canvas.viewportTransform[4] = (canvasWidth - groupWidth * scale) / 2 - (group.left || 0) * scale;
		canvas.viewportTransform[5] = (canvasHeight - groupHeight * scale) / 2 - (group.top || 0) * scale;
		canvas.requestRenderAll();
		group.destroy();
	}

	export function getSelectedObjects() {
		return canvas ? canvas.getActiveObjects() : [];
	}

	export function deleteSelected() {
		if (!canvas) return;
		const activeObjects = canvas.getActiveObjects();
		activeObjects.forEach((obj) => canvas.remove(obj));
		canvas.discardActiveObject();
		canvas.requestRenderAll();
	}

	export function addLine(x1, y1, x2, y2) {
		const line = new fabric.Line([x1, y1, x2, y2], {
			stroke: '#ff6b6b',
			strokeWidth: 1.5,
			selectable: true,
			data: { type: 'line' }
		});
		canvas.add(line);
	}

	export function addCircle(x, y, radius) {
		const circle = new fabric.Circle({
			left: x - radius,
			top: y - radius,
			radius: radius,
			fill: 'transparent',
			stroke: '#4ade80',
			strokeWidth: 2,
			selectable: true,
			data: { type: 'notch' }
		});
		canvas.add(circle);
	}
</script>

<canvas bind:this={canvasEl} class="w-full h-full" />
