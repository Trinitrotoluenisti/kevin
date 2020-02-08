function testpass(modulo){
    if (modulo.pass.value != modulo.passconfirm.value) {
        alert("Password aren't matching!")
        modulo.pass.focus()
        modulo.pass.select()
        return false
    }
    return true
}