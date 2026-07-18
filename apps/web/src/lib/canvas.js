/**
 * Canvas rendering utilities for Zervi Pattern Platform.
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

export function renderPattern(ctx, pattern, view) {
	const { width, height, scale, offsetX, offsetY } = view;
	ctx.clearRect(0, 0, width, height);
	ctx.save();

	// Apply view transform
	ctx.translate(offsetX, offsetY);
	ctx.scale(scale, scale);

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
				ctx.fillStyle = COLORS.PANEL_FILL;
				ctx.fill();
				ctx.strokeStyle = COLORS.PANEL_OUTLINE;
				ctx.lineWidth = 1.5 / scale;
				ctx.stroke();
			}
		}
	}

	// Draw holes
	if (pattern.holes) {
		for (const hole of pattern.holes) {
			ctx.beginPath();
			ctx.arc(hole.center[0], hole.center[1], hole.radius_mm, 0, Math.PI * 2);
			ctx.strokeStyle = hole.classification === 'notch' ? COLORS.NOTCH : COLORS.HOLE;
			ctx.lineWidth = 2 / scale;
			ctx.stroke();
		}
	}

	// Draw labels
	if (pattern.labels) {
		for (const label of pattern.labels) {
			if (!label.position || !label.text) continue;
			ctx.fillStyle = getLayerColor(label.layer);
			ctx.font = `${(label.height || 10) * 0.8}px Arial`;
			ctx.textAlign = 'center';
			ctx.textBaseline = 'middle';
			ctx.fillText(label.text, label.position[0], label.position[1]);
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
