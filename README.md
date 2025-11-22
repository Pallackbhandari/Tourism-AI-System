🌍 Tourism AI System

Turn any travel thought into instant weather + places to visit!
This project is a multi-agent AI system that helps you explore cities around the world.

✨ What this project does

🧠 Parent Agent – manages communication between all agents

🌤 Weather Agent – fetches real-time weather for a location

🗺 Places Agent – finds interesting tourist spots nearby

🚫 Error Handling – gives readable messages when a city isn’t found

🎨 Modern UI – clean Streamlit interface for easy use

You can use it in two ways:

🖥 Web app (Streamlit)

💻 Command-line interface (CLI)

🚀 Quick Start Guide
🔹 Prerequisites

Make sure you have:

Python 3.7+

pip

Internet connection 🌐

1️⃣ Clone the Repository
git clone <repository-url>
cd Inkel3/Inkel

2️⃣ Create a Virtual Environment (Recommended)

Windows

python -m venv venv
.\venv\Scripts\activate


macOS/Linux

python3 -m venv venv
source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

🖥 Option 1 — Streamlit Web App (Recommended)

Run the app:

streamlit run streamlit_app.py


Then open: http://localhost:8501

Try Asking:

“I'm going to Bangalore, let's plan my trip”

“What's the weather in Mumbai?”

“What can I see in Delhi?”

“Show me attractions in Tokyo”

You’ll see:

✔ Detected location
✔ Current weather
✔ Top nearby attractions

💻 Option 2 — Command Line App

Run:

python main.py


Example queries:

Tokyo

New York

Temperature in Goa

exit → to quit

🧩 How it works (Behind the scenes)

You ask a question (e.g., "places to visit in Manali")

System extracts the location

Nominatim converts place to coordinates

Weather Agent fetches weather from Open-Meteo

Places Agent fetches attractions via Overpass

Parent Agent returns a clean combined response

🔌 APIs Used
API	Purpose
Nominatim	Geocoding (City → Lat/Long)
Open-Meteo	Weather Information
Overpass API	Tourist Attractions from OpenStreetMap
📝 Example Output
▶ Command Line
🌎 Welcome to the Tourism AI System! 🌎
Enter a place name (e.g., 'New York', 'Tokyo', 'Paris')
Type 'exit' to quit.

Enter a place name: Tokyo
Fetching information, please wait...

==================================================
Location: Tokyo, Japan
Weather: Clear sky, 22°C

Top Attractions:
1. Tokyo Tower (attraction)
2. Senso-ji (temple)
3. Meiji Shrine (attraction)
4. Ueno Zoo (zoo)
5. Tokyo Skytree (viewpoint)
==================================================

📄 License

This project is open-source and released under the MIT License.
Feel free to use it, improve it, and build amazing things — just keep the license included 🚀