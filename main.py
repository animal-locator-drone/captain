from configparser import ConfigParser
import os
from uuid import uuid4
import asyncio

import uvicorn
from fastapi import FastAPI, Response, status
from pydantic import BaseModel



import drone_flight

drone = None
last_waypoint_index = 0
spiral_task = None

class Mission(BaseModel):
        id: str
        name: str
        path_preview: str

missions_store = [
        Mission(
                id=str(uuid4()),
                name=file.split(".")[0],
                path_preview="path"+str(uuid4())
        ) for file in os.listdir("missions_available")
]

app = FastAPI()

def read_config():
        config = ConfigParser()
        config.read('config.ini')

        host = config.get('app', 'host')
        port = config.getint('app', 'port')
        do_reload = config.getboolean('app', 'reload')

        return host, port, do_reload

@app.get("/missions_available")
# async def missions_available() -> list[Mission]: # new python
async def missions_available(): # python 3.8 etc.
        return missions_store

async def init_drone():
        global drone
        drone = await drone_flight.initialize_drone()
        return drone

@app.post("/select_mission/{mission_id}", status_code=200)
async def select_mission(mission_id: str, response: Response):
        if not os.path.exists("missions_available"):
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "error - mission folder missing"}
        if mission_id + ".plan" not in os.listdir("missions_available"):
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "error - mission not found"}
        if drone:
                await drone_flight.run_mission(drone, mission_id)
                return {"status": f"success - mission {mission_id} selected"}
        try:
                await asyncio.wait_for(
                        init_drone(),
                        timeout=10
                ) 
        except asyncio.TimeoutError:
                print("Drone initialization timeout")
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "error - drone initialization timeout"}
        if not drone:
                print("Drone connection failed")
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "error - drone connection failed"}
        
        await drone_flight.run_mission(drone, mission_id)
        return {"status": f"success - mission {mission_id} selected"}

@app.post("/track_dog/{dog_id}", status_code=200)
async def track_dog(dog_id: str, response: Response):
        global last_waypoint_index
        global spiral_task
        
        if not drone:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "error - drone not connected"}
        
        print("getting current waypoint")
        last_waypoint_index = await drone_flight.get_current_waypoint(drone)
        
        print("pausing current mission")
        await drone_flight.pause_current_mission(drone)
        
        print("begin spiral mode")
        spiral_task = asyncio.ensure_future(drone_flight.spiral(drone))
        
        print("done")
        return {"status": "success"}

class MissionStatus(BaseModel):
        battery_percent: int
        time_elapsed: int
        current_location: list
        time_remaining: int
        progress_percent: int
        in_mission: bool

@app.get("/mission_status")
async def mission_status() -> MissionStatus:
        if not drone:
                return MissionStatus(
                        battery_percent=0,
                        time_elapsed=0,
                        current_location=[0, 0],
                        time_remaining=0,
                        progress_percent=0,
                        in_mission=False
                )
        
        battery_percent = await drone_flight.get_battery(drone)
        current_location = await drone_flight.get_current_location(drone)
        progress_percent = await drone_flight.get_progress_percent(drone)
        in_mission = await drone_flight.get_in_mission(drone)
        
        return MissionStatus(
                battery_percent=battery_percent,
                time_elapsed=0,
                current_location=current_location,
                time_remaining=0,
                progress_percent=progress_percent,
                in_mission=in_mission
        )

@app.post("/resume_mission", status_code=200)
async def resume_mission(response: Response):
        global drone
        global last_waypoint_index
        global spiral_task
        
        if not drone:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "error - drone not connected"}
        
        if spiral_task:
                spiral_task.cancel()
        await drone.mission_raw.start_mission()
        await drone.mission_raw.set_current_mission_item(last_waypoint_index)
        return {"status": "success"}

@app.post("/abort_mission")
async def abort_mission():
        global drone
        global spiral_task
        if spiral_task:
                spiral_task.cancel()
                try:
                        await asyncio.wait_for(spiral_task, timeout=10)
                except asyncio.CancelledError:
                        pass
                except asyncio.TimeoutError:
                        pass
                finally:
                        spiral_task = None
        await drone.action.return_to_launch()
        return {"status": "success"}

@app.get("/current_location")
async def current_location():
        global drone
        return {"current_location": [1, 2]}

# Run the FastAPI app with configured options
if __name__ == '__main__':
        host, port, reload = read_config()
        uvicorn.run("main:app", host=host, port=port, reload=reload)
        
    