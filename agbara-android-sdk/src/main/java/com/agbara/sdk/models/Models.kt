// Agbara SDK Models and Data Classes
package com.agbara.sdk.models

import com.google.gson.annotations.SerializedName
import java.util.Date

// Main request/response models

data class AgbaraAIRequest(
    val userId: String,
    val message: String,
    @SerializedName("igbo_mode")
    val igboMode: Boolean = false,
    val mode: String = "auto",
    @SerializedName("preferred_expert")
    val preferredExpert: ExpertType? = null,
    @SerializedName("expert_model")
    val expertModel: String? = null,
    val context: Map<String, Any>? = null
)

data class AgbaraAIResponseData(
    val response: String,
    @SerializedName("expert_used")
    val expertUsed: String,
    @SerializedName("processing_time")
    val processingTime: Double,
    val confidence: Float,
    val metadata: Map<String, Any>? = null
)

sealed class AgbaraAIResponse {
    data class Success(val data: AgbaraAIResponseData) : AgbaraAIResponse()
    data class Error(val error: AgbaraError) : AgbaraAIResponse()
}

// Stream response
data class StreamChunk(
    val text: String,
    val status: StreamStatus
)

enum class StreamStatus {
    START,
    PROGRESS,
    COMPLETE,
    ERROR
}

// WebSocket messages
sealed class WebSocketMessage {
    data class Response(val data: AgbaraAIResponseData) : WebSocketMessage()
    data class Error(val error: AgbaraError) : WebSocketMessage()
    data class Connected(val userId: String) : WebSocketMessage()
    data class Disconnected(val reason: String?) : WebSocketMessage()
}

// Batch processing
sealed class BatchResult {
    data class Success(val responses: List<AgbaraAIResponse>) : BatchResult()
    data class Error(val error: AgbaraError) : BatchResult()
}

// Sync operations
sealed class SyncResult {
    data class Success(
        @SerializedName("messages_synced")
        val messagesSynced: Int,
        @SerializedName("messages_failed")
        val messagesFailed: Int
    ) : SyncResult()

    data class Error(val error: AgbaraError) : SyncResult()
}

// Preload operations
sealed class PreloadResult {
    data class Success(val timeMs: Long) : PreloadResult()
    data class Error(val error: AgbaraError) : PreloadResult()
}

// Igbo language models
data class IgboProverb(
    val text: String,
    val translation: String,
    val meaning: String,
    @SerializedName("cultural_context")
    val culturalContext: String? = null
)

data class IgboTranslation(
    val text: String,
    @SerializedName("original_text")
    val originalText: String,
    val direction: TranslationDirection
)

enum class TranslationDirection {
    @SerializedName("igbo_to_english")
    IGBO_TO_ENGLISH,
    @SerializedName("english_to_igbo")
    ENGLISH_TO_IGBO
}

data class CulturalConcept(
    val name: String,
    val explanation: String,
    val examples: List<String>,
    @SerializedName("related_concepts")
    val relatedConcepts: List<String>? = null
)

// Error handling
data class AgbaraError(
    val type: ErrorType,
    val message: String,
    val code: String? = null,
    val retryable: Boolean = false
) : Exception(message) {
    companion object {
        fun network(message: String, retryable: Boolean = true) =
            AgbaraError(ErrorType.NETWORK, message, retryable = retryable)

        fun authentication(message: String) =
            AgbaraError(ErrorType.AUTHENTICATION, message, retryable = false)

        fun rateLimit(message: String) =
            AgbaraError(ErrorType.RATE_LIMIT, message, retryable = true)

        fun invalidInput(message: String) =
            AgbaraError(ErrorType.INVALID_INPUT, message, retryable = false)

        fun serverError(message: String, retryable: Boolean = true) =
            AgbaraError(ErrorType.SERVER_ERROR, message, retryable = retryable)

        fun unknown(message: String) =
            AgbaraError(ErrorType.UNKNOWN, message, retryable = false)
    }
}

enum class ErrorType {
    NETWORK,
    AUTHENTICATION,
    RATE_LIMIT,
    INVALID_INPUT,
    SERVER_ERROR,
    UNKNOWN
}

// Custom exception
class AgbaraException(
    val errorCode: ErrorCode,
    override val message: String?
) : Exception(message)

enum class ErrorCode(val code: String) {
    INITIALIZATION_FAILED("INIT_FAILED"),
    NETWORK_ERROR("NETWORK_ERROR"),
    AUTHENTICATION_FAILED("AUTH_FAILED"),
    RATE_LIMIT_EXCEEDED("RATE_LIMIT"),
    INVALID_REQUEST("INVALID_REQUEST"),
    SERVER_ERROR("SERVER_ERROR"),
    BATCH_FAILED("BATCH_FAILED"),
    SYNC_FAILED("SYNC_FAILED"),
    PRELOAD_FAILED("PRELOAD_FAILED"),
    UNKNOWN("UNKNOWN")
}

// Expert types
enum class ExpertType {
    TEXT,
    VISION,
    AUDIO,
    VIDEO,
    CODE,
    MATH,
    CULTURE,
    MIXED
}

// Model sizes
enum class ModelSize {
    SMALL,
    MEDIUM,
    LARGE
}

// Igbo dialects
enum class IgboDialect {
    STANDARD,
    OWA,
    ONITSHA
}

// Configuration models
data class AgbaraConfig(
    // API Configuration
    val apiKey: String,
    val baseUrl: String = "https://api.agbara.ai",
    @SerializedName("web_socket_url")
    val webSocketUrl: String = "wss://api.agbara.ai/ws/chat",

    // AI Configuration
    @SerializedName("enable_local_ai")
    var enableLocalAI: Boolean = true,
    @SerializedName("enable_remote_ai")
    var enableRemoteAI: Boolean = true,
    @SerializedName("local_model_path")
    var localModelPath: String = "",
    @SerializedName("local_model_size")
    var localModelSize: ModelSize = ModelSize.SMALL,

    // Performance
    @SerializedName("max_concurrent_requests")
    var maxConcurrentRequests: Int = 5,
    @SerializedName("request_timeout")
    var requestTimeout: Int = 30000,
    @SerializedName("cache_enabled")
    var cacheEnabled: Boolean = true,
    @SerializedName("cache_max_size")
    var cacheMaxSize: Int = 100,

    // Privacy
    @SerializedName("enable_encryption")
    var enableEncryption: Boolean = true,
    @SerializedName("data_retention_days")
    var dataRetentionDays: Int = 30,
    @SerializedName("allow_analytics")
    var allowAnalytics: Boolean = false,

    // Igbo Language
    @SerializedName("igbo_mode")
    var igboMode: Boolean = false,
    @SerializedName("igbo_dialect")
    var igboDialect: IgboDialect = IgboDialect.STANDARD,

    // Debug
    @SerializedName("enable_logging")
    var enableLogging: Boolean = true,
    @SerializedName("log_level")
    var logLevel: LogLevel = LogLevel.INFO
) {
    companion object {
        fun fromOptions(options: AgbaraClientOptions, apiKey: String): AgbaraConfig {
            return AgbaraConfig(
                apiKey = apiKey,
                enableLocalAI = options.enableLocalAI,
                enableRemoteAI = options.enableRemoteAI,
                localModelPath = options.localModelPath,
                localModelSize = options.localModelSize,
                maxConcurrentRequests = options.maxConcurrentRequests,
                requestTimeout = options.requestTimeout,
                cacheEnabled = options.cacheEnabled,
                cacheMaxSize = options.cacheMaxSize,
                enableEncryption = options.enableEncryption,
                dataRetentionDays = options.dataRetentionDays,
                allowAnalytics = options.allowAnalytics,
                igboMode = options.igboMode,
                igboDialect = options.igboDialect,
                enableLogging = options.enableLogging,
                logLevel = options.logLevel
            )
        }
    }
}

// Performance metrics
data class PerformanceMetrics(
    @SerializedName("avg_response_time")
    val avgResponseTime: Double,
    @SerializedName("cache_hit_rate")
    val cacheHitRate: Float,
    @SerializedName("battery_usage")
    val batteryUsage: Float,
    @SerializedName("memory_usage")
    val memoryUsage: Long,
    @SerializedName("active_requests")
    val activeRequests: Int
)

// Cache configuration
data class CacheConfig(
    val enabled: Boolean = true,
    val maxSize: Int = 100,
    @SerializedName("ttl_seconds")
    val ttlSeconds: Int = 3600
)

// Log levels
enum class LogLevel {
    DEBUG,
    INFO,
    WARN,
    ERROR
}

// Platform integration models
data class UserVerification(
    val userId: String,
    val verified: Boolean,
    val userData: UserData? = null
)

data class UserData(
    val name: String,
    val email: String,
    @SerializedName("digital_id")
    val digitalId: String?,
    @SerializedName("created_at")
    val createdAt: Date
)

data class Transaction(
    val id: String,
    val amount: Double,
    @SerializedName("sender_id")
    val senderId: String,
    @SerializedName("recipient_id")
    val recipientId: String,
    val timestamp: Date,
    val location: String? = null,
    val status: String
)

// Ikorochat-specific models
sealed class ChatCategory {
    object GENERAL : ChatCategory()
    object MARKETPLACE : ChatCategory()
    object TRANSACTION : ChatCategory()
    object HELP : ChatCategory()
    object EMERGENCY : ChatCategory()
}

sealed class ChatAssistance {
    data class Success(
        val suggestion: String,
        val category: ChatCategory,
        val confidence: Float
    ) : ChatAssistance()

    data class Error(val error: AgbaraError) : ChatAssistance()
}

sealed class MarketAnalysis {
    data class Success(
        @SerializedName("price_recommendation")
        val priceRecommendation: Double,
        @SerializedName("demand_level")
        val demandLevel: DemandLevel,
        @SerializedName("category_rank")
        val categoryRank: Int,
        val suggestions: List<String>
    ) : MarketAnalysis()

    data class Error(val error: AgbaraError) : MarketAnalysis()
}

enum class DemandLevel {
    LOW,
    MEDIUM,
    HIGH
}

sealed class FraudAnalysis {
    data class Success(
        @SerializedName("risk_level")
        val riskLevel: RiskLevel,
        @SerializedName("suspicious_patterns")
        val suspiciousPatterns: List<String>,
        val recommendation: FraudRecommendation,
        val confidence: Float
    ) : FraudAnalysis()

    data class Error(val error: AgbaraError) : FraudAnalysis()
}

enum class RiskLevel {
    LOW,
    MEDIUM,
    HIGH
}

enum class FraudRecommendation {
    APPROVE,
    REJECT,
    REQUIRES_REVIEW
}