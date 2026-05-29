# Agbara Android SDK - Unit Tests

## Test Coverage Goals
- Unit tests: 90%+
- Integration tests: 80%+
- Critical paths: 100%

## Running Tests

```bash
./gradlew test
./gradlew connectedAndroidTest
```

## Test Suites

### 1. AgbaraClient Tests
```kotlin
class AgbaraClientTest {
    @Test
    fun testInitialization() {
        val client = AgbaraClient.create(
            context = testContext,
            apiKey = "test-key",
            options = {
                enableLocalAI = false
                enableRemoteAI = false
            }
        )
        assertNotNull(client)
    }

    @Test
    fun testProcessMessage() = runTest {
        val client = createTestClient()
        val request = AgbaraAIRequest(
            userId = "test-user",
            message = "Hello, Agbara!"
        )

        client.processMessage(request) { response ->
            assertTrue(response is AgbaraAIResponse.Success)
            assertNotNull((response as AgbaraAIResponse.Success).data.response)
        }
    }

    @Test
    fun testOfflineQueueing() = runTest {
        val client = createTestClient()
        val offlineManager = client.getOfflineManager()

        val request = AgbaraAIRequest(
            userId = "test-user",
            message = "Offline message"
        )

        offlineManager.queueMessage(request)
        assertEquals(1, offlineManager.getQueueSize())
    }

    @Test
    fun testIgboProverb() {
        val client = createTestClient()
        val proverb = client.getIgboProverb()
        assertNotNull(proverb.text)
        assertNotNull(proverb.translation)
        assertNotNull(proverb.meaning)
    }

    @Test
    fun testTranslateIgbo() {
        val client = createTestClient()
        val translation = client.translateIgbo(
            text = "Ndeewo",
            direction = TranslationDirection.IGBO_TO_ENGLISH
        )
        assertEquals("Hello, welcome", translation.text)
    }

    @Test
    fun testConfiguration() {
        val config = AgbaraConfig(
            apiKey = "test-key",
            cacheEnabled = true,
            cacheMaxSize = 50
        )
        assertEquals(50, config.cacheMaxSize)
    }
}
```

### 2. ApiClient Tests
```kotlin
class ApiClientTest {
    @Test
    fun testProcessSuccess() = runTest {
        val client = ApiClient(testContext, testConfig)
        val request = AgbaraAIRequest(
            userId = "test-user",
            message = "Test message"
        )

        val response = client.process(request)
        assertNotNull(response.response)
        assertNotNull(response.expertUsed)
        assertTrue(response.confidence > 0)
    }

    @Test
    fun testNetworkError() = runTest {
        val client = ApiClient(testContext, testConfig.copy(baseUrl = "http://invalid-url"))
        val request = AgbaraAIRequest(
            userId = "test-user",
            message = "Test message"
        )

        assertThrows<AgbaraException> {
            client.process(request)
        }
    }

    @Test
    fun testNetworkAvailable() {
        val client = ApiClient(testContext, testConfig)
        val available = client.isNetworkAvailable()
        // This will depend on test environment
    }

    @Test
    fun testUserIdManagement() {
        val client = ApiClient(testContext, testConfig)
        client.setUserId("test-user-123")
        assertEquals("test-user-123", client.currentUserId)
    }
}
```

### 3. CacheManager Tests
```kotlin
class CacheManagerTest {
    @Test
    fun testPutAndGet() {
        val cacheManager = CacheManager(testConfig)
        val key = "test-key"
        val data = AgbaraAIResponseData(
            response = "Test response",
            expertUsed = "test-expert",
            processingTime = 1.0,
            confidence = 0.9f
        )

        runBlocking {
            cacheManager.put(key, data)
            val retrieved = cacheManager.get(key)
            assertNotNull(retrieved)
            assertEquals("Test response", retrieved!!.response)
        }
    }

    @Test
    fun testCacheHitRate() {
        val cacheManager = CacheManager(testConfig)
        
        runBlocking {
            val key = "test-key"
            val data = AgbaraAIResponseData(
                response = "Test response",
                expertUsed = "test-expert",
                processingTime = 1.0,
                confidence = 0.9f
            )

            // First call - miss
            cacheManager.get(key)
            assertEquals(0.0f, cacheManager.getCacheHitRate())

            // Add to cache
            cacheManager.put(key, data)

            // Second call - hit
            cacheManager.get(key)
            assertEquals(0.5f, cacheManager.getCacheHitRate())
        }
    }

    @Test
    fun testCacheEviction() {
        val cacheManager = CacheManager(testConfig.copy(cacheMaxSize = 2))
        
        runBlocking {
            // Add 3 items to cache (max is 2)
            for (i in 1..3) {
                val data = AgbaraAIResponseData(
                    response = "Response $i",
                    expertUsed = "test-expert",
                    processingTime = 1.0,
                    confidence = 0.9f
                )
                cacheManager.put("key$i", data)
            }

            // Only 2 items should remain
            assertEquals(2, cacheManager.getSize())
        }
    }

    @Test
    fun testCacheExpiration() {
        val cacheManager = CacheManager(
            testConfig.copy(cacheMaxSize = 10)
        )
        cacheManager.setConfiguration(
            CacheConfig(enabled = true, maxSize = 10, ttlSeconds = 1)
        )
        
        runBlocking {
            val key = "expiring-key"
            val data = AgbaraAIResponseData(
                response = "Test response",
                expertUsed = "test-expert",
                processingTime = 1.0,
                confidence = 0.9f
            )

            cacheManager.put(key, data)
            Thread.sleep(1500) // Wait for expiration

            val retrieved = cacheManager.get(key)
            assertNull(retrieved)
        }
    }

    @Test
    fun testCacheClear() {
        val cacheManager = CacheManager(testConfig)
        
        runBlocking {
            val data = AgbaraAIResponseData(
                response = "Test response",
                expertUsed = "test-expert",
                processingTime = 1.0,
                confidence = 0.9f
            )

            cacheManager.put("key1", data)
            cacheManager.put("key2", data)
            assertEquals(2, cacheManager.getSize())

            cacheManager.clear()
            assertEquals(0, cacheManager.getSize())
        }
    }
}
```

### 4. OfflineManager Tests
```kotlin
class OfflineManagerTest {
    @Test
    fun testQueueMessage() = runBlocking {
        val offlineManager = OfflineManager(testContext, testConfig)
        val request = AgbaraAIRequest(
            userId = "test-user",
            message = "Offline message"
        )

        offlineManager.queueMessage(request)
        assertEquals(1, offlineManager.getQueueSize())
    }

    @Test
    fun testQueueFull() = runBlocking {
        val offlineManager = OfflineManager(testContext, testConfig)
        val request = AgbaraAIRequest(
            userId = "test-user",
            message = "Test message"
        )

        // Fill queue to max (1000)
        repeat(1000) {
            offlineManager.queueMessage(request)
        }

        // Try to add one more - should fail
        val initialSize = offlineManager.getQueueSize()
        offlineManager.queueMessage(request)
        assertEquals(initialSize, offlineManager.getQueueSize())
    }

    @Test
    fun testSyncSuccess() = runBlocking {
        val offlineManager = OfflineManager(testContext, testConfig)
        val apiClient = mockk<ApiClient>()

        // Add messages to queue
        repeat(5) {
            offlineManager.queueMessage(
                AgbaraAIRequest(
                    userId = "test-user",
                    message = "Test message"
                )
            )
        }

        coEvery { apiClient.process(any()) } returns AgbaraAIResponseData(
            response = "Processed",
            expertUsed = "test",
            processingTime = 1.0,
            confidence = 0.9f
        )

        val result = offlineManager.sync(apiClient)
        assertTrue(result is SyncResult.Success)
        assertEquals(5, (result as SyncResult.Success).messagesSynced)
    }

    @Test
    fun testSyncRetry() = runBlocking {
        val offlineManager = OfflineManager(testContext, testConfig)
        val apiClient = mockk<ApiClient>()

        offlineManager.queueMessage(
            AgbaraAIRequest(
                userId = "test-user",
                message = "Test message"
            )
        )

        var attemptCount = 0
        coEvery { apiClient.process(any()) } answers {
            attemptCount++
            if (attemptCount == 3) {
                AgbaraAIResponseData(
                    response = "Success",
                    expertUsed = "test",
                    processingTime = 1.0,
                    confidence = 0.9f
                )
            } else {
                throw AgbaraException(
                    ErrorCode.NETWORK_ERROR,
                    "Temporary error",
                    retryable = true
                )
            }
        }

        val result = offlineManager.sync(apiClient)
        assertTrue(result is SyncResult.Success)
        assertEquals(3, attemptCount)
    }

    @Test
    fun testClearQueue() = runBlocking {
        val offlineManager = OfflineManager(testContext, testConfig)

        // Add messages to queue
        repeat(5) {
            offlineManager.queueMessage(
                AgbaraAIRequest(
                    userId = "test-user",
                    message = "Test message"
                )
            )
        }

        assertEquals(5, offlineManager.getQueueSize())

        offlineManager.clearQueue()
        assertEquals(0, offlineManager.getQueueSize())
    }
}
```

### 5. IgboClient Tests
```kotlin
class IgboClientTest {
    @Test
    fun testGetProverb() {
        val igboClient = IgboClient(testConfig)
        val proverb = igboClient.getProverb()

        assertNotNull(proverb.text)
        assertNotNull(proverb.translation)
        assertNotNull(proverb.meaning)
        assertTrue(proverb.text.isNotBlank())
        assertTrue(proverb.translation.isNotBlank())
        assertTrue(proverb.meaning.isNotBlank())
    }

    @Test
    fun testTranslateIgboToEnglish() {
        val igboClient = IgboClient(testConfig)
        val translation = igboClient.translateIgbo(
            text = "Ndeewo",
            direction = TranslationDirection.IGBO_TO_ENGLISH
        )

        assertEquals("Ndeewo", translation.originalText)
        assertEquals(TranslationDirection.IGBO_TO_ENGLISH, translation.direction)
        assertTrue(translation.text.isNotBlank())
    }

    @Test
    fun testTranslateEnglishToIgbo() {
        val igboClient = IgboClient(testConfig)
        val translation = igboClient.translateIgbo(
            text = "Hello",
            direction = TranslationDirection.ENGLISH_TO_IGBO
        )

        assertEquals("Hello", translation.originalText)
        assertEquals(TranslationDirection.ENGLISH_TO_IGBO, translation.direction)
    }

    @Test
    fun testExplainConcept() {
        val igboClient = IgboClient(testConfig)
        val concept = igboClient.explainCulturalConcept("Chi")

        assertEquals("Chi", concept.name)
        assertNotNull(concept.explanation)
        assertNotNull(concept.examples)
        assertTrue(concept.explanation.isNotBlank())
    }

    @Test
    fun testGetAllProverbs() {
        val igboClient = IgboClient(testConfig)
        val proverbs = igboClient.getAllProverbs()

        assertNotNull(proverbs)
        assertTrue(proverbs.isNotEmpty())
        assertTrue(proverbs.size >= 5)
    }

    @Test
    fun testSearchProverb() {
        val igboClient = IgboClient(testConfig)
        val results = igboClient.searchProverb("unity")

        assertNotNull(results)
        // Should find proverb about unity
        assertTrue(results.any { it.translation.contains("unity", ignoreCase = true) })
    }

    @Test
    fun testVocabularySize() {
        val igboClient = IgboClient(testConfig)
        val size = igboClient.getVocabularySize()

        assertTrue(size > 0)
    }
}
```

### 6. Ikorochat Integration Tests
```kotlin
class IkoroChatIntelligenceTest {
    @Test
    fun testAssistChat() = runTest {
        val chatAI = IkoroChatIntelligence(createTestAgbaraClient())
        
        var receivedAssistance: ChatAssistance? = null
        chatAI.assistChat(
            userId = "test-user",
            message = "I want to buy this product",
            context = ChatContext(isMarketplace = true),
            callback = { assistance ->
                receivedAssistance = assistance
            }
        )

        delay(1000)
        assertNotNull(receivedAssistance)
        assertTrue(receivedAssistance is ChatAssistance.Success)
    }

    @Test
    fun testCategorizeMessage() = runTest {
        val chatAI = IkoroChatIntelligence(createTestAgbaraClient())
        
        val marketplaceMsg = chatAI.categorizeMessage("I'll buy it for 50 ₿")
        assertEquals(ChatCategory.MARKETPLACE, marketplaceMsg)

        val transactionMsg = chatAI.categorizeMessage("Send 10 ₿ to user123")
        assertEquals(ChatCategory.TRANSACTION, transactionMsg)

        val helpMsg = chatAI.categorizeMessage("How do I use this?")
        assertEquals(ChatCategory.HELP, helpMsg)

        val generalMsg = chatAI.categorizeMessage("Hello there!")
        assertEquals(ChatCategory.GENERAL, generalMsg)
    }

    @Test
    fun testGenerateSmartReplies() = runTest {
        val chatAI = IkoroChatIntelligence(createTestAgbaraClient())
        
        val replies = chatAI.generateSmartReplies(
            userId = "test-user",
            message = "How much for this?",
            context = ChatContext(),
            count = 3
        )

        assertNotNull(replies)
        assertEquals(3, replies.size)
        replies.forEach { assertTrue(it.isNotBlank()) }
    }
}

class IkoroMarketAnalyzerTest {
    @Test
    fun testAnalyzeProduct() = runTest {
        val marketAnalyzer = IkoroMarketAnalyzer(createTestAgbaraClient())
        
        val product = ProductData(
            id = "prod-1",
            name = "Sample Product",
            category = "Electronics",
            price = 100.0,
            description = "Great product",
            sellerName = "Test Seller",
            rating = 4.5f,
            imageCount = 3
        )

        val result = marketAnalyzer.analyzeProduct(
            userId = "test-user",
            product = product,
            marketData = MarketData()
        )

        delay(2000)
        assertNotNull(result)
    }

    @Test
    fun testPriceRecommendation() = runTest {
        val marketAnalyzer = IkoroMarketAnalyzer(createTestAgbaraClient())
        
        val product = ProductData(
            id = "prod-1",
            name = "Sample Product",
            category = "Electronics",
            price = 100.0,
            description = "Great product",
            sellerName = "Test Seller",
            rating = 4.5f,
            imageCount = 3
        )

        val analysis = marketAnalyzer.analyzeProduct(
            userId = "test-user",
            product = product,
            marketData = MarketData(avgPrice = 80.0, minPrice = 50.0, maxPrice = 120.0)
        )

        delay(2000)
        assertTrue(analysis is MarketAnalysis.Success)
        
        val success = analysis as MarketAnalysis.Success
        assertTrue(success.priceRecommendation.minPrice >= 50.0)
        assertTrue(success.priceRecommendation.maxPrice <= 120.0)
    }
}

class IkoroTransactionAITest {
    @Test
    fun testAnalyzeTransactionRisk() = runTest {
        val transactionAI = IkoroTransactionAI(createTestAgbaraClient())
        
        val transaction = TransactionData(
            id = "txn-1",
            amount = 100.0,
            senderId = "user1",
            recipientId = "user2",
            timestamp = "2024-05-22T10:00:00Z",
            location = "Lagos, Nigeria",
            deviceInfo = "Android 12, Pixel 6",
            ipAddress = "192.168.1.1",
            description = "Product purchase"
        )

        val userProfile = UserProfile(
            accountAge = 365,
            totalTransactions = 50,
            trustScore = 95,
            verificationLevel = "VERIFIED",
            lastLogin = "2024-05-22T09:00:00Z",
            loginLocation = "Lagos, Nigeria",
            deviceUsage = "Consistent"
        )

        val result = transactionAI.analyzeTransactionRisk(
            userId = "user1",
            transaction = transaction,
            userProfile = userProfile
        )

        delay(2000)
        assertNotNull(result)
    }

    @Test
    fun testFraudDetection() = runTest {
        val transactionAI = IkoroTransactionAI(createTestAgbaraClient())
        
        // High-risk transaction (new user, large amount)
        val highRiskTxn = TransactionData(
            id = "txn-1",
            amount = 1000.0,
            senderId = "new-user-1",
            recipientId = "unknown-recipient",
            timestamp = "2024-05-22T10:00:00Z",
            location = "Unknown",
            deviceInfo = "New Device",
            ipAddress = "192.168.1.100",
            description = "Large transfer"
        )

        val highRiskProfile = UserProfile(
            accountAge = 1,
            totalTransactions = 0,
            trustScore = 0,
            verificationLevel = "UNVERIFIED",
            lastLogin = "2024-05-22T10:00:00Z",
            loginLocation = "Unknown",
            deviceUsage = "New",
            suspiciousFlags = listOf("New account", "Large transaction")
        )

        val result = transactionAI.analyzeTransactionRisk(
            userId = "new-user-1",
            transaction = highRiskTxn,
            userProfile = highRiskProfile
        )

        delay(2000)
        assertTrue(result is FraudAnalysis.Success)
        
        val success = result as FraudAnalysis.Success
        // Should flag as high risk
        assertTrue(success.riskLevel == RiskLevel.HIGH || success.riskLevel == RiskLevel.MEDIUM)
    }
}
```

## Mock Objects

```kotlin
// Mock AgbaraClient for testing
fun createTestAgbaraClient(): AgbaraClient {
    val config = AgbaraConfig(
        apiKey = "test-api-key",
        baseUrl = "http://localhost:8000",
        webSocketUrl = "ws://localhost:8000/ws/chat",
        enableLocalAI = false,
        enableRemoteAI = false
    )
    return AgbaraClient.create(testContext, config.apiKey) {
        enableLocalAI = false
        enableRemoteAI = false
    }
}

// Mock API client
fun createMockApiClient(): ApiClient {
    return mockk<ApiClient>(relaxed = true) {
        coEvery { it.process(any()) } returns AgbaraAIResponseData(
            response = "Mock response",
            expertUsed = "mock-expert",
            processingTime = 0.5,
            confidence = 1.0f
        )
    }
}
```

## Test Utilities

```kotlin
object TestUtils {
    fun createTestContext(): Context {
        return InstrumentationRegistry.getInstrumentation().targetContext
    }

    val testConfig: AgbaraConfig
        get() = AgbaraConfig(
            apiKey = "test-key",
            baseUrl = "http://localhost:8000",
            webSocketUrl = "ws://localhost:8000/ws/chat",
            enableLocalAI = false,
            enableRemoteAI = false,
            cacheEnabled = false,
            maxConcurrentRequests = 1
        )
}
```

## Running Tests

```bash
# Unit tests
./gradlew testDebugUnitTest

# Integration tests
./gradlew connectedAndroidTest

# All tests
./gradlew test

# With coverage
./gradlew testDebugUnitTest jacocoTestReport
```