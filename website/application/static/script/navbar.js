function update_navbar() {
	if (document.cookie.includes('access_token') && document.cookie.includes('refresh_token')) {
		to_remove = '.unlogged_buttons';
		to_show = '.logged_buttons';
	} else {
		to_remove = '.logged_buttons';
		to_show = '.unlogged_buttons';
	}

	Array.from($(to_remove)).forEach(e => e.remove());
	Array.from($(to_show)).forEach(e => e.style.display = 'unset');
}
