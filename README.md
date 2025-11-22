# 🌍 Tourism AI System
Traveling somewhere? ✈️ Just ask — and instantly get:

✔ What’s the weather like there?
✔ What are the best places to visit nearby?

This project is a multi-agent AI system that helps users explore cities around the world using simple natural language queries

## ✨ Why This Project?

Because travel planning should be easy ❤️
You type:

"I'm traveling to Tokyo next week — recommend places!"

The system gives you:
☀ Live weather + 🗺 Top tourist attractions
… in seconds! 💨

## ✨ Features

- 🧠 **Parent Agent** – coordinates communication between other agents  
- 🌤 **Weather Agent** – fetches real-time weather for a location  
- 🗺 **Places Agent** – finds interesting tourist spots near the location  
- 🚫 **Smart Error Handling** – gives clean messages if a city isn’t found  
- 🎨 **Modern UI** – beautiful Streamlit-based web interface  
- 🖥 Available in **Web App** + **Command Line Interface (CLI)**  

---

## 🚀 Live Application

🔗 **Try the deployed app here:**  
👉 https://tourism-ai-system-thtjujejttbmappptmsalu4.streamlit.app/

---

## 🖼 Screenshots
<img width="1919" height="811" alt="image" src="https://github.com/user-attachments/assets/748f128c-5763-487b-a9aa-06883063be1c" />

<img width="1914" height="775" alt="image" src="https://github.com/user-attachments/assets/f426629a-ddb8-4e2e-9ddb-d9c326e00cd4" />

<img width="1897" height="833" alt="image" src="https://github.com/user-attachments/assets/cd1e88f8-6642-4b79-b6a8-b84aa3c38ac4" />

<img width="1918" height="811" alt="image" src="https://github.com/user-attachments/assets/1ae4c921-ce40-4120-b36b-d07810f2f2d9" />


### 🌐 Web Interface  
<img width="1919" height="815" alt="image" src="https://github.com/user-attachments/assets/5bef1983-9b81-4212-96b0-6b407662f661" />




### 💻 Command Line Output  
<img width="1034" height="381" alt="image" src="https://github.com/user-attachments/assets/d3362be0-4919-48f5-8011-d4e1e9ce41fb" />




---

## 🏁 Getting Started

### 🔹 Prerequisites

Make sure you have installed:
- Python 3.7 or above
- pip (package installer)
- Internet connection 🌐

---

### 📥 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd Inkel3/Inkel
```

## 🛠 2️⃣ Create Virtual Environment (Recommended)
Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

🖥 Option 1 — Streamlit Web App (Recommended)
```bash
streamlit run streamlit_app.py
```

Then open in browser:
➡ http://localhost:8501

📝 Try queries like:

“I'm going to Bangalore, let's plan my trip”

“What's the weather in Mumbai?”

“What can I see in Delhi?”

“Show me attractions in Tokyo”

✔ Weather + Attractions — displayed together!

💻 Option 2 — Command Line App
```bash
python main.py
```

Example queries:

Tokyo

New York

Temperature in Goa

Type exit to quit

### 🧩 How It Works

1️⃣ Extract location from user input

2️⃣ Get latitude/longitude using Nominatim

3️⃣ Fetch live weather from Open-Meteo

4️⃣ Find attractions from Overpass API

5️⃣ Response combined & displayed neatly

### 🔌 APIs Used
API Name	                                     Purpose

Nominatim	                                     Geocoding (City → Coordinates)

Open-Meteo	                                     Live weather details

Overpass API	                                 Tourist attractions from OpenStreetMap

📝 Example Output (CLI)

🌎 Welcome to the Tourism AI System! 🌎

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

## 📄 License

This project is Open-Source under the MIT License.
Feel free to improve and build amazing things — just keep the license included 🚀





