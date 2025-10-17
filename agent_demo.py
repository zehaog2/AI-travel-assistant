"""
Agent Demo: Maps natural language to structured actions with policy validation
"""
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

class Intent(Enum):
    #Supported intent types
    SEARCH_FLIGHT = "SearchFlight"
    BOOK_HOTEL = "BookHotel"
    CANCEL_FLIGHT = "CancelFlight"
    CHECK_POLICY = "CheckPolicy"
    UNKNOWN = "Unknown"

class TravelPolicyRules:
    @staticmethod
    def validate_flight_class(from_city: str, to_city: str, flight_class: str) -> Tuple[bool, str]:
        #Validate if flight class is allowed per policy
        # Simplified logic - check if domestic or international
        domestic_cities = ["Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Chengdu", "Hong Kong", "Si Chuan"]
        
        is_domestic = from_city in domestic_cities and to_city in domestic_cities
        
        if is_domestic and flight_class in ["business", "first"]:
            return False, "Policy violation: Domestic flights must use economy class"
        
        if flight_class == "first":
            return False, "Policy violation: First class requires executive approval"
            
        return True, "Compliant with travel policy"

class IntentRecognizer:
    #Maps user input to intents and extracts parameters
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.policy_validator = TravelPolicyRules()
    
    def _load_intent_patterns(self) -> Dict:
        #Define patterns for intent recognition
        return {
            Intent.SEARCH_FLIGHT: {
                "keywords": ["flight", "fly", "flights", "airplane", "airfare", "air","plane","teleport"],
                "patterns": [
                    r"(?:flight|fly|flights?)\s+(?:from\s+)?(\w+)\s+to\s+(\w+)",
                    r"(?:need|want|book|find|search)\s+.*?(?:flight|fly)",
                    r"(?:from\s+)?(\w+)\s+to\s+(\w+)\s+(?:flight|flights?)",
                ]
            },
            Intent.BOOK_HOTEL: {
                "keywords": ["hotel", "accommodation", "stay", "lodging", "room","sleep","rest","shower"],
                "patterns": [
                    r"(?:book|reserve|find|need)\s+.*?hotel",
                    r"hotel\s+(?:in|at|near)\s+(\w+)",
                    r"(?:stay|accommodation|lodging)\s+(?:in|at)\s+(\w+)"
                ]
            },
            Intent.CANCEL_FLIGHT: {
                "keywords": ["cancel", "cancellation", "refund", "void"],
                "patterns": [
                    r"cancel\s+(?:my\s+)?flight",
                    r"(?:cancel|refund|void)\s+.*?(?:ticket|booking|reservation)",
                    r"flight\s+cancellation"
                ]
            },
            Intent.CHECK_POLICY: {
                "keywords": ["policy", "rule", "allowed", "guidelines", "regulations", "policies"],
                "patterns": [
                    r"(?:what|check|tell).*?policy",
                    r"(?:is|are)\s+.*?allowed",
                    r"(?:travel|company)\s+(?:policy|rules|guidelines)"
                ]
            }
        }
    '''
Intent classification enables structured action execution
Parameter extraction converts natural language to API calls
Policy validation prevents non-compliant bookings
Confidence scoring helps identify unclear requests
'''
    def classify_intent(self, user_input: str) -> Intent:
        #Classify user input into an intent category
        input_lower = user_input.lower()
        # Score each intent based on keyword and pattern matching
        intent_scores = {}
        
        for intent, config in self.intent_patterns.items():
            score = 0
            
            # Check keywords
            for keyword in config["keywords"]:
                if keyword in input_lower:
                    score += 2
            
            # Check patterns
            for pattern in config["patterns"]:
                if re.search(pattern, input_lower):
                    score += 3
            
            if score > 0:
                intent_scores[intent] = score
        
        # Return intent with highest score, or UNKNOWN
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return Intent.UNKNOWN
    
    def extract_parameters(self, user_input: str, intent: Intent) -> Dict[str, Any]:
        #Extract parameters based on intent type
        input_lower = user_input.lower()
        
        if intent == Intent.SEARCH_FLIGHT:
            return self._extract_flight_params(user_input)
        elif intent == Intent.BOOK_HOTEL:
            return self._extract_hotel_params(user_input)
        elif intent == Intent.CANCEL_FLIGHT:
            return self._extract_cancellation_params(user_input)
        elif intent == Intent.CHECK_POLICY:
            return self._extract_policy_params(user_input)
        else:
            return {}
    
    def _extract_flight_params(self, text: str) -> Dict:
        #Extract flight search parameters"""
        params = {}
        
        # Extract cities using pattern matching
        city_pattern = r"(?:from\s+)?([A-Z][a-z]+)\s+to\s+([A-Z][a-z]+)"
        city_match = re.search(city_pattern, text)
        if city_match:
            params["from_city"] = city_match.group(1)
            params["to_city"] = city_match.group(2)
        
        # Extract date
        date_patterns = [
            r"(tomorrow|today|next\s+\w+day)",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}"
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                params["date"] = self._parse_date(date_match.group(0))
                break
        
        # Extract time preference
        if any(word in text.lower() for word in ["morning", "afternoon", "evening", "night"]):
            for time in ["morning", "afternoon", "evening", "night"]:
                if time in text.lower():
                    params["time_preference"] = time
                    break
        
        # Extract class preference
        for flight_class in ["economy", "business", "first"]:
            if flight_class in text.lower():
                params["class_preference"] = flight_class
                break
        
        return params
    
    def _extract_hotel_params(self, text: str) -> Dict:
        #Extract hotel booking parameters
        params = {}
        
        # Extract city
        city_pattern = r"(?:in|at|near)\s+([A-Z][a-z]+)"
        city_match = re.search(city_pattern, text)
        if city_match:
            params["city"] = city_match.group(1)
        
        # Extract dates
        if "tonight" in text.lower():
            params["check_in_date"] = datetime.now().strftime("%Y-%m-%d")
            params["check_out_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "tomorrow" in text.lower():
            params["check_in_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            params["check_out_date"] = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        # Extract hotel class
        for star_rating in ["5-star", "4-star", "3-star", "luxury", "budget"]:
            if star_rating in text.lower():
                params["hotel_class"] = star_rating
                break
        
        # Extract budget if mentioned
        budget_pattern = r"\$?(\d+)"
        budget_match = re.search(budget_pattern, text)
        if budget_match:
            params["budget"] = float(budget_match.group(1))
        
        return params
    
    def _extract_cancellation_params(self, text: str) -> Dict:
        #Extract flight cancellation parameters
        params = {}
        
        # Look for booking ID
        booking_pattern = r"(?:booking|confirmation|reference)\s*(?:id|number|code)?\s*[:#]?\s*([A-Z0-9]+)"
        booking_match = re.search(booking_pattern, text, re.IGNORECASE)
        if booking_match:
            params["booking_id"] = booking_match.group(1)
        
        # Look for flight number
        flight_pattern = r"(?:flight\s*#?|flight\s+number\s*[:#]?)\s*([A-Z]{2}\d{3,4})"
        flight_match = re.search(flight_pattern, text, re.IGNORECASE)
        if flight_match:
            params["flight_number"] = flight_match.group(1)
        
        # Simple pattern for booking ID like #ABC123
        simple_booking = r"#([A-Z0-9]+)"
        simple_match = re.search(simple_booking, text)
        if simple_match:
            params["booking_id"] = simple_match.group(1)
        
        return params
    
    def _extract_policy_params(self, text: str) -> Dict:
        #Extract policy check parameters
        params = {}
        
        # Identify policy topic
        topics = ["flight", "hotel", "meal", "visa", "insurance", "refund", "budget"]
        for topic in topics:
            if topic in text.lower():
                params["topic"] = topic
                break
        
        if "topic" not in params:
            params["topic"] = "general"
        
        params["specific_query"] = text
        
        return params
    
    def _parse_date(self, date_str: str) -> str:
        #Parse various date formats to YYYY-MM-DD
        date_str_lower = date_str.lower()
        
        if date_str_lower == "today":
            return datetime.now().strftime("%Y-%m-%d")
        elif date_str_lower == "tomorrow":
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next monday" in date_str_lower:
            # Find next Monday
            today = datetime.now()
            days_ahead = 0 - today.weekday() + 7  # Monday is 0
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        else:
            # Return as-is for now (would need more sophisticated parsing)
            return date_str
    
    def process_request(self, user_input: str) -> Dict:
        #Main processing pipeline: classify intent, extract params, validate policy
        intent = self.classify_intent(user_input)
        parameters = self.extract_parameters(user_input, intent)
        
        # Validate against policy if applicable
        policy_check = {"status": "PASSED", "message": "No policy validation required"}
        
        if intent == Intent.SEARCH_FLIGHT and "from_city" in parameters:
            class_pref = parameters.get("class_preference", "economy")
            is_valid, message = self.policy_validator.validate_flight_class(
                parameters.get("from_city", ""),
                parameters.get("to_city", ""),
                class_pref
            )
            policy_check = {"status": "PASSED" if is_valid else "FAILED", "message": message}
            
            # Also check booking timeline if date is provided
            if "date" in parameters:
                # Simple timeline check
                try:
                    travel_date = datetime.strptime(parameters["date"], "%Y-%m-%d")
                    days_advance = (travel_date - datetime.now()).days
                    
                    if days_advance < 2:
                        policy_check["warnings"] = "Policy warning: Last-minute booking requires manager approval"
                    elif days_advance < 7:
                        policy_check["warnings"] = "Policy notice: Booking less than 7 days in advance may have higher rates"
                except:
                    pass  # Skip timeline check if date parsing fails
        
        return {
            "intent": intent.value,
            "parameters": parameters,
            "policy_check": policy_check,
            "confidence": 0.95 if intent != Intent.UNKNOWN else 0.0,
            "original_input": user_input
        }

def demo_intent_recognition():
    """Demonstrate the intent recognition and action mapping system"""
    print("=" * 60)
    print("EBUDDY TRAVEL ASSISTANT - AGENT DEMO")
    print("=" * 60)
    
    # Initialize recognizer
    recognizer = IntentRecognizer()
    
    # Test cases
    test_inputs = [
        "Book a flight from Shanghai to Boston next Monday",
        "Book a flight from Boston to London next Month",
        "I need to fly from Beijing to Singapore tomorrow morning in business class",
        "Find me a hotel in New York for tonight",
        "Cancel my flight booking #ABC123",
        "What's the company policy on meal allowances?",
        "I want to book a 5-star hotel in Paris with a budget of $400",
        "Can I get a refund if I cancel my flight today?",
        "Can I get a refund if I cancel my flight tomorrow?",
        "Search flights from Shanghai to Beijing for January 15th"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n User Input {i}: \"{user_input}\"")
        
        result = recognizer.process_request(user_input)
        
        print(f"\n Recognition Result:")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.1%}")
        
        if result['parameters']:
            print(f"   Parameters:")
            for key, value in result['parameters'].items():
                print(f"      - {key}: {value}")
        
        print(f"   Policy Check: {result['policy_check']['status']}")
        if result['policy_check']['status'] != "PASSED":
            print(f"{result['policy_check']['message']}")
        if "warnings" in result['policy_check']:
            print(f"{result['policy_check']['warnings']}")
        
        print("-" * 60)
    
    print("\nAgent Demo Complete!")

if __name__ == "__main__":
    demo_intent_recognition()