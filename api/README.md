# API

### Install

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Run APIs

```bash
python3 run.py
```

### Check logs while API are running

```bash
watch --colors -n 0.2 python3 view_logs.py
```

### Example of `secrets.py`

```python
def hash_passwords(password):
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
        "sqlite3": "sqlite:///database/database.db",
        "posts_path": "application/database/posts"
    },

    "LOG": {
        "filename": "api.log"
    }
}
```
