import fastf1
from flask import Flask, request, send_file
from flask_cors import CORS
import fastf1.plotting
from matplotlib import pyplot as plt
import base64

fastf1.plotting.setup_mpl()
fastf1.Cache.enable_cache("cache")

sort_to_long_name = fastf1.plotting.DRIVER_TRANSLATE
driver_colors = fastf1.plotting.DRIVER_COLORS

app = Flask(__name__)

drivers = {
    "driver-0": "VER",
    "driver-1": "HAM",
    "driver-2": "PER",
    "driver-3": "LEC",
    "driver-4": "SAI",
    "driver-5": "ALO",
    "driver-6": "RUS",
    "driver-7": "STR",
    "driver-8": "NOR",
    "driver-9": "ALB",
    "driver-10": "BOT",
    "driver-11": "ZHO",
    "driver-12": "OCO",
    "driver-13": "GAS",
    "driver-14": "TSU",
    "driver-15": "DEV",
    "driver-16": "MAG",
    "driver-17": "HUL",
    "driver-18": "PIA",
    "driver-19": "SAR",

}


@app.route("/Schedule", methods=["GET"])
def get_event():
    next_event = fastf1.get_events_remaining().iloc[0]
    data = {
        "name": next_event["EventName"],
        "country": str(next_event["Country"]) + " --- " + str(next_event["Location"]),
        "fp1": str(next_event["Session1"]) + " ----- " + str(next_event["Session1Date"]).split(" ")[1],
        "fp2": str(next_event["Session2"]) + " ----- " + str(next_event["Session2Date"]).split(" ")[1],
        "fp3": str(next_event["Session3"]) + " ----- " + str(next_event["Session3Date"]).split(" ")[1],
        "q": str(next_event["Session4"]) + " ----- " + str(next_event["Session4Date"]).split(" ")[1],
        "r": str(next_event["Session5"]) + " ----- " + str(next_event["Session5Date"]).split(" ")[1],
        "closes_date": str(next_event["Session1Date"])
    }
    print(next_event)
    return {"data": data}, 200


@app.route("/Laps", methods=["POST"])
def get_aps():
    receive = request.json
    session = fastf1.get_session(2023, 2, receive["session"])
    session.load()
    laps = session.laps
    for column in ["Time", "LapTime", "PitOutTime", "PitInTime", "Sector1Time", "Sector2Time", "Sector3Time",
                   "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime"]:
        laps[column] = laps[column].dt.total_seconds()
    laps = laps.fillna(0)
    laps = laps.drop(columns=["FreshTyre", "DriverNumber", "IsAccurate", "LapStartDate", "LapStartTime",
                              "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "SpeedFL", "SpeedI1",
                              "SpeedI2", "SpeedST", "Team", "Time", "TrackStatus"])
    driver1 = drivers[receive["0"]]
    try:
        driver2 = drivers[receive["1"]]
        ones = laps.loc[laps["Driver"] == driver1].to_dict("list")
        second = laps.loc[laps["Driver"] == driver2].to_dict("list")
        return {"data": [ones, second]}, 200
    except:
        ones = laps.loc[laps["Driver"] == driver1].to_dict("list")
        return {"data": [ones]}, 200


@app.route("/Telemetry", methods=["POST"])
def telemetry_comp():
    receive = request.json
    session = fastf1.get_session(2023, receive["race"], receive["session"])
    session.load()
    first = receive["first"]
    second = receive["second"]
    driver1 = session.laps.pick_driver(first).pick_fastest()
    driver2 = session.laps.pick_driver(second).pick_fastest()
    data1 = driver1.get_car_data()
    data2 = driver2.get_car_data()
    t1 = data1["Time"]
    t2 = data2["Time"]
    throttle1 = data1["Throttle"]
    speed1 = data1["Speed"]
    speed2 = data2["Speed"]
    throttle2 = data2["Throttle"]
    fig, ax = plt.subplots(3, 1, figsize=(9, 9))
    ax[0].plot(t1, speed1, label=first)
    ax[0].plot(t2, speed2, label=second)
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Speed [Km/h]')
    ax[0].legend(loc="upper right")
    ax[1].plot(t1, data1["RPM"], label=f"RPM {first}")
    ax[1].plot(t2, data2["RPM"], label=f"RPM {second}")
    ax[1].set_ylabel('RPM')
    ax[2].plot(t1, throttle1, label=f"THROTTLE {first}")
    ax[2].plot(t2, throttle2, label=f"THROTTLE {second}")
    ax[2].set_ylabel('Throttle')
    plt.savefig("temp.png")
    return send_file("temp.png")

if __name__ == "__main__":
    CORS(app)
    app.run()
"""
session = fastf1.get_session(2023, "Bahrein", "FP2")
session.load()
laps = session.laps
"""