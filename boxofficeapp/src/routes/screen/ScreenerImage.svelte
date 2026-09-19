<script lang="ts">
	let {
		movies,
		title
	}: {
		movies: {
			title: string
			poster_path: string
			stat: string
		}[]
		title: string
	} = $props()

	import { tmdb_path_to_url } from '$lib/utils'

	let canvasElement: HTMLCanvasElement | null = $state(null)
	let imageData: string | null = $state(null)

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

	const drawImage = async () => {
		console.log('Drawing image...')

		const canvas = canvasElement

		if (!canvas) {
			console.error('Canvas element not found')
			return
		}

		const ctx = canvas.getContext('2d')
		if (!ctx) {
			console.error('2D context not found')
			return
		}

		let columnCount = 0
		if (movies.length % 5 === 0) {
			columnCount = 5
		} else if (movies.length % 6 === 0) {
			columnCount = 6
		} else {
			columnCount = 4
		}

		const impliedRowCount = Math.ceil(movies.length / columnCount)
		const posterAspectRatio = 2 / 3

		const xPadding = (canvas.width * 3) / columnCount / 20
		const yPadding = (canvas.height * 3) / columnCount / 15
		const posterWidth = canvas.width / (columnCount) - xPadding * 1.1
		const posterHeight = posterWidth / posterAspectRatio

		// change the canvas height so it can fit all rows
		canvas.height = posterHeight * impliedRowCount + yPadding * (impliedRowCount * 4 + 2)
		let x = xPadding
		let y = yPadding

		// canvas black background
		ctx.fillStyle = '#000'
		ctx.fillRect(0, 0, canvas.width, canvas.height)
		
		// include a title at the top
		ctx.font = '48px sans-serif'
		ctx.fillStyle = '#fff'
		ctx.textAlign = 'center'
		y += 30 // move down a bit for the title

		const mainTitle = title
		const textWidth = ctx.measureText(mainTitle).width
		const canvasWidth = canvas.width

		const mainTitleLines = wrapText(
			ctx,
			mainTitle,
			canvasWidth / 2,
			y,
			canvas.width,
			30
		)
		y += mainTitleLines * 5 + yPadding

		// Load all images first
		const imagePromises = movies.map((movie) => {
			return new Promise<HTMLImageElement>((resolve, reject) => {
				const img = new Image()
				img.crossOrigin = 'anonymous'
				const url = tmdb_path_to_url(movie.poster_path)
				img.src = url
				img.onload = () => resolve(img)
				img.onerror = reject
			})
		})

		try {
			const loadedImages = await Promise.all(imagePromises)

			console.log('All images loaded successfully')

			// Now draw all images
			let currentX = xPadding
			let currentY = y
			let maxLinesDrawn = 0

			loadedImages.forEach((img, index) => {
				const movie = movies[index]

				ctx.drawImage(img, currentX, currentY, posterWidth, posterHeight)

				// Draw wrapped title
				const fontSize = 32
				ctx.font = `${fontSize}px sans-serif`
				ctx.fillStyle = '#fff'
				ctx.textAlign = 'center'
				const nameY = currentY + posterHeight + fontSize + fontSize / 4
				const lineHeight = fontSize
				let titleLinesDrawn = wrapText(
					ctx,
					movie.title,
					currentX + posterWidth / 2,
					nameY,
					posterWidth,
					lineHeight
				)

				// Draw gross (no wrapping needed, but you can if desired)
				ctx.font = `${fontSize}px sans-serif`
				ctx.fillStyle = '#ffd700'
				const grossY = nameY + lineHeight * 2 // leave space for title
				let grossLinesDrawn = wrapText(
					ctx,
					movie.stat,
					currentX + posterWidth / 2,
					grossY,
					posterWidth,
					lineHeight
				)

				// Update max lines drawn
				maxLinesDrawn = Math.max(maxLinesDrawn, titleLinesDrawn + grossLinesDrawn)

				currentX += posterWidth + xPadding
				if ((index + 1) % columnCount=== 0) {
					currentX = xPadding
					currentY += posterHeight + yPadding + maxLinesDrawn * 18
					console.log(`Moving to next row at y: ${currentY}, max lines drawn: ${maxLinesDrawn}`)
					maxLinesDrawn = 0 // reset for next row
				}
			})

			if (canvasElement) {
				imageData = canvasElement.toDataURL('image/png')
			}
		} catch (error) {
			console.error('Error loading images:', error)
		}
	}

	$inspect(movies)
</script>

<button onclick={drawImage} class="btn btn-primary mb-2">Generate Image</button>

{#if canvasElement}
	<img src={imageData} alt="Screener" class="h-auto max-w-full border" />
{/if}
<canvas bind:this={canvasElement} width="2000" height="1125" class="hidden"> </canvas>
