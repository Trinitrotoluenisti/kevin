from application import app, scheduler


scheduler.start()
app.run(host='0.0.0.0', port=8080)
