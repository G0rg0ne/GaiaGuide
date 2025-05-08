import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_weather_data(city, start_date, end_date):
    try:
        logger.info(f"Requesting weather data for city: {city} from {start_date} to {end_date}")
        # Make request to weather service
        response = requests.post(
            "http://weather_service:8000/weather",
            json={
                "city": city,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        if response.status_code == 200:
            weather_data = response.json()
            logger.info(f"Successfully received weather data: {weather_data}")
            return weather_data
        else:
            logger.error(f"Failed to fetch weather data. Status code: {response.status_code}")
            return {
                "error": "Failed to fetch weather data",
                "forecast": []
            }
    except Exception as e:
        logger.error(f"Error in get_weather_data: {str(e)}")
        return {
            "error": str(e),
            "forecast": []
        }

def get_flight_data(origin, destination, date):
    # This is a placeholder for flight API integration
    # You would replace this with actual API calls to a flight service
    return {
        "price": "$300",
        "airline": "Example Airlines",
        "departure_time": "10:00 AM"
    }

def generate_travel_plan(destination, start_date, end_date, preferences, weather_summary):
    # Create a prompt for the OpenAI API
    prompt = f"""
    Create a detailed travel plan for {destination} from {start_date} to {end_date}.
    Preferences: {preferences}
    
    Weather Summary for the period:
    - Average Temperature: {weather_summary['temperature']['average']}
    - Temperature Range: {weather_summary['temperature']['min']} to {weather_summary['temperature']['max']}
    - Most Common Weather Conditions: {', '.join([cond['condition'] for cond in weather_summary['most_common_conditions']])}
    - Average Humidity: {weather_summary['humidity']['average']}
    - Average Wind Speed: {weather_summary['wind_speed']['average']}
    
    Include:
    1. Daily itinerary (considering the weather conditions)
    2. Recommended activities (suitable for the expected weather)
    3. Local transportation options
    4. Dining recommendations
    5. Budget considerations
    6. Weather-appropriate packing suggestions
    
    Format the response in a clear, organized manner.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating travel plan: {str(e)}")
        return f"Error generating travel plan: {str(e)}"

# Set page config with favicon
st.set_page_config(
    page_title="Travel Planning Assistant",
    page_icon="images/favicon.png",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
        width: 100%;
    }
    .logo-container img {
        border-radius: 50%;
        object-fit: cover;
        padding: 5px;
        background-color: #f0f2f6;
        margin: 0 auto;
        display: block;
    }
    .weather-summary {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .weather-note {
        font-style: italic;
        color: #666;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Main content area
main_content = st.empty()

# Sidebar for user inputs
with st.sidebar:
    # Add website logo in sidebar
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("images/logo.png", width=150, use_column_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("Trip Details")
    destination = st.text_input("Destination")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    preferences = st.text_area("Preferences (e.g., budget, interests, dietary restrictions)")
    
    if st.button("Generate Travel Plan"):
        if destination and start_date and end_date:
            logger.info(f"Generating travel plan for {destination} from {start_date} to {end_date}")
            with st.spinner("Generating your personalized travel plan..."):
                # Get weather and flight data
                logger.info("Fetching weather data...")
                weather_data = get_weather_data(destination, start_date, end_date)
                logger.info(f"Weather data received: {weather_data}")
                
                logger.info("Fetching flight data...")
                flight_data = get_flight_data("Your Location", destination, start_date)
                logger.info(f"Flight data received: {flight_data}")
                
                # Generate travel plan with weather summary
                logger.info("Generating travel plan with OpenAI...")
                travel_plan = generate_travel_plan(
                    destination, 
                    start_date, 
                    end_date, 
                    preferences,
                    weather_data.get('summary', {})
                )
                logger.info("Travel plan generated successfully")
                
                # Display results
                st.success("Travel plan generated successfully!")
                
                # Replace main content with the travel plan
                with main_content.container():
                    st.markdown("## ✈️ Your Personalized Travel Plan")
                    st.markdown(travel_plan)
                    
                    st.markdown("## 🌤️ Weather Information")
                    
                    # Display weather summary
                    if "summary" in weather_data:
                        st.markdown('<div class="weather-summary">', unsafe_allow_html=True)
                        st.markdown("### Weather Summary")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("#### Temperature")
                            st.markdown(f"Average: {weather_data['summary']['temperature']['average']}")
                            st.markdown(f"Range: {weather_data['summary']['temperature']['min']} to {weather_data['summary']['temperature']['max']}")
                        
                        with col2:
                            st.markdown("#### Humidity")
                            st.markdown(f"Average: {weather_data['summary']['humidity']['average']}")
                            st.markdown(f"Range: {weather_data['summary']['humidity']['min']} to {weather_data['summary']['humidity']['max']}")
                        
                        with col3:
                            st.markdown("#### Wind")
                            st.markdown(f"Average: {weather_data['summary']['wind_speed']['average']}")
                            st.markdown(f"Range: {weather_data['summary']['wind_speed']['min']} to {weather_data['summary']['wind_speed']['max']}")
                        
                        st.markdown("#### Most Common Weather Conditions")
                        for condition in weather_data['summary']['most_common_conditions']:
                            st.markdown(f"- {condition['condition']} ({condition['days']} days)")
                        
                        if "note" in weather_data:
                            st.markdown(f'<div class="weather-note">{weather_data["note"]}</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display daily forecast
                    if "forecast" in weather_data and weather_data["forecast"]:
                        st.markdown("### Daily Weather Details")
                        forecast_data = []
                        for day in weather_data["forecast"]:
                            forecast_data.append({
                                "Date": day["date"],
                                "Temperature": day["temperature"],
                                "Conditions": day["conditions"],
                                "Humidity": day["humidity"],
                                "Wind Speed": day["wind_speed"]
                            })
                        st.table(forecast_data)
                    else:
                        st.warning("Weather forecast data is not available")
                    
                    st.markdown("## 🛫 Flight Information")
                    st.json(flight_data)
        else:
            logger.warning("Missing required fields in travel plan request")
            st.error("Please fill in all required fields.")

# Initial welcome message
with main_content.container():
    st.markdown("""
        ### Welcome to your AI-powered Travel Planning Assistant!
        
        This tool helps you create personalized travel plans using:
        - AI-powered itinerary generation
        - Historical weather patterns
        - Flight information
        - Local recommendations
        
        To get started, fill in your trip details in the sidebar and click "Generate Travel Plan".
        """) 