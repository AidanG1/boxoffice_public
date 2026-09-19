<!-- profitability breakdown based on Dan Murrell -->

<script lang="ts">
	import { formatKMB, type MovieData, type ScreenerData } from '$lib/utils'

	let {
		data,
		screener_data
	}: {
		data: MovieData
		screener_data: ScreenerData
	} = $props()

	// china 20% - don't have this
	// international 40% - have this but it includes china so put at 35%
	// domestic week 1 60%
	// domestic week 2 55%
	// domestic week 3+ 50%
	// budget
	// P&A estimate at the same as budget
	// showcase gross, net, costs, and theatrical profit

	// first calculate domestic week 1
	const domestic_week_1 = $derived(
		data.boxofficedays.slice(0, 7).reduce((acc, day) => acc + day.revenue, 0)
	)
	// then calculate domestic week 2
	const domestic_week_2 = $derived(
		data.boxofficedays.slice(7, 14).reduce((acc, day) => acc + day.revenue, 0)
	)
	// then calculate domestic week 3+
	const domestic_week_3_plus = $derived(
		data.boxofficedays.slice(14).reduce((acc, day) => acc + day.revenue, 0)
	)

	const net = $derived(
		domestic_week_1 * 0.6 +
			domestic_week_2 * 0.55 +
			domestic_week_3_plus * 0.5 +
			(screener_data.international_box_office ? screener_data.international_box_office * 0.35 : 0)
	)

	const costs = $derived(screener_data.budget ? screener_data.budget * 2 : 0) // assuming P&A is same as budget
	const profit = $derived(net - costs)
</script>

<h2>Profitability Breakdown</h2>
<div class="grid grid-cols-2">
	<div class="p-2">
		<h3>Domestic</h3>
		<p>Week 1: ${formatKMB(domestic_week_1, 2)}</p>

		<div
			class="tooltip tooltip-right cursor-help text-sm"
			data-tip="Investor share during week 1 is estimated at 60% of the gross revenue"
		>
			Investor Share: ${formatKMB(domestic_week_1 * 0.6, 2)}
		</div>
		<p>Week 2: ${formatKMB(domestic_week_2, 2)}</p>
		<p
			class="tooltip tooltip-right cursor-help text-sm"
			data-tip="Investor share during week 2 is estimated at 55% of the gross revenue"
		>
			Investor Share: ${formatKMB(domestic_week_2 * 0.55, 2)}
		</p>
		<p>Week 3+: ${formatKMB(domestic_week_3_plus, 2)}</p>
		<p
			class="tooltip tooltip-right cursor-help text-sm"
			data-tip="Investor share during week 3+ is estimated at 50% of the gross revenue"
		>
			Investor Share: ${formatKMB(domestic_week_3_plus * 0.5, 2)}
		</p>
		<h3 class="mt-2">International</h3>
		<p>
			${screener_data.international_box_office
				? formatKMB(screener_data.international_box_office, 2)
				: 'N/A'} ({(100 * (screener_data.international_box_office || 0) /
				((screener_data.international_box_office ||
					0) + domestic_week_1 + domestic_week_2 + domestic_week_3_plus)).toFixed(2)}%)
		</p>
		<p
			class="tooltip tooltip-right cursor-help text-sm"
			data-tip="Investor share is estimated at 35% of the international box office. This is based on China's 20% and the rest of the international market's 40% share."
		>
			Investor Share: ${screener_data.international_box_office
				? formatKMB(screener_data.international_box_office * 0.35, 2)
				: 'N/A'}
		</p>
	</div>
	<div class="p-2">
		<h3>Costs</h3>
		<p
			class="tooltip tooltip-right cursor-help"
			data-tip="The budget is the estimated production cost of the movie."
		>
			Budget: ${screener_data.budget ? formatKMB(screener_data.budget) : 'N/A'}
		</p>
		<br />
		<p
			class="tooltip tooltip-right cursor-help"
			data-tip="P&A (Prints and Advertising) costs are estimated to be the same as the budget."
		>
			P&A: ${screener_data.budget ? formatKMB(screener_data.budget) : 'N/A'}
		</p>
		<h3 class="mt-2">Breakdown</h3>
		<p
			class="tooltip tooltip-right cursor-help"
			data-tip="Gross revenue is the total amount made from the theatrical window in all markets before any deductions."
		>
			Gross: ${formatKMB(
				(screener_data.domestic_revenue || 0) + (screener_data.international_box_office || 0),
				2
			)}
		</p>
		<br />
		<p
			class="tooltip tooltip-right cursor-help"
			data-tip="Net revenue is the total amount returned to investors from the theatrical window."
		>
			Net: ${formatKMB(
				domestic_week_1 * 0.6 +
					domestic_week_2 * 0.55 +
					domestic_week_3_plus * 0.5 +
					(screener_data.international_box_office
						? screener_data.international_box_office * 0.35
						: 0),
				2
			)}
		</p>
		<br />
		<p
			class="tooltip tooltip-right cursor-help"
			data-tip="Total costs include both the budget and P&A."
		>
			Costs: ${formatKMB(costs, 2)}
		</p>
		<h3 class="mt-2">Profit</h3>
		<p
			class="tooltip tooltip-right {profit < 0 ? 'text-error' : 'text-success'}"
			data-tip="Breaking even in the theatrical window is considered a success. Profit is calculated as net revenue minus total costs."
		>
			Profit: ${formatKMB(profit, 2)}
			{profit < 0 ? '(Loss)' : ''}
		</p>
	</div>
</div>

<div>
	<p>
		The profitability breakdown is based on <a
			href="https://www.youtube.com/channel/UCbiOAho0h23IMInURiESx1w"
			target="_blank">Dan Murrell's YouTube videos</a
		> (Dan Murrell is not affiliated with Reel Numbers). The breakdown only includes the theatrical
		release and does not account for any post-theatrical revenue streams such as streaming, home video,
		or merchandise sales. Additionally, the breakdown does not include any tax incentives, sponsorships,
		or product placement that may have occurred during production.
	</p>
</div>
