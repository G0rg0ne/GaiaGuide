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

# Initialize session state for tracking if results are shown
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

def reset_page():
    """Reset the page state and clear results"""
    st.session_state.show_results = False
    st.rerun()

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

def get_flight_data(origin_city, origin_iata, destination_city, destination_iata, date):
    try:
        logger.info(f"Requesting flight data from {origin_iata} to {destination_iata} on {date}")
        # Make request to flight service
        response = requests.post(
            "http://flight_service:8001/flights",
            json={
                "origin_iata": origin_iata,
                "destination_iata": destination_iata,
                "departure_date": date.isoformat()
            }
        )
        if response.status_code == 200:
            flight_data = response.json()
            logger.info(f"Successfully received flight data: {flight_data}")
            return flight_data
        else:
            logger.error(f"Failed to fetch flight data. Status code: {response.status_code}")
            return {
                "error": "Failed to fetch flight data",
                "flights": []
            }
    except Exception as e:
        logger.error(f"Error in get_flight_data: {str(e)}")
        return {
            "error": str(e),
            "flights": []
        }

def generate_travel_plan(destination, start_date, end_date, preferences, weather_summary, flight_data):
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

    Available Flight Options:
    {format_flight_options(flight_data)}
    
    Please analyze the flight options and recommend the best choice considering:
    1. Price vs. duration ratio
    2. Convenient departure/arrival times for vacation planning
    3. Number of connections (direct flights preferred)
    4. Overall value for money
    
    Include in your response:
    1. Flight recommendation with justification
    2. Daily itinerary (considering the weather conditions and flight times)
    3. Recommended activities (suitable for the expected weather)
    4. Local transportation options
    5. Dining recommendations
    6. Budget considerations
    7. Weather-appropriate packing suggestions
    
    Format the response in a clear, organized manner with sections for flight analysis and travel plan.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel planning assistant with expertise in analyzing flight options and creating optimized vacation plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating travel plan: {str(e)}")
        return f"Error generating travel plan: {str(e)}"

def format_flight_options(flight_data):
    if "error" in flight_data or not flight_data.get("flights"):
        return "No flight options available."
    
    formatted_options = []
    for idx, flight in enumerate(flight_data["flights"], 1):
        option = f"\nOption {idx}:\n"
        option += f"Price: {flight['price']['total']} {flight['price']['currency']}\n"
        
        for itinerary in flight["itineraries"]:
            for segment in itinerary["segments"]:
                option += f"Flight: {segment['carrier']} {segment['flight_number']}\n"
                option += f"From: {segment['departure']['airport']} at {segment['departure']['time']}\n"
                option += f"To: {segment['arrival']['airport']} at {segment['arrival']['time']}\n"
        
        formatted_options.append(option)
    
    return "\n".join(formatted_options)

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
        padding-left: 2rem;
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
    .help-icon {
        color: #666;
        cursor: pointer;
        margin-left: 5px;
    }
    .help-tooltip {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-top: 5px;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# Main content area
main_content = st.empty()

# Sidebar for user inputs
with st.sidebar:
    # Add website logo in sidebar
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("images/logo.png", width=200, use_column_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("Trip Details")
    # Departure details
    st.subheader("Departure")
    departure_city = st.text_input("From (City)")
    col1, col2 = st.columns([3, 1])
    with col1:
        departure_iata = st.text_input("From (Airport IATA Code)", max_chars=3).upper()
    with col2:
        st.markdown("""
            <div style="margin-top: 1.5rem;">
                <a href="https://www.iata.org/en/publications/directories/code-search/" target="_blank" title="Search IATA codes">
                    🔍 IATA Search
                </a>
            </div>
        """, unsafe_allow_html=True)
    
    # Destination details
    st.subheader("Destination")
    destination = st.text_input("To (City)")
    col3, col4 = st.columns([3, 1])
    with col3:
        destination_iata = st.text_input("To (Airport IATA Code)", max_chars=3).upper()
    with col4:
        st.markdown("""
            <div style="margin-top: 1.5rem;">
                <a href="https://www.iata.org/en/publications/directories/code-search/" target="_blank" title="Search IATA codes">
                    🔍 IATA Search
                </a>
            </div>
        """, unsafe_allow_html=True)
    
    # Add IATA code help information
    with st.expander("ℹ️ What are IATA codes?"):
        st.markdown("""
        IATA codes are three-letter codes used to identify airports worldwide. For example:
        - JFK for John F. Kennedy International Airport (New York)
        - LHR for London Heathrow Airport
        - CDG for Charles de Gaulle Airport (Paris)
        
        You can find IATA codes for any airport using the IATA search tool linked above.
        """)
    
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    preferences = st.text_area("Preferences (e.g., budget, interests, dietary restrictions)")
    
    if st.button("Generate Travel Plan"):
        if (destination and destination_iata and departure_city and departure_iata 
            and start_date and end_date):
            st.session_state.show_results = True
            logger.info(f"Generating travel plan for {destination} from {start_date} to {end_date}")
            with st.spinner("Generating your personalized travel plan..."):
                # Get weather and flight data
                logger.info("Fetching weather data...")
                weather_data = get_weather_data(destination, start_date, end_date)
                logger.info(f"Weather data received: {weather_data}")
                
                logger.info("Fetching flight data...")
                flight_data = get_flight_data(departure_city, departure_iata, destination, destination_iata, start_date)
                logger.info(f"Flight data received: {flight_data}")
                
                # Generate travel plan with weather summary and flight data
                logger.info("Generating travel plan with OpenAI...")
                travel_plan = generate_travel_plan(
                    destination, 
                    start_date, 
                    end_date, 
                    preferences,
                    weather_data.get('summary', {}),
                    flight_data
                )
                logger.info("Travel plan generated successfully")
                
                # Store results in session state
                st.session_state.weather_data = weather_data
                st.session_state.flight_data = flight_data
                st.session_state.travel_plan = travel_plan
                st.session_state.destination = destination
                
                st.rerun()
        else:
            logger.warning("Missing required fields in travel plan request")
            st.error("Please fill in all required fields.")
    
    # Add reset button below Generate Travel Plan
    if st.session_state.show_results:
        st.markdown("---")  # Add a separator
        if st.button("🔄 Make New Prediction", use_container_width=True):
            reset_page()

# Display results if they exist
if st.session_state.show_results:
    with main_content.container():
        st.markdown("## ✈️ Your Personalized Travel Plan")
        st.markdown(st.session_state.travel_plan)
        
        st.markdown("## 🌤️ Weather Information")
        
        # Display weather summary
        if "summary" in st.session_state.weather_data:
            st.markdown('<div class="weather-summary">', unsafe_allow_html=True)
            st.markdown("### Weather Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Temperature")
                st.markdown(f"Average: {st.session_state.weather_data['summary']['temperature']['average']}")
                st.markdown(f"Range: {st.session_state.weather_data['summary']['temperature']['min']} to {st.session_state.weather_data['summary']['temperature']['max']}")
            
            with col2:
                st.markdown("#### Humidity")
                st.markdown(f"Average: {st.session_state.weather_data['summary']['humidity']['average']}")
                st.markdown(f"Range: {st.session_state.weather_data['summary']['humidity']['min']} to {st.session_state.weather_data['summary']['humidity']['max']}")
            
            with col3:
                st.markdown("#### Wind")
                st.markdown(f"Average: {st.session_state.weather_data['summary']['wind_speed']['average']}")
                st.markdown(f"Range: {st.session_state.weather_data['summary']['wind_speed']['min']} to {st.session_state.weather_data['summary']['wind_speed']['max']}")
            
            st.markdown("#### Most Common Weather Conditions")
            for condition in st.session_state.weather_data['summary']['most_common_conditions']:
                st.markdown(f"- {condition['condition']} ({condition['days']} days)")
            
            if "note" in st.session_state.weather_data:
                st.markdown(f'<div class="weather-note">{st.session_state.weather_data["note"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display daily forecast
        if "forecast" in st.session_state.weather_data and st.session_state.weather_data["forecast"]:
            st.markdown("### Daily Weather Details")
            forecast_data = []
            for day in st.session_state.weather_data["forecast"]:
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
        
        if "flights" in st.session_state.flight_data and st.session_state.flight_data["flights"]:
            for idx, flight in enumerate(st.session_state.flight_data["flights"], 1):
                with st.container():
                    st.markdown(f"### Flight Option {idx}")
                    
                    # Create columns for price and details
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("#### Price")
                        st.markdown(f"""
                            <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 10px; text-align: center;'>
                                <h2 style='margin: 0; color: #1f77b4;'>{flight['price']['total']} {flight['price']['currency']}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        for itinerary in flight["itineraries"]:
                            for segment in itinerary["segments"]:
                                st.markdown("#### Flight Details")
                                st.markdown(f"""
                                    <div style='background-color: #797df7; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                                            <div>
                                                <strong>{segment['departure']['airport']}</strong> → <strong>{segment['arrival']['airport']}</strong>
                                                <br>
                                                <small>{segment['carrier']} {segment['flight_number']}</small>
                                            </div>
                                            <div style='text-align: right;'>
                                                <div>Departure: {segment['departure']['time']}</div>
                                                <div>Arrival: {segment['arrival']['time']}</div>
                                            </div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    st.markdown("---")
        else:
            st.warning("No flight information available")

# Initial welcome message
if not st.session_state.show_results:
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