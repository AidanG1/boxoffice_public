import { goto } from '$app/navigation'
import {
	type Filter,
	type Sort,
	defaultFilters,
	defaultSort,
	getBase64Screener,
	parseBase64Screener,
	screen
} from '$lib/screener'

export class FilterSort {
	changed: boolean = $state(false)
	filters: Filter[] = $state(defaultFilters)
	sort: Sort = $state(defaultSort)

	editing_indices: number[] = $state([])
	newFilterName: Filter['name'] = $state('budget')
	newFilterValue: Filter['value'] = $state('0')
	newFilterType: Filter['type'] = $state('=')

	default_display_columns = ['title', 'poster_path', 'release_date', 'budget', 'domestic_revenue']
	always_remove_columns = ['title', 'poster_path']

	filterInput: HTMLInputElement | null = null
	sortInput: HTMLInputElement | null = null
	sortNameInput: HTMLSelectElement | null = null

	constructor(b64: string) {
		// Initialize filters and sort from the URL
		if (b64) {
			const { filters: newFilters, sort: newSort } = parseBase64Screener(b64)
			this.filters = newFilters
			this.sort = newSort
		}

		if (this.sortNameInput) {
			this.sortNameInput.value = this.sort.name
		}
	}

	sortDirectionChanged() {
		this.sort.direction = this.sort.direction === 'asc' ? 'desc' : 'asc'
		this.gotoBase64()
	}

	removeFilter(index: number) {
		this.editing_indices = this.editing_indices.filter((i) => i !== index)
		this.filters = this.filters.filter((_, i) => i !== index)
		this.gotoBase64()
	}

	updateFilter(index: number, filter: Filter) {
		this.editing_indices = this.editing_indices.filter((i) => i !== index)
		this.filters[index] = filter
		this.gotoBase64()
	}

	editFilter(index: number) {
		if (!this.editing_indices.includes(index)) {
			this.editing_indices.push(index)
		}
	}

	addFilter() {
		this.filters.push({
			name: this.newFilterName,
			value: this.newFilterValue,
			type: this.newFilterType
		})
		this.newFilterName = 'budget'
		this.newFilterValue = '0'
		this.newFilterType = '='
		this.gotoBase64()
	}

	gotoBase64() {
		const newB64 = getBase64Screener(this.filters, this.sort)
		goto(`?b64=${newB64}`, { replaceState: true })
		this.changed = true
	}

	async submit() {
		if (this.filterInput) {
			this.filterInput.value = JSON.stringify(this.filters)
		}
		if (this.sortInput) {
			this.sortInput.value = JSON.stringify(this.sort)
		}
		this.changed = false

		const results = await screen(this.filters, this.sort)

		this.gotoBase64()

        return results
	}

	getDisplayColumns() {
		const filterList = this.default_display_columns
			.concat(this.filters.map((f) => f.name))
			.concat(this.sort.name)

		// remove always remove columns
		this.always_remove_columns.forEach((col) => {
			const index = filterList.indexOf(col)
			if (index !== -1) {
				filterList.splice(index, 1)
			}
		})

		// return unique columns
		return Array.from(new Set(filterList)).map((name) => {
			return {
				name,
				type: this.filters.find((f) => f.name === name)?.type || '='
			}
		})
	}
}
