import openmeteo_requests
import requests_cache
from retry_requests import retry
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime


app = Flask(__name__)

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


from flask import make_response

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        city = request.form['city']
        lat, lon = get_geolocation(city)
        if lat is not None and lon is not None:
            weather = get_weather(lat, lon)
            response = make_response(render_template('home.html', weather=weather, city=city))
            response.set_cookie('last_city', city)
            return response
        else:
            return "Could not find location."
    else:
        last_city = request.cookies.get('last_city')
        if last_city:
            lat, lon = get_geolocation(last_city)
            if lat is not None and lon is not None:
                weather = get_weather(lat, lon)
                response = make_response(render_template('home.html', weather=weather, city=last_city))
                return response
    response = make_response(render_template('home.html'))
    return response




@app.route('/suggestions', methods=['GET'])
def suggestions():
    api_key = 'f97d9f9e53c04519b390006a2bc871a5'
    query = request.args.get('q')
    if query:
        url = f"https://api.opencagedata.com/geocode/v1/json?q={query}&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            suggestions = [result['formatted'] for result in data['results']]
            return jsonify(suggestions)
    return jsonify([])


def get_geolocation(city_name):
    api_key = 'f97d9f9e53c04519b390006a2bc871a5'
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city_name}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return float(data['results'][0]['geometry']['lat']), float(data['results'][0]['geometry']['lng'])
    else:
        return None, None


def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "apparent_temperature",
        "forecast_days": 1,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        iso_time = weather_data['current']['time']
        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        formatted_time = dt.strftime("%d %B %Y года, %H:%M")
        weather_data['current']['time'] = formatted_time
        return weather_data
    else:
        return None


if __name__ == '__main__':
    app.run(debug=True)