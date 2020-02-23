from application import app, scheduler, logging


# Log the start
logging.error("API started")

# Start the schedule
scheduler.start()

# Start the app
app.run(host="0.0.0.0", port=8080, debug=True)

# Log the stop
logging.error("API stopped")
