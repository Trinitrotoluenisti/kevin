from application import app, logging


logging.error("API Started")
app.run(host='0.0.0.0', port=8080)
logging.error("API Stopped")
