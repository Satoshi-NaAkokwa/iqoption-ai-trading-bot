// Demo App - Agbara SDK Integration Example
// This demonstrates how to integrate Agbara SDK into an Android app

package com.agbara.demo

import android.os.Bundle
import android.util.Log
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.agbara.sdk.*
import kotlinx.coroutines.launch

class DemoActivity : AppCompatActivity() {

    private lateinit var agbaraClient: AgbaraClient
    private lateinit var messageInput: EditText
    private lateinit var sendButton: Button
    private lateinit var responseText: TextView
    private lateinit var proverbText: TextView
    private lateinit var statusText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_demo)

        // Initialize views
        messageInput = findViewById(R.id.messageInput)
        sendButton = findViewById(R.id.sendButton)
        responseText = findViewById(R.id.responseText)
        proverbText = findViewById(R.id.proverbText)
        statusText = findViewById(R.id.statusText)

        // Initialize Agbara SDK
        initializeAgbaraSDK()

        // Load an Igbo proverb
        loadIgboProverb()

        // Setup send button
        sendButton.setOnClickListener {
            sendMessage()
        }
    }

    private fun initializeAgbaraSDK() {
        try {
            // Create Agbara client
            agbaraClient = AgbaraClient.create(
                context = this,
                apiKey = BuildConfig.AGBARA_API_KEY,
                options = {
                    enableRemoteAI = true
                    enableLocalAI = false // Set to true if you have local models
                    enableCache = true
                    enableOfflineQueue = true
                    cacheMaxSize = 50
                    logLevel = LogLevel.INFO
                }
            )

            // Get current user ID (in a real app, get from auth)
            val userId = "user_${System.currentTimeMillis()}"

            // Set user ID for tracking
            agbaraClient.setUserId(userId)

            statusText.text = "✓ SDK Initialized"
            statusText.setTextColor(resources.getColor(android.R.color.holo_green_dark))

            Log.d("AgbaraDemo", "SDK initialized successfully")

        } catch (e: Exception) {
            statusText.text = "✗ Initialization Failed: ${e.message}"
            statusText.setTextColor(resources.getColor(android.R.color.holo_red_dark))
            Log.e("AgbaraDemo", "SDK initialization failed", e)
        }
    }

    private fun loadIgboProverb() {
        lifecycleScope.launch {
            try {
                val proverb = agbaraClient.getIgboProverb()
                
                proverbText.text = buildString {
                    append("🌟 ${proverb.text}\n\n")
                    append("📖 ${proverb.translation}\n\n")
                    append("💡 ${proverb.meaning}")
                }

            } catch (e: Exception) {
                proverbText.text = "Failed to load proverb: ${e.message}"
                Log.e("AgbaraDemo", "Failed to load proverb", e)
            }
        }
    }

    private fun sendMessage() {
        val message = messageInput.text.toString().trim()
        
        if (message.isEmpty()) {
            Toast.makeText(this, "Please enter a message", Toast.LENGTH_SHORT).show()
            return
        }

        sendButton.isEnabled = false
        sendButton.text = "Processing..."
        responseText.text = "Processing your message..."

        lifecycleScope.launch {
            try {
                // Create request
                val request = AgbaraAIRequest(
                    userId = agbaraClient.getUserId(),
                    message = message,
                    igboMode = false, // Set to true for Igbo language support
                    streaming = false  // Set to true for streaming responses
                )

                // Send message
                agbaraClient.processMessage(request) { response ->
                    runOnUiThread {
                        when (response) {
                            is AgbaraAIResponse.Success -> {
                                val data = response.data
                                
                                responseText.text = buildString {
                                    append("Response:\n${data.response}\n\n")
                                    append("Expert: ${data.expertUsed}\n")
                                    append("Processing Time: ${data.processingTime}s\n")
                                    append("Confidence: ${(data.confidence * 100).toInt()}%\n")
                                }

                                Log.d("AgbaraDemo", "Message processed successfully")
                            }
                            
                            is AgbaraAIResponse.Error -> {
                                responseText.text = "Error: ${response.error.message}"
                                Log.e("AgbaraDemo", "Message processing failed", response.error)
                            }
                        }
                        
                        sendButton.isEnabled = true
                        sendButton.text = "Send"
                    }
                }

            } catch (e: Exception) {
                responseText.text = "Error: ${e.message}"
                sendButton.isEnabled = true
                sendButton.text = "Send"
                Log.e("AgbaraDemo", "Failed to send message", e)
            }
        }
    }

    private fun demonstrateStreamingResponse() {
        lifecycleScope.launch {
            try {
                val request = AgbaraAIRequest(
                    userId = agbaraClient.getUserId(),
                    message = "Tell me a story about African culture",
                    streaming = true
                )

                var fullResponse = ""
                
                agbaraClient.processMessageStream(request) { chunk ->
                    when (chunk) {
                        is StreamChunk.Progress -> {
                            fullResponse += chunk.text
                            responseText.text = fullResponse
                        }
                        is StreamChunk.Complete -> {
                            responseText.text = "Streaming complete!\n\n$fullResponse"
                        }
                        is StreamChunk.Error -> {
                            responseText.text = "Streaming error: ${chunk.message}"
                        }
                    }
                }

            } catch (e: Exception) {
                responseText.text = "Error: ${e.message}"
            }
        }
    }

    private fun demonstrateIgboTranslation() {
        lifecycleScope.launch {
            try {
                // Translate Igbo to English
                val translation = agbaraClient.translateIgbo(
                    text = "Ndeewo, ka ị mere?",
                    direction = TranslationDirection.IGBO_TO_ENGLISH
                )

                responseText.text = buildString {
                    append("Igbo: ${translation.originalText}\n")
                    append("English: ${translation.text}\n")
                }

            } catch (e: Exception) {
                responseText.text = "Error: ${e.message}"
            }
        }
    }

    private fun demonstrateCulturalConcept() {
        lifecycleScope.launch {
            try {
                // Explain a cultural concept
                val concept = agbaraClient.explainCulturalConcept("Chi")

                responseText.text = buildString {
                    append("Concept: ${concept.name}\n\n")
                    append("Explanation:\n${concept.explanation}\n\n")
                    append("Examples:\n")
                    concept.examples.forEach { example ->
                        append("  - $example\n")
                    }
                    append("\nRelated:\n")
                    concept.relatedConcepts.forEach { related ->
                        append("  - $related\n")
                    }
                }

            } catch (e: Exception) {
                responseText.text = "Error: ${e.message}"
            }
        }
    }

    private fun demonstrateOfflineQueue() {
        lifecycleScope.launch {
            try {
                // Queue a message when offline
                val request = AgbaraAIRequest(
                    userId = agbaraClient.getUserId(),
                    message = "This message will be queued and sent when online"
                )

                val offlineManager = agbaraClient.getOfflineManager()
                offlineManager.queueMessage(request)

                val queueSize = offlineManager.getQueueSize()
                responseText.text = "Message queued! Queue size: $queueSize"

                Toast.makeText(this, "Message queued for later", Toast.LENGTH_SHORT).show()

            } catch (e: Exception) {
                responseText.text = "Error: ${e.message}"
            }
        }
    }

    private fun demonstrateCache() {
        lifecycleScope.launch {
            try {
                val cacheManager = agbaraClient.getCacheManager()
                
                // Get cache statistics
                val cacheSize = cacheManager.getSize()
                val cacheCapacity = cacheManager.getCapacity()
                val hitRate = cacheManager.getCacheHitRate()

                responseText.text = buildString {
                    append("Cache Statistics:\n")
                    append("Size: $cacheSize / $cacheCapacity\n")
                    append("Hit Rate: ${(hitRate * 100).toInt()}%\n")
                }

            } catch (e: Exception) {
                responseText.text = "Error: ${e.message}"
            }
        }
    }

    private fun demonstrateIkorochatIntegration() {
        lifecycleScope.launch {
            try {
                // Ikorochat-specific integration
                val chatAI = IkoroChatIntelligence(agbaraClient)
                
                chatAI.assistChat(
                    userId = agbaraClient.getUserId(),
                    message = "I want to buy this product",
                    context = ChatContext(
                        isMarketplace = true,
                        productName = "Sample Product",
                        productPrice = 100.0
                    )
                ) { assistance ->
                    when (assistance) {
                        is ChatAssistance.Success -> {
                            responseText.text = buildString {
                                append("Suggestion:\n${assistance.suggestion}\n\n")
                                append("Category: ${assistance.category}\n")
                                append("Confidence: ${(assistance.confidence * 100).toInt()}%\n")
                            }
                        }
                        is ChatAssistance.Error -> {
                            responseText.text = "Error: ${assistance.error.message}"
                        }
                    }
                }

            } catch (e: Exception) {
                responseText.text = "Error: ${e.message}"
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Cleanup resources
        try {
            agbaraClient.cleanup()
        } catch (e: Exception) {
            Log.e("AgbaraDemo", "Failed to cleanup", e)
        }
    }
}