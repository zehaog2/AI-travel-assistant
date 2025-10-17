"""
Runs rag-> agent -> personalition
Show example (input + output)
"""
from rag_demo import TravelPolicyRAG
from agent_demo import IntentRecognizer
from personalization_demo import PersonalizationEngine
# Problem 1
def demo_rag():
    """Demo Problem 1: RAG System"""
    print("\n" + "="*60)
    print("PROBLEM 1: RAG DEMO")
    print("="*60)
    
    rag = TravelPolicyRAG()
    
    # Test queries (EDIT the following to test different queries)
    queries = [
        "Can I refund my ticket within 24 hours?",
        "What's the policy on business class flights?",
        "What are the Air China benefits?",
        "Is Air China better or United better?",
        "How long does it take to travel from Boston to Shanghai?",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = rag.query(query)
        print(f"Answer: {result['answer']}")
        print(f"Sources: {len(result['sources'])} documents")
# Problem 2
def demo_intent():
    """Demo Problem 2: Intent Recognition"""
    print("\n" + "="*60)
    print("PROBLEM 2: INTENT RECOGNITION DEMO")
    print("="*60)
    
    recognizer = IntentRecognizer()
    
    # Test inputs
    inputs = [
        "Book a flight from Shanghai to Boston next Monday",
        "I need a hotel in Singapore for tonight",
        "Cancel my flight booking #ABC123",
        "What's the company policy on meal allowances?",
        "Search for flights from Tokyo to London next month",
        "do nothing and chill",
    ]
    
    for user_input in inputs:
        print(f"\n Input: {user_input}")
        result = recognizer.process_request(user_input)
        print(f"Intent: {result['intent']}")
        print(f"Parameters: {result['parameters']}")
        print(f"Policy: {result['policy_check']['status']}")

#Problem 3
def demo_personalization():
    """Demo Problem 3: Personalization"""
    print("\n" + "="*60)
    print("PROBLEM 3: PERSONALIZATION DEMO")
    print("="*60)
    
    engine = PersonalizationEngine()
    query = "Find me flights from Shanghai to Boston"
    
    # Without personalization
    engine.load_user("guest_user")
    print(f"\n Generic Response:")
    print(engine.generate_response(query, with_profile=False))
    
    # With personalization
    engine.load_user("henry_guo")
    print(f"\n Personalized Response:")
    print(engine.generate_response(query, with_profile=True))
    
    # Show personalized prompt
    base_prompt = "You are a travel assistant."
    personalized_prompt = engine.build_personalized_prompt(base_prompt)
    print(f"\n Personalized System Prompt:")
    print(personalized_prompt)

def main():
    """Run all demos"""
    print("EBUDDY AI TRAVEL ASSISTANT - COMPLETE DEMO")
    demo_rag()
    input("\n\nPress Enter to continue...")
    demo_intent()
    input("\n\nPress Enter to continue...")
    demo_personalization()
    print("\n\n All demos completed!")

if __name__ == "__main__":
    main()