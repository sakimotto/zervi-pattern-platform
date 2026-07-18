/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				zervi: {
					50: '#eff6ff',
					100: '#dbeafe',
					500: '#4f8cff',
					600: '#2563eb',
					700: '#1d4ed8',
					900: '#1e3a8a'
				}
			}
		}
	},
	plugins: []
};
