# API

### Install

#### Linux

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
mkdir application/database
```

#### Windows

```bash
python3 -m venv env
env\Scripts\activate.bat
pip install -r requirements.txt
mkdir application\database
```

Then you have to create a copy of `api/secrets.py`, like [this](#Example of `api/secrets.py`).

### Run APIs

```bash
python3 run.py
```

### Run Tests

```bash
python3 tests.py
```

### Check logs while API are running

```bash
watch -c -n 0.2 python3 view_logs.py
```

### Example of `api/secrets.py`

```python
def hash_password(password):
    return password

configs = {
    "API": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": True
    },

    "JWT": {
        "secret_key": "###",
        "token_expiration": {"minutes": 45},
        "blacklist_clean": {"minutes": 30}
    },

    "DB": {
        "sqlite3": "sqlite:///database/database.db", # from api/application/
        "posts_path": "application/database/posts"   # from api/
    },

    "LOG": {
        "filename": "api.log"                        # from api/
    }
}
```
