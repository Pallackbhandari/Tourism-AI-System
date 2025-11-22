import streamlit as st
from main import TourismAgent
import time
import random
from collections import defaultdict

# Common tourism-related phrases and their next word predictions
TOURISM_PHRASES = {
    "i'm going to": ["visit", "explore", "travel to", "see", "tour"],
    "i want to": ["visit", "see", "explore", "go to", "travel to"],
    "show me": ["attractions", "places", "hotels", "restaurants", "landmarks"],
    "what to do in": ["", "the", "this", "my"],
    "best time to visit": ["", "the", "this", "my"],
    "how to reach": ["", "the", "this", "my"],
    "where to stay in": ["", "the", "this", "my"],
    "best restaurants in": ["", "the", "this", "my"],
    "things to do in": ["", "the", "this", "my"],
    "weather in": ["", "the", "this", "my"],
    "hotels in": ["", "the", "this", "my"],
    "places to visit in": ["", "the", "this", "my"]
}

def predict_next_word(text):
    """Predict the next word based on the input text."""
    text = text.lower().strip()
    if not text:
        return []
        
    # Check for matching phrases
    for phrase, next_words in TOURISM_PHRASES.items():
        if text.endswith(phrase):
            return next_words
            
    # If no exact match, find the last few words that match the start of any phrase
    words = text.split()
    for i in range(len(words)):
        partial_phrase = ' '.join(words[i:]).lower()
        for phrase, next_words in TOURISM_PHRASES.items():
            if phrase.startswith(partial_phrase) and phrase != partial_phrase:
                remaining = phrase[len(partial_phrase):].strip().split()[0]
                if remaining and remaining not in next_words:
                    return [remaining] + next_words[:3]
                return next_words[:4]
    
    # If no match, return some common next words
    return ["visit", "see", "explore", "in"]

# Page configuration
st.set_page_config(
    page_title="Tourism AI System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .weather-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .attraction-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
    </style>
""", unsafe_allow_html=True)

def get_suggestions(query: str, limit: int = 8) -> list:
    """Get place suggestions based on user input - search engine style autocomplete."""
    if not query or len(query) < 1:
        return []
    
    query_lower = query.lower().strip()
    
    # Comprehensive list of popular places (cities and countries)
    popular_places = [
        # Indian cities
        "Bangalore", "Mumbai", "Delhi", "Chennai", "Kolkata", "Hyderabad", 
        "Pune", "Jaipur", "Ahmedabad", "Surat", "Lucknow", "Kanpur",
        "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Varanasi",
        
        # International cities
        "Bangkok", "Tokyo", "Paris", "London", "New York", "Los Angeles",
        "Sydney", "Melbourne", "Dubai", "Singapore", "Hong Kong", "Seoul",
        "Shanghai", "Beijing", "Moscow", "Istanbul", "Rome", "Madrid",
        "Barcelona", "Amsterdam", "Berlin", "Munich", "Vienna", "Prague",
        "Copenhagen", "Stockholm", "Oslo", "Zurich", "Lisbon", "Athens",
        "Cairo", "Alexandria", "Luxor", "Marrakech", "Casablanca", "Lagos",
        "Nairobi", "Cape Town", "Johannesburg", "Lima", "Buenos Aires",
        "Rio de Janeiro", "Sao Paulo", "Santiago", "Bogota", "Caracas",
        "Mexico City", "Toronto", "Vancouver", "Montreal", "Chicago",
        "Miami", "San Francisco", "Las Vegas", "Boston", "Washington",
        "Philadelphia", "Houston", "Phoenix", "Seattle", "Portland",
        
        # Countries
        "Egypt", "India", "Thailand", "Japan", "France", "Italy", "Spain",
        "Germany", "Australia", "Canada", "Brazil", "Russia", "China",
        "Turkey", "Greece", "Mexico", "South Africa", "Argentina", "Chile",
        "Peru", "Morocco", "Israel", "UAE", "Singapore", "Malaysia",
        "Indonesia", "Vietnam", "Philippines", "South Korea", "Portugal",
        "Netherlands", "Belgium", "Switzerland", "Austria", "Czech Republic",
        "Poland", "Norway", "Sweden", "Denmark", "Finland", "Iceland",
        "Ireland", "United Kingdom", "United States", "USA", "UK"
    ]
    
    # Priority: places that START with the query (exact prefix match)
    exact_matches = []
    # Secondary: places that contain the query
    contains_matches = []
    
    for place in popular_places:
        place_lower = place.lower()
        if place_lower.startswith(query_lower):
            exact_matches.append(place)
        elif query_lower in place_lower:
            contains_matches.append(place)
    
    # Sort exact matches alphabetically, then add contains matches
    exact_matches.sort()
    contains_matches.sort()
    
    # Combine: exact matches first, then contains matches
    suggestions = exact_matches + contains_matches
    return suggestions[:limit]

def parse_response(response_text):
    """Parse the response text into structured data."""
    result = {
        'weather': None,
        'weather_raw': None,
        'places': [],
        'error': None,
        'location': None,
        'raw_text': response_text
    }
    
    lines = response_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for weather info - format: "In {location} it's currently {weather}."
        if 'currently' in line.lower() or ('it\'s' in line.lower() and ('°c' in line.lower() or 'temperature' in line.lower())):
            if 'not available' not in line.lower():
                result['weather'] = line
                result['weather_raw'] = line
                # Extract location from weather line if possible
                if 'In ' in line:
                    loc_part = line.split('In ', 1)[1].split(' it\'s')[0].strip()
                    result['location'] = loc_part
        
        # Check for places - numbered list format: "1. Place Name"
        elif line and line[0].isdigit() and '.' in line and len(line.split('.', 1)) > 1:
            place_name = line.split('.', 1)[1].strip()
            if place_name:
                result['places'].append(place_name)
        
        # Check for location info in places section
        elif 'places you can visit' in line.lower() or 'these are the places' in line.lower():
            if 'In ' in line:
                loc_part = line.split('In ', 1)[1].split(' these')[0].strip()
                if loc_part:
                    result['location'] = loc_part
        
        # Check for errors
        elif any(word in line.lower() for word in ['couldn\'t', 'could not', 'error', 'not found', 'not available', 'large region']):
            if result['error'] is None:
                result['error'] = line
            else:
                result['error'] += f"\n{line}"
    
    return result

def update_query(new_query):
    """Update the query in session state and trigger a rerun."""
    st.session_state.query_input = new_query

def main():
    # Initialize session state - force recreation of agent to ensure latest code is loaded
    # Clear and recreate agent to pick up any code changes
    if 'agent' not in st.session_state:
        st.session_state.agent = TourismAgent()
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'auto_search' not in st.session_state:
        st.session_state.auto_search = False
    if 'query_input' not in st.session_state:
        st.session_state.query_input = ""
    
    # Header
    st.markdown('<h1 class="main-header">🌍 Tourism AI System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Get weather and tourist attraction information for any location worldwide</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📖 How to Use")
        st.markdown("""
        Enter a natural language query about a location:
        
        **Examples:**
        - "I'm going to Bangalore, let's plan my trip"
        - "What's the weather in Mumbai?"
        - "What can I see in Delhi?"
        - "Show me attractions in Tokyo"
        - "Weather in Paris"
        
        **Tip:** Start typing and see next-word predictions!
        """)
        
        st.markdown("---")
        st.header("🔍 Recent Queries")
        if st.session_state.query_history:
            for i, query in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                st.text(f"{i}. {query}")
        else:
            st.info("No queries yet")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This system uses:
        - 🌤️ Open-Meteo API for weather
        - 🗺️ Overpass API for attractions
        - 📍 Nominatim for geocoding
        """)
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    # Get the current query from session state
    user_query = st.session_state.query_input
    
    # Display the search box
    with col1:
        user_input = st.text_input(
            "Enter your query:",
            value=user_query,
            placeholder="e.g., I'm going to Bangalore, let's plan my trip",
            key="query_input_display"
        )
        
        # Update the session state if the user types in the input
        if user_input != user_query:
            st.session_state.query_input = user_input
            st.rerun()
    
    with col2:
        st.write("")  # Spacing
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Process autocomplete suggestions and next-word predictions
    suggestions_list = []
    next_word_predictions = []
    search_term = ""
    query_prefix = ""
    query_lower = user_query.lower() if user_query else ""
    
    # Get next word predictions
    if user_query:
        next_word_predictions = predict_next_word(user_query)
        
        # Show next word predictions as buttons
        if next_word_predictions and not search_button:
            st.write("Next word suggestions:")
            cols = st.columns(4)  # Create 4 columns for the buttons
            
            for idx, word in enumerate(next_word_predictions[:4]):  # Show max 4 predictions
                if cols[idx].button(
                    f"{word}",
                    key=f"pred_{idx}",
                    use_container_width=True,
                    type="secondary"
                ):
                    # When a prediction is clicked, update the query using the callback
                    new_query = f"{user_query.strip()} {word}".strip()
                    update_query(new_query)
                    st.rerun()
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Process autocomplete suggestions - show as you type (only when NOT searching)
    
    # Show suggestions only if user is typing and hasn't clicked search
    if user_query and len(user_query.strip()) >= 1 and not search_button:
        query_words = user_query.split()
        common_words = ['to', 'in', 'at', 'for', 'the', 'and', 'or', 'i', 'am', 'going', 'im', "i'm", 'lets', 'let', 'plan', 'my', 'trip', 'what', 'show', 'me', 'is', 'a']
        
        # Get the last word that's not a common word for autocomplete
        if query_words:
            # Check if last word is significant (not common)
            last_word = query_words[-1].lower().strip('.,!?;:')
            
            if last_word not in common_words and len(last_word) >= 1:
                search_term = last_word
                query_prefix = " ".join(query_words[:-1])
            else:
                # If last word is common, check second-to-last
                if len(query_words) > 1:
                    second_last = query_words[-2].lower().strip('.,!?;:')
                    if second_last not in common_words:
                        search_term = second_last
                        query_prefix = " ".join(query_words[:-2])
        
        # Get suggestions even for single character
        if search_term:
            suggestions_list = get_suggestions(search_term, limit=6)
    
    # Display autocomplete suggestions - show them prominently
    # Note: In Streamlit, suggestions appear after you finish typing (press Enter or click away)
    if suggestions_list and user_query:
        # Only hide suggestions after search is clicked
        if not search_button:
            st.markdown("---")
            st.markdown("**💡 Autocomplete suggestions (click to auto-fill):**")
            
            # Show suggestions in a nice box
            suggestion_cols = st.columns(min(len(suggestions_list), 6))
            for idx, suggestion in enumerate(suggestions_list[:6]):
                with suggestion_cols[idx]:
                    # Build the complete query - smart word completion
                    if query_prefix:
                        # Replace the partial word with the full suggestion
                        suggested_query = f"{query_prefix} {suggestion}".strip()
                    else:
                        # Context-aware query building
                        if any(word in query_lower for word in ['going', 'visit', 'trip', 'travel']):
                            suggested_query = f"I'm going to {suggestion}, let's plan my trip"
                        elif any(word in query_lower for word in ['weather', 'temperature', 'forecast']):
                            suggested_query = f"What's the weather in {suggestion}?"
                        elif any(word in query_lower for word in ['see', 'attractions', 'places', 'explore']):
                            suggested_query = f"What can I see in {suggestion}?"
                        else:
                            # Just the suggestion word
                            suggested_query = suggestion
                    
                    # Create suggestion button with better styling
                    if st.button(f"📍 {suggestion}", 
                               key=f"autocomplete_{idx}_{hash(str(user_query) + str(idx))}", 
                               use_container_width=True,
                               help=f"Click to complete: {suggested_query}"):
                        st.session_state.query_input = suggested_query
                        st.session_state.auto_search = False
                        st.rerun()
            st.markdown("---")
    
    # Determine if we should process the query
    should_process = search_button and user_query
    
    # Auto-trigger search if example query was clicked
    if st.session_state.auto_search and user_query:
        st.session_state.auto_search = False
    
    # Process query
    if should_process:
        with st.spinner("Fetching information, please wait..."):
            try:
                response = st.session_state.agent.process_query(user_query)
                
                # Add to history
                if user_query not in st.session_state.query_history:
                    st.session_state.query_history.append(user_query)
                
                # Parse response
                parsed = parse_response(response)
                
                # Display results
                st.markdown("---")
                
                # Show location if available
                if parsed['location']:
                    st.markdown(f"### 📍 Location: {parsed['location']}")
                
                # Show weather if available
                if parsed['weather']:
                    st.markdown(f"""
                    <div class="weather-box">
                        <h3>🌤️ Weather Information</h3>
                        <p style="font-size: 1.3rem; margin: 0.5rem 0;">{parsed['weather']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show places if available
                if parsed['places']:
                    st.markdown("### 🏛️ Tourist Attractions")
                    for i, place in enumerate(parsed['places'], 1):
                        st.markdown(f"""
                        <div class="attraction-box">
                            <strong style="font-size: 1.1rem;">{i}. {place}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show error if any
                if parsed['error']:
                    st.error(f"⚠️ {parsed['error']}")
                
                # If response doesn't match expected format, show raw response
                if not parsed['weather'] and not parsed['places'] and not parsed['error']:
                    st.info("📝 Response:")
                    st.write(response)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please try again with a different query.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 2rem 0;'>"
        "Built with ❤️ using Streamlit | Tourism AI System v1.0"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

