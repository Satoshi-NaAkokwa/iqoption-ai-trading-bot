package com.agbara.sdk

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.google.gson.Gson

/**
 * Logger for Agbara SDK
 */
object AgbaraLogger {
    private const val TAG = "AgbaraSDK"
    private var enableLogging = true
    private var minLogLevel = LogLevel.INFO

    fun enable(enabled: Boolean) {
        this.enableLogging = enabled
    }

    fun setMinLevel(level: LogLevel) {
        this.minLogLevel = level
    }

    fun debug(tag: String, message: String) {
        if (enableLogging && LogLevel.DEBUG >= minLogLevel) {
            Log.d("[$TAG]$tag", message)
        }
    }

    fun info(tag: String, message: String) {
        if (enableLogging && LogLevel.INFO >= minLogLevel) {
            Log.i("[$TAG]$tag", message)
        }
    }

    fun warn(tag: String, message: String) {
        if (enableLogging && LogLevel.WARN >= minLogLevel) {
            Log.w("[$TAG]$tag", message)
        }
    }

    fun error(tag: String, message: String, throwable: Throwable? = null) {
        if (enableLogging && LogLevel.ERROR >= minLogLevel) {
            if (throwable != null) {
                Log.e("[$TAG]$tag", message, throwable)
            } else {
                Log.e("[$TAG]$tag", message)
            }
        }
    }
}

/**
 * Security manager for encryption and data protection
 */
class SecurityManager(private val context: Context) {
    private val masterKeyAlias = "agbara_master_key"

    fun encryptData(data: String): String {
        // In a real implementation, use Android Keystore for encryption
        // For now, use a simple encoding
        return android.util.Base64.encodeToString(
            data.toByteArray(),
            android.util.Base64.DEFAULT
        )
    }

    fun decryptData(encryptedData: String): String {
        return String(
            android.util.Base64.decode(encryptedData, android.util.Base64.DEFAULT)
        )
    }

    fun hashData(data: String): String {
        return java.security.MessageDigest.getInstance("SHA-256")
            .digest(data.toByteArray())
            .joinToString("") { "%02x".format(it) }
    }
}

/**
 * Data persistence helper
 */
class DataPersistence(private val context: Context) {
    private val preferences: SharedPreferences = context.getSharedPreferences("agbara_data", Context.MODE_PRIVATE)
    private val gson = Gson()

    fun <T> save(key: String, data: T) {
        val json = gson.toJson(data)
        preferences.edit().putString(key, json).apply()
    }

    fun <T> load(key: String, type: Class<T>): T? {
        val json = preferences.getString(key, null) ?: return null
        return gson.fromJson(json, type)
    }

    fun remove(key: String) {
        preferences.edit().remove(key).apply()
    }

    fun clear() {
        preferences.edit().clear().apply()
    }

    fun contains(key: String): Boolean {
        return preferences.contains(key)
    }
}

/**
 * Network connectivity checker
 */
class NetworkConnectivity(private val context: Context) {

    fun isNetworkAvailable(): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE)
                as? android.net.ConnectivityManager ?: return false

        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return capabilities.hasCapability(android.net.NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    fun getNetworkType(): NetworkType {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE)
                as? android.net.ConnectivityManager ?: return NetworkType.NONE

        val network = connectivityManager.activeNetwork ?: return NetworkType.NONE
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return NetworkType.NONE

        return when {
            capabilities.hasTransport(android.net.NetworkCapabilities.TRANSPORT_WIFI) -> NetworkType.WIFI
            capabilities.hasTransport(android.net.NetworkCapabilities.TRANSPORT_CELLULAR) -> NetworkType.CELLULAR
            capabilities.hasTransport(android.net.NetworkCapabilities.TRANSPORT_ETHERNET) -> NetworkType.ETHERNET
            else -> NetworkType.NONE
        }
    }

    enum class NetworkType {
        NONE,
        WIFI,
        CELLULAR,
        ETHERNET
    }
}

/**
 * Performance monitor for tracking SDK performance
 */
class PerformanceMonitor {
    private val metrics = mutableMapOf<String, MutableList<Long>>()

    fun recordMetric(name: String, durationMs: Long) {
        if (!metrics.containsKey(name)) {
            metrics[name] = mutableListOf()
        }
        metrics[name]?.add(durationMs)
    }

    fun getAverageMetric(name: String): Double {
        val values = metrics[name] ?: return 0.0
        if (values.isEmpty()) return 0.0
        return values.average()
    }

    fun getP95Metric(name: String): Double {
        val values = metrics[name] ?: return 0.0
        if (values.isEmpty()) return 0.0
        val sorted = values.sorted()
        val index = (sorted.size * 0.95).toInt().coerceAtMost(sorted.size - 1)
        return sorted[index].toDouble()
    }

    fun getP99Metric(name: String): Double {
        val values = metrics[name] ?: return 0.0
        if (values.isEmpty()) return 0.0
        val sorted = values.sorted()
        val index = (sorted.size * 0.99).toInt().coerceAtMost(sorted.size - 1)
        return sorted[index].toDouble()
    }

    fun clear() {
        metrics.clear()
    }
}

/**
 * Utilities for common operations
 */
object Utils {
    fun generateRequestId(): String {
        return "req_${System.currentTimeMillis()}_${(0..9999).random()}"
    }

    fun generateUserId(): String {
        return "user_${System.currentTimeMillis()}_${(100000..999999).random()}"
    }

    fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }

    fun sanitizeInput(input: String): String {
        // Remove potentially dangerous characters
        return input.replace(Regex("[<>\"']"), "")
    }

    fun formatFileSize(bytes: Long): String {
        val kb = bytes / 1024.0
        val mb = kb / 1024.0
        val gb = mb / 1024.0

        return when {
            gb >= 1 -> "%.2f GB".format(gb)
            mb >= 1 -> "%.2f MB".format(mb)
            kb >= 1 -> "%.2f KB".format(kb)
            else -> "$bytes B"
        }
    }

    fun formatDate(timestamp: Long): String {
        val date = java.util.Date(timestamp)
        val format = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.getDefault())
        return format.format(date)
    }
}

/**
 * Validation utilities
 */
object Validation {
    fun validateApiKey(apiKey: String): Boolean {
        // Basic API key validation
        return apiKey.isNotEmpty() && apiKey.length >= 20
    }

    fun validateUserId(userId: String): Boolean {
        // Basic user ID validation
        return userId.isNotEmpty() && userId.matches(Regex("^[a-zA-Z0-9_-]+$"))
    }

    fun validateMessage(message: String): ValidationResult {
        return when {
            message.isEmpty() -> ValidationResult.ERROR("Message cannot be empty")
            message.length > 10000 -> ValidationResult.ERROR("Message too long (max 10,000 characters)")
            message.contains("<script>") -> ValidationResult.ERROR("Invalid content detected")
            else -> ValidationResult.SUCCESS
        }
    }

    sealed class ValidationResult {
        object SUCCESS : ValidationResult()
        data class ERROR(val message: String) : ValidationResult()
    }
}