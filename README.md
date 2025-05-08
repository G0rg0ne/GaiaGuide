# Travel Planning Assistant

An AI-powered web application that helps users create personalized travel plans using Streamlit and OpenAI's GPT model. The application provides comprehensive travel planning assistance, including itinerary generation, weather forecasts, and flight information.

## Features

- 🤖 AI-powered travel itinerary generation
- 🌤️ Weather forecast integration
- ✈️ Flight information lookup
- 📅 Date-based planning
- 🎯 Personalized recommendations based on user preferences
- 💰 Budget considerations
- 🍽️ Dining recommendations
- 🚗 Local transportation options

## Prerequisites

- Python 3.7 or higher
- OpenAI API key
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/travel-planning-assistant.git
cd travel-planning-assistant
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Use the sidebar to input your travel details:
   - Destination
   - Start Date
   - End Date
   - Preferences (budget, interests, dietary restrictions)

4. Click "Generate Travel Plan" to create your personalized itinerary

## Docker Deployment

The application can be deployed using Docker:

1. Build the Docker image:
```bash
docker build -t travel-planning-assistant .
```

2. Run the container:
```bash
docker run -p 8501:8501 travel-planning-assistant
```

## Project Structure

```
travel-planning-assistant/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .env              # Environment variables (create this)
├── images/           # Static images and assets
└── README.md         # This file
```

## Dependencies

- streamlit==1.32.0
- openai==1.12.0
- python-dotenv==1.0.1
- requests==2.31.0
- pandas==2.2.1
- python-dateutil==2.8.2

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the license included in the repository.

## Acknowledgments

- OpenAI for providing the GPT API
- Streamlit for the web application framework
- All contributors who have helped improve this project 