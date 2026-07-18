/**
 * Canvas rendering utilities for Zervi Pattern Platform.
 * CAD coordinates: X right, Y up.
 * Canvas coordinates: X right, Y down.
 * We flip Y when rendering.
 */

export const COLORS = {
	CUT: '#ff6b6b',
	NOTCH: '#4ade80',
	STITCH: '#fbbf24',
	TEXT: '#e8eaed',
	DIMS: '#60a5fa',
	HOLE: '#4ade80',
	PANEL_FILL: 'rgba(79, 140, 255, 0.08)',
	PANEL_OUTLINE: '#4f8cff',
	SELECTED: '#f97316'
};

export function getLayerColor(layer) {
	const l = layer.toUpperCase();
	if (l.includes('CUT')) return COLORS.CUT;
	if (l.includes('NOTCH')) return COLORS.NOTCH;
	if (l.includes('STITCH')) return COLORS.STITCH;
	if (l.includes('TEXT') || l.includes('PART') || l.includes('PANEL')) return COLORS.TEXT;
	if (l.includes('DIM')) return COLORS.DIMS;
	if (l.includes('HOLE')) return COLORS.HOLE;
	return COLORS.TEXT;
}

export function pointInPolygon(point, polygon) {
	// Ray casting algorithm
	let inside = false;
	const x = point[0];
	const y = point[1];
	for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
		const xi = polygon[i][0];
		const yi = polygon[i][1];
		const xj = polygon[j][0];
		const yj = polygon[j][1];
		const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
		if (intersect) inside = !inside;
	}
	return inside;
}

export function renderPattern(ctx, pattern, view, visibleLayers = null, selectedPanelIds = []) {
	const { width, height, scale, offsetX, offsetY } = view;
	ctx.clearRect(0, 0, width, height);
	ctx.save();

	// Apply view transform with Y-flip:
	// 1. Move origin to (offsetX, offsetY + height)
	// 2. Scale X by scale, Y by -scale (flip Y)
	ctx.translate(offsetX, offsetY + height);
	ctx.scale(scale, -scale);

	// Draw panel fills first
	if (pattern.panels) {
		for (const panel of pattern.panels) {
			ctx.beginPath();
			const pts = panel.polygon;
			if (pts && pts.length > 0) {
				ctx.moveTo(pts[0][0], pts[0][1]);
				for (let i = 1; i < pts.length; i++) {
					ctx.lineTo(pts[i][0], pts[i][1]);
				}
				ctx.closePath();
				const isSelected = selectedPanelIds.includes(panel.id);
				ctx.fillStyle = isSelected ? 'rgba(249, 115, 22, 0.2)' : COLORS.PANEL_FILL;
				ctx.fill();
				ctx.strokeStyle = isSelected ? COLORS.SELECTED : COLORS.PANEL_OUTLINE;
				ctx.lineWidth = (isSelected ? 3 : 1.5) / scale;
				ctx.stroke();
			}
		}
	}

	// Draw holes
	if (pattern.holes) {
		for (const hole of pattern.holes) {
			if (visibleLayers && !visibleLayers.has(hole.layer)) continue;
			ctx.beginPath();
			ctx.arc(hole.center[0], hole.center[1], hole.radius_mm, 0, Math.PI * 2);
			ctx.strokeStyle = hole.classification === 'notch' ? COLORS.NOTCH : COLORS.HOLE;
			ctx.lineWidth = 2 / scale;
			ctx.stroke();
		}
	}

	// Draw custom entities (user-drawn lines, etc.)
	if (pattern.entities) {
		for (const entity of pattern.entities) {
			if (visibleLayers && !visibleLayers.has(entity.layer)) continue;
			if (entity.type === 'LINE') {
				ctx.beginPath();
				ctx.moveTo(entity.geometry.start[0], entity.geometry.start[1]);
				ctx.lineTo(entity.geometry.end[0], entity.geometry.end[1]);
				ctx.strokeStyle = COLORS.CUT;
				ctx.lineWidth = 1.5 / scale;
				ctx.stroke();
			}
		}
	}

	// Draw labels
	if (pattern.labels) {
		for (const label of pattern.labels) {
			if (visibleLayers && !visibleLayers.has(label.layer)) continue;
			if (!label.position || !label.text) continue;
			ctx.fillStyle = getLayerColor(label.layer);
			ctx.font = `${(label.height || 10) * 0.8}px Arial`;
			ctx.textAlign = 'center';
			ctx.textBaseline = 'middle';
			// Text needs to be flipped back so it reads correctly
			ctx.save();
			ctx.translate(label.position[0], label.position[1]);
			ctx.scale(1, -1);
			ctx.fillText(label.text, 0, 0);
			ctx.restore();
		}
	}

	ctx.restore();
}

export function fitToView(pattern, canvasWidth, canvasHeight, padding = 50) {
	const bbox = pattern.bounding_box;
	if (!bbox) {
		return { scale: 1, offsetX: 0, offsetY: 0 };
	}

	const minX = bbox.min[0];
	const minY = bbox.min[1];
	const maxX = bbox.max[0];
	const maxY = bbox.max[1];

	const patternWidth = maxX - minX;
	const patternHeight = maxY - minY;

	const scaleX = (canvasWidth - padding * 2) / patternWidth;
	const scaleY = (canvasHeight - padding * 2) / patternHeight;
	const scale = Math.min(scaleX, scaleY);

	const offsetX = (canvasWidth - patternWidth * scale) / 2 - minX * scale;
	const offsetY = (canvasHeight - patternHeight * scale) / 2 - minY * scale;

	return { scale, offsetX, offsetY };
}
