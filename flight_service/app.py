from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from amadeus import Client, ResponseError
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Amadeus client
amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

class FlightRequest(BaseModel):
    origin_iata: str
    destination_iata: str
    departure_date: str

@app.post("/flights")
async def get_flights(request: FlightRequest):
    try:
        logger.info(f"Searching flights from {request.origin_iata} to {request.destination_iata} on {request.departure_date}")
        
        # Search for flights using Amadeus API
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=request.origin_iata,
            destinationLocationCode=request.destination_iata,
            departureDate=request.departure_date,
            adults=1,
            max=5  # Limit to 5 results
        )

        # Process and format the flight data
        flights = []
        for offer in response.data:
            flight = {
                "price": {
                    "total": offer["price"]["total"],
                    "currency": offer["price"]["currency"]
                },
                "itineraries": []
            }
            
            for itinerary in offer["itineraries"]:
                segments = []
                for segment in itinerary["segments"]:
                    segments.append({
                        "departure": {
                            "airport": segment["departure"]["iataCode"],
                            "time": segment["departure"]["at"]
                        },
                        "arrival": {
                            "airport": segment["arrival"]["iataCode"],
                            "time": segment["arrival"]["at"]
                        },
                        "carrier": segment["carrierCode"],
                        "flight_number": segment["number"]
                    })
                flight["itineraries"].append({
                    "segments": segments
                })
            
            flights.append(flight)

        return {
            "status": "success",
            "flights": flights
        }

    except ResponseError as error:
        logger.error(f"Amadeus API error: {error}")
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as e:
        logger.error(f"Error in get_flights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 