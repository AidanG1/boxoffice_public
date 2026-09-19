<!-- generate an image with a grid of the different movies posters -->

<script lang="ts">
	import type { TableType } from '$lib/components/table_type'
	import { tmdb_path_to_url } from '$lib/utils'

	let {
		data,
		date,
		type = 'Day',
		movie_count = 10
	}: {
		data: TableType[]
		date: Date
		type?: 'Day' | 'Weekend'
		movie_count?: number
	} = $props()

	import { onMount } from 'svelte'

	let canvasElement: HTMLCanvasElement | null = $state(null)

	function wrapText(
		ctx: CanvasRenderingContext2D,
		text: string,
		x: number,
		y: number,
		maxWidth: number,
		lineHeight: number
	) {
		const words = text.split(' ')
		let line = ''
		let linesDrawn = 1
		for (let n = 0; n < words.length; n++) {
			const testLine = line + words[n] + ' '
			const metrics = ctx.measureText(testLine)
			const testWidth = metrics.width
			if (testWidth > maxWidth && n > 0) {
				ctx.fillText(line, x, y)
				line = words[n] + ' '
				y += lineHeight
				linesDrawn++
			} else {
				line = testLine
			}
		}
		ctx.fillText(line, x, y)

		// return the number of lines drawn
		return linesDrawn + 1
	}

	onMount(() => {
		const canvas = canvasElement
		const ctx = canvas.getContext('2d')
		if (!ctx) return

		// canvas black background
		ctx.fillStyle = '#000'
		ctx.fillRect(0, 0, canvas.width, canvas.height)

		const posterWidth = canvas.width / 8
		const posterHeight = canvas.height / 3
		const xPadding = (canvas.width * 3/8) / 20
        const yPadding = (canvas.height * 3/8) / 15

		let x = xPadding
		let y = yPadding

		const movieData = data.slice(0, movie_count)

		// include a title at the top
		ctx.font = '24px sans-serif'
		ctx.fillStyle = '#fff'
		ctx.textAlign = 'center'
        y += 30 // move down a bit for the title

        const mainTitle = `Movie Recap for ${type} of ${date.toLocaleDateString()}`
        const textWidth = ctx.measureText(mainTitle).width
        const canvasWidth = canvas.width - xPadding * 2

		const mainTitleLines = wrapText(
			ctx,
			mainTitle,
            canvasWidth / 2 - textWidth / 2,
			y,
			canvas.width - yPadding * 2,
			30
		)
		y += mainTitleLines * 5 + yPadding

		movieData.forEach((movie, index) => {
			const img = new Image()
			const url = tmdb_path_to_url(movie.poster_path)

			img.src = url

			let maxLinesDrawn = 0

			img.onload = () => {
				ctx.drawImage(img, x, y, posterWidth, posterHeight)

				// Draw wrapped title
				ctx.font = '16px sans-serif'
				ctx.fillStyle = '#fff'
				ctx.textAlign = 'center'
				const nameY = y + posterHeight + 20
				const lineHeight = 18
				let titleLinesDrawn = wrapText(
					ctx,
					movie.title,
					x + posterWidth / 2,
					nameY,
					posterWidth,
					lineHeight
				)

				// Draw gross (no wrapping needed, but you can if desired)
				ctx.font = '14px sans-serif'
				ctx.fillStyle = '#ffd700'
				const grossY = nameY + lineHeight * 2 // leave space for title
				let grossLinesDrawn = wrapText(
					ctx,
					`$${movie.revenue.toLocaleString()}`,
					x + posterWidth / 2,
					grossY,
					posterWidth,
					lineHeight
				)

				// Update max lines drawn
				maxLinesDrawn = Math.max(maxLinesDrawn, titleLinesDrawn + grossLinesDrawn)

				x += posterWidth + xPadding
				if ((index + 1) % 5 === 0) {
					x = xPadding
					y += posterHeight + yPadding + maxLinesDrawn * 18
					console.log(`Moving to next row at y: ${y}, max lines drawn: ${maxLinesDrawn}`)
					maxLinesDrawn = 0 // reset for next row
				}
			}
		})
	})
</script>

<canvas bind:this={canvasElement} width="2000" height="1125"> </canvas>
