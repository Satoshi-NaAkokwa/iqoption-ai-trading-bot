// Cache Manager for intelligent caching
package com.agbara.sdk.cache

import android.content.Context
import com.agbara.sdk.config.AgbaraConfig
import com.agbara.sdk.config.CacheConfig
import com.agbara.sdk.models.AgbaraAIResponseData
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue

class CacheManager(
    private val config: AgbaraConfig
) {
    private val cache = ConcurrentHashMap<String, CacheEntry>()
    private val accessQueue = ConcurrentLinkedQueue<String>()
    private var currentSize = 0
    private var totalRequests = 0
    private var cacheHits = 0
    private var totalResponseTime = 0.0

    private var cacheConfig: CacheConfig = CacheConfig(
        enabled = config.cacheEnabled,
        maxSize = config.cacheMaxSize,
        ttlSeconds = 3600
    )

    fun initialize() {
        AgbaraLogger.info("CacheManager", "Cache manager initialized")
    }

    fun setConfiguration(newConfig: CacheConfig) {
        this.cacheConfig = newConfig
        AgbaraLogger.info("CacheManager", "Cache config updated: enabled=${newConfig.enabled}, maxSize=${newConfig.maxSize}")
    }

    suspend fun get(key: String): AgbaraAIResponseData? = withContext(Dispatchers.IO) {
        if (!cacheConfig.enabled) {
            return@withContext null
        }

        totalRequests++

        val entry = cache[key]
        if (entry != null) {
            // Check if expired
            if (isExpired(entry)) {
                remove(key)
                return@withContext null
            }

            cacheHits++
            AgbaraLogger.debug("CacheManager", "Cache hit: $key")
            entry.data
        } else {
            null
        }
    }

    suspend fun put(key: String, data: AgbaraAIResponseData) = withContext(Dispatchers.IO) {
        if (!cacheConfig.enabled) {
            return@withContext
        }

        val now = System.currentTimeMillis()
        val entry = CacheEntry(
            data = data,
            timestamp = now,
            ttl = cacheConfig.ttlSeconds * 1000L
        )

        // If key exists, update it
        if (cache.containsKey(key)) {
            cache[key] = entry
            AgbaraLogger.debug("CacheManager", "Cache updated: $key")
            return@withContext
        }

        // Check size limit
        if (currentSize >= cacheConfig.maxSize) {
            evictOldest()
        }

        cache[key] = entry
        accessQueue.add(key)
        currentSize++

        AgbaraLogger.debug("CacheManager", "Cache added: $key (size: $currentSize/${cacheConfig.maxSize})")
    }

    suspend fun remove(key: String) = withContext(Dispatchers.IO) {
        cache.remove(key)
        accessQueue.remove(key)
        currentSize--
        AgbaraLogger.debug("CacheManager", "Cache removed: $key")
    }

    suspend fun clear() = withContext(Dispatchers.IO) {
        cache.clear()
        accessQueue.clear()
        currentSize = 0
        AgbaraLogger.info("CacheManager", "Cache cleared")
    }

    private fun evictOldest() {
        while (currentSize >= cacheConfig.maxSize && accessQueue.isNotEmpty()) {
            val oldestKey = accessQueue.poll()
            if (oldestKey != null) {
                cache.remove(oldestKey)
                currentSize--
                AgbaraLogger.debug("CacheManager", "Cache evicted: $oldestKey")
            }
        }
    }

    private fun isExpired(entry: CacheEntry): Boolean {
        val now = System.currentTimeMillis()
        return (now - entry.timestamp) > entry.ttl
    }

    fun getCacheHitRate(): Float {
        if (totalRequests == 0) return 0.0f
        return cacheHits.toFloat() / totalRequests.toFloat()
    }

    fun getAvgResponseTime(): Double {
        if (totalRequests == 0) return 0.0
        return totalResponseTime / totalRequests
    }

    fun recordResponseTime(timeMs: Double) {
        totalResponseTime += timeMs
    }

    fun cleanup() {
        clear()
        AgbaraLogger.info("CacheManager", "Cache manager cleaned up")
    }

    fun getSize(): Int = currentSize

    fun getCapacity(): Int = cacheConfig.maxSize

    private data class CacheEntry(
        val data: AgbaraAIResponseData,
        val timestamp: Long,
        val ttl: Long
    )
}