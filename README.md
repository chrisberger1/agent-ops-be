# agent-ops-be
Backend for Agent Ops DE Hackathon Project 2025

# Developer Setup
## Setup Virtual Environment
Ensure `python3` is installed on your machine - [Download](https://www.python.org/downloads/)

Create venv
``` bash
python3 -m venv .venv
```

Activate venv
``` bash
source .venv/bin/activate
```

When needed, to deactivate your venv, run
``` bash
deactivate
```

## Install pip packages
``` bash 
python3 -m pip install -r requirements.txt
```

If you install new packages, make sure to run the following command to make sure everyone is using the same versions of each package
```bash
python3 -m pip freeze > requirements.txt
```

## Run application
``` bash
python3 main.py
```
Application will be accessible through `localhost:5000`, verify application is running by navigating to that URL and ensuring you see 

<p>Agent Ops backend is running!</p>
