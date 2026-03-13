from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = Flask(__name__)

STOP_URL = "https://bustimes.org/stops/210021507080"

def get_bus_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    status_msg = "Online"
    buses = []

    try:
        response = requests.get(STOP_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            status_msg = f"HTTP Error {response.status_code}"
            return [], status_msg

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look specifically for table rows inside the main departures table
        # Bustimes usually puts live data in a <tbody>
        rows = soup.select('table.table tr') or soup.find_all('tr')
        
        print(f"Debug: Found {len(rows)} potential rows") # Check your terminal for this!

        for row in rows:
            # Skip the header row
            if row.find('th'): continue
            
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 3:
                # 0: Service Number, 1: Destination, 2: Scheduled, 3: Expected
                line = cols[0].get_text(strip=True)
                dest = cols[1].get_text(strip=True)
                
                # Handle cases where the 'Expected' column might be missing
                sched = cols[2].get_text(strip=True)
                expected = cols[3].get_text(strip=True) if len(cols) > 3 else ""
                
                active_time = expected if expected else sched
                
                if not active_time or ":" not in active_time and "Due" not in active_time:
                    continue

                now = datetime.now()
                try:
                    if "Due" in active_time:
                        mins = 0
                    else:
                        target = datetime.strptime(active_time, "%H:%M").replace(
                            year=now.year, month=now.month, day=now.day)
                        mins = int((target - now).total_seconds() / 60)
                except: 
                    mins = 0

                buses.append({
                    'line': line, 
                    'dest': dest.replace('\n', ' ').strip(), 
                    'sched': sched,
                    'expected': expected if expected else "On Time", 
                    'mins': mins,
                    'is_live': bool(expected),
                    'id': f"{line}-{active_time}-{dest[:5]}"
                })

    except Exception as e:
        status_msg = f"Error: {str(e)}"
        print(f"Error detail: {e}")
        
    return buses, status_msg

@app.route('/')
def index():
    buses, status = get_bus_data()
    return render_template('index.html', buses=buses, status=status, now=datetime.now().strftime("%H:%M:%S"))

if __name__ == '__main__':
    app.run(debug=True, port=8000)