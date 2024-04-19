from flask import Flask, render_template
import requests
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

chirpstack_email = ""  # Replace with your Chirpstack email
chirpstack_password = ""  # Replace with your Chirpstack password
chirpstack_url = ""  # Replace with your Chirpstack server URL

def apilogin(email, password, url):
    url = url + '/api/internal/login'
    credentials = '{"password": "' + password + '","email": "' + email + '"}'
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    
    # Make a POST request to obtain the JWT token
    response2 = requests.post(url, data=credentials, headers=headers)
    data = response2.json()
    
    if 'jwt' in data:
        print(data)
        return data['jwt']
    else:
        print("Failed to obtain JWT token.")
        return None

# Function to get device information
# API - /api/applications
@app.route('/api/chirpstack-data-applications')
def get_applications_info(): 
    token = apilogin(chirpstack_email, chirpstack_password, chirpstack_url)
    
    if not token:
        return "Failed to obtain JWT token."
    
    url = chirpstack_url
    
    # Set headers with authentication token
    headers = {
        "Accept": "application/json",
        "Grpc-Metadata-Authorization": "Bearer " + token
    }
    
    # Make a GET request to fetch applications information
    response = requests.get(url + "/api/applications?limit=10", headers=headers, stream=False)
    
    # Parse the JSON response and extract device details
    data = response.json()
    response = [app['name'] for app in data['result']]
    
    return response

# API - api/gateways
@app.route('/api/chirpstack-data-gateways')
def get_gateways_info():
    token = apilogin(chirpstack_email, chirpstack_password, chirpstack_url)
    
    if not token:
        return "Failed to obtain JWT token."
    
    url = chirpstack_url

    # Set headers with authentication token
    headers = {
        "Accept": "application/json",
        "Grpc-Metadata-Authorization": "Bearer " + token
    }

    # Make a GET request to fetch gateways information
    
    response = requests.get(url + "/api/gateways?limit=50", headers=headers, stream=False)
    data = response.json()

    gateway_data = {}

    for item in data['result']:
        gateway_name = item['name']

        timestamp_string = item['lastSeenAt']

        if timestamp_string is not None:
            utc_time = datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%S.%fZ')
            ist_timezone = pytz.timezone('Asia/Kolkata')
            ist_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(ist_timezone)
            date_only = ist_time.strftime('%Y-%m-%d')
            time_only = ist_time.strftime('%H:%M:%S')

        lat = item.get('location', {}).get('latitude')
        lon = item.get('location', {}).get('longitude')
        gateway_data[gateway_name] = {
            'latitude': lat,
            'longitude': lon,
            'timeStamp': timestamp_string,
            'lastSeenTime': time_only,
            'lastSeenDate': date_only
        }

    return gateway_data

@app.route('/')
def index():
    data = get_gateways_info()
    gateway_data = data
    return render_template('index.html', data={"data": data, "gw": gateway_data})

if __name__ == '__main__':
    app.run(debug=True)
