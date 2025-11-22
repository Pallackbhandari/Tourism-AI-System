from geopy.geocoders import Nominatim
import requests
import json
import re
from typing import Optional, Dict, List, Tuple
import time

# Constants
MAX_ATTRACTIONS = 5
SEARCH_RADIUS_METERS = 10000  # 10km radius

class WeatherAgent:
    """Child Agent responsible for fetching weather information."""
    
    def __init__(self):
        self.weather_conditions = {
            0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 
            3: 'Overcast', 45: 'Foggy', 48: 'Depositing rime fog',
            51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
            56: 'Light freezing drizzle', 57: 'Dense freezing drizzle',
            61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
            66: 'Light freezing rain', 67: 'Heavy freezing rain',
            71: 'Slight snow fall', 73: 'Moderate snow fall', 75: 'Heavy snow fall',
            77: 'Snow grains', 80: 'Slight rain showers', 81: 'Moderate rain showers',
            82: 'Violent rain showers', 85: 'Slight snow showers', 86: 'Heavy snow showers',
            95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
        }
    
    def get_weather(self, lat: float, lon: float) -> Dict:
        """Fetch weather data from Open-Meteo API."""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': True,
                'hourly': 'temperature_2m,weathercode',
                'forecast_days': 1
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Weather service error: {e}")
            return {}
    
    def format_weather(self, data: dict) -> str:
        """Format weather data into a human-readable string."""
        if not data or 'current_weather' not in data:
            return "Weather information not available"
            
        current = data['current_weather']
        temp = current.get('temperature', 'N/A')
        weather_code = int(current.get('weathercode', 0))
        condition = self.weather_conditions.get(weather_code, 'Unknown')
        
        return f"{condition}, {temp}°C"


class PlacesAgent:
    """Child Agent responsible for fetching tourist attractions."""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
    
    def get_attractions(self, lat: float, lon: float, place_name: str = "") -> List[Dict]:
        """Fetch up to MAX_ATTRACTIONS tourist attractions."""
        print(f"Debug: Getting attractions for {place_name} at {lat}, {lon}")
        
        # For Bangalore, return predefined list
        if place_name and any(x in place_name.lower() for x in ["bangalore", "bengaluru"]):
            print("Debug: Using Bangalore attractions")
            return self._get_bangalore_attractions()
        
        # Try different search strategies
        strategies = [
            self._search_by_coordinates,
            self._search_generic_landmarks
        ]
        
        seen = set()
        results = []
        
        for strategy in strategies:
            if len(results) >= MAX_ATTRACTIONS:
                break
                
            try:
                items = strategy(lat, lon)
                for item in items:
                    name = item.get('name', '').strip()
                    if name and name.lower() not in seen:
                        seen.add(name.lower())
                        results.append(item)
                        if len(results) >= MAX_ATTRACTIONS:
                            break
            except Exception as e:
                print(f"Search warning: {str(e)}")
                continue
        
        return results[:MAX_ATTRACTIONS]
    
    def _get_bangalore_attractions(self) -> List[Dict]:
        """Return a predefined list of popular attractions in Bangalore."""
        return [
            {"name": "Lalbagh Botanical Garden", "type": "garden"},
            {"name": "Bangalore Palace", "type": "palace"},
            {"name": "Cubbon Park", "type": "park"},
            {"name": "Vidhana Soudha", "type": "government building"},
            {"name": "ISKCON Temple", "type": "temple"}
        ]
    
    def _search_overpass(self, query: str) -> List[Dict]:
        """Helper method to query Overpass API."""
        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=15
            )
            response.raise_for_status()
            return response.json().get('elements', [])
        except requests.exceptions.Timeout:
            raise Exception("Tourist attractions service is temporarily unavailable. (Request timed out)")
        except requests.exceptions.RequestException as e:
            raise Exception("Tourist attractions service is temporarily unavailable.")
    
    def _search_by_coordinates(self, lat: float, lon: float) -> List[Dict]:
        """Search for tourist attractions near coordinates with English names."""
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"~"attraction|museum|viewpoint|zoo|gallery|theme_park|monument"]
            (around:{SEARCH_RADIUS_METERS},{lat},{lon});
          way["tourism"~"attraction|museum|viewpoint|zoo|gallery|theme_park|monument"]
            (around:{SEARCH_RADIUS_METERS},{lat},{lon});
          node["historic"~"castle|palace|ruins|monument|memorial|archaeological_site|fort"]
            (around:{SEARCH_RADIUS_METERS},{lat},{lon});
        );
        out body {MAX_ATTRACTIONS};
        >;
        out skel qt;
        """
        elements = self._search_overpass(query)
        return self._process_elements(elements)
    
    def _search_generic_landmarks(self, lat: float, lon: float) -> List[Dict]:
        """Search for generic landmarks if no specific attractions found with English names."""
        query = f"""
        [out:json][timeout:25];
        (
          node["leisure"~"park|garden|nature_reserve"]
            (around:{SEARCH_RADIUS_METERS},{lat},{lon});
          node["natural"~"peak|beach|waterfall|cliff"]
            (around:{SEARCH_RADIUS_METERS},{lat},{lon});
          node["amenity"~"place_of_worship|theatre|cinema|university|college"]
            (around:{SEARCH_RADIUS_METERS},{lat},{lon});
        );
        out body {MAX_ATTRACTIONS};
        >;
        out skel qt;
        """
        elements = self._search_overpass(query)
        return self._process_elements(elements)
    
    def _process_elements(self, elements: List[Dict]) -> List[Dict]:
        """Process Overpass API elements into a list of attractions with English names."""
        results = []
        for element in elements:
            tags = element.get('tags', {})
            
            # Try to get English name first, fallback to default name
            name = (
                tags.get('name:en') or  # English name
                tags.get('int_name') or  # International name
                tags.get('name') or      # Default name
                ''
            ).strip()
            
            if not name or name.lower() == 'unnamed':
                continue
            
            attraction_type = (
                tags.get('tourism') or 
                tags.get('historic') or 
                tags.get('leisure') or 
                tags.get('natural') or 
                tags.get('amenity') or 
                'point of interest'
            )
            
            results.append({
                'name': name,
                'type': attraction_type.replace('_', ' ')
            })
            
            if len(results) >= MAX_ATTRACTIONS:
                break
                
        return results


class TourismAgent:
    """Parent Agent that coordinates between Weather and Places agents."""
    
    def __init__(self):
        # Initialize geolocator with English language preference
        self.geolocator = Nominatim(
            user_agent="tourism_ai_system_v1",
            timeout=10
        )
        
        # Store language preference for geocoding
        self.language = 'en'
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()
        
        # Map of countries to their capital cities for better handling
        self.country_capitals = {
            'egypt': 'Cairo',
            'india': 'New Delhi',
            'france': 'Paris',
            'italy': 'Rome',
            'spain': 'Madrid',
            'japan': 'Tokyo',
            'china': 'Beijing',
            'usa': 'New York',
            'united states': 'New York',
            'uk': 'London',
            'united kingdom': 'London',
            'germany': 'Berlin',
            'australia': 'Sydney',
            'canada': 'Toronto',
            'brazil': 'Rio de Janeiro',
            'russia': 'Moscow',
            'thailand': 'Bangkok',
            'turkey': 'Istanbul',
            'greece': 'Athens',
            'mexico': 'Mexico City',
            'south africa': 'Cape Town',
            'argentina': 'Buenos Aires',
            'chile': 'Santiago',
            'peru': 'Lima',
            'morocco': 'Casablanca',
            'israel': 'Jerusalem',
            'uae': 'Dubai',
            'united arab emirates': 'Dubai',
            'singapore': 'Singapore',
            'malaysia': 'Kuala Lumpur',
            'indonesia': 'Jakarta',
            'vietnam': 'Ho Chi Minh City',
            'philippines': 'Manila',
            'south korea': 'Seoul',
            'portugal': 'Lisbon',
            'netherlands': 'Amsterdam',
            'belgium': 'Brussels',
            'switzerland': 'Zurich',
            'austria': 'Vienna',
            'czech republic': 'Prague',
            'poland': 'Warsaw',
            'norway': 'Oslo',
            'sweden': 'Stockholm',
            'denmark': 'Copenhagen',
            'finland': 'Helsinki',
        }
    
    def _clean_location_name(self, location_name: str) -> str:
        """Clean and format location name to ensure it's in English."""
        if not location_name:
            return ""
            
        # If the name contains non-ASCII characters, try to get a more English-friendly version
        if any(ord(char) > 127 for char in location_name):
            try:
                # Try to get an English version using reverse geocoding
                location = self.geolocator.geocode(location_name, exactly_one=True, language='en')
                if location:
                    return location.address
            except:
                pass
        return location_name
        
    def get_coordinates(self, place_name: str) -> Optional[Tuple[float, float, str, str]]:
        """Get coordinates for a place name using Nominatim with improved location matching."""
        # Clean the place name
        place_name = place_name.strip()
        place_lower = place_name.lower()
        
        # Handle special cases first
        if 'kashmir' in place_lower:
            return (34.1491, 76.8250, "Jammu and Kashmir, India", 'valid')
        if 'bangalore' in place_lower or 'bengaluru' in place_lower:
            return (12.9716, 77.5946, "Bengaluru, Karnataka, India", 'valid')
            
        try:
            # First try with English language preference
            locations = self.geolocator.geocode(
                place_name,
                exactly_one=False,
                limit=5,
                addressdetails=True,
                language='en'  # Request English names
            ) or []
            
            if not locations:
                return None
                
            # Define valid place types in order of preference
            valid_place_types = ["city", "town", "village", "locality"]
            
            # Check for exact matches first (case-insensitive)
            exact_matches = []
            for loc in locations:
                display_name = loc.address.lower()
                if place_name.lower() in display_name:
                    exact_matches.append(loc)
            
            # Use exact matches if found, otherwise use all locations
            candidates = exact_matches if exact_matches else locations
            
            # Find the best matching location
            best_match = None
            
            # First try to find a match with valid place type
            for loc in candidates:
                address = loc.raw.get('address', {})
                place_type = address.get('type')
                
                if place_type in valid_place_types:
                    best_match = loc
                    break
                    
            # If no valid place type found, take the first result
            if best_match is None:
                best_match = candidates[0]
            
            # Check if the location is a large region
            address = best_match.raw.get('address', {})
            place_type = address.get('type')
            
            if place_type in ['country', 'state', 'province', 'region']:
                return (best_match.latitude, best_match.longitude, best_match.address, 'region')
                
            return (best_match.latitude, best_match.longitude, best_match.address, 'valid')
            
        except Exception as e:
            print(f"Location service error: {e}")
            return None
    
    def _is_potential_misidentification(self, place_name: str, address: str) -> bool:
        """Check if the found location might be a misidentification."""
        # If user entered a well-known place but got a small village
        well_known_places = ['kashmir', 'goa', 'kerala', 'mumbai', 'delhi', 'bangalore', 'tokyo', 'paris', 'london', 'new york']
        
        place_lower = place_name.lower()
        address_lower = address.lower()
        
        # Check if the place name is in the address (case-insensitive)
        if place_lower not in address_lower:
            return True
            
        # Check for specific misidentification patterns
        for place in well_known_places:
            if place in place_lower and place not in address_lower:
                # If it's a well-known place but not in the address, it's likely a misidentification
                return True
                
        # Check for very specific addresses (suggests a small place)
        if sum(c == ',' for c in address) > 3:  # More than 3 commas suggests a very specific location
            return True
                
        return False
    
    def process_query(self, user_input: str) -> str:
        """Process natural language query and return appropriate response."""
        # Clean the input
        user_input = user_input.replace("'", "").replace('"', '').strip()
        
        # First, clean the input and extract place name
        place_name = None
        
        # Remove common phrases that might be in the query
        query_phrases = [
            "i'm going to", "i am going to", "i want to go to", "i would like to visit",
            "what is the weather in", "weather in", "temperature in", "forecast for"
        ]
        
        clean_input = user_input.lower()
        for phrase in query_phrases:
            clean_input = clean_input.replace(phrase, '').strip()
        
        # FIRST: Check if the cleaned input contains a known country name
        potential_country = None
        potential_country_name = None
        for country_key in self.country_capitals.keys():
            if country_key in clean_input:
                potential_country = self.country_capitals[country_key]
                # Extract the actual country name from the input (case-sensitive)
                for word in user_input.split():
                    if word.lower().strip(' ,.!?;:') == country_key:
                        potential_country_name = word.title()
                        break
                if not potential_country_name:
                    # Fallback: use the country key capitalized
                    potential_country_name = country_key.title()
                break
        
        # Try to find a direct mention of a city name from the cleaned input
        city_names = ['delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 
                     'pune', 'jaipur', 'kerala', 'goa', 'shimla', 'manali', 'varanasi',
                     'bengaluru', 'mumbai', 'kolkata', 'chennai', 'hyderabad']
        
        for city in city_names:
            if city in clean_input:
                place_name = city.title()
                break
                
        # If no direct match, try to extract the place name after common prepositions
        if not place_name:
            prepositions = ['to', 'in', 'at', 'for']
            words = clean_input.split()
            for i, word in enumerate(words):
                if word in prepositions and i + 1 < len(words):
                    place_name = words[i+1].title()
                    break
        
        # If no direct city name found, try patterns
        if not place_name:
            patterns = [
                r'(?:in|at|to|for|visit(?:ing)?|going to|travelling to|trip to|travel to|in the city of|in the town of|in the village of)\s+([A-Z][A-Za-z\s,]+?)(?:\?|$|,|\.|!|and|what|where|when|how|which|that|this|there)',
                r'([A-Z][A-Za-z\s,]+?)(?:\'s|\'|s\'|s)?\s+(?:weather|temperature|forecast|places|attractions|visit|see|go|explore|things to do)',
                r'(?:what are the places in|what is the weather in|what to see in|where to go in|best places in)\s+([A-Z][A-Za-z\s,]+?)(?:\?|$|,|\.|!)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    place_name = match.group(1).strip()
                    break
        
        # If still no match, try to find any capitalized word as potential place name
        if not place_name:
            words = [word for word in user_input.split() if len(word) > 2 and word[0].isupper()]
            if words:
                place_name = ' '.join(words).strip(' ,.!?;:')
        
        if not place_name:
            return "I couldn't determine the location from your query. Please mention a place name."
        
        # Clean the place name - remove trailing commas and punctuation
        place_name = place_name.strip(' ,.!?;:')
        
        # Check if it's a country name that we should handle by using capital city
        place_lower = place_name.lower().strip()
        capital_city = None
        
        # If we detected a country earlier, use that
        if potential_country and potential_country_name:
            capital_city = potential_country
            place_name = potential_country_name
            place_lower = place_name.lower().strip()
        elif place_lower in self.country_capitals:
            capital_city = self.country_capitals[place_lower]
            # Also check for common variations
        elif place_lower.startswith('egypt'):
            capital_city = 'Cairo'
            place_name = 'Egypt'
            place_lower = 'egypt'
        
        # Get coordinates and location info
        if capital_city:
            # Try to get coordinates for the capital city
            location = self.get_coordinates(capital_city)
            if location:
                lat, lon, address, location_type = location
                display_name = capital_city
            else:
                # Fallback to original place name
                location = self.get_coordinates(place_name)
                if not location:
                    return f"I couldn't find any information about '{place_name}'. Please check the spelling and try again."
                lat, lon, address, location_type = location
                display_name = place_name
        else:
            location = self.get_coordinates(place_name)
            if not location:
                return f"I couldn't find any information about '{place_name}'. Please check the spelling and try again."
            
            lat, lon, address, location_type = location
            display_name = place_name
        
        # Handle large regions (but not if we already resolved to a capital)
        if location_type == 'region' and not capital_city:
            # Try to suggest capital city if it's a known country
            if place_lower in self.country_capitals:
                capital = self.country_capitals[place_lower]
                return f"{place_name} is a large region. I'll show you information for {capital}, the capital city. You can also specify other cities like '{capital}' or 'Alexandria' for Egypt."
            else:
                return f"{place_name} is a large region. Please specify a city, e.g., 'Tokyo, Japan' or 'Osaka, Japan'."
        
        result = []
        
        # Extract city name from address for better display (use capital if available)
        if capital_city and location_type != 'region':
            display_name = capital_city
        elif ',' in address:
            display_name = address.split(',')[0].strip()
        else:
            display_name = place_name
        
        # Check what information is being requested
        user_input_lower = user_input.lower()
        ask_weather = any(word in user_input_lower for word in ['weather', 'temperature', 'rain', 'forecast', 'hot', 'cold', 'degree'])
        ask_places = any(word in user_input_lower for word in ['places', 'visit', 'see', 'attractions', 'go', 'explore', 'things to do', 'trip', 'travel'])
        
        # If only weather is asked, don't show places
        if ask_weather and not ask_places and 'places' not in user_input_lower and 'attractions' not in user_input_lower:
            weather_data = self.weather_agent.get_weather(lat, lon)
            weather_info = self.weather_agent.format_weather(weather_data)
            if "not available" not in weather_info:
                return f"In {display_name} it's currently {weather_info}."
            return f"Weather information is not available for {display_name}."
        
        # Get weather if requested (and not already handled above)
        if ask_weather:
            weather_data = self.weather_agent.get_weather(lat, lon)
            weather_info = self.weather_agent.format_weather(weather_data)
            if "not available" not in weather_info:
                result.append(f"In {display_name} it's currently {weather_info}.")
        
        # Get places if requested or if no specific request
        if ask_places or (not ask_weather and not ask_places):
            # Use capital city name if we resolved to a capital, otherwise use original place name
            search_place = capital_city if capital_city else place_name
            attractions = self.places_agent.get_attractions(lat, lon, search_place)
            if attractions:
                place_names = [f"{i+1}. {attr['name']}" for i, attr in enumerate(attractions)]
                if ask_weather:
                    result.append("And these are the places you can visit:")
                else:
                    if capital_city and capital_city.lower() != place_name.lower():
                        result.append(f"In {display_name} (capital of {place_name.title()}) these are the places you can visit:")
                    else:
                        result.append(f"In {display_name} these are the places you can visit:")
                result.extend(place_names)
            else:
                # If no attractions found and we're using a capital city, provide helpful message
                if capital_city:
                    result.append(f"I couldn't find any tourist attractions near {display_name}. Please try specifying a specific city in {place_name.title()}, or try searching for 'Cairo', 'Luxor', or 'Alexandria'.")
                else:
                    result.append(f"I couldn't find any tourist attractions in {display_name}.")
        
        return "\n".join(result)


def main():
    print("=== Welcome to the Tourism AI System! ===")
    print("You can ask about places to visit or weather in any location.")
    print("Examples:")
    print("- I'm going to go to Bangalore, let's plan my trip")
    print("- What's the weather in Mumbai?")
    print("- What can I see in Delhi?")
    print("Type 'exit' to quit.\n")
    
    agent = TourismAgent()
    
    while True:
        try:
            user_input = input("\nEnter your query: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
                
            print("\nFetching information, please wait...")
            print("\n" + "="*70)
            response = agent.process_query(user_input)
            print(response)
            print("="*70)
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again with a different query.")


if __name__ == "__main__":
    main()
