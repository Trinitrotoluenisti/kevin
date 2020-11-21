function update_navbar() {
    cookies = Object.fromEntries(document.cookie.split(';').map(c => c.split('=')));

    if (cookies.accessToken) {
        $('.logged_buttons').css('display', 'unset');
        $('.unlogged_buttons').remove();

        $('.logged_buttons')[1].href = '/users'

    } else {
        $('.unlogged_buttons').css('display', 'unset');
        $('.logged_buttons').remove();
    }
}
