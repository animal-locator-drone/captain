from fastapi import FastAPI
from pydantic import BaseModel
from configparser import ConfigParser
import os
from uuid import uuid4

class Mission(BaseModel):
        id: str
        name: str
        path_preview: str

missions_store = [Mission(
                        id=str(uuid4()),
                        name=file.split(".")[0],
                        path_preview="path"+str(uuid4())
                ) for file in os.listdir("missions_available")]

app = FastAPI()

def read_config():
    # Read configuration from config.ini
    config = ConfigParser()
    config.read('config.ini')
    # Get configuration values
    host = config.get('app', 'host')
    port = config.getint('app', 'port')
    do_reload = config.getboolean('app', 'reload')
    return host, port, do_reload

# Define FastAPI routes


@app.get("/missions_available")
# async def missions_available() -> list[Mission]: # new python
async def missions_available(): # python 3.8 etc.
        return missions_store


@app.post("/select_mission/{mission_id}")
async def select_mission(mission_id: str):
        if not os.path.exists("missions_available"):
                return {"status": "error - mission folder missing"}
        if mission_id + ".plan" not in os.listdir("missions_available"):
                return {"status": "error - mission not found"}
        return {"status": f"success - mission {mission_id} selected"}

class MissionStatus(BaseModel):
        battery_percent: int
        time_elapsed: int
        current_location: list
        time_remaining: int
        progress_percent: int

@app.get("/mission_status")
async def mission_status() -> MissionStatus:
        return MissionStatus(
                        battery_percent=100,
                        time_elapsed=100,
                        current_location=[1, 2],
                        time_remaining=100,
                        progress_percent=100
                )


@app.post("/abort_mission")
async def abort_mission():
        return {"status": "success"}

# Run the FastAPI app with configured options
if __name__ == '__main__':
    host, port, reload = read_config()
    import uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=reload)