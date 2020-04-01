from .main import configs, app, logging, scheduler


def startAPI():
    # Log the start
    logging.error("API started")

    # Start the schedule
    scheduler.start()

    # Start the app
    app.run(**configs['API'])

    # Log the stop
    logging.error("API stopped")
