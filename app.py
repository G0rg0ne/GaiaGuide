import streamlit as st
import openai
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set page config
st.set_page_config(
    page_title="Travel Planning Assistant",
    page_icon="✈️",
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
    </style>
    """, unsafe_allow_html=True)

def get_weather_data(city, date):
    # This is a placeholder for weather API integration
    # You would replace this with actual API calls to a weather service
    return {
        "temperature": "20°C",
        "conditions": "Sunny",
        "humidity": "60%"
    }

def get_flight_data(origin, destination, date):
    # This is a placeholder for flight API integration
    # You would replace this with actual API calls to a flight service
    return {
        "price": "$300",
        "airline": "Example Airlines",
        "departure_time": "10:00 AM"
    }

def generate_travel_plan(destination, start_date, end_date, preferences):
    # Create a prompt for the OpenAI API
    prompt = f"""
    Create a detailed travel plan for {destination} from {start_date} to {end_date}.
    Preferences: {preferences}
    
    Include:
    1. Daily itinerary
    2. Recommended activities
    3. Local transportation options
    4. Dining recommendations
    5. Budget considerations
    
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
        return f"Error generating travel plan: {str(e)}"

# Main Streamlit interface
st.title("✈️ Travel Planning Assistant")

# Sidebar for user inputs
with st.sidebar:
    st.header("Trip Details")
    destination = st.text_input("Destination")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    preferences = st.text_area("Preferences (e.g., budget, interests, dietary restrictions)")
    
    if st.button("Generate Travel Plan"):
        if destination and start_date and end_date:
            with st.spinner("Generating your personalized travel plan..."):
                # Get weather and flight data
                weather_data = get_weather_data(destination, start_date)
                flight_data = get_flight_data("Your Location", destination, start_date)
                
                # Generate travel plan
                travel_plan = generate_travel_plan(destination, start_date, end_date, preferences)
                
                # Display results
                st.success("Travel plan generated successfully!")
                
                # Create tabs for different sections
                tab1, tab2, tab3 = st.tabs(["Travel Plan", "Weather", "Flights"])
                
                with tab1:
                    st.markdown(travel_plan)
                
                with tab2:
                    st.write("Weather Forecast:")
                    st.json(weather_data)
                
                with tab3:
                    st.write("Flight Information:")
                    st.json(flight_data)
        else:
            st.error("Please fill in all required fields.")

# Main content area
st.markdown("""
    ### Welcome to your AI-powered Travel Planning Assistant!
    
    This tool helps you create personalized travel plans using:
    - AI-powered itinerary generation
    - Real-time weather data
    - Flight information
    - Local recommendations
    
    To get started, fill in your trip details in the sidebar and click "Generate Travel Plan".
    """) 