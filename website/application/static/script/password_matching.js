function check_passwords(form) {
	if (form.password.value != form.cpassword.value) {
		alert("Password aren't matching!");
	}

	return form.password.value == form.cpassword.value;
}
