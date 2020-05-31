function check_passwords(form) {
	if (form.password != form.cpassword) {
		alert("Password aren't matching!");
	}

	return form.password == form.cpassword;
}
