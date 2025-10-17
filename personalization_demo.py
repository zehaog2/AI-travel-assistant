"""
Manage user profiles and preferences
Create custom/general responses
Show difference in response quality
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class UserProfile:
    """User profile for personalization"""
    user_id: str
    name: str
    home_city: str
    preferred_airline: str
    budget_limit: float = 2000.0
    language: str = "en"
    seat_preference: str = "aisle"
    frequent_destinations: List[str] = field(default_factory=list)

class PersonalizationEngine:
    def __init__(self):
        self.profiles = self._load_sample_profiles()
        self.current_user: Optional[UserProfile] = None
    
    def _load_sample_profiles(self) -> Dict[str, UserProfile]:
        return {
            "henry_guo": UserProfile(
                user_id="henry_guo",
                name="Henry Guo",
                home_city="Shanghai",
                preferred_airline="Air China",
                budget_limit=2000.0,
                seat_preference="aisle",
                frequent_destinations=["Shanghai", "Boston"]
            ),
            "guest_user": UserProfile(
                user_id="guest_user",
                name="Guest",
                home_city="Unknown",
                preferred_airline="Any",
                budget_limit=1500.0
            )
        }
    
    def load_user(self, user_id: str) -> bool:
        """Load a user profile for personalization"""
        if user_id in self.profiles:
            self.current_user = self.profiles[user_id]
            return True
        self.current_user = self.profiles["guest_user"]
        return False
    
    def build_personalized_prompt(self, base_prompt: str) -> str:
        """Build a personalized system prompt based on user profile"""
        if not self.current_user or self.current_user.user_id == "guest_user":
            return base_prompt
        
        personalization = f"""
User Context:
- Name: {self.current_user.name}
- Preferred Airline: {self.current_user.preferred_airline}
- Budget: ${self.current_user.budget_limit}
- Home: {self.current_user.home_city}

Always prefer {self.current_user.preferred_airline} flights and keep under ${self.current_user.budget_limit} budget.
"""
        return base_prompt + personalization
    
    def generate_response(self, query: str, with_profile: bool = True) -> str:
        """Generate response with(out) personalization"""
        query_lower = query.lower()
        
        if "flight" in query_lower and "Boston" in query_lower:
            if with_profile and self.current_user and self.current_user.user_id != "guest_user":
                return (
                    f"Hi {self.current_user.name}, I found 2 Air China flights:\n"
                    f"1. CA66 - ¥1666 (within your ¥{self.current_user.budget_limit} budget)\n"
                    f"2. CA88 - ¥1888\n"
                    f"Both have {self.current_user.seat_preference} seats available."
                )
            else:
                return (
                    "I found 3 flights from Shanghai to Boston:\n"
                    "1. Flight NH11 - ¥2,100\n"
                    "2. Flight CA22 - ¥1,850\n"
                    "3. Flight MU33 - ¥1,950"
                )
        
        return "How can I help you with your travel needs?"