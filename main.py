from fastapi import FastAPI
from pydantic import BaseModel
from configparser import ConfigParser

app = FastAPI()

def read_config():
    # Read configuration from config.ini
    config = ConfigParser()
    config.read('config.ini')
    # Get configuration values
    host = config.get('app', 'host')
    port = config.getint('app', 'port')
    reload = config.getboolean('app', 'reload')
    return host, port, reload

# Define FastAPI routes
class Mission(BaseModel):
        id: str
        name: str
        path_preview: str

@app.get("/missions_available")
async def missions_available() -> list[Mission]:
        return [
                Mission(
                        id="1",
                        name="Mission 1",
                        path_preview="path1"
                ),
        ]


@app.post("/select_mission")
async def select_mission():
        return {"status": "Mission Started"}

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