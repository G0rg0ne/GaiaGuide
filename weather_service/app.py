from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import logging
from collections import Counter
from statistics import mean

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="Weather Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeatherRequest(BaseModel):
    city: str
    start_date: str
    end_date: str

def get_coordinates(city, api_key):
    """Get coordinates for a city using OpenWeather Geocoding API"""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return data['lat'], data['lon']
    raise HTTPException(status_code=404, detail=f"City '{city}' not found")

def get_historical_weather(lat, lon, api_key, date):
    """Get historical weather data for a specific date"""
    timestamp = int(date.timestamp())
    url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def generate_weather_summary(forecast_data):
    """Generate a summary of weather conditions for the period"""
    if not forecast_data:
        return None
    
    # Extract numerical values from forecast data
    temperatures = [float(day['temperature'].replace('°C', '')) for day in forecast_data]
    humidities = [float(day['humidity'].replace('%', '')) for day in forecast_data]
    wind_speeds = [float(day['wind_speed'].replace(' m/s', '')) for day in forecast_data]
    conditions = [day['conditions'] for day in forecast_data]
    
    # Calculate statistics
    temp_stats = {
        'average': f"{mean(temperatures):.1f}°C",
        'min': f"{min(temperatures):.1f}°C",
        'max': f"{max(temperatures):.1f}°C"
    }
    
    humidity_stats = {
        'average': f"{mean(humidities):.1f}%",
        'min': f"{min(humidities):.1f}%",
        'max': f"{max(humidities):.1f}%"
    }
    
    wind_stats = {
        'average': f"{mean(wind_speeds):.1f} m/s",
        'min': f"{min(wind_speeds):.1f} m/s",
        'max': f"{max(wind_speeds):.1f} m/s"
    }
    
    # Get most common weather conditions
    condition_counter = Counter(conditions)
    most_common_conditions = condition_counter.most_common(3)
    
    return {
        'temperature': temp_stats,
        'humidity': humidity_stats,
        'wind_speed': wind_stats,
        'most_common_conditions': [{'condition': cond, 'days': count} for cond, count in most_common_conditions],
        'total_days': len(forecast_data)
    }

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Weather Service is running"}

@app.post("/weather")
async def get_weather(request: WeatherRequest):
    try:
        logger.info(f"Weather request received for city: {request.city}")
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            logger.error("OpenWeather API key not configured")
            raise HTTPException(status_code=500, detail="OpenWeather API key not configured")

        # Convert string dates to datetime objects
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
        
        logger.info(f"Requested date range: {start_date.date()} to {end_date.date()}")
        
        # Get city coordinates
        lat, lon = get_coordinates(request.city, api_key)
        logger.info(f"Got coordinates for {request.city}: {lat}, {lon}")
        
        # Calculate the same period from last year
        last_year_start = start_date.replace(year=start_date.year - 1)
        last_year_end = end_date.replace(year=end_date.year - 1)
        
        logger.info(f"Fetching historical data for period: {last_year_start.date()} to {last_year_end.date()}")
        
        # Get historical weather data
        processed_forecast = []
        current_date = last_year_start
        
        while current_date <= last_year_end:
            data = get_historical_weather(lat, lon, api_key, current_date)
            if data and 'data' in data:
                # Use the first data point of the day (usually midnight)
                day_data = data['data'][0]
                processed_forecast.append({
                    'date': current_date.date().isoformat(),
                    'temperature': f"{day_data['temp']:.1f}°C",
                    'conditions': day_data['weather'][0]['description'],
                    'humidity': f"{day_data['humidity']}%",
                    'wind_speed': f"{day_data['wind_speed']} m/s"
                })
            current_date += timedelta(days=1)
        
        if not processed_forecast:
            logger.warning(f"No historical weather data available for the specified period")
            return {
                'city': request.city,
                'forecast': [],
                'summary': None,
                'error': "No historical weather data available for the specified period",
                'timestamp': datetime.now().isoformat()
            }
        
        # Generate weather summary
        weather_summary = generate_weather_summary(processed_forecast)
        
        return {
            'city': request.city,
            'forecast': processed_forecast,
            'summary': weather_summary,
            'timestamp': datetime.now().isoformat(),
            'note': "This data represents the weather conditions from the same period last year"
        }
    except Exception as e:
        logger.error(f"Error processing weather request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 