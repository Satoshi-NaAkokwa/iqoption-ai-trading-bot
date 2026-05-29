# Agbara Android SDK

**Version:** 1.0.0  
**License:** Apache 2.0  
**Platform:** Android 8.0+ (API 26+)  

## Overview

Agbara Android SDK provides seamless integration of Agbara AI capabilities into Android applications, specifically designed for Ikorochat-android mesh messaging platform.

## Features

- ✅ **Local AI Inference** - On-device processing with quantized models
- ✅ **Remote API Integration** - Cloud-based AI when internet available
- ✅ **Offline-First Architecture** - Full functionality without internet
- ✅ **Intelligent Caching** - Reduce API calls and improve performance
- ✅ **Igbo Language Support** - Proverbs, translations, cultural concepts
- ✅ **Real-time Chat** - WebSocket-based streaming responses
- ✅ **Privacy-Preserving** - End-to-end encryption, local processing
- ✅ **Battery Optimized** - < 5% battery usage per hour
- ✅ **Performance Optimized** - < 2s local response, < 500ms remote

## Installation

### Gradle

```kotlin
dependencies {
    implementation("com.agbara:sdk:1.0.0")
}
```

### Maven

```xml
<dependency>
    <groupId>com.agbara</groupId>
    <artifactId>sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Quick Start

### Initialization

```kotlin
import com.agbara.sdk.AgbaraClient

// Initialize client
val agbaraClient = AgbaraClient.create(
    context = applicationContext,
    apiKey = "your-api-key-here",
    options = {
        enableLocalAI = true
        enableRemoteAI = true
        igboMode = false
        cacheEnabled = true
    }
)
```

### Basic Usage

```kotlin
// Send a message
val request = AgbaraAIRequest(
    userId = "user123",
    message = "Hello, Agbara!",
    igboMode = false
)

agbaraClient.processMessage(request) { response ->
    when (response) {
        is AgbaraAIResponse.Success -> {
            println("Response: ${response.data.response}")
            println("Expert used: ${response.data.expertUsed}")
            println("Confidence: ${response.data.confidence}")
        }
        is AgbaraAIResponse.Error -> {
            println("Error: ${response.error.message}")
        }
    }
}
```

### Real-time Chat

```kotlin
// Connect WebSocket
agbaraClient.connectWebSocket(userId = "user123") { message ->
    when (message) {
        is WebSocketMessage.Response -> {
            println("Response: ${message.data.response}")
        }
        is WebSocketMessage.Connected -> {
            println("Connected as: ${message.userId}")
        }
        is WebSocketMessage.Disconnected -> {
            println("Disconnected: ${message.reason}")
        }
    }
}

// Send message via WebSocket
agbaraClient.sendWebSocketMessage(
    AgbaraAIRequest(
        userId = "user123",
        message = "Tell me about Igbo culture"
    )
)
```

### Igbo Language

```kotlin
// Get Igbo proverb
val proverb = agbaraClient.getIgboProverb()
println("Proverb: ${proverb.text}")
println("Translation: ${proverb.translation}")

// Translate text
val translation = agbaraClient.translateIgbo(
    text = "Kedu ihe bụ chi?",
    direction = TranslationDirection.IGBO_TO_ENGLISH
)
println("Translation: ${translation.text}")

// Explain cultural concept
val concept = agbaraClient.explainCulturalConcept("Chi")
println("Concept: ${concept.name}")
println("Explanation: ${concept.explanation}")
```

### Offline Mode

```kotlin
// Queue message for offline processing
val offlineManager = agbaraClient.getOfflineManager()
offlineManager.queueMessage(
    AgbaraAIRequest(
        userId = "user123",
        message = "Process when online"
    )
)

// Sync queued messages when online
agbaraClient.syncOfflineMessages { result ->
    when (result) {
        is SyncResult.Success -> {
            println("Synced ${result.messagesSynced} messages")
        }
        is SyncResult.Error -> {
            println("Sync failed: ${result.error.message}")
        }
    }
}
```

## Configuration

### Basic Configuration

```kotlin
val config = AgbaraConfig(
    // API Configuration
    apiKey = "your-api-key",
    baseUrl = "https://api.agbara.ai",
    webSocketUrl = "wss://api.agbara.ai/ws/chat",

    // AI Configuration
    enableLocalAI = true,
    enableRemoteAI = true,
    localModelPath = "/data/local/ai/models",
    localModelSize = ModelSize.SMALL,

    // Performance
    maxConcurrentRequests = 5,
    requestTimeout = 30000,
    cacheEnabled = true,
    cacheMaxSize = 100,

    // Privacy
    enableEncryption = true,
    dataRetentionDays = 30,
    allowAnalytics = false,

    // Igbo Language
    igboMode = false,
    igboDialect = IgboDialect.STANDARD,

    // Debug
    enableLogging = true,
    logLevel = LogLevel.INFO
)

val agbaraClient = AgbaraClient.create(context, apiKey, config)
```

### Advanced Configuration

```kotlin
// Cache configuration
val cacheConfig = CacheConfig(
    enabled = true,
    maxSize = 100,
    ttlSeconds = 3600
)
agbaraClient.setCacheConfig(cacheConfig)

// Update configuration
agbaraClient.updateConfiguration {
    maxConcurrentRequests = 10
    requestTimeout = 60000
}
```

## Ikorochat Integration

### Chat Intelligence

```kotlin
class IkoroChatIntelligence(private val agbaraClient: AgbaraClient) {

    fun assistChat(
        userId: String,
        message: String,
        context: ChatContext,
        callback: (ChatAssistance) -> Unit
    ) {
        val prompt = buildString {
            append("Assist with this chat message:\n")
            append("Message: $message\n")
            append("Context: ${context.type}\n")
            if (context.isMarketplace) {
                append("Product: ${context.product}\n")
                append("Price: ${context.price}\n")
            }
            append("\nProvide helpful suggestions.")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            context = mapOf(
                "app" to "ikoro-chat",
                "chat_context" to context
            )
        )

        agbaraClient.processMessage(request) { response ->
            when (response) {
                is AgbaraAIResponse.Success -> {
                    callback(ChatAssistance.Success(
                        suggestion = response.data.response,
                        category = categorizeAssistance(message),
                        confidence = response.data.confidence
                    ))
                }
                is AgbaraAIResponse.Error -> {
                    callback(ChatAssistance.Error(response.error))
                }
            }
        }
    }
}
```

### Market Analysis

```kotlin
class IkoroMarketAI(private val agbaraClient: AgbaraClient) {

    fun analyzeProduct(
        product: Product,
        marketData: MarketData,
        callback: (MarketAnalysis) -> Unit
    ) {
        val prompt = buildString {
            append("Analyze this product for the Ikoro marketplace:\n\n")
            append("Product Information:\n")
            append("Name: ${product.name}\n")
            append("Category: ${product.category}\n")
            append("Price: ${product.price} ₿\n")
            append("Description: ${product.description}\n")
            append("\nMarket Data:\n")
            append("Average Price: ${marketData.avgPrice} ₿\n")
            append("Demand Level: ${marketData.demandLevel}\n")
            append("Competition: ${marketData.competition}\n")
            append("\nProvide:\n")
            append("1. Price recommendation (range)\n")
            append("2. Market demand assessment\n")
            append("3. Competitive analysis\n")
            append("4. Improvement suggestions\n")
            append("5. Marketing strategy\n")
        }

        val request = AgbaraAIRequest(
            userId = product.sellerId,
            message = prompt,
            preferredExpert = ExpertType.VISION
        )

        agbaraClient.processMessage(request) { response ->
            when (response) {
                is AgbaraAIResponse.Success -> {
                    val analysis = parseMarketAnalysis(response.data.response)
                    callback(analysis)
                }
                is AgbaraAIResponse.Error -> {
                    callback(MarketAnalysis.Error(response.error))
                }
            }
        }
    }
}
```

### Transaction Security

```kotlin
class IkoroTransactionAI(private val agbaraClient: AgbaraClient) {

    fun analyzeTransactionRisk(
        transaction: Transaction,
        userProfile: UserProfile,
        callback: (FraudAnalysis) -> Unit
    ) {
        val prompt = buildString {
            append("Analyze this transaction for fraud risk:\n\n")
            append("Transaction Details:\n")
            append("Amount: ${transaction.amount} ₿\n")
            append("Sender ID: ${transaction.senderId}\n")
            append("Recipient ID: ${transaction.recipientId}\n")
            append("Timestamp: ${transaction.timestamp}\n")
            append("Location: ${transaction.location}\n")
            append("Device: ${transaction.deviceInfo}\n")
            append("\nSender Profile:\n")
            append("Account Age: ${userProfile.accountAge} days\n")
            append("Previous Transactions: ${userProfile.totalTransactions}\n")
            append("Trust Score: ${userProfile.trustScore}\n")
            append("Suspicious Activity: ${userProfile.suspiciousFlags}\n")
            append("\nAssess:\n")
            append("1. Fraud risk level (LOW/MEDIUM/HIGH)\n")
            append("2. Suspicious patterns\n")
            append("3. Recommendation (APPROVE/REJECT/REQUIRES_REVIEW)\n")
            append("4. Confidence score\n")
            append("5. Additional verification needed?\n")
        }

        val request = AgbaraAIRequest(
            userId = transaction.senderId,
            message = prompt,
            context = mapOf(
                "transaction_id" to transaction.id,
                "priority" to "HIGH"
            )
        )

        agbaraClient.processMessage(request) { response ->
            when (response) {
                is AgbaraAIResponse.Success -> {
                    val analysis = parseFraudAnalysis(response.data.response)
                    callback(analysis)
                }
                is AgbaraAIResponse.Error -> {
                    callback(FraudAnalysis.Error(response.error))
                }
            }
        }
    }
}
```

## Performance Optimization

### Preloading Models

```kotlin
// Preload local models on app startup
agbaraClient.preloadLocalModels { result ->
    when (result) {
        is PreloadResult.Success -> {
            println("Models preloaded in ${result.timeMs}ms")
        }
        is PreloadResult.Error -> {
            println("Preload failed: ${result.error.message}")
        }
    }
}
```

### Performance Monitoring

```kotlin
// Get performance metrics
val metrics = agbaraClient.getMetrics()

println("Average Response Time: ${metrics.avgResponseTime}ms")
println("Cache Hit Rate: ${metrics.cacheHitRate}%")
println("Battery Usage: ${metrics.batteryUsage}%")
println("Memory Usage: ${metrics.memoryUsage}MB")
println("Active Requests: ${metrics.activeRequests}")
```

## Error Handling

### Comprehensive Error Handling

```kotlin
agbaraClient.processMessage(request) { response ->
    when (response) {
        is AgbaraAIResponse.Success -> {
            // Handle success
        }
        is AgbaraAIResponse.Error -> {
            when (response.error.type) {
                ErrorType.NETWORK -> {
                    if (response.error.retryable) {
                        // Retry automatically
                        agbaraClient.retry(request) { retryResponse ->
                            // Handle retry response
                        }
                    } else {
                        // Show network error to user
                    }
                }
                ErrorType.AUTHENTICATION -> {
                    // Re-authenticate user
                }
                ErrorType.RATE_LIMIT -> {
                    // Wait and retry
                    agbaraClient.waitForRateLimitReset()
                }
                ErrorType.INVALID_INPUT -> {
                    // Show validation error
                }
                ErrorType.SERVER_ERROR -> {
                    // Show server error
                }
                ErrorType.UNKNOWN -> {
                    // Show generic error
                }
            }
        }
    }
}
```

## Security & Privacy

### Data Encryption

```kotlin
// All sensitive data is encrypted by default
val config = AgbaraConfig(
    apiKey = "your-api-key",
    enableEncryption = true,
    dataRetentionDays = 30,
    allowAnalytics = false
)
```

### Privacy Controls

```kotlin
// User can control data retention
agbaraClient.updateConfiguration {
    dataRetentionDays = 7  // Keep only 7 days
    allowAnalytics = false  // Disable analytics
}
```

## Troubleshooting

### Common Issues

**Issue:** SDK not initializing  
**Solution:** Check API key and network connection

**Issue:** Local AI not working  
**Solution:** Ensure models are preloaded and device has sufficient storage

**Issue:** WebSocket not connecting  
**Solution:** Check internet connection and WebSocket URL

**Issue:** High battery usage  
**Solution:** Disable local AI or use smaller model size

## Requirements

- Android 8.0 (API level 26) or higher
- Kotlin 1.9+
- 50MB free storage for local models
- 2GB RAM minimum
- Internet connection (optional, for remote AI)

## Permissions

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
```

## License

```
Copyright 2024 Agbara Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Support

- **GitHub Issues:** https://github.com/Satoshi-NaAkokwa/agbara-android-sdk/issues
- **Documentation:** https://docs.agbara.ai/android
- **Email:** support@agbara.ai
- **Community:** https://discord.gg/agbara

## Changelog

### Version 1.0.0 (2024-05-22)

- ✅ Initial release
- ✅ Local AI inference
- ✅ Remote API integration
- ✅ Offline support
- ✅ Igbo language support
- ✅ WebSocket streaming
- ✅ Ikorochat integration modules
- ✅ Comprehensive documentation

---

**Built with ❤️ by Agbara Team**