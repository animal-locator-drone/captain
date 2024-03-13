# Captain

Talks to PX4 and provides telemetry and guidance for the mission. 

## Setup and Running

### Prerequisites

1. Install python 3.6+ for your system preferably latest stable version of python
2. Get the code
   1. `https://github.com/animal-locator-drone/dogfinder-backend.git`
3. cd into the folder
   1. `cd dogfinder-backend`
4. Setup a venv and activate it
   1. `python -m venv .venv`
   2. `source .venv/bin/activate`
      1. You will need to rerun this in each new terminal unless you automate with VScode
5. Install dependencies with pip
   1. `pip install -r requirements.txt`

### Running

1. Activate the venv (see Prerequisites 4.2)
2. Run the web server with auto reload
   1. `uvicorn main:app --reload`

## Contributing

1. Read the documentation it has an excellent tutorial for beginners.
   1. <https://fastapi.tiangolo.com/tutorial/>