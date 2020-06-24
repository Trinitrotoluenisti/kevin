function update_navbar() {
	var to_remove;
	var to_show;

	if (document.cookie.includes('refreshToken')) {
		to_remove = '.unlogged_buttons';
		to_show = '.logged_buttons';
	} else {
		to_remove = '.logged_buttons';
		to_show = '.unlogged_buttons';
	}

	Array.from($(to_remove)).forEach((e) => e.remove());
	Array.from($(to_show)).forEach((e) => e.style.display = 'unset');
}