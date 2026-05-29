// API Client for HTTP and WebSocket communication
package com.agbara.sdk.network

import android.content.Context
import com.agbara.sdk.config.AgbaraConfig
import com.agbara.sdk.models.*
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

class ApiClient(
    private val context: Context,
    private val config: AgbaraConfig
) {
    private val gson: Gson = GsonBuilder()
        .setDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
        .create()

    private val okHttpClient: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(config.requestTimeout.toLong(), TimeUnit.MILLISECONDS)
        .readTimeout(config.requestTimeout.toLong(), TimeUnit.MILLISECONDS)
        .writeTimeout(config.requestTimeout.toLong(), TimeUnit.MILLISECONDS)
        .addInterceptor(createLoggingInterceptor())
        .addInterceptor(createAuthInterceptor())
        .build()

    private val webSocketClient: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(10_000, TimeUnit.MILLISECONDS)
        .readTimeout(0, TimeUnit.MILLISECONDS) // No timeout for streaming
        .writeTimeout(10_000, TimeUnit.MILLISECONDS)
        .addInterceptor(createAuthInterceptor())
        .build()

    var currentUserId: String? = null

    fun setUserId(userId: String) {
        currentUserId = userId
    }

    suspend fun process(request: AgbaraAIRequest): AgbaraAIResponseData = withContext(Dispatchers.IO) {
        try {
            val endpoint = if (request.igboMode) {
                "/v1/chat/completions"
            } else {
                "/v1/chat/completions"
            }

            val payload = JSONObject().apply {
                put("model", if (request.igboMode) "agbara-igbo" else "agbara")
                put("messages", listOf(
                    JSONObject().apply {
                        put("role", "user")
                        put("content", request.message)
                    }
                ))
                put("stream", false)
                put("user", request.userId)
                request.preferredExpert?.let { put("expert", it) }
                request.expertModel?.let { put("expert_model", it) }
                request.context?.let { put("context", JSONObject(it)) }
            }

            val requestBody = payload.toString()
                .toRequestBody("application/json".toMediaType())

            val httpRequest = Request.Builder()
                .url("${config.baseUrl}$endpoint")
                .post(requestBody)
                .build()

            val response = okHttpClient.newCall(httpRequest).execute()

            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                val jsonResponse = JSONObject(responseBody ?: "")

                if (jsonResponse.has("choices")) {
                    val choices = jsonResponse.getJSONArray("choices")
                    if (choices.length() > 0) {
                        val choice = choices.getJSONObject(0)
                        val message = choice.getJSONObject("message")
                        val content = message.getString("content")

                        return@withContext AgbaraAIResponseData(
                            response = content,
                            expertUsed = jsonResponse.optString("expert_used", "mixed-experts"),
                            processingTime = jsonResponse.optDouble("processing_time", 0.0),
                            confidence = jsonResponse.optDouble("confidence", 0.9).toFloat(),
                            metadata = jsonResponse.optJSONObject("metadata")?.let { metadata ->
                                mapOf(
                                    "source" to metadata.optString("source"),
                                    "model" to metadata.optString("model")
                                )
                            }
                        )
                    }
                }

                throw AgbaraException(ErrorCode.INVALID_REQUEST, "Invalid response format")
            } else {
                throw AgbaraException(
                    ErrorCode.SERVER_ERROR,
                    "API error: ${response.code} - ${response.message}"
                )
            }
        } catch (e: IOException) {
            AgbaraLogger.error("ApiClient", "Network error", e)
            throw AgbaraException(
                ErrorCode.NETWORK_ERROR,
                "Network error: ${e.message}",
                retryable = true
            )
        } catch (e: Exception) {
            AgbaraLogger.error("ApiClient", "API error", e)
            throw AgbaraException(
                ErrorCode.UNKNOWN,
                "API error: ${e.message}"
            )
        }
    }

    suspend fun processStream(
        request: AgbaraAIRequest,
        callback: (StreamChunk) -> Unit
    ) = withContext(Dispatchers.IO) {
        try {
            val endpoint = "/v1/chat/completions"
            val payload = JSONObject().apply {
                put("model", if (request.igboMode) "agbara-igbo" else "agbara")
                put("messages", listOf(
                    JSONObject().apply {
                        put("role", "user")
                        put("content", request.message)
                    }
                ))
                put("stream", true)
                put("user", request.userId)
            }

            val requestBuilder = Request.Builder()
                .url("${config.baseUrl}$endpoint")
                .post(payload.toString().toRequestBody("application/json".toMediaType()))

            val webSocket = webSocketClient.newWebSocket(
                requestBuilder.build(),
                object : WebSocketListener() {
                    override fun onOpen(webSocket: WebSocket, response: Response) {
                        AgbaraLogger.debug("ApiClient", "WebSocket connected")
                    }

                    override fun onMessage(webSocket: WebSocket, text: String) {
                        try {
                            if (text.startsWith("data: ")) {
                                val data = text.substring(6)
                                if (data == "[DONE]") {
                                    callback(StreamChunk("", StreamStatus.COMPLETE))
                                    webSocket.close(1000, "Stream complete")
                                    return
                                }

                                val jsonResponse = JSONObject(data)
                                if (jsonResponse.has("choices")) {
                                    val choices = jsonResponse.getJSONArray("choices")
                                    if (choices.length() > 0) {
                                        val choice = choices.getJSONObject(0)
                                        val delta = choice.getJSONObject("delta")
                                        val content = delta.optString("content", "")

                                        if (content.isNotEmpty()) {
                                            callback(StreamChunk(content, StreamStatus.PROGRESS))
                                        }
                                    }
                                }
                            }
                        } catch (e: Exception) {
                            AgbaraLogger.error("ApiClient", "Stream parsing error", e)
                            callback(StreamChunk(e.message ?: "Stream error", StreamStatus.ERROR))
                        }
                    }

                    override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                        AgbaraLogger.debug("ApiClient", "WebSocket closing: $code - $reason")
                    }

                    override fun onFailure(
                        webSocket: WebSocket,
                        t: Throwable,
                        response: Response?
                    ) {
                        AgbaraLogger.error("ApiClient", "WebSocket error", t)
                        callback(StreamChunk(t.message ?: "WebSocket error", StreamStatus.ERROR))
                    }
                }
            )

            // Wait for stream to complete
            while (true) {
                kotlinx.coroutines.delay(100)
            }

        } catch (e: Exception) {
            AgbaraLogger.error("ApiClient", "Stream error", e)
            throw AgbaraException(
                ErrorCode.NETWORK_ERROR,
                "Stream error: ${e.message}",
                retryable = true
            )
        }
    }

    fun isNetworkAvailable(): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE)
                as? android.net.ConnectivityManager

        val network = connectivityManager?.activeNetwork
        val capabilities = connectivityManager?.getNetworkCapabilities(network)

        return capabilities != null
    }

    fun getBatteryUsage(): Float {
        // Estimate battery usage based on active operations
        // This would use BatteryManager in a real implementation
        return 0.0f
    }

    private fun createLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = when (config.logLevel) {
                LogLevel.DEBUG -> HttpLoggingInterceptor.Level.BODY
                LogLevel.INFO -> HttpLoggingInterceptor.Level.BASIC
                else -> HttpLoggingInterceptor.Level.NONE
            }
        }
    }

    private fun createAuthInterceptor(): Interceptor {
        return Interceptor { chain ->
            val originalRequest = chain.request()
            val requestBuilder = originalRequest.newBuilder()
                .header("Authorization", "Bearer ${config.apiKey}")
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")

            chain.proceed(requestBuilder.build())
        }
    }

    fun getPlatformClient(): PlatformClient {
        return PlatformClient(context, config)
    }
}

class PlatformClient(
    private val context: Context,
    private val config: AgbaraConfig
) {
    private val gson: Gson = Gson()
    private val okHttpClient: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(10_000, TimeUnit.MILLISECONDS)
        .readTimeout(30_000, TimeUnit.MILLISECONDS)
        .addInterceptor(Interceptor { chain ->
            val originalRequest = chain.request()
            val requestBuilder = originalRequest.newBuilder()
                .header("Authorization", "Bearer ${config.apiKey}")
                .header("X-Platform", "ikoro-chat-android")

            chain.proceed(requestBuilder.build())
        })
        .build()

    suspend fun verifyUser(userId: String): UserVerification = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("https://api.agbara.ai/users/$userId/verify")
                .get()
                .build()

            val response = okHttpClient.newCall(request).execute()

            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                val jsonResponse = JSONObject(responseBody ?: "")

                UserVerification(
                    userId = userId,
                    verified = jsonResponse.optBoolean("verified", false),
                    userData = jsonResponse.optJSONObject("user")?.let { user ->
                        UserData(
                            name = user.optString("name"),
                            email = user.optString("email"),
                            digitalId = user.optString("digital_id"),
                            createdAt = java.util.Date()
                        )
                    }
                )
            } else {
                throw AgbaraException(
                    ErrorCode.AUTHENTICATION_FAILED,
                    "User verification failed"
                )
            }
        } catch (e: Exception) {
            AgbaraLogger.error("PlatformClient", "Verify user error", e)
            throw AgbaraException(
                ErrorCode.NETWORK_ERROR,
                "Verification error: ${e.message}",
                retryable = true
            )
        }
    }

    suspend fun processTransaction(
        userId: String,
        amount: Double,
        recipient: String,
        description: String?
    ): kotlin.Result<Transaction> = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
        try {
            val payload = JSONObject().apply {
                put("sender_id", userId)
                put("recipient_id", recipient)
                put("amount", amount)
                put("description", description)
                put("platform", "ikoro-chat")
            }

            val request = Request.Builder()
                .url("https://api.agbara.ai/transactions")
                .post(payload.toString().toRequestBody("application/json".toMediaType()))
                .build()

            val response = okHttpClient.newCall(request).execute()

            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                val jsonResponse = JSONObject(responseBody ?: "")

                kotlin.Result.success(
                    Transaction(
                        id = jsonResponse.optString("transaction_id"),
                        amount = amount,
                        senderId = userId,
                        recipientId = recipient,
                        timestamp = java.util.Date(),
                        location = null,
                        status = jsonResponse.optString("status")
                    )
                )
            } else {
                kotlin.Result.failure(
                    AgbaraException(
                        ErrorCode.SERVER_ERROR,
                        "Transaction failed"
                    )
                )
            }
        } catch (e: Exception) {
            AgbaraLogger.error("PlatformClient", "Transaction error", e)
            kotlin.Result.failure(
                AgbaraException(
                    ErrorCode.NETWORK_ERROR,
                    "Transaction error: ${e.message}",
                    retryable = true
                )
            )
        }
    }
}