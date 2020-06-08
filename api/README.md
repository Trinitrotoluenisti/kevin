# API

## Installing

Once cloned the repository and moved to `/api`, you have to create a python venv, by using `python3 -m venv env`. After that you can activate it with `source env/bin/activate` on linux or `env\\Scripts\\activate.bat` on windows.
Then install all the dependencies with `pip install -r requirements.txt` and create a stupid `application/passwords.py`, [this](#passwords.py).

## passwords.py

```python
def hash_password(password):
	return password
```

## Running

Once activated the venv, you just have to run

```bash
python3 run.py
```

For default, `ProductionConfigs` are loaded.
To use `DebugConfigs`, add `-d` to the end.
To use `TestingConfigs`, add `-t` to the end.

If you want to see the API's log while they're running, use

```bash
watch -c -n 0.2 python3 log_visualizer.py
```

where `-n 0.2` indicates the number of seconds after which the list id updated.

## Testing

If you make some changes at the APIs, you can check if you've damaged something with the unittests.
To run them, use

```bash
python3 unittests.py
```

_NB: in unittests, `TestingConfigs` are loaded for default._

### Coverage

If you also want to see which pieces of code are tested, you can use

```bash
coverage run --source /application unittests.py
coverage report -m
```

Remember to delete the `.coverage` file once run.
