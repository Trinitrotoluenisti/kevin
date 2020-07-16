from application import app, scheduler



if __name__ == '__main__':
    scheduler.start()
    app.run(host='0.0.0.0', port=8080, debug=True)
