<script>
	import { goto } from '$app/navigation';
	let uploading = false;

	async function handleUpload(event) {
		const file = event.target.files[0];
		if (!file) return;

		uploading = true;
		const formData = new FormData();
		formData.append('file', file);

		try {
			const response = await fetch('/api/v1/patterns/ingest', {
				method: 'POST',
				body: formData
			});
			const result = await response.json();
			sessionStorage.setItem('zervi-pattern', JSON.stringify(result));
			goto('/viewer');
		} catch (error) {
			console.error(error);
			alert('Upload failed');
		} finally {
			uploading = false;
		}
	}
</script>

<main class="flex flex-col items-center justify-center min-h-screen p-8">
	<div class="max-w-2xl w-full text-center space-y-8">
		<h1 class="text-4xl font-bold text-[var(--accent)]">
			Zervi Pattern Platform
		</h1>
		<p class="text-[var(--text-secondary)] text-lg">
			AI-first design intelligence for car seat cover manufacturing.
		</p>

		<div class="border-2 border-dashed border-[var(--border-color)] rounded-xl p-12 hover:border-[var(--accent)] transition-colors">
			<label class="cursor-pointer block {uploading ? 'opacity-50 pointer-events-none' : ''}">
				<input
					type="file"
					accept=".dxf"
					class="hidden"
					on:change={handleUpload}
					disabled={uploading}
				/>
				<div class="space-y-4">
					<div class="text-5xl">📐</div>
					<div class="text-xl font-medium">
						{uploading ? 'Parsing DXF...' : 'Upload DXF Pattern'}
					</div>
					<div class="text-sm text-[var(--text-secondary)]">
						Drop a Zervi-template DXF file here or click to browse
					</div>
				</div>
			</label>
		</div>

		<div class="grid grid-cols-3 gap-4 text-sm text-[var(--text-secondary)]">
			<div class="p-4 rounded-lg bg-[var(--bg-secondary)]">
				<div class="text-2xl mb-2">🔍</div>
				<div>Auto-detect panels</div>
			</div>
			<div class="p-4 rounded-lg bg-[var(--bg-secondary)]">
				<div class="text-2xl mb-2">📋</div>
				<div>Multi-level BOM</div>
			</div>
			<div class="p-4 rounded-lg bg-[var(--bg-secondary)]">
				<div class="text-2xl mb-2">🤖</div>
				<div>AI agents</div>
			</div>
		</div>
	</div>
</main>
