function close_cookie_popup() {
	$('#popup-box').remove();
	localStorage.setItem("cookie-accepted", 1);
}
		
if (localStorage.getItem("cookie-accepted") == 1) {
	close_cookie_popup();
}
