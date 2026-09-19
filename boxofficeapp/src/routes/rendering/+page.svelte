<!-- shows the current rendering mode -->
 <script lang="ts">
    const ssr = import.meta.env.VITE_CLOUDFLARE === 'true'
 </script>

 <h1>Using SSR: {ssr}</h1>
 <h2>Vite variable has value {import.meta.env.VITE_CLOUDFLARE}</h2>