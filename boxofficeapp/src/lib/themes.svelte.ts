export const themeState: {
	theme: string
	theme_type: 'light' | 'dark'
	preferred_light_theme: string
	preferred_dark_theme: string
} = $state({
	theme: 'jaws',
	theme_type: 'light',
	preferred_light_theme: 'jaws',
	preferred_dark_theme: 'godfather'
})

type ThemeState = typeof themeState

export const syncTheme = (themeState: ThemeState) => {
	document.documentElement.setAttribute('data-theme', themeState.theme)
	localStorage.setItem('theme', themeState.theme)
	localStorage.setItem('theme_type', themeState.theme_type)
	setPreferredTheme(themeState.theme, themeState.theme_type)
}

const setPreferredTheme = (theme: string, theme_type: 'light' | 'dark') => {
	if (theme_type === 'light') {
		localStorage.setItem('preferred_light_theme', theme)
		themeState.preferred_light_theme = theme
	}
	if (theme_type === 'dark') {
		localStorage.setItem('preferred_dark_theme', theme)
		themeState.preferred_dark_theme = theme
	}
}

export const getThemeType = () => {
	const theme_type = localStorage.getItem('theme_type')
	if (theme_type === 'dark' || theme_type === 'light') {
		return theme_type
	}
	return 'light' // default fallback
}

export const toggleTheme = () => {
	const currentThemeType = themeState.theme_type

	if (currentThemeType === 'light') {
		themeState.theme = themeState.preferred_dark_theme
		themeState.theme_type = 'dark'
	} else {
		themeState.theme = themeState.preferred_light_theme
		themeState.theme_type = 'light'
	}
}

export const initializeTheme = () => {
	const theme = localStorage.getItem('theme') || 'jaws'
	const themeType = localStorage.getItem('theme_type') || 'light'
	const preferredLightTheme = localStorage.getItem('preferred_light_theme') || 'jaws'
	const preferredDarkTheme = localStorage.getItem('preferred_dark_theme') || 'godfather'

	themeState.theme = theme
	themeState.theme_type = themeType === 'dark' || themeType === 'light' ? themeType : 'light'
	themeState.preferred_light_theme = preferredLightTheme
	themeState.preferred_dark_theme = preferredDarkTheme
}
