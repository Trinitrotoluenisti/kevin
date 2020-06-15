# Kevin

Kevin, a brand new social!

## Summary
- [Installing](#Installing)
   - [Installing APIs](#Installing_APIs)
   - [Installing Website](#Installing_Website)
- [Running](#Running)
   - [Running APIs](#Running_APIs)
   - [Running Website](#Running_Website)
- [Contributing](#Contributing)
- [Authors](#Authors)
- [License](/LICENSE)

## Installing

### Installing APIs

Once gone to `/api`, you just have to create a python venv, install dependencies and create a new file, `application/passwords.py`, which must contain a function called `hash_password`, that requires a string and returns another, like this:

```python
def hash_password(password):
	# things
	return password
```

**Example Installation (Linux):**
```bash
cd api/

# Create venv
python3 -m venv env

# Install dependencies
source env/bin/activate
pip install -r requirements.txt

# Create a fake password hasher (WARNING: this one keeps passwords in plain text, it's just for testing)
printf 'def hash_password(password):\n    return password\n' > application/passwords.py
```

**Example Installation (Windows):**
```batch
cd api/

# Create venv
python3 -m venv env

# Install dependencies
env\\Scripts\\activate.bat
pip install -r requirements.txt

# Create a fake password hasher (WARNING: this one keeps passwords in plain text, it's just for testing)
printf 'def hash_password(password):\n    return password\n' > application/passwords.py
```

### Installing Website

Again, the commands to run are still the same: create a venv and install dependencies. 

**Example Installation (Linux):**
```bash
cd website/

# Create venv
python3 -m venv env

# Install dependencies
source env/bin/activate
pip install -r requirements.txt
```

**Example Installation (Windows):**
```batch
cd website/

# Create venv
python3 -m venv env

# Install dependencies
env\\Scripts\\activate.bat
pip install -r requirements.txt
```

### Running

### Running APIs

You can easily run apis just by typing `python3 run.py`, once loaded the venv.

> For default, it loads `ProductionConfigs`: to load `DebugConfigs` or `TestingConfigs` add a `-d` or a `-t` respectively (for more informations see [api/application/configs.py](/api/application/configs.py)).

If you also want to see APIs logs, use `python3 log_visualizer.py`.

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
