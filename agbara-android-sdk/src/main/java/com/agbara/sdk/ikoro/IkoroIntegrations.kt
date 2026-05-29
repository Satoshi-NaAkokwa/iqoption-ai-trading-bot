// Ikorochat-specific integration modules for Agbara AI
package com.agbara.sdk.ikoro

import com.agbara.sdk.AgbaraClient
import com.agbara.sdk.models.*
import kotlinx.coroutines.*

/**
 * Chat Intelligence Assistant for Ikorochat
 * Provides AI-powered chat suggestions and assistance
 */
class IkoroChatIntelligence(
    private val agbaraClient: AgbaraClient
) {

    suspend fun assistChat(
        userId: String,
        message: String,
        context: ChatContext = ChatContext(),
        callback: (ChatAssistance) -> Unit
    ) {
        val prompt = buildString {
            append("You are an intelligent chat assistant for Ikorochat, a mesh messaging app. ")
            append("Help the user with their chat message:\n\n")
            append("User Message: $message\n")
            append("Chat Type: ${context.type}\n")
            
            if (context.isMarketplace) {
                append("Context: Marketplace conversation\n")
                append("Product: ${context.productName}\n")
                append("Price: ${context.productPrice} ₿\n")
                append("Category: ${context.category}\n")
                append("\nProvide helpful suggestions for:")
                append("- Negotiation strategies")
                append("- Product questions to ask")
                append("- Price recommendations")
                append("- Buying advice\n")
            } else if (context.isTransaction) {
                append("Context: Transaction discussion\n")
                append("Amount: ${context.transactionAmount} ₿\n")
                append("Recipient: ${context.recipient}\n")
                append("\nProvide helpful assistance for:")
                append("- Transaction safety tips")
                append("- Verification steps")
                append("- Security advice\n")
            } else {
                append("Provide helpful suggestions for:")
                append("- Response suggestions")
                append("- Conversation starters")
                append("- Polite responses")
                append("- Cultural sensitivity (Igbo language support if relevant)\n")
            }
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            context = mapOf(
                "app" to "ikoro-chat",
                "chat_context" to "general"
            )
        )

        agbaraClient.processMessage(request) { response ->
            when (response) {
                is AgbaraAIResponse.Success -> {
                    val assistance = parseChatAssistance(
                        response.data.response,
                        message
                    )
                    callback(assistance)
                }
                is AgbaraAIResponse.Error -> {
                    callback(ChatAssistance.Error(response.error))
                }
            }
        }
    }

    private fun parseChatAssistance(
        aiResponse: String,
        originalMessage: String
    ): ChatAssistance {
        // Parse the AI response and categorize the suggestions
        val suggestions = aiResponse.lines().filter { it.isNotBlank() }
        
        return ChatAssistance.Success(
            suggestion = suggestions.joinToString("\n"),
            category = categorizeMessage(originalMessage),
            confidence = 0.85f,
            suggestions = suggestions
        )
    }

    private fun categorizeMessage(message: String): ChatCategory {
        return when {
            message.contains("buy") || message.contains("price") ||
            message.contains("cost") || message.contains("pay") -> ChatCategory.MARKETPLACE
            
            message.contains("send") || message.contains("transfer") ||
            message.contains("₿") || message.contains("bitcoin") -> ChatCategory.TRANSACTION
            
            message.contains("help") || message.contains("how") ||
            message.contains("what") || message.contains("why") -> ChatCategory.HELP
            
            message.contains("emergency") || message.contains("SOS") ||
            message.contains("help me") -> ChatCategory.EMERGENCY
            
            else -> ChatCategory.GENERAL
        }
    }

    suspend fun generateSmartReplies(
        userId: String,
        message: String,
        context: ChatContext = ChatContext(),
        count: Int = 3
    ): List<String> = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Generate $count smart reply suggestions for this message in Ikorochat:\n\n")
            append("Original Message: $message\n")
            append("Context: ${context.type}\n")
            append("\nEach reply should be:")
            append("- Natural and conversational")
            append("- Polite and helpful")
            append("- Culturally appropriate")
            append("- Concise (under 140 characters)\n")
            append("\nFormat each suggestion on a new line:")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt
        )

        try {
            val response = agbaraClient.processMessage(request)
            if (response is AgbaraAIResponse.Success) {
                response.data.response.lines()
                    .filter { it.isNotBlank() }
                    .take(count)
                    .map { it.trim() }
            } else {
                emptyList()
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun analyzeConversationSentiment(
        userId: String,
        conversation: List<String>
    ): ConversationAnalysis = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Analyze the sentiment and tone of this conversation:\n\n")
            conversation.forEachIndexed { index, message ->
                append("Message ${index + 1}: $message\n")
            }
            append("\nProvide analysis of:")
            append("- Overall sentiment (positive/negative/neutral)")
            append("- Conversation tone (formal/casual/friendly)")
            append("- Potential issues or conflicts")
            append("- Suggested improvements")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt
        )

        try {
            val response = agbaraClient.processMessage(request)
            if (response is AgbaraAIResponse.Success) {
                ConversationAnalysis.Success(
                    sentiment = extractSentiment(response.data.response),
                    tone = extractTone(response.data.response),
                    issues = extractIssues(response.data.response),
                    suggestions = extractSuggestions(response.data.response),
                    confidence = response.data.confidence
                )
            } else {
                ConversationAnalysis.Error(response.error)
            }
        } catch (e: Exception) {
            ConversationAnalysis.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun extractSentiment(response: String): String {
        val sentimentRegex = """sentiment[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
        val match = sentimentRegex.find(response)
        return match?.groupValues?.get(1) ?: "neutral"
    }

    private fun extractTone(response: String): String {
        val toneRegex = """tone[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
        val match = toneRegex.find(response)
        return match?.groupValues?.get(1) ?: "casual"
    }

    private fun extractIssues(response: String): List<String> {
        val issuesSection = response.substringAfter("Potential issues:", "").substringBefore("Suggested")
        return issuesSection.lines()
            .filter { it.isNotBlank() && it.startsWith("-") }
            .map { it.trim().removePrefix("-").trim() }
    }

    private fun extractSuggestions(response: String): List<String> {
        val suggestionsSection = response.substringAfter("Suggested improvements:", "")
        return suggestionsSection.lines()
            .filter { it.isNotBlank() && it.startsWith("-") }
            .map { it.trim().removePrefix("-").trim() }
    }
}

/**
 * Market Analysis AI for Ikorochat Marketplace
 */
class IkoroMarketAnalyzer(
    private val agbaraClient: AgbaraClient
) {

    suspend fun analyzeProduct(
        userId: String,
        product: ProductData,
        marketData: MarketData = MarketData()
    ): MarketAnalysis = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Analyze this product for the Ikorochat marketplace:\n\n")
            append("=== PRODUCT INFORMATION ===\n")
            append("Name: ${product.name}\n")
            append("Category: ${product.category}\n")
            append("Price: ${product.price} ₿\n")
            append("Description: ${product.description}\n")
            append("Seller: ${product.sellerName}\n")
            append("Rating: ${product.rating}/5\n")
            append("Images: ${product.imageCount}\n")
            
            if (product.specifications.isNotEmpty()) {
                append("Specifications:\n")
                product.specifications.forEach { (key, value) ->
                    append("  $key: $value\n")
                }
            }
            
            append("\n=== MARKET DATA ===\n")
            append("Average Price: ${marketData.avgPrice} ₿\n")
            append("Min Price: ${marketData.minPrice} ₿\n")
            append("Max Price: ${marketData.maxPrice} ₿\n")
            append("Demand Level: ${marketData.demandLevel}\n")
            append("Competition: ${marketData.competitionLevel}\n")
            append("Recent Sales: ${marketData.recentSales}\n")
            append("Trending: ${marketData.isTrending}\n")
            
            append("\n=== ANALYSIS REQUIRED ===\n")
            append("Provide:\n")
            append("1. Price recommendation (min, max, optimal range)\n")
            append("2. Market demand assessment (LOW/MEDIUM/HIGH)\n")
            append("3. Competitive analysis (how many similar products, their prices)\n")
            append("4. Category ranking (1-10, where 1 is best)\n")
            append("5. Improvement suggestions (at least 5 specific recommendations)\n")
            append("6. Marketing strategy (how to promote this product)\n")
            append("7. Potential issues or concerns\n")
            append("\nFormat your response with clear sections.")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            preferredExpert = ExpertType.VISION,
            context = mapOf(
                "app" to "ikoro-chat",
                "feature" to "marketplace-analysis"
            )
        )

        try {
            val response = agbaraClient.processMessage(request)
            if (response is AgbaraAIResponse.Success) {
                parseMarketAnalysis(response.data.response, product, marketData)
            } else {
                MarketAnalysis.Error(response.error)
            }
        } catch (e: Exception) {
            MarketAnalysis.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun parseMarketAnalysis(
        response: String,
        product: ProductData,
        marketData: MarketData
    ): MarketAnalysis {
        return MarketAnalysis.Success(
            product = product,
            priceRecommendation = PriceRecommendation(
                minPrice = extractPrice(response, "min price") ?: marketData.minPrice * 0.9,
                maxPrice = extractPrice(response, "max price") ?: marketData.maxPrice * 1.1,
                optimalRange = extractPriceRange(response) ?: PriceRange(
                    marketData.avgPrice * 0.95,
                    marketData.avgPrice * 1.05
                ),
                reasoning = extractReasoning(response, "price")
            ),
            demandLevel = extractDemandLevel(response),
            categoryRank = extractCategoryRank(response),
            competitionLevel = extractCompetitionLevel(response),
            suggestions = extractSuggestions(response),
            marketingStrategy = extractMarketingStrategy(response),
            potentialIssues = extractPotentialIssues(response),
            overallScore = calculateOverallScore(response),
            confidence = 0.88f
        )
    }

    private fun extractPrice(response: String, label: String): Double? {
        val regex = """${label}[^\d]*(\d+(?:\.\d+)?)\s*₿""".toRegex(RegexOption.IGNORE_CASE)
        val match = regex.find(response)
        return match?.groupValues?.get(1)?.toDoubleOrNull()
    }

    private fun extractPriceRange(response: String): PriceRange? {
        val minPrice = extractPrice(response, "min price")
        val maxPrice = extractPrice(response, "max price")
        return if (minPrice != null && maxPrice != null) {
            PriceRange(minPrice, maxPrice)
        } else {
            null
        }
    }

    private fun extractReasoning(response: String, section: String): String {
        val sectionStart = response.indexOf("$section reasoning", ignoreCase = true)
        if (sectionStart == -1) return ""
        
        val sectionEnd = response.indexOf("\n\n", sectionStart + 1)
        if (sectionEnd == -1) return ""
        
        return response.substring(sectionStart + section.length + 1, sectionEnd)
            .trim()
            .removePrefix(":")
            .trim()
    }

    private fun extractDemandLevel(response: String): DemandLevel {
        val demandRegex = """demand\s+(?:level|assessment)[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
        val match = demandRegex.find(response)
        val level = match?.groupValues?.get(1)?.lowercase() ?: "medium"
        
        return when (level) {
            "low" -> DemandLevel.LOW
            "medium" -> DemandLevel.MEDIUM
            "high" -> DemandLevel.HIGH
            else -> DemandLevel.MEDIUM
        }
    }

    private fun extractCategoryRank(response: String): Int {
        val rankRegex = """category\s+rank[^\d]*(\d+)""".toRegex(RegexOption.IGNORE_CASE)
        val match = rankRegex.find(response)
        return match?.groupValues?.get(1)?.toIntOrNull() ?: 5
    }

    private fun extractCompetitionLevel(response: String): String {
        val compRegex = """competition[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
        val match = compRegex.find(response)
        return match?.groupValues?.get(1) ?: "MEDIUM"
    }

    private fun extractSuggestions(response: String): List<String> {
        val suggestionsSection = response.substringAfter("Improvement suggestions:")
            .substringBefore("\n\n")
        return suggestionsSection.lines()
            .filter { it.isNotBlank() && it.startsWith("-") }
            .map { it.trim().removePrefix("-").trim() }
            .take(5)
    }

    private fun extractMarketingStrategy(response: String): String {
        val strategySection = response.substringAfter("Marketing strategy:")
            .substringBefore("\n\n")
        return strategySection.trim()
    }

    private fun extractPotentialIssues(response: String): List<String> {
        val issuesSection = response.substringAfter("Potential issues:")
            .substringBefore("\n\n")
        return issuesSection.lines()
            .filter { it.isNotBlank() && it.startsWith("-") }
            .map { it.trim().removePrefix("-").trim() }
    }

    private fun calculateOverallScore(response: String): Float {
        // Simple scoring based on keyword presence
        var score = 0.5f
        
        if (response.contains("high demand", ignoreCase = true)) score += 0.2f
        if (response.contains("good competition", ignoreCase = true)) score += 0.1f
        if (response.contains("competitive price", ignoreCase = true)) score += 0.1f
        if (response.contains("unique features", ignoreCase = true)) score += 0.1f
        
        return score.coerceIn(0f, 1f)
    }
}

/**
 * Transaction Fraud Detection AI
 */
class IkoroTransactionAI(
    private val agbaraClient: AgbaraClient
) {

    suspend fun analyzeTransactionRisk(
        userId: String,
        transaction: TransactionData,
        userProfile: UserProfile
    ): FraudAnalysis = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Analyze this transaction for fraud risk:\n\n")
            append("=== TRANSACTION DETAILS ===\n")
            append("Transaction ID: ${transaction.id}\n")
            append("Amount: ${transaction.amount} ₿\n")
            append("Sender ID: ${transaction.senderId}\n")
            append("Recipient ID: ${transaction.recipientId}\n")
            append("Timestamp: ${transaction.timestamp}\n")
            append("Location: ${transaction.location}\n")
            append("Device: ${transaction.deviceInfo}\n")
            append("IP Address: ${transaction.ipAddress}\n")
            append("Description: ${transaction.description}\n")
            
            append("\n=== SENDER PROFILE ===\n")
            append("Account Age: ${userProfile.accountAge} days\n")
            append("Total Transactions: ${userProfile.totalTransactions}\n")
            append("Trust Score: ${userProfile.trustScore}/100\n")
            append("Verification Level: ${userProfile.verificationLevel}\n")
            append("Last Login: ${userProfile.lastLogin}\n")
            append("Login Location: ${userProfile.loginLocation}\n")
            append("Device Usage: ${userProfile.deviceUsage}\n")
            
            if (userProfile.suspiciousFlags.isNotEmpty()) {
                append("\nSuspicious Flags:\n")
                userProfile.suspiciousFlags.forEach { flag ->
                    append("  - $flag\n")
                }
            }
            
            append("\n=== RISK ASSESSMENT REQUIRED ===\n")
            append("Assess the following:\n")
            append("1. Fraud risk level (LOW/MEDIUM/HIGH)\n")
            append("2. Specific suspicious patterns or red flags\n")
            append("3. Recommendation (APPROVE/REJECT/REQUIRES_REVIEW)\n")
            append("4. Confidence score (0-1)\n")
            append("5. Additional verification needed?\n")
            append("6. Reasoning for your assessment\n")
            append("\nConsider these factors:\n")
            append("- Amount relative to user's typical transactions\n")
            append("- New recipient vs frequent recipient\n")
            append("- Location consistency\n")
            append("- Device consistency\n")
            append("- Time of transaction\n")
            append("- Transaction velocity\n")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            context = mapOf(
                "app" to "ikoro-chat",
                "feature" to "fraud-detection",
                "priority" to "HIGH"
            )
        )

        try {
            val response = agbaraClient.processMessage(request)
            if (response is AgbaraAIResponse.Success) {
                parseFraudAnalysis(response.data.response, transaction, userProfile)
            } else {
                FraudAnalysis.Error(response.error)
            }
        } catch (e: Exception) {
            FraudAnalysis.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun parseFraudAnalysis(
        response: String,
        transaction: TransactionData,
        userProfile: UserProfile
    ): FraudAnalysis {
        val riskLevel = extractRiskLevel(response)
        val suspiciousPatterns = extractSuspiciousPatterns(response)
        val recommendation = extractRecommendation(response)
        val confidence = extractConfidence(response)
        val reasoning = extractReasoning(response, "Reasoning")
        val verificationNeeded = extractVerificationNeeded(response)

        return FraudAnalysis.Success(
            transactionId = transaction.id,
            riskLevel = riskLevel,
            suspiciousPatterns = suspiciousPatterns,
            recommendation = recommendation,
            confidence = confidence,
            reasoning = reasoning,
            verificationNeeded = verificationNeeded,
            factors = extractRiskFactors(response),
            suggestedActions = extractSuggestedActions(response)
        )
    }

    private fun extractRiskLevel(response: String): RiskLevel {
        val riskRegex = """risk\s+level[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
        val match = riskRegex.find(response)
        val level = match?.groupValues?.get(1)?.lowercase() ?: "medium"
        
        return when (level) {
            "low" -> RiskLevel.LOW
            "medium" -> RiskLevel.MEDIUM
            "high" -> RiskLevel.HIGH
            else -> RiskLevel.MEDIUM
        }
    }

    private fun extractSuspiciousPatterns(response: String): List<String> {
        val patternsSection = response.substringAfter("Suspicious patterns:")
            .substringBefore("\n\n")
        return patternsSection.lines()
            .filter { it.isNotBlank() && it.startsWith("-") }
            .map { it.trim().removePrefix("-").trim() }
    }

    private fun extractRecommendation(response: String): FraudRecommendation {
        val recRegex = """recommendation[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
        val match = recRegex.find(response)
        val rec = match?.groupValues?.get(1)?.uppercase() ?: "REQUIRES_REVIEW"
        
        return try {
            FraudRecommendation.valueOf(rec)
        } catch (e: Exception) {
            FraudRecommendation.REQUIRES_REVIEW
        }
    }

    private fun extractConfidence(response: String): Float {
        val confRegex = """confidence[^\d]*(\d+(?:\.\d+)?)""".toRegex(RegexOption.IGNORE_CASE)
        val match = confRegex.find(response)
        return match?.groupValues?.get(1)?.toFloatOrNull() ?: 0.8f
    }

    private fun extractVerificationNeeded(response: String): Boolean {
        return response.contains("additional verification", ignoreCase = true)
    }

    private fun extractRiskFactors(response: String): List<String> {
        val factorsSection = response.substringAfter("Consider these factors:")
            .substringBefore("\n\n")
        return factorsSection.lines()
            .filter { it.isNotBlank() && it.startsWith("-") }
            .map { it.trim().removePrefix("-").trim() }
    }

    private fun extractSuggestedActions(response: String): List<String> {
        val actionsSection = response.substringAfter("Additional verification:")
            .substringBefore("\n\n")
        return actionsSection.lines()
            .filter { it.isNotBlank() && it.startsWith("-") }
            .map { it.trim().removePrefix("-").trim() }
    }
}

/**
 * Emergency Response AI for Ikorochat Emergency Mode
 */
class IkoroEmergencyAI(
    private val agbaraClient: AgbaraClient
) {

    suspend fun handleEmergency(
        userId: String,
        emergencyType: EmergencyType,
        location: LocationData,
        situationDescription: String
    ): EmergencyResponse = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("You are an emergency response AI assistant for Ikorochat. ")
            append("Help with this emergency:\n\n")
            append("=== EMERGENCY INFORMATION ===\n")
            append("Type: ${emergencyType.name}\n")
            append("Description: $situationDescription\n")
            append("Location: ${location.address}\n")
            append("Coordinates: ${location.latitude}, ${location.longitude}\n")
            append("Accuracy: ${location.accuracy}m\n")
            append("Timestamp: ${location.timestamp}\n")
            
            append("\n=== ASSISTANCE REQUIRED ===\n")
            append("Provide:\n")
            append("1. Immediate actions to take\n")
            append("2. First aid instructions (if applicable)\n")
            append("3. Contact information for emergency services\n")
            append("4. Nearby resources (hospitals, police, etc.)\n")
            append("5. Safety precautions\n")
            append("6. How to help others nearby\n")
            append("7. Information to provide to responders\n")
            append("\nBe clear, concise, and actionable. Use Igbo language if appropriate.")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            context = mapOf(
                "app" to "ikoro-chat",
                "feature" to "emergency-mode",
                "priority" to "CRITICAL"
            )
        )

        try {
            val response = agbaraClient.processMessage(request)
            if (response is AgbaraAIResponse.Success) {
                parseEmergencyResponse(response.data.response, emergencyType, location)
            } else {
                EmergencyResponse.Error(response.error)
            }
        } catch (e: Exception) {
            EmergencyResponse.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun parseEmergencyResponse(
        response: String,
        emergencyType: EmergencyType,
        location: LocationData
    ): EmergencyResponse {
        val immediateActions = extractSection(response, "Immediate actions")
        val firstAidInstructions = extractSection(response, "First aid instructions")
        val contactInfo = extractSection(response, "Contact information")
        val nearbyResources = extractSection(response, "Nearby resources")
        val safetyPrecautions = extractSection(response, "Safety precautions")
        val howToHelpOthers = extractSection(response, "How to help others")
        val informationForResponders = extractSection(response, "Information to provide")

        return EmergencyResponse.Success(
            emergencyType = emergencyType,
            immediateActions = immediateActions,
            firstAidInstructions = firstAidInstructions,
            contactInfo = contactInfo,
            nearbyResources = nearbyResources,
            safetyPrecautions = safetyPrecautions,
            howToHelpOthers = howToHelpOthers,
            informationForResponders = informationForResponders,
            location = location,
            confidence = 0.92f
        )
    }

    private fun extractSection(response: String, sectionName: String): List<String> {
        val sectionStart = response.indexOf(sectionName, ignoreCase = true)
        if (sectionStart == -1) return emptyList()
        
        val sectionEnd = response.indexOf("\n\n", sectionStart + 1)
        val sectionContent = if (sectionEnd == -1) {
            response.substring(sectionStart + sectionName.length + 1)
        } else {
            response.substring(sectionStart + sectionName.length + 1, sectionEnd)
        }
        
        return sectionContent.lines()
            .filter { it.isNotBlank() }
            .map { it.trim().removePrefix("-").trim() }
            .filter { it.isNotEmpty() }
    }
}

// Data classes for Ikorochat integration
data class ChatContext(
    val type: ChatType = ChatType.GENERAL,
    val isMarketplace: Boolean = false,
    val isTransaction: Boolean = false,
    val productName: String = "",
    val productPrice: Double = 0.0,
    val category: String = "",
    val transactionAmount: Double = 0.0,
    val recipient: String = ""
)

enum class ChatType {
    GENERAL,
    MARKETPLACE,
    TRANSACTION,
    EMERGENCY,
    GROUP
}

data class ProductData(
    val id: String,
    val name: String,
    val category: String,
    val price: Double,
    val description: String,
    val sellerName: String,
    val rating: Float,
    val imageCount: Int,
    val specifications: Map<String, String> = emptyMap()
)

data class MarketData(
    val avgPrice: Double = 0.0,
    val minPrice: Double = 0.0,
    val maxPrice: Double = 0.0,
    val demandLevel: String = "MEDIUM",
    val competitionLevel: String = "MEDIUM",
    val recentSales: Int = 0,
    val isTrending: Boolean = false
)

data class TransactionData(
    val id: String,
    val amount: Double,
    val senderId: String,
    val recipientId: String,
    val timestamp: String,
    val location: String,
    val deviceInfo: String,
    val ipAddress: String,
    val description: String
)

data class UserProfile(
    val accountAge: Int,
    val totalTransactions: Int,
    val trustScore: Int,
    val verificationLevel: String,
    val lastLogin: String,
    val loginLocation: String,
    val deviceUsage: String,
    val suspiciousFlags: List<String> = emptyList()
)

data class LocationData(
    val address: String,
    val latitude: Double,
    val longitude: Double,
    val accuracy: Float,
    val timestamp: String
)

enum class EmergencyType {
    MEDICAL,
    FIRE,
    CRIME,
    ACCIDENT,
    NATURAL_DISASTER,
    OTHER
}