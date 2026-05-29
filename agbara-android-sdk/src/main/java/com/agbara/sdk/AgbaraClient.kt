// Agbara Android SDK - Main Client
package com.agbara.sdk

import android.content.Context
import android.content.SharedPreferences
import com.agbara.sdk.cache.CacheManager
import com.agbara.sdk.config.AgbaraConfig
import com.agbara.sdk.models.*
import com.agbara.sdk.network.ApiClient
import com.agbara.sdk.network.WebSocketClient
import com.agbara.sdk.offline.OfflineManager
import com.agbara.sdk.igbo.IgboClient
import com.agbara.sdk.platform.PlatformClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import org.json.JSONObject
import java.util.concurrent.ConcurrentHashMap

/**
 * Main Agbara client for Android applications
 * Provides access to all Agbara AI capabilities
 */
class AgbaraClient private constructor(
    private val context: Context,
    private val config: AgbaraConfig
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val preferences: SharedPreferences =
        context.getSharedPreferences("agbara_prefs", Context.MODE_PRIVATE)

    // Clients
    private val apiClient: ApiClient = ApiClient(context, config)
    private val webSocketClient: WebSocketClient = WebSocketClient(config)
    private val cacheManager: CacheManager = CacheManager(config)
    private val offlineManager: OfflineManager = OfflineManager(context, config)
    private val igboClient: IgboClient = IgboClient(config)
    private val platformClient: PlatformClient = ApiClient(context, config).getPlatformClient()

    // State
    private val activeRequests = ConcurrentHashMap<String, AgbaraAIRequest>()
    private var isInitialized = false

    companion object {
        private const val TAG = "AgbaraClient"
        private const val KEY_INITIALIZED = "initialized"
        private const val KEY_USER_ID = "user_id"

        @Volatile
        private var instance: AgbaraClient? = null

        /**
         * Create a new AgbaraClient instance
         */
        fun create(
            context: Context,
            apiKey: String,
            options: AgbaraClientOptions.() -> Unit = {}
        ): AgbaraClient {
            val clientOptions = AgbaraClientOptions().apply(options)
            val config = AgbaraConfig.fromOptions(clientOptions, apiKey)

            return AgbaraClient(context.applicationContext, config).also {
                instance = it
            }
        }

        /**
         * Get the shared instance
         */
        fun getInstance(): AgbaraClient? = instance

        /**
         * Initialize the client with configuration
         */
        fun initialize(context: Context, config: AgbaraConfig): AgbaraClient {
            return AgbaraClient(context.applicationContext, config).also {
                instance = it
            }
        }
    }

    init {
        initialize()
    }

    private fun initialize() {
        if (isInitialized) return

        try {
            // Initialize components
            cacheManager.initialize()
            offlineManager.initialize()

            // Set user ID
            val userId = preferences.getString(KEY_USER_ID, null)
            if (userId != null) {
                setUserId(userId)
            }

            isInitialized = true

            AgbaraLogger.info(TAG, "AgbaraClient initialized successfully")
        } catch (e: Exception) {
            AgbaraLogger.error(TAG, "Failed to initialize AgbaraClient", e)
            throw AgbaraException(ErrorCode.INITIALIZATION_FAILED, e.message)
        }
    }

    // Public API

    /**
     * Set the current user ID
     */
    fun setUserId(userId: String) {
        preferences.edit().putString(KEY_USER_ID, userId).apply()
        apiClient.setUserId(userId)
    }

    /**
     * Get the current user ID
     */
    fun getUserId(): String? {
        return preferences.getString(KEY_USER_ID, null)
    }

    /**
     * Process a message through Agbara AI
     */
    fun processMessage(
        request: AgbaraAIRequest,
        callback: (AgbaraAIResponse) -> Unit
    ) {
        scope.launch {
            try {
                // Add to active requests
                val requestId = generateRequestId()
                activeRequests[requestId] = request

                // Check cache first
                val cacheKey = generateCacheKey(request)
                cacheManager.get(cacheKey)?.let { cachedResponse ->
                    AgbaraLogger.debug(TAG, "Cache hit for request: $cacheKey")
                    callback(AgbaraAIResponse.Success(cachedResponse))
                    return@launch
                }

                // Process the request
                val response = processRequest(request)

                // Cache the response
                cacheManager.put(cacheKey, response)

                // Return result
                callback(AgbaraAIResponse.Success(response))

                // Remove from active requests
                activeRequests.remove(requestId)

            } catch (e: AgbaraException) {
                AgbaraLogger.error(TAG, "Agbara exception: ${e.message}", e)
                callback(AgbaraAIResponse.Error(e))
            } catch (e: Exception) {
                AgbaraLogger.error(TAG, "Unexpected error", e)
                callback(AgbaraAIResponse.Error(
                    AgbaraException(ErrorCode.UNKNOWN, e.message)
                ))
            }
        }
    }

    /**
     * Process message with streaming response
     */
    fun processMessageStream(
        request: AgbaraAIRequest,
        callback: (StreamChunk) -> Unit
    ) {
        scope.launch {
            try {
                apiClient.processStream(request, callback)
            } catch (e: AgbaraException) {
                AgbaraLogger.error(TAG, "Stream processing error", e)
                callback(StreamChunk.Error(e))
            }
        }
    }

    /**
     * Process multiple requests in batch
     */
    fun processBatch(
        requests: List<AgbaraAIRequest>,
        callback: (BatchResult) -> Unit
    ) {
        scope.launch {
            try {
                val responses = mutableListOf<AgbaraAIResponse.Success>()

                requests.forEach { request ->
                    try {
                        val response = processRequest(request)
                        responses.add(AgbaraAIResponse.Success(response))
                    } catch (e: AgbaraException) {
                        responses.add(AgbaraAIResponse.Error(e))
                    }
                }

                callback(BatchResult.Success(responses))
            } catch (e: Exception) {
                callback(BatchResult.Error(AgbaraException(ErrorCode.BATCH_FAILED, e.message)))
            }
        }
    }

    /**
     * Retry a failed request
     */
    fun retry(
        request: AgbaraAIRequest,
        callback: (AgbaraAIResponse) -> Unit
    ) {
        processMessage(request, callback)
    }

    // WebSocket API

    /**
     * Connect to WebSocket for real-time communication
     */
    fun connectWebSocket(
        userId: String,
        messageHandler: (WebSocketMessage) -> Unit
    ) {
        webSocketClient.connect(userId, messageHandler)
    }

    /**
     * Disconnect WebSocket
     */
    fun disconnectWebSocket() {
        webSocketClient.disconnect()
    }

    /**
     * Send message via WebSocket
     */
    fun sendWebSocketMessage(request: AgbaraAIRequest) {
        webSocketClient.send(request)
    }

    // Offline Manager

    /**
     * Get offline manager
     */
    fun getOfflineManager(): OfflineManager = offlineManager

    /**
     * Sync offline messages
     */
    fun syncOfflineMessages(callback: (SyncResult) -> Unit) {
        scope.launch {
            try {
                val result = offlineManager.sync(apiClient)
                callback(result)
            } catch (e: Exception) {
                callback(SyncResult.Error(AgbaraException(ErrorCode.SYNC_FAILED, e.message)))
            }
        }
    }

    // Igbo Language

    /**
     * Get Igbo proverb
     */
    fun getIgboProverb(): IgboProverb {
        return igboClient.getProverb()
    }

    /**
     * Translate Igbo text
     */
    fun translateIgbo(
        text: String,
        direction: TranslationDirection
    ): IgboTranslation {
        return igboClient.translate(text, direction)
    }

    /**
     * Explain cultural concept
     */
    fun explainCulturalConcept(concept: String): CulturalConcept {
        return igboClient.explainConcept(concept)
    }

    // Platform Integration

    /**
     * Get platform client
     */
    fun getPlatformClient(): PlatformClient = platformClient

    // Configuration

    /**
     * Update configuration
     */
    fun updateConfiguration(updates: AgbaraConfig.() -> Unit) {
        config.updates()
        // Reinitialize affected components
        cacheManager.initialize()
    }

    /**
     * Get current configuration
     */
    fun getConfiguration(): AgbaraConfig = config

    // Performance & Monitoring

    /**
     * Get performance metrics
     */
    fun getMetrics(): PerformanceMetrics {
        return PerformanceMetrics(
            avgResponseTime = cacheManager.getAvgResponseTime(),
            cacheHitRate = cacheManager.getCacheHitRate(),
            batteryUsage = apiClient.getBatteryUsage(),
            memoryUsage = getMemoryUsage(),
            activeRequests = activeRequests.size
        )
    }

    /**
     * Set cache configuration
     */
    fun setCacheConfig(cacheConfig: CacheConfig) {
        cacheManager.setConfiguration(cacheConfig)
    }

    /**
     * Preload local models
     */
    fun preloadLocalModels(callback: (PreloadResult) -> Unit) {
        scope.launch {
            try {
                val startTime = System.currentTimeMillis()
                // Preload logic here
                val time = System.currentTimeMillis() - startTime
                callback(PreloadResult.Success(time))
            } catch (e: Exception) {
                callback(PreloadResult.Error(AgbaraException(ErrorCode.PRELOAD_FAILED, e.message)))
            }
        }
    }

    // Cleanup

    /**
     * Cleanup resources
     */
    fun cleanup() {
        try {
            webSocketClient.disconnect()
            cacheManager.cleanup()
            offlineManager.cleanup()

            isInitialized = false

            AgbaraLogger.info(TAG, "AgbaraClient cleaned up")
        } catch (e: Exception) {
            AgbaraLogger.error(TAG, "Error during cleanup", e)
        }
    }

    // Private helper methods

    private suspend fun processRequest(request: AgbaraAIRequest): AgbaraAIResponseData {
        // Check if we should use local AI
        if (config.enableLocalAI && shouldUseLocalAI(request)) {
            return processWithLocalAI(request)
        }

        // Otherwise, use remote API
        return processWithRemoteAPI(request)
    }

    private fun shouldUseLocalAI(request: AgbaraAIRequest): Boolean {
        // Use local AI if:
        // 1. No internet connection
        // 2. Request is simple enough for local model
        // 3. User prefers local processing
        val isOnline = isNetworkAvailable()
        val isSimpleRequest = request.message.length < 500
        val prefersLocal = request.mode == "local"

        return !isOnline || (isSimpleRequest && prefersLocal)
    }

    private suspend fun processWithLocalAI(request: AgbaraAIRequest): AgbaraAIResponseData {
        // Implementation of local AI processing
        // This would use quantized models running on device
        return AgbaraAIResponseData(
            response = "Local AI response",
            expertUsed = "local-model",
            processingTime = 0.5,
            confidence = 0.85,
            metadata = mapOf(
                "source" to "local",
                "model" to "quantized-small"
            )
        )
    }

    private suspend fun processWithRemoteAPI(request: AgbaraAIRequest): AgbaraAIResponseData {
        // Call remote API
        return apiClient.process(request)
    }

    private fun generateRequestId(): String {
        return "req_${System.currentTimeMillis()}_${(0..9999).random()}"
    }

    private fun generateCacheKey(request: AgbaraAIRequest): String {
        return "${request.userId}_${request.message}_${request.igboMode}"
    }

    private fun isNetworkAvailable(): Boolean {
        // Check network connectivity
        return apiClient.isNetworkAvailable()
    }

    private fun getMemoryUsage(): Long {
        val runtime = Runtime.getRuntime()
        val usedMemory = runtime.totalMemory() - runtime.freeMemory()
        return usedMemory / (1024 * 1024) // Convert to MB
    }

    fun waitForRateLimitReset() {
        // Wait for rate limit to reset
        // Implementation would depend on API rate limiting policy
    }
}

// Client options
data class AgbaraClientOptions(
    var enableLocalAI: Boolean = true,
    var enableRemoteAI: Boolean = true,
    var igboMode: Boolean = false,
    var igboDialect: IgboDialect = IgboDialect.STANDARD,
    var localModelPath: String = "",
    var localModelSize: ModelSize = ModelSize.SMALL,
    var maxConcurrentRequests: Int = 5,
    var requestTimeout: Int = 30000,
    var cacheEnabled: Boolean = true,
    var cacheMaxSize: Int = 100,
    var enableEncryption: Boolean = true,
    var dataRetentionDays: Int = 30,
    var allowAnalytics: Boolean = false,
    var enableLogging: Boolean = true,
    var logLevel: LogLevel = LogLevel.INFO
)