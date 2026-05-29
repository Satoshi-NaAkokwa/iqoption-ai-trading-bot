// Offline Manager for queueing and syncing messages
package com.agbara.sdk.offline

import android.content.Context
import android.content.SharedPreferences
import com.agbara.sdk.config.AgbaraConfig
import com.agbara.sdk.models.AgbaraAIRequest
import com.agbara.sdk.models.AgbaraAIResponse
import com.agbara.sdk.models.AgbaraAIResponseData
import com.agbara.sdk.models.SyncResult
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.ConcurrentLinkedQueue

class OfflineManager(
    private val context: Context,
    private val config: AgbaraConfig
) {
    private val preferences: SharedPreferences = context.getSharedPreferences("agbara_offline", Context.MODE_PRIVATE)
    private val gson = Gson()
    private val messageQueue = ConcurrentLinkedQueue<QueuedMessage>()
    private val maxQueueSize = 1000

    suspend fun initialize() = withContext(Dispatchers.IO) {
        AgbaraLogger.info("OfflineManager", "Offline manager initialized")
        loadQueueFromStorage()
    }

    suspend fun queueMessage(request: AgbaraAIRequest) = withContext(Dispatchers.IO) {
        if (messageQueue.size >= maxQueueSize) {
            AgbaraLogger.warn("OfflineManager", "Queue is full, message not queued")
            return@withContext
        }

        val queuedMessage = QueuedMessage(
            id = generateId(),
            request = request,
            timestamp = System.currentTimeMillis(),
            attempts = 0,
            status = QueueStatus.PENDING
        )

        messageQueue.add(queuedMessage)
        saveQueueToStorage()

        AgbaraLogger.info("OfflineManager", "Message queued: ${queuedMessage.id}")
    }

    suspend fun sync(apiClient: com.agbara.sdk.network.ApiClient): SyncResult = withContext(Dispatchers.IO) {
        var synced = 0
        var failed = 0

        val iterator = messageQueue.iterator()
        while (iterator.hasNext()) {
            val queuedMessage = iterator.next()

            if (queuedMessage.status == QueueStatus.PENDING) {
                try {
                    // Update status to processing
                    queuedMessage.status = QueueStatus.PROCESSING
                    queuedMessage.attempts++
                    saveQueueToStorage()

                    // Process the message
                    val response = apiClient.process(queuedMessage.request)

                    // Save response
                    saveResponse(queuedMessage.id, response)

                    // Mark as completed
                    queuedMessage.status = QueueStatus.COMPLETED
                    synced++

                    // Remove from queue
                    iterator.remove()

                    AgbaraLogger.info("OfflineManager", "Message synced: ${queuedMessage.id}")

                } catch (e: Exception) {
                    AgbaraLogger.error("OfflineManager", "Sync failed for ${queuedMessage.id}", e)

                    if (queuedMessage.attempts >= 3) {
                        // Max retries reached, mark as failed
                        queuedMessage.status = QueueStatus.FAILED
                        failed++
                    } else {
                        // Retry later
                        queuedMessage.status = QueueStatus.PENDING
                    }

                    saveQueueToStorage()
                }
            }
        }

        saveQueueToStorage()

        SyncResult.Success(
            messagesSynced = synced,
            messagesFailed = failed
        )
    }

    suspend fun getQueueSize(): Int = withContext(Dispatchers.IO) {
        messageQueue.size
    }

    suspend fun clearQueue() = withContext(Dispatchers.IO) {
        messageQueue.clear()
        preferences.edit().clear().apply()
        AgbaraLogger.info("OfflineManager", "Queue cleared")
    }

    private fun loadQueueFromStorage() {
        val queueJson = preferences.getString("queue", "[]")
        val queueType = object : TypeToken<List<QueuedMessage>>() {}.type
        val savedQueue: List<QueuedMessage> = gson.fromJson(queueJson, queueType) ?: emptyList()

        savedQueue.forEach { messageQueue.add(it) }

        AgbaraLogger.info("OfflineManager", "Loaded ${savedQueue.size} messages from storage")
    }

    private fun saveQueueToStorage() {
        val queueJson = gson.toJson(messageQueue.toList())
        preferences.edit()
            .putString("queue", queueJson)
            .apply()
    }

    private fun saveResponse(messageId: String, response: AgbaraAIResponseData) {
        val responseJson = gson.toJson(response)
        preferences.edit()
            .putString("response_$messageId", responseJson)
            .apply()
    }

    private fun generateId(): String {
        return "offline_${System.currentTimeMillis()}_${(0..9999).random()}"
    }

    fun cleanup() {
        clearQueue()
        AgbaraLogger.info("OfflineManager", "Offline manager cleaned up")
    }

    data class QueuedMessage(
        val id: String,
        val request: AgbaraAIRequest,
        val timestamp: Long,
        var attempts: Int,
        var status: QueueStatus
    )

    enum class QueueStatus {
        PENDING,
        PROCESSING,
        COMPLETED,
        FAILED
    }
}