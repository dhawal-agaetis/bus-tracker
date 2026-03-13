from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

# API Config
APP_ID = "3a15bca0"
APP_KEY = "3ab36a9d7a3b822938c841a12cf4f32b"
STOP_ID = "210021507080"

def get_bus_data():
    url = f"https://transportapi.com/v3/uk/bus/stop/{STOP_ID}/live.json"
    params = {"app_id": APP_ID, "app_key": APP_KEY, "group": "no", "nextbuses": "yes"}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        departures = data.get('departures', {}).get('all', [])
        
        # Add a "minutes away" calculation to each bus
        for bus in departures:
            time_str = bus.get('expected_departure_time') or bus.get('aimed_departure_time')
            now = datetime.now()
            target = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
            diff = (target - now).total_seconds() / 60
            bus['mins_away'] = int(diff) if diff > 0 else 0
            bus['is_live'] = bus.get('expected_departure_time') is not None
            
        return departures
    except:
        return []

@app.route('/')
def index():
    buses = get_bus_data()
    return render_template('index.html', buses=buses, now=datetime.now().strftime("%H:%M:%S"))

if __name__ == '__main__':
    app.run(debug=True, port=5000)