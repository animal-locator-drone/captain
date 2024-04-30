import math
from mavsdk import System
import asyncio

async def initialize_drone():
        # try:
                # async with asyncio.timeout(10):
        print("Connecting to drone...")
        drone = System()
        await drone.connect()
        
        await drone.mission.set_return_to_launch_after_mission(True)
        
        
        print("completed drone initialization")
        return drone
        # except TimeoutError:
        #         print("Drone initialization timeout")
        #         return None

async def spiral(drone):
    ## Spiral flight pattern
    # Set the initial position
    start_position = None
    async for position in drone.telemetry.position():
        start_position = position
        start_lat = start_position.latitude_deg
        start_lon = start_position.longitude_deg
        start_altitude = start_position.absolute_altitude_m
        break

    # Convert to radians
    start_lat_rad = math.radians(start_lat)
    start_lon_rad = math.radians(start_lon)

    # Set the spiral parameters
    a = 1
    radius = 1
    target_radius = 50
    theta = math.atan2(start_lat_rad, start_lon_rad)

    # Fly the spiral pattern
    while radius < target_radius:
        # Calculate the current position on the spiral
        radius = a * theta
        curr_lat = radius * math.cos(theta)
        curr_lon = radius * math.sin(theta)

        # Move the drone to the current position
        await drone.action.goto_location(
            latitude_deg=math.degrees(curr_lat),
            longitude_deg=math.degrees(curr_lon), 
            absolute_altitude_m=start_altitude,
            yaw_deg=0)

        # Increase the radius for the next loop
        theta += 5
        
async def run_mission(drone, mission):
        mission_import_data = await \
                drone.mission_raw.import_qgroundcontrol_mission(
                "missions_available/" + mission + ".plan")
        print(f"{len(mission_import_data.mission_items)} mission items imported")
        await drone.mission_raw.upload_mission(mission_import_data.mission_items)
        print("Mission uploaded")
        print("-- Arming")
        await drone.action.arm()
        print("-- Takeoff")
        await drone.action.takeoff()
        print("-- Starting mission")
        await drone.mission.start_mission()

async def get_battery(drone):
        print("getting battery")
        battery_status = None
        async for battery in drone.telemetry.battery():
                battery_status = battery.remaining_percent
                break
        return battery_status

async def print_gps_info(drone):
        gps_info_array = []
        async for gps_info in drone.telemetry.gps_info():
                gps_info_array.append(gps_info)
                

async def print_in_mission(drone):
        in_mission = False
        async for flight_mode in drone.telemetry.flight_mode():
                print(flight_mode)
                if flight_mode == "MISSION":
                        in_mission = True
                        break
        return in_mission