"""
RAG Demo for Ebuddy Travel Assistant
Simplified version that works without sentence-transformers
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re
from collections import Counter

@dataclass
class Document:
    """Represents a travel policy document"""
    id: str
    content: str
    metadata: Dict[str, str]

class TravelPolicyRAG:
    """RAG system for travel policies using keyword matching"""
    
    def __init__(self):
        self.documents: List[Document] = []
        self._load_documents()
    
    def _load_documents(self):
        """Load travel policy documents"""
        travel_policies = [
            {
                "id": "policy_01",
                "content": "Company Travel Policy: All employees must book economy class for domestic flights unless the flight duration exceeds 4 hours, in which case premium economy is permitted. Business class is only approved for international flights over 6 hours duration. First class requires executive approval.",
                "metadata": {"category": "flight_class", "region": "global"}
            },
            {
                "id": "policy_02", 
                "content": "Hotel Booking Policy: Standard room rates should not exceed $200 USD per night for domestic travel and $300 USD for international travel. Employees can book 4-star hotels or below. 5-star hotels require manager approval. Cancellations must be made 24 hours in advance to avoid penalties.",
                "metadata": {"category": "hotel", "region": "global"}
            },
            {
                "id": "policy_03",
                "content": "Ticket Change and Refund Policy: Flight tickets can be refunded within 24 hours of booking for a full refund. After 24 hours, refunds incur a $200 fee for domestic and $400 for international flights. Changes can be made up to 2 hours before departure with applicable airline fees.",
                "metadata": {"category": "changes", "vendor": "all"}
            },
            {
                "id": "policy_04",
                "content": "Meal Allowance: Daily meal allowance is $50 for domestic travel and $75 for international travel. Receipts required for all expenses over $25. Alcohol is not reimbursable. Team dinners with clients can exceed limits with pre-approval.",
                "metadata": {"category": "meals", "region": "global"}
            },
            {
                "id": "policy_05",
                "content": "Ground Transportation: Use company-preferred vendors when available. Taxi and rideshare allowed for trips under $50. Car rentals permitted for trips over 3 days or when more economical. Luxury vehicles are not reimbursable.",
                "metadata": {"category": "transport", "region": "global"}
            },
            {
                "id": "policy_06",
                "content": "Airline Specific - Air China: Preferred carrier for China domestic routes. Corporate discount code: EBUDDY2025. Includes priority check-in and 2 free checked bags. Changes allowed up to 6 hours before departure without fee.",
                "metadata": {"category": "airline", "vendor": "Air China"}
            },
            {
                "id": "policy_07",
                "content": "Travel Insurance: Mandatory for all international trips. Coverage includes medical emergencies, trip cancellation, and lost luggage. Premium is company-paid. Claims must be filed within 30 days of incident.",
                "metadata": {"category": "insurance", "region": "international"}
            },
            {
                "id": "policy_08",
                "content": "Booking Timeline: All travel must be booked at least 7 days in advance for best rates. Last-minute bookings (less than 48 hours) require manager approval and justification. Use company travel portal for all bookings to ensure policy compliance.",
                "metadata": {"category": "booking", "region": "global"}
            },
            {
                "id": "policy_09",
                "content": "Per Diem Rates: Shanghai: 500 CNY per day, Beijing: 450 CNY per day, Tokyo: 8000 JPY per day, Singapore: 150 SGD per day. Rates include meals and incidentals. Unused per diem cannot be claimed. Weekend travel includes 50% per diem unless working.",
                "metadata": {"category": "per_diem", "region": "asia"}
            },
            {
                "id": "policy_10",
                "content": "Visa and Documentation: Company covers visa fees for business travel. Applications must be submitted 30 days before travel. Passport must be valid for 6 months beyond travel dates. Keep copies of all travel documents in company portal.",
                "metadata": {"category": "visa", "region": "international"}
            }
        ]
        
        # Create Document objects
        for policy in travel_policies:
            doc = Document(
                id=policy["id"],
                content=policy["content"],
                metadata=policy["metadata"]
            )
            self.documents.append(doc)
    
    def _calculate_similarity(self, query: str, document: str) -> float:
        """
        keyword-based similarity scoring
        Returns a score between 0 and 1
        """
        # Convert query to lowercase
        query_lower = query.lower()
        doc_lower = document.lower()
        
        # Extract query ketwords
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        doc_words = set(re.findall(r'\b\w+\b', doc_lower))
        
        # Remove common words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 
                      'was', 'were', 'in', 'of', 'to', 'for', 'with', 'that', 'it', 
                      'can', 'i', 'what', 'when', 'where', 'how', 'why', 'my', 'our'}
        query_words = query_words - stop_words
        
        if not query_words:
            return 0.0
        
        # Count matching words
        matches = 0
        for word in query_words:
            if word in doc_lower:
                matches += 1
                # Give extra weight to exact phrase matches
                if f" {word} " in f" {doc_lower} ":
                    matches += 0.5
        
        # Calculate similarity score
        score = matches / len(query_words)
        
        # Boost score for specific keyword matches
        boost_terms = {
            'refund': ['refund', '24 hours', 'cancel'],
            'business class': ['business class', 'economy', 'flight class'],
            'hotel': ['hotel', 'accommodation', 'room rate'],
            'meal': ['meal', 'allowance', 'per diem'],
            'air china': ['air china', 'preferred carrier'],
            'visa': ['visa', 'passport', 'documentation'],
            'insurance': ['insurance', 'coverage', 'emergency']
        }
        
        for key, terms in boost_terms.items():
            if any(term in query_lower for term in terms):
                if any(term in doc_lower for term in terms):
                    score *= 1.5  # Boost relevant documents
        
        return min(score, 1.0)  # Cap at 1.0
    
    def retrieve(self, query: str, top_k: int = 3, filters: Optional[Dict[str, str]] = None) -> List[Document]:
        """
        Retrieve most relevant documents for a query using keyword matching
        """
        # Filter documents if needed
        candidate_docs = self.documents
        if filters:
            candidate_docs = [
                doc for doc in self.documents
                if all(doc.metadata.get(k) == v for k, v in filters.items())
            ]
        
        if not candidate_docs:
            return []
        
        # Calculate similarities
        doc_scores = []
        for doc in candidate_docs:
            score = self._calculate_similarity(query, doc.content)
            doc_scores.append((doc, score))
        
        # Sort by score and get top-k with score >0.2
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in doc_scores[:top_k] if score > 0.2]
    
    def generate_answer(self, query: str, context_docs: List[Document]) -> str:
        if not context_docs:
            return "No policy about that. Please contact support."
        # Build context from retrieved documents
        context = "\n\n".join([f"Policy {i+1}: {doc.content}" for i, doc in enumerate(context_docs)])
        # Simulate LLM response (rule-based for demo)
        response = self._simulate_llm_response(query, context, context_docs)
        return response
    
    def _simulate_llm_response(self, query: str, context: str, context_docs: List[Document]) -> str:
        query_lower = query.lower()
        
        # Pattern matching for common questions
        if "refund" in query_lower and "24" in query_lower:
            return "Yes, according to company policy, flight tickets can be refunded within 24 hours of booking for a full refund. After 24 hours, refunds incur a $200 fee for domestic flights and $400 for international flights."
        
        elif "business class" in query_lower:
            return "According to company policy, business class is only approved for international flights over 6 hours duration. For domestic flights, you must book economy class unless the flight exceeds 4 hours, in which case premium economy is permitted."
        
        elif "hotel" in query_lower and ("limit" in query_lower or "maximum" in query_lower or "policy" in query_lower):
            return "The company hotel policy limits are $200 USD per night for domestic travel and $300 USD for international travel. You can book up to 4-star hotels without approval. 5-star hotels require manager approval."
        
        elif "meal" in query_lower or "food" in query_lower or "allowance" in query_lower:
            return "The daily meal allowance is $50 for domestic travel and $75 for international travel. Remember to keep receipts for all expenses over $25, and note that alcohol is not reimbursable."
        
        elif "air china" in query_lower:
            return "Air China is our preferred carrier for China domestic routes. Use corporate code EBUDDY2025 for discounts, priority check-in, and 2 free checked bags. You can make changes up to 6 hours before departure without fees."
        
        elif "insurance" in query_lower:
            return "Travel insurance is mandatory for all international trips. It covers medical emergencies, trip cancellation, and lost luggage. The premium is company-paid, and claims must be filed within 30 days of any incident."
        
        elif "visa" in query_lower or "passport" in query_lower:
            return "The company covers visa fees for business travel. Applications must be submitted 30 days before travel. Your passport must be valid for 6 months beyond travel dates. Keep copies of all documents in the company portal."
        
        else:
            # Return first part of context as generic answer
            first_doc = context_docs[0].content if context_docs else ""
            return f"Based on company travel policies: {first_doc[:300]}..."
    
    def query(self, question: str, filters: Optional[Dict[str, str]] = None) -> Dict:
        """RAG pipeline:
        Input:
            question: User's question
            filters: Optional metadata filters
        Output:
            Dict with answer and retrieved documents
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(question, top_k=3, filters=filters)
        
        # Generate answer
        answer = self.generate_answer(question, retrieved_docs)
        
        return {
            "question": question,
            "answer": answer,
            "sources": [{"id": doc.id, "content": doc.content[:200] + "..."} for doc in retrieved_docs],
            "filters_applied": filters
        }

def demo_rag_system():
    """Demonstrate the RAG system with example queries"""
    print("=" * 60)
    print("EBUDDY TRAVEL ASSISTANT - RAG DEMO (Simplified Version)")
    print("=" * 60)
    
    # Initialize RAG system
    rag = TravelPolicyRAG()
    
    # Test queries
    test_queries = [
        {
            "question": "Can I refund my ticket within 24 hours?",
            "filters": None
        },
        {
            "question": "What's the minimum hotel rate I can book for a trip to Boston?",
            "filters": None
        },
        {
            "question": "Can I book business class for my flight from Shanghai to Beijing?",
            "filters": None
        },
        {
            "question": "What are the benefits with Air China?",
            "filters": {"vendor": "Air China"}
        },
        {
            "question": "What's the meal allowance for international travel?",
            "filters": None
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n Query {i}: {test['question']}")
        if test['filters']:
            print(f"   Filters: {test['filters']}")
        
        result = rag.query(test['question'], test['filters'])
        
        print(f"\n Answer: {result['answer']}")
        print(f"\n Sources Used: {len(result['sources'])} documents")
        for source in result['sources']:
            print(f"   - {source['id']}: {source['content'][:100]}...")
        print("-" * 60)
    
    print("\n RAG Demo Complete!")
    print("\n Key Insights:")
    print("• Retrieval ensures answers are grounded in actual policies")
    print("• Metadata filtering enables targeted searches (e.g., vendor-specific)")
    print("• Even simple keyword matching can provide good retrieval results")

if __name__ == "__main__":
    demo_rag_system()