# Kevin

![](https://img.shields.io/codacy/grade/26666125fb93412eb0cbff0196cb820c)
![](https://img.shields.io/codacy/coverage/26666125fb93412eb0cbff0196cb820c)
![](https://img.shields.io/travis/com/trinitrotoluenisti/kevin)
![](https://img.shields.io/github/license/trinitrotoluenisti/kevin?color=blue)
![](https://img.shields.io/badge/developers-4-blue)

Kevin:tm:, a brand new social!

## Summary
- [Installing](#installing)
   - [Installing APIs](#installing-apis)
   - [Installing Website](#installing-website)
- [Running](#running)
   - [Running APIs](#running-apis)
   - [Running Website](#running-website)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](/LICENSE)

## Installing

### Installing APIs

Once gone to `/api`, you just have to create a python venv, install dependencies and create a new file, `application/passwords.py`, which must contain a function called `hash_password`, that requires a string and returns another, like this:

```python
from hashlib import sha256

def hash_password(password):
    return sha256(password.encode('utf-8')).hexdigest()
```

**Example Installation (Linux):**
```bash
cd api/

# Creates venv
python3 -m venv env

# Installs dependencies
source env/bin/activate
pip install -r requirements.txt

# Creates a password hasher
printf "from hashlib import sha256\n\ndef hash_password(password):\n    return sha256(password.encode('utf-8')).hexdigest()\n" > application/passwords.py
```

**Example Installation (Windows):**
```batch
cd api/

# Creates venv
python3 -m venv env

# Installs dependencies
env\\Scripts\\activate.bat
pip install -r requirements.txt

# Creates a password hasher
printf "from hashlib import sha256\n\ndef hash_password(password):\n    return sha256(password.encode('utf-8')).hexdigest()\n" > application/passwords.py
```

### Installing Website

Again, the commands to run are still the same: create a venv and install dependencies. 

**Example Installation (Linux):**
```bash
cd website/

# Creates venv
python3 -m venv env

# Installs dependencies
source env/bin/activate
pip install -r requirements.txt
```

**Example Installation (Windows):**
```batch
cd website/

# Creates venv
python3 -m venv env

# Installs dependencies
env\\Scripts\\activate.bat
pip install -r requirements.txt
```

### Running

### Running APIs

You can easily run apis just by typing `python3 run.py`, once loaded the venv.

> For default, it loads `ProductionConfigs`: to load `TestingConfigs` just set the `TESTING` variable to `true` (for more informations see [api/application/configs.py](/api/application/configs.py)).

### Running Website

`python3 run.py`. Rememer to activate the venv first.


## Contributing

If you want to contribute to this open source project, you're free to pull-request us! We'll check your submission as soon as we can.


## Authors

- **Parri Gianluca** - *The guy who developed APIs. Also called Dr. Bee.* - [@gianluparri03](https://github.com/gianluparri03)
- **Andreanelli Tommaso** - *The guy who routed the routes (Website)* - [@TommyAnd](https://github.com/TommyAnd)
- **Mariotti Giuseppe** - *Frontender* - [@Caesar-7](https://github.com/Caesar-7)
- **Bartocetti Enrico** - *Frontender v2.0 (also called the one in love with Bootstrap:tm:)* - [@EnryBarto](https://github.com/EnryBarto)

Click on [this link](https://github.com/trinitrotoluenisti/kevin/graphs/contributors) to see the list of contributors who participated in this project.
