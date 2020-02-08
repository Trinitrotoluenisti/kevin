function testpass(modulo){
    // Verifico che il campo password sia valorizzato in caso contrario
    // avverto dell'errore tramite un Alert
    if (modulo.pass.value == ""){
        alert("Errore: inserire una password!")
        modulo.pass.focus()
        return false
    }
    // Verifico che le due password siano uguali, in caso contrario avverto
    // dell'errore con un Alert
    if (modulo.pass.value != modulo.passconfirm.value) {
        alert("La password inserita non coincide con la prima!")
        modulo.pass.focus()
        modulo.pass.select()
        return false
    }
    return true
    }