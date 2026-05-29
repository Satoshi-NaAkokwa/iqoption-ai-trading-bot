# Agbara Android SDK - Developer Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Features](#core-features)
4. [Advanced Usage](#advanced-usage)
5. [Ikorochat Integration](#ikorochat-integration)
6. [Testing](#testing)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Step 1: Add SDK Dependency

In your app's `settings.gradle.kts`:
```kotlin
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

include(":agbara-android-sdk")
```

In your app's `build.gradle.kts`:
```kotlin
dependencies {
    implementation(project(":agbara-android-sdk"))
}
```

### Step 2: Configure API Key

Add to `local.properties`:
```properties
AGBARA_API_KEY=your_api_key_here
```

In `build.gradle.kts`:
```kotlin
android {
    defaultConfig {
        buildConfigField("String", "AGBARA_API_KEY", "\"${properties["AGBARA_API_KEY"]}\"")
    }
}
```

---

## Quick Start

### Initialize the SDK

```kotlin
import com.agbara.sdk.AgbaraClient
import com.agbara.sdk.config.LogLevel

class MyApplication : Application() {
    lateinit var agbaraClient: AgbaraClient

    override fun onCreate() {
        super.onCreate()
        
        agbaraClient = AgbaraClient.create(
            context = this,
            apiKey = BuildConfig.AGBARA_API_KEY,
            options = {
                enableRemoteAI = true
                enableLocalAI = false
                enableCache = true
                enableOfflineQueue = true
                cacheMaxSize = 50
                logLevel = LogLevel.INFO
            }
        )
    }
}
```

### Send Your First Message

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var agbaraClient: AgbaraClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        agbaraClient = (application as MyApplication).agbaraClient
        agbaraClient.setUserId("user_${System.currentTimeMillis()}")
        
        sendMessage("Hello, Agbara!")
    }

    private fun sendMessage(message: String) {
        val request = AgbaraAIRequest(
            userId = agbaraClient.getUserId(),
            message = message
        )

        agbaraClient.processMessage(request) { response ->
            when (response) {
                is AgbaraAIResponse.Success -> {
                    textView.text = response.data.response
                }
                is AgbaraAIResponse.Error -> {
                    textView.text = "Error: ${response.error.message}"
                }
            }
        }
    }
}
```

---

## Core Features

### 1. Basic Chat

```kotlin
val request = AgbaraAIRequest(
    userId = userId,
    message = "What's the weather like today?",
    temperature = 0.7f,
    maxTokens = 500
)

agbaraClient.processMessage(request) { response ->
    // Handle response
}
```

### 2. Streaming Responses

```kotlin
val request = AgbaraAIRequest(
    userId = userId,
    message = "Tell me a long story",
    streaming = true
)

var fullResponse = ""
agbaraClient.processMessageStream(request) { chunk ->
    when (chunk) {
        is StreamChunk.Progress -> {
            fullResponse += chunk.text
            textView.text = fullResponse
        }
        is StreamChunk.Complete -> {
            textView.text = "Complete!\n$fullResponse"
        }
        is StreamChunk.Error -> {
            textView.text = "Error: ${chunk.message}"
        }
    }
}
```

### 3. Igbo Language Support

```kotlin
// Get Igbo proverb
val proverb = agbaraClient.getIgboProverb()
textView.text = "${proverb.text}\n${proverb.translation}"

// Translate Igbo
val translation = agbaraClient.translateIgbo(
    text = "Ndeewo",
    direction = TranslationDirection.IGBO_TO_ENGLISH
)
textView.text = translation.text

// Explain cultural concept
val concept = agbaraClient.explainCulturalConcept("Chi")
textView.text = """
    Concept: ${concept.name}
    Meaning: ${concept.explanation}
    Examples: ${concept.examples.joinToString("\n")}
""".trimIndent()
```

### 4. Cache Management

```kotlin
val cacheManager = agbaraClient.getCacheManager()

// Get cache statistics
val cacheHitRate = cacheManager.getCacheHitRate()
val cacheSize = cacheManager.getSize()
val avgResponseTime = cacheManager.getAvgResponseTime()

Log.d("Agbara", "Cache hit rate: ${cacheHitRate * 100}%")
Log.d("Agbara", "Cache size: $cacheSize/${cacheManager.getCapacity()}")

// Clear cache
cacheManager.clear()
```

### 5. Offline Queueing

```kotlin
val offlineManager = agbaraClient.getOfflineManager()

// Queue message when offline
val request = AgbaraAIRequest(
    userId = userId,
    message = "This will be sent when online"
)
offlineManager.queueMessage(request)

// Check queue size
val queueSize = offlineManager.getQueueSize()
Log.d("Agbara", "Queued messages: $queueSize")

// Sync when online (automatic on reconnection)
val result = offlineManager.sync(agbaraClient.getApiClient())
when (result) {
    is SyncResult.Success -> {
        Log.d("Agbara", "Synced ${result.messagesSynced} messages")
    }
    is SyncResult.Error -> {
        Log.e("Agbara", "Sync failed: ${result.error.message}")
    }
}
```

---

## Advanced Usage

### Custom Configuration

```kotlin
val config = AgbaraConfig(
    apiKey = "your-api-key",
    baseUrl = "https://api.agbara.ai",
    webSocketUrl = "wss://api.agbara.ai/ws/chat",
    enableLocalAI = false,
    enableRemoteAI = true,
    cacheEnabled = true,
    cacheMaxSize = 100,
    cacheTtlSeconds = 3600,
    requestTimeout = 30000,
    logLevel = LogLevel.DEBUG,
    maxConcurrentRequests = 10
)

val agbaraClient = AgbaraClient.create(context, config.apiKey) {
    // Apply custom configuration
}
```

### Custom Error Handling

```kotlin
agbaraClient.processMessage(request) { response ->
    when (response) {
        is AgbaraAIResponse.Success -> {
            handleSuccess(response.data)
        }
        is AgbaraAIResponse.Error -> {
            when (response.error.type) {
                ErrorType.NETWORK_ERROR -> {
                    showNetworkError()
                    // Retry automatically
                    retryMessage(request)
                }
                ErrorType.AUTHENTICATION_FAILED -> {
                    showAuthError()
                    // Re-authenticate
                    reauthenticate()
                }
                ErrorType.VALIDATION_ERROR -> {
                    showValidationError(response.error.message)
                }
                else -> {
                    showGenericError(response.error.message)
                }
            }
        }
    }
}
```

### Performance Monitoring

```kotlin
val perfMonitor = PerformanceMonitor()

// Record API request time
val startTime = System.currentTimeMillis()
agbaraClient.processMessage(request) { response ->
    val duration = System.currentTimeMillis() - startTime
    perfMonitor.recordMetric("api_request", duration)
    
    val avgTime = perfMonitor.getAverageMetric("api_request")
    val p95Time = perfMonitor.getP95Metric("api_request")
    
    Log.d("Performance", "Avg: ${avgTime}ms, P95: ${p95Time}ms")
}
```

### Custom Logging

```kotlin
AgbaraLogger.enable(true)
AgbaraLogger.setMinLevel(LogLevel.DEBUG)

AgbaraLogger.debug("MyApp", "Debug message")
AgbaraLogger.info("MyApp", "Info message")
AgbaraLogger.warn("MyApp", "Warning message")
AgbaraLogger.error("MyApp", "Error message", exception)
```

---

## Ikorochat Integration

### Chat Intelligence

```kotlin
val chatAI = IkoroChatIntelligence(agbaraClient)

chatAI.assistChat(
    userId = userId,
    message = "I want to buy this product",
    context = ChatContext(
        type = ChatType.MARKETPLACE,
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

### Market Analysis

```kotlin
val marketAnalyzer = IkoroMarketAnalyzer(agbaraClient)

lifecycleScope.launch {
    val analysis = marketAnalyzer.analyzeProduct(
        userId = userId,
        product = ProductData(
            id = "prod-1",
            name = "Sample Product",
            category = "Electronics",
            price = 100.0,
            description = "Great product",
            sellerName = "Test Seller",
            rating = 4.5f,
            imageCount = 3
        ),
        marketData = MarketData(
            avgPrice = 80.0,
            minPrice = 50.0,
            maxPrice = 120.0
        )
    )
    
    when (analysis) {
        is MarketAnalysis.Success -> {
            displayPriceRecommendations(analysis.priceRecommendation)
            displaySuggestions(analysis.suggestions)
        }
        is MarketAnalysis.Error -> {
            showErrorMessage(analysis.error.message)
        }
    }
}
```

### Transaction Fraud Detection

```kotlin
val transactionAI = IkoroTransactionAI(agbaraClient)

lifecycleScope.launch {
    val analysis = transactionAI.analyzeTransactionRisk(
        userId = userId,
        transaction = TransactionData(
            id = "txn-1",
            amount = 1000.0,
            senderId = "user1",
            recipientId = "user2",
            timestamp = "2024-05-22T10:00:00Z",
            location = "Lagos, Nigeria",
            deviceInfo = "Android 12",
            ipAddress = "192.168.1.1",
            description = "Product purchase"
        ),
        userProfile = UserProfile(
            accountAge = 365,
            totalTransactions = 50,
            trustScore = 95,
            verificationLevel = "VERIFIED",
            lastLogin = "2024-05-22T09:00:00Z",
            loginLocation = "Lagos, Nigeria",
            deviceUsage = "Consistent"
        )
    )
    
    when (analysis) {
        is FraudAnalysis.Success -> {
            when (analysis.riskLevel) {
                RiskLevel.LOW -> approveTransaction()
                RiskLevel.MEDIUM -> requireAdditionalVerification()
                RiskLevel.HIGH -> blockTransaction()
            }
        }
        is FraudAnalysis.Error -> {
            showErrorMessage(analysis.error.message)
        }
    }
}
```

---

## Testing

### Unit Tests

```kotlin
class AgbaraClientTest {
    @Test
    fun testInitialization() {
        val client = AgbaraClient.create(
            context = testContext,
            apiKey = "test-key"
        )
        assertNotNull(client)
    }

    @Test
    fun testProcessMessage() = runTest {
        val client = createTestClient()
        val request = AgbaraAIRequest(
            userId = "test-user",
            message = "Hello"
        )

        client.processMessage(request) { response ->
            assertTrue(response is AgbaraAIResponse.Success)
        }
    }
}
```

### Mocking for Tests

```kotlin
fun createMockClient(): AgbaraClient {
    val mockApiClient = mockk<ApiClient>()
    
    coEvery { mockApiClient.process(any()) } returns AgbaraAIResponseData(
        response = "Mock response",
        expertUsed = "mock-expert",
        processingTime = 0.5,
        confidence = 1.0f
    )
    
    return AgbaraClient.create(testContext, "test-key") {
        enableRemoteAI = false
        enableLocalAI = false
    }
}
```

---

## Best Practices

### 1. Initialize Once

```kotlin
// ✅ Good - Initialize in Application class
class MyApplication : Application() {
    lateinit var agbaraClient: AgbaraClient
    
    override fun onCreate() {
        agbaraClient = AgbaraClient.create(this, BuildConfig.AGBARA_API_KEY)
    }
}

// ❌ Bad - Initialize in every Activity
class MainActivity : AppCompatActivity() {
    private val agbaraClient = AgbaraClient.create(this, BuildConfig.AGBARA_API_KEY)
}
```

### 2. Use Kotlin Coroutines

```kotlin
// ✅ Good - Use coroutines
lifecycleScope.launch {
    val response = withContext(Dispatchers.IO) {
        agbaraClient.processMessage(request)
    }
    textView.text = response.data.response
}

// ❌ Bad - Block main thread
val response = agbaraClient.processMessage(request)  // Blocking!
textView.text = response.data.response
```

### 3. Handle Errors Gracefully

```kotlin
// ✅ Good - Comprehensive error handling
agbaraClient.processMessage(request) { response ->
    when (response) {
        is AgbaraAIResponse.Success -> {
            handleSuccess(response.data)
        }
        is AgbaraAIResponse.Error -> {
            when (response.error.type) {
                ErrorType.NETWORK_ERROR -> handleNetworkError()
                ErrorType.AUTHENTICATION_FAILED -> handleAuthError()
                else -> handleGenericError()
            }
        }
    }
}
```

### 4. Enable Caching

```kotlin
// ✅ Good - Enable caching for better performance
agbaraClient = AgbaraClient.create(context, apiKey) {
    enableCache = true
    cacheMaxSize = 50
    cacheTtlSeconds = 3600
}
```

### 5. Enable Offline Support

```kotlin
// ✅ Good - Enable offline queueing
agbaraClient = AgbaraClient.create(context, apiKey) {
    enableOfflineQueue = true
}

// Sync when back online
override fun onNetworkAvailable() {
    lifecycleScope.launch {
        val result = offlineManager.sync(apiClient)
        // Handle sync result
    }
}
```

---

## Troubleshooting

### Common Issues

**Issue: SDK not initialized**
```kotlin
// Solution: Initialize in Application class
class MyApplication : Application() {
    lateinit var agbaraClient: AgbaraClient
    
    override fun onCreate() {
        agbaraClient = AgbaraClient.create(this, BuildConfig.AGBARA_API_KEY)
    }
}
```

**Issue: Network errors**
```kotlin
// Solution: Check network status and implement retry logic
val networkConnectivity = NetworkConnectivity(context)
if (!networkConnectivity.isNetworkAvailable()) {
    // Queue message for later
    offlineManager.queueMessage(request)
} else {
    // Send immediately
    agbaraClient.processMessage(request)
}
```

**Issue: Slow responses**
```kotlin
// Solution: Enable caching and use streaming
agbaraClient = AgbaraClient.create(context, apiKey) {
    enableCache = true
}

val request = AgbaraAIRequest(
    userId = userId,
    message = message,
    streaming = true
)
agbaraClient.processMessageStream(request) { chunk ->
    // Display chunks as they arrive
}
```

---

**For more information, see the API Reference and Quick Start guides.**