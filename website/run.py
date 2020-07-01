from requests import get
from application import app, server



if __name__ == '__main__':
    try:
        get(server)
    except ConnectionError:
        raise ConnectionError("There isn't an API running in that URL") from None

    app.run(host='0.0.0.0', port=8000, debug=True)
