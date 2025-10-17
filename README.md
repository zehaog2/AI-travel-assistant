# Ebuddy-travel-assistant

## Quick Start
```bash
python main.py
```
The demo runs through the problems sequentially:
- **Problem 1**: RAG system answering policy questions
- **Problem 2**: Intent recognition and parameter extraction
- **Problem 3**: Personalized vs generic responses
---

## Problem 1: RAG System
### Approach
I built a Retrieval-Augmented Generation system that answers travel policy questions by retrieving relevant documents and using them to generate accurate responses.

**Key Components:**
- **Document Store**: 10 sample travel policy documents
- **Retrieval Method**: Keyword-based similarity scoring with pattern matching
- **Answer Generation**: Rule-based response system that simulates LLM behavior

### How Document Retrieval Works

Instead of using vector embeddings (which would require `sentence-transformers`), I implemented a **keyword-based retrieval system** that:

1. **Tokenizes** the query and documents into words
2. **Removes stop words
3. **Counts matches** between query keywords and document content
4. **Applies boosting** for domain-specific terms (e.g., "refund", "business class", "Air China")
5. **Calculates similarity score** as: `matches / total_query_keywords`
6. **Returns top-k documents** with scores above 0.2 threshold

### Why Retrieval Improves Answer Quality

**Without RAG:**
- May hallucinate
- Cannot cite sources
- Outdated information if policies change
- No traceability for compliance

**With RAG:**
- Answers based on actual policy documents
- Can show which policies support the answer
- Easy to update document store without retraining
- Compliance teams can verify source documents
- LLM works with provided context, not memory

### Bonus: Metadata Filtering
Documents include metadata fields (`category`, `region`, `vendor`) enabling filtered searches:

```python
# Find only Air China policies
result = rag.query("What are the benefits?", filters={"vendor": "Air China"})
```

This prevents irrelevant documents from cluttering the context and improves precision.

---

## Problem 2: Intent Recognition

### Approach

I built an agent system that maps natural language to structured actions, enabling the AI to trigger backend operations.

**Supported Intents:**
1. `SearchFlight` - Find available flights
2. `BookHotel` - Reserve accommodations
3. `CancelFlight` - Cancel existing bookings
4. `CheckPolicy` - Answer policy questions
5. `Unknown` - Fallback for unclear requests

### How It Works

**Intent Classification:**
- Pattern matching using regex for common phrasings
- Keyword scoring (e.g., "hotel", "accommodation" → BookHotel)
- Returns intent with highest confidence score

**Parameter Extraction:**
- Intent-specific extractors parse relevant details
- `SearchFlight`: extracts cities, dates, times, class preferences
- `BookHotel`: extracts city, check-in/out dates, hotel class, budget
- `CancelFlight`: extracts booking IDs and flight numbers
- `CheckPolicy`: identifies policy topic

### Bonus: Policy Validation

Before executing actions, the system validates against company policies:

- Checks if business/first class is allowed based on route
- Warns if booking less than 7 days in advance
- Prevents policy violations before they happen

---

## Problem 3: Personalization

### Approach

User profiles enable personalized recommendations that respect individual preferences and constraints.

**User Profile Fields:**
- `user_id`: Unique identifier
- `name`: For friendly greetings
- `home_city`: Default departure location
- `preferred_airline`: Favorite carrier
- `budget_limit`: Maximum spending constraint
- `language`: Communication preference
- `seat_preference`: Aisle vs window
- `frequent_destinations`: Common routes

### How Personalization Works

**1. Profile Integration in Prompts:**

The `build_personalized_prompt()` method augments system prompts with user context:

```python
User Context:
- Name: Henry Guo
- Preferred Airline: Air China
- Budget: $2000
- Home: Shanghai

Always prefer Air China flights and keep under $2000 budget."""
```

**2. Response Comparison:**

**Generic Response (Guest User):**
```
I found 3 flights from Shanghai to Boston:
1. Flight NH11 - ¥2,100
2. Flight CA22 - ¥1,850
3. Flight MU33 - ¥1,950
```

**Personalized Response (Henry Guo):**
```
Hi Henry Guo, I found 2 Air China flights:
1. CA66 - ¥1666 (within your ¥2000 budget)
2. CA88 - ¥1888
Both have aisle seats available.
```

**Key Differences:**
- Uses user's name for rapport
- Filters to preferred airline only
- Highlights budget compliance
- Mentions seat preference
- More concise (shows only relevant options)

### What User Data Helps Personalization

**High-Value Data:**
- **Preferences** (airline, seat, class)
- **Constraints** (budget, home city)
- **History** (frequent destinations)
- **Context** (language, timezone)
---

## Architecture & Design Decisions

### Pro & Cons
- doesn't catch synonyms well
- Requires exact keyword matches
- Zero dependencies, runs anywhere
- Fast and predictable
- Easy to debug and explain
- Good enough for demo purposes

### Why Rule-Based LLM Simulation?

The `_simulate_llm_response()` method uses pattern matching instead of calling actual LLMs (GPT-4, Claude, etc.).

**Reasons:**
- No API keys needed to run the demo
- Deterministic outputs for testing
- Zero latency and cost
- Shows RAG architecture clearly

**For production**: Replace with OpenAI API, Anthropic Claude API, or local models like Llama.

---

## Project Structure
```
ebuddy-travel-assistant/
│
├── main.py                    # Runs all three demos
├── rag_demo.py               # Problem 1: RAG system
├── agent_demo.py             # Problem 2: Intent recognition
├── personalization_demo.py   # Problem 3: User personalization
└── README.md                 # This file
```
---


