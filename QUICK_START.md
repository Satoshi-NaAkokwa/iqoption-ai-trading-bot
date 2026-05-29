# Quick Start Guide - Agbara Integration

## 🚀 Get Started in 10 Minutes

### Prerequisites
- Python 3.11+
- Android Studio (for Android development)
- Docker (optional, for containerized deployment)
- kubectl (optional, for Kubernetes deployment)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/agbara-integration.git
cd agbara-integration
```

### 2. Install Python Server

```bash
cd agbara-integration-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. Install Android SDK

```bash
cd agbara-android-sdk

# Add to your app's build.gradle.kts:
implementation(project(":agbara-android-sdk"))
```

### 4. Get API Keys

You'll need:
- Agbara AI API key from https://agbara.ai/
- agbara.ai platform credentials

---

## 🚀 Running the Server

### Local Development

```bash
cd agbara-integration-server
source venv/bin/activate
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

Server will be available at:
- API: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws/chat`
- Docs: `http://localhost:8000/docs`

### Docker Deployment

```bash
cd agbara-integration-server
docker build -t agbara-integration-server:dev .
docker run -d -p 8000:8000 --env-file .env agbara-integration-server:dev
```

### Using the Deployment Script

```bash
cd agbara-integration-server

# Start locally
./deploy.sh local development start

# Start with Docker
./deploy.sh docker staging start

# Start with Kubernetes
./deploy.sh kubernetes production start
```

---

## 📱 Android Integration

### Step 1: Add Dependency

In your app's `build.gradle.kts`:

```kotlin
dependencies {
    implementation(project(":agbara-android-sdk"))
}
```

### Step 2: Initialize SDK

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var agbaraClient: AgbaraClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize Agbara SDK
        agbaraClient = AgbaraClient.create(
            context = this,
            apiKey = BuildConfig.AGBARA_API_KEY, // From local.properties or env vars
            options = {
                enableRemoteAI = true
                enableLocalAI = false // Set to true if you have local models
                enableCache = true
                enableOfflineQueue = true
                cacheMaxSize = 50
                logLevel = LogLevel.INFO
            }
        )

        // Set user ID
        agbaraClient.setUserId("user_${System.currentTimeMillis()}")
    }
}
```

### Step 3: Send a Message

```kotlin
// Simple message
val request = AgbaraAIRequest(
    userId = agbaraClient.getUserId(),
    message = "Hello, Agbara!"
)

agbaraClient.processMessage(request) { response ->
    when (response) {
        is AgbaraAIResponse.Success -> {
            val aiResponse = response.data
            textView.text = aiResponse.response
            println("Expert: ${aiResponse.expertUsed}")
        }
        is AgbaraAIResponse.Error -> {
            textView.text = "Error: ${response.error.message}"
        }
    }
}
```

### Step 4: Get Igbo Proverb

```kotlin
val proverb = agbaraClient.getIgboProverb()
textView.text = """
    ${proverb.text}
    
    ${proverb.translation}
    
    ${proverb.meaning}
""".trimIndent()
```

### Step 5: Ikorochat Integration

```kotlin
// Chat intelligence
val chatAI = IkoroChatIntelligence(agbaraClient)
chatAI.assistChat(
    userId = "user-123",
    message = "I want to buy this product",
    context = ChatContext(
        isMarketplace = true,
        productName = "Phone",
        productPrice = 500.0
    )
) { assistance ->
    when (assistance) {
        is ChatAssistance.Success -> {
            textView.text = assistance.suggestion
        }
        is ChatAssistance.Error -> {
            textView.text = "Error: ${assistance.error.message}"
        }
    }
}
```

---

## 🧪 Testing

### Python Server Tests

```bash
cd agbara-integration-server
source venv/bin/activate

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test
pytest tests/test_api_client.py -v
```

### Android SDK Tests

```bash
cd agbara-android-sdk

# Run unit tests
./gradlew test

# Run integration tests
./gradlew connectedAndroidTest

# Run with coverage
./gradlew testDebugUnitTest jacocoTestReport
```

---

## 📚 API Documentation

### REST API Endpoints

#### Health Check
```http
GET /health
```

#### Chat Completion
```http
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "model": "agbara",
  "messages": [
    {
      "role": "user",
      "content": "Hello, Agbara!"
    }
  ],
  "stream": false
}
```

#### Streaming Chat
```http
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "model": "agbara",
  "messages": [
    {
      "role": "user",
      "content": "Tell me a story"
    }
  ],
  "stream": true
}
```

### WebSocket Endpoint

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
    ws.send(JSON.stringify({
        model: 'agbara',
        messages: [
            { role: 'user', content: 'Hello!' }
        ],
        stream: true
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.choices && data.choices[0].delta.content) {
        console.log(data.choices[0].delta.content);
    }
};
```

---

## 🔧 Configuration

### Environment Variables (Python Server)

Create `.env` file:

```env
# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# API Keys
AGBARA_API_KEY=your_agbara_api_key
AGBARA_PLATFORM_KEY=your_platform_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Database
DATABASE_URL=postgresql://user:password@localhost/agbara

# Monitoring
MONITORING_ENABLED=true
METRICS_PORT=9090
```

### Android SDK Configuration

```kotlin
val config = AgbaraConfig(
    apiKey = "your_api_key",
    baseUrl = "http://localhost:8000",
    webSocketUrl = "ws://localhost:8000/ws/chat",
    enableLocalAI = false,
    enableRemoteAI = true,
    cacheEnabled = true,
    cacheMaxSize = 50,
    cacheTtlSeconds = 3600,
    requestTimeout = 30000,
    logLevel = LogLevel.INFO
)
```

---

## 🎯 Common Use Cases

### 1. Simple Chat Bot

```kotlin
fun handleUserMessage(message: String) {
    val request = AgbaraAIRequest(
        userId = getUserId(),
        message = message
    )
    
    agbaraClient.processMessage(request) { response ->
        when (response) {
            is AgbaraAIResponse.Success -> {
                displayMessage(response.data.response)
            }
            is AgbaraAIResponse.Error -> {
                displayError(response.error.message)
            }
        }
    }
}
```

### 2. Igbo Language Support

```kotlin
fun translateToIgbo(englishText: String) {
    val request = AgbaraAIRequest(
        userId = getUserId(),
        message = englishText,
        igboMode = true
    )
    
    agbaraClient.processMessage(request) { response ->
        when (response) {
            is AgbaraAIResponse.Success -> {
                displayTranslation(response.data.response)
            }
            is AgbaraAIResponse.Error -> {
                displayError(response.error.message)
            }
        }
    }
}
```

### 3. Marketplace Assistance

```kotlin
fun assistMarketplaceChat(userMessage: String, product: Product) {
    val marketAnalyzer = IkoroMarketAnalyzer(agbaraClient)
    
    lifecycleScope.launch {
        val analysis = marketAnalyzer.analyzeProduct(
            userId = getUserId(),
            product = ProductData(
                id = product.id,
                name = product.name,
                category = product.category,
                price = product.price,
                description = product.description,
                sellerName = product.sellerName,
                rating = product.rating,
                imageCount = product.images.size
            )
        )
        
        when (analysis) {
            is MarketAnalysis.Success -> {
                displayMarketAnalysis(analysis)
            }
            is MarketAnalysis.Error -> {
                displayError(analysis.error.message)
            }
        }
    }
}
```

### 4. Transaction Fraud Detection

```kotlin
fun checkTransactionRisk(transaction: Transaction) {
    val transactionAI = IkoroTransactionAI(agbaraClient)
    
    lifecycleScope.launch {
        val analysis = transactionAI.analyzeTransactionRisk(
            userId = getUserId(),
            transaction = TransactionData(
                id = transaction.id,
                amount = transaction.amount,
                senderId = transaction.senderId,
                recipientId = transaction.recipientId,
                timestamp = transaction.timestamp,
                location = transaction.location,
                deviceInfo = transaction.deviceInfo,
                ipAddress = transaction.ipAddress,
                description = transaction.description
            ),
            userProfile = getUserProfile()
        )
        
        when (analysis) {
            is FraudAnalysis.Success -> {
                when (analysis.riskLevel) {
                    RiskLevel.LOW -> proceedWithTransaction()
                    RiskLevel.MEDIUM -> requestAdditionalVerification()
                    RiskLevel.HIGH -> blockTransaction()
                }
            }
            is FraudAnalysis.Error -> {
                displayError(analysis.error.message)
            }
        }
    }
}
```

### 5. Offline Support

```kotlin
fun queueMessageForLater(message: String) {
    val request = AgbaraAIRequest(
        userId = getUserId(),
        message = message
    )
    
    val offlineManager = agbaraClient.getOfflineManager()
    offlineManager.queueMessage(request)
    
    Toast.makeText(this, "Message queued for when online", Toast.LENGTH_SHORT).show()
}
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Server won't start**
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
```

**Issue: API key errors**
```bash
# Verify .env file exists
ls -la .env

# Check environment variables
echo $AGBARA_API_KEY
```

**Issue: Android SDK build errors**
```bash
# Clean and rebuild
./gradlew clean
./gradlew build
```

**Issue: WebSocket connection fails**
```bash
# Check WebSocket endpoint
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: localhost:8000" \
  -H "Origin: http://localhost:8000" \
  http://localhost:8000/ws/chat
```

---

## 📊 Monitoring

### Server Metrics

```bash
# View metrics
curl http://localhost:8000/metrics

# Health check
curl http://localhost:8000/health

# Check logs
docker logs -f agbara-server
```

### Android SDK Metrics

```kotlin
// Get cache statistics
val cacheManager = agbaraClient.getCacheManager()
val cacheHitRate = cacheManager.getCacheHitRate()
val avgResponseTime = cacheManager.getAvgResponseTime()

// Get offline queue size
val offlineManager = agbaraClient.getOfflineManager()
val queueSize = offlineManager.getQueueSize()

// Get performance metrics
val perfMonitor = PerformanceMonitor()
val avgTime = perfMonitor.getAverageMetric("api_request")
```

---

## 🎓 Next Steps

1. **Read the full documentation** - See `agbara-integration-technical-specs.md`
2. **Run the demo app** - See `agbara-demo-app/`
3. **Explore examples** - Check the `examples/` directory
4. **Review the API** - Visit `http://localhost:8000/docs`
5. **Write tests** - Follow the test suite examples

---

## 🆘 Support

- Documentation: See `/docs` directory
- API Reference: `http://localhost:8000/docs`
- Issues: Create an issue on GitHub
- Email: support@agbara.ai

---

**Happy coding! 🚀**