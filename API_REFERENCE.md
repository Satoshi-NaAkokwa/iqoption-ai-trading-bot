# API Reference - Agbara Integration

## REST API Endpoints

### Base URL
```
Development: http://localhost:8000
Staging: https://staging.api.agbara.ai
Production: https://api.agbara.ai
```

---

## Authentication

All requests require an API key in the header:

```http
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Health Check

Check server health status.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-05-22T12:00:00Z",
  "version": "1.0.0"
}
```

---

### 2. Chat Completion

Generate AI chat completions.

```http
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
```

**Request Body:**
```json
{
  "model": "agbara",
  "messages": [
    {
      "role": "user",
      "content": "Hello, Agbara!"
    }
  ],
  "stream": false,
  "user": "user-123",
  "temperature": 0.7,
  "max_tokens": 1000,
  "expert": null,
  "expert_model": null,
  "context": {}
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Model name (`agbara`, `agbara-igbo`) |
| messages | array | Yes | Array of message objects |
| stream | boolean | No | Enable streaming (default: false) |
| user | string | No | User ID for tracking |
| temperature | float | No | Temperature (0.0-2.0, default: 0.7) |
| max_tokens | int | No | Max tokens to generate (default: 1000) |
| expert | string | No | Specific expert to use |
| expert_model | string | No | Specific expert model |
| context | object | No | Additional context |

**Response (non-streaming):**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699012345,
  "model": "agbara",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
  "expert_used": "mixed-experts",
  "processing_time": 0.123,
  "confidence": 0.95
}
```

**Response (streaming):**
```
data: {"choices":[{"delta":{"content":"Hello"},"finish_reason":null}]}
data: {"choices":[{"delta":{"content":"! How "},"finish_reason":null}]}
data: {"choices":[{"delta":{"content":"can I help you?"},"finish_reason":"stop"}]}
data: [DONE]
```

---

### 3. WebSocket Chat

Real-time streaming chat via WebSocket.

```http
WS /ws/chat
```

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

// Send message
ws.send(JSON.stringify({
  model: 'agbara',
  messages: [
    { role: 'user', content: 'Tell me a story' }
  ],
  stream: true,
  user: 'user-123'
}));

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.choices[0].delta.content);
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Close connection
ws.close();
```

---

### 4. Igbo Proverbs

Get random Igbo proverb.

```http
GET /igbo/proverb
```

**Response:**
```json
{
  "text": "Egbe bere ugo bere",
  "translation": "Let the kite perch and let the eagle perch",
  "meaning": "Everyone deserves their space and rights",
  "cultural_context": "Traditional Igbo philosophy of coexistence"
}
```

---

### 5. Igbo Translation

Translate between Igbo and English.

```http
POST /igbo/translate
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Ndeewo",
  "direction": "igbo_to_english"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| text | string | Yes | Text to translate |
| direction | string | Yes | `igbo_to_english` or `english_to_igbo` |

**Response:**
```json
{
  "original_text": "Ndeewo",
  "translated_text": "Hello, welcome",
  "direction": "igbo_to_english"
}
```

---

### 6. Cultural Concepts

Get explanation of Igbo cultural concepts.

```http
GET /igbo/concepts/{concept_name}
```

**Example:**
```http
GET /igbo/concepts/Chi
```

**Response:**
```json
{
  "name": "Chi",
  "explanation": "Chi is your personal spiritual guide and destiny in Igbo culture...",
  "examples": [
    "Chi gị mụ - Your Chi is great",
    "Chi na-echetegọ - My Chi is supporting me"
  ],
  "related_concepts": ["Ikenga", "Arụsị", "Ndichie"]
}
```

---

### 7. Ikorochat Chat Assistance

Get AI assistance for Ikorochat conversations.

```http
POST /ikoro/chat/assist
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "user-123",
  "message": "I want to buy this product",
  "context": {
    "type": "marketplace",
    "product_name": "Phone",
    "product_price": 500.0,
    "category": "Electronics"
  }
}
```

**Response:**
```json
{
  "suggestion": "You could ask about: 1) Warranty 2) Shipping 3) Return policy",
  "category": "MARKETPLACE",
  "confidence": 0.87,
  "suggestions": [
    "Ask about warranty",
    "Inquire about shipping",
    "Check return policy"
  ]
}
```

---

### 8. Ikorochat Market Analysis

Analyze products for Ikorochat marketplace.

```http
POST /ikoro/market/analyze
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "user-123",
  "product": {
    "id": "prod-1",
    "name": "Sample Product",
    "category": "Electronics",
    "price": 100.0,
    "description": "Great product",
    "seller_name": "Test Seller",
    "rating": 4.5,
    "image_count": 3
  },
  "market_data": {
    "avg_price": 80.0,
    "min_price": 50.0,
    "max_price": 120.0,
    "demand_level": "MEDIUM",
    "competition_level": "MEDIUM",
    "recent_sales": 100,
    "is_trending": false
  }
}
```

**Response:**
```json
{
  "product": {
    "id": "prod-1",
    "name": "Sample Product"
  },
  "price_recommendation": {
    "min_price": 75.0,
    "max_price": 115.0,
    "optimal_range": [85.0, 95.0],
    "reasoning": "Based on market data, price is slightly above average"
  },
  "demand_level": "MEDIUM",
  "category_rank": 5,
  "competition_level": "MEDIUM",
  "suggestions": [
    "Consider competitive pricing",
    "Highlight unique features",
    "Add more product images"
  ],
  "marketing_strategy": "Focus on product quality and customer reviews",
  "overall_score": 0.78,
  "confidence": 0.88
}
```

---

### 9. Transaction Fraud Detection

Analyze transaction for fraud risk.

```http
POST /ikoro/transaction/analyze
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "user-123",
  "transaction": {
    "id": "txn-1",
    "amount": 1000.0,
    "sender_id": "user1",
    "recipient_id": "user2",
    "timestamp": "2024-05-22T10:00:00Z",
    "location": "Lagos, Nigeria",
    "device_info": "Android 12, Pixel 6",
    "ip_address": "192.168.1.1",
    "description": "Product purchase"
  },
  "user_profile": {
    "account_age": 365,
    "total_transactions": 50,
    "trust_score": 95,
    "verification_level": "VERIFIED",
    "last_login": "2024-05-22T09:00:00Z",
    "login_location": "Lagos, Nigeria",
    "device_usage": "Consistent"
  }
}
```

**Response:**
```json
{
  "transaction_id": "txn-1",
  "risk_level": "LOW",
  "suspicious_patterns": [],
  "recommendation": "APPROVE",
  "confidence": 0.92,
  "reasoning": "Transaction appears legitimate based on user history",
  "verification_needed": false,
  "factors": [
    "Consistent location",
    "Verified user",
    "Typical transaction amount"
  ],
  "suggested_actions": []
}
```

---

### 10. Emergency Response

Get emergency response assistance.

```http
POST /ikoro/emergency/handle
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "user-123",
  "emergency_type": "MEDICAL",
  "location": {
    "address": "123 Main St, Lagos",
    "latitude": 6.5244,
    "longitude": 3.3792,
    "accuracy": 10.0,
    "timestamp": "2024-05-22T10:00:00Z"
  },
  "situation_description": "Someone is having chest pain"
}
```

**Response:**
```json
{
  "emergency_type": "MEDICAL",
  "immediate_actions": [
    "Call emergency services immediately",
    "Check if person is breathing",
    "Perform CPR if necessary"
  ],
  "first_aid_instructions": [
    "Keep person calm",
    "Loosen tight clothing",
    "Monitor vital signs"
  ],
  "contact_info": [
    "Emergency: 112",
    "Nearest Hospital: Lagos General Hospital"
  ],
  "nearby_resources": [
    "Lagos General Hospital - 2km",
    "Lagos State Medical Center - 3.5km"
  ],
  "safety_precautions": [
    "Stay calm",
    "Keep area clear",
    "Do not move person unnecessarily"
  ],
  "information_for_responders": "Chest pain, conscious, breathing",
  "confidence": 0.95
}
```

---

## Error Responses

All endpoints may return error responses.

**Error Response Format:**
```json
{
  "error": {
    "type": "VALIDATION_ERROR",
    "message": "Invalid request: missing required field",
    "details": {
      "field": "messages",
      "reason": "required"
    }
  }
}
```

**Error Types:**

| Error Type | HTTP Code | Description |
|------------|-----------|-------------|
| VALIDATION_ERROR | 400 | Invalid request data |
| AUTHENTICATION_FAILED | 401 | Invalid API key |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| SERVER_ERROR | 500 | Internal server error |
| NETWORK_ERROR | 503 | Network connectivity issue |

---

## Rate Limiting

Default rate limits:
- 100 requests per minute per API key
- 1000 requests per day per API key

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699012345
```

---

## SDK Reference

### Android SDK

```kotlin
// Initialize
val agbaraClient = AgbaraClient.create(
    context = this,
    apiKey = BuildConfig.AGBARA_API_KEY
)

// Send message
agbaraClient.processMessage(request) { response ->
    // Handle response
}

// Get Igbo proverb
val proverb = agbaraClient.getIgboProverb()

// Translate Igbo
val translation = agbaraClient.translateIgbo(text, direction)

// Explain concept
val concept = agbaraClient.explainCulturalConcept("Chi")
```

### Python Client

```python
from agbara_ai_client import AgbaraAIClient

# Initialize
client = AgbaraAIClient(api_key="your-api-key")

# Send message
response = client.process_message("Hello, Agbara!")

# Get proverb
proverb = client.get_proverb()

# Translate
translation = client.translate_igbo("Ndeewo", "igbo_to_english")
```

---

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

---

**For more information, see the full documentation.**