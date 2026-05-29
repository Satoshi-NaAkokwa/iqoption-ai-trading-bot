# Ikorochat Integration Examples

This guide provides practical examples of integrating Agbara into Ikorochat-android.

## Table of Contents
1. [Chat Features](#chat-features)
2. [Marketplace Features](#marketplace-features)
3. [Transaction Features](#transaction-features)
4. [Emergency Features](#emergency-features)
5. [Creator Economy Features](#creator-economy-features)

---

## Chat Features

### 1. Smart Chat Assistant

```kotlin
class ChatActivity : AppCompatActivity() {
    private lateinit var chatAI: IkoroChatIntelligence
    private lateinit var agbaraClient: AgbaraClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        agbaraClient = (application as IkorochatApplication).agbaraClient
        chatAI = IkoroChatIntelligence(agbaraClient)
    }

    fun onSendMessage(message: String) {
        // Get AI assistance for the message
        chatAI.assistChat(
            userId = getCurrentUserId(),
            message = message,
            context = ChatContext(
                type = ChatType.GENERAL,
                isMarketplace = false
            )
        ) { assistance ->
            when (assistance) {
                is ChatAssistance.Success -> {
                    // Show smart suggestions
                    showSmartSuggestions(assistance.suggestions)
                }
                is ChatAssistance.Error -> {
                    // Handle error
                }
            }
        }
    }

    fun onReceiveMessage(message: Message) {
        // Analyze conversation sentiment
        lifecycleScope.launch {
            val conversation = loadRecentMessages(message.chatId, 10)
            val analysis = chatAI.analyzeConversationSentiment(
                userId = message.senderId,
                conversation = conversation
            )

            when (analysis) {
                is ConversationAnalysis.Success -> {
                    // Flag if sentiment is negative
                    if (analysis.sentiment == "negative") {
                        showSentimentWarning(analysis)
                    }
                }
                is ConversationAnalysis.Error -> {
                    // Handle error
                }
            }
        }
    }
}
```

### 2. Smart Reply Generation

```kotlin
class ChatActivity : AppCompatActivity() {
    fun showSmartReplies(message: Message) {
        lifecycleScope.launch {
            val chatAI = IkoroChatIntelligence(agbaraClient)
            
            val smartReplies = chatAI.generateSmartReplies(
                userId = getCurrentUserId(),
                message = message.content,
                count = 3
            )

            if (smartReplies.isNotEmpty()) {
                showSmartReplyChips(smartReplies)
            }
        }
    }

    private fun showSmartReplyChips(replies: List<String>) {
        val chipGroup = findViewById<ChipGroup>(R.id.smartReplies)
        
        replies.forEach { reply ->
            val chip = Chip(this).apply {
                text = reply
                setOnClickListener { sendQuickReply(reply) }
            }
            chipGroup.addView(chip)
        }
    }
}
```

---

## Marketplace Features

### 1. Product Price Analysis

```kotlin
class ProductActivity : AppCompatActivity() {
    private lateinit var marketAnalyzer: IkoroMarketAnalyzer
    private lateinit var agbaraClient: AgbaraClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        agbaraClient = (application as IkorochatApplication).agbaraClient
        marketAnalyzer = IkoroMarketAnalyzer(agbaraClient)
    }

    fun analyzeProductPrice(product: Product) {
        lifecycleScope.launch {
            val productData = ProductData(
                id = product.id,
                name = product.name,
                category = product.category,
                price = product.price,
                description = product.description,
                sellerName = product.sellerName,
                rating = product.rating,
                imageCount = product.images.size
            )

            // Get market data from your backend
            val marketData = fetchMarketData(product.category)

            val analysis = marketAnalyzer.analyzeProduct(
                userId = getCurrentUserId(),
                product = productData,
                marketData = marketData
            )

            when (analysis) {
                is MarketAnalysis.Success -> {
                    displayPriceAnalysis(analysis)
                    showPriceRecommendations(analysis.priceRecommendation)
                }
                is MarketAnalysis.Error -> {
                    showError(analysis.error.message)
                }
            }
        }
    }

    private fun displayPriceAnalysis(analysis: MarketAnalysis.Success) {
        // Display overall score
        val scoreText = "Market Score: ${(analysis.overallScore * 100).toInt()}%"
        textView.text = scoreText

        // Display suggestions
        val suggestions = analysis.suggestions.joinToString("\n• ") { "• $it" }
        suggestionsView.text = suggestions

        // Display category rank
        val rankText = "Category Rank: ${analysis.categoryRank}/10"
        rankView.text = rankText
    }
}
```

### 2. Seller Trust Analysis

```kotlin
class SellerProfileActivity : AppCompatActivity() {
    fun analyzeSellerTrust(sellerId: String) {
        lifecycleScope.launch {
            val userProfile = fetchUserProfile(sellerId)
            
            // Create a transaction to check trust
            val testTransaction = TransactionData(
                id = "trust-check-${System.currentTimeMillis()}",
                amount = 100.0,  // Test amount
                senderId = getCurrentUserId(),
                recipientId = sellerId,
                timestamp = getCurrentTimestamp(),
                location = getUserLocation(),
                deviceInfo = getDeviceInfo(),
                ipAddress = getIpAddress(),
                description = "Trust verification"
            )

            val transactionAI = IkoroTransactionAI(agbaraClient)
            val analysis = transactionAI.analyzeTransactionRisk(
                userId = getCurrentUserId(),
                transaction = testTransaction,
                userProfile = userProfile
            )

            when (analysis) {
                is FraudAnalysis.Success -> {
                    displayTrustScore(analysis)
                }
                is FraudAnalysis.Error -> {
                    showError(analysis.error.message)
                }
            }
        }
    }

    private fun displayTrustScore(analysis: FraudAnalysis.Success) {
        when (analysis.riskLevel) {
            RiskLevel.LOW -> {
                trustBadge.setImageResource(R.drawable.ic_trust_high)
                trustBadge.backgroundTintList = ColorStateList.valueOf(
                    ContextCompat.getColor(this, android.R.color.holo_green_dark)
                )
            }
            RiskLevel.MEDIUM -> {
                trustBadge.setImageResource(R.drawable.ic_trust_medium)
                trustBadge.backgroundTintList = ColorStateList.valueOf(
                    ContextCompat.getColor(this, android.R.color.holo_orange_dark)
                )
            }
            RiskLevel.HIGH -> {
                trustBadge.setImageResource(R.drawable.ic_trust_low)
                trustBadge.backgroundTintList = ColorStateList.valueOf(
                    ContextCompat.getColor(this, android.R.color.holo_red_dark)
                )
            }
        }
    }
}
```

---

## Transaction Features

### 1. Pre-Transaction Risk Check

```kotlin
class SendBitcoinActivity : AppCompatActivity() {
    private lateinit var transactionAI: IkoroTransactionAI

    fun sendBitcoin(recipientId: String, amount: Double) {
        lifecycleScope.launch {
            val transaction = TransactionData(
                id = generateTransactionId(),
                amount = amount,
                senderId = getCurrentUserId(),
                recipientId = recipientId,
                timestamp = getCurrentTimestamp(),
                location = getUserLocation(),
                deviceInfo = getDeviceInfo(),
                ipAddress = getIpAddress(),
                description = "Bitcoin transfer"
            )

            val userProfile = getUserProfile()
            
            val analysis = transactionAI.analyzeTransactionRisk(
                userId = getCurrentUserId(),
                transaction = transaction,
                userProfile = userProfile
            )

            when (analysis) {
                is FraudAnalysis.Success -> {
                    handleRiskAnalysis(analysis, transaction)
                }
                is FraudAnalysis.Error -> {
                    showError(analysis.error.message)
                }
            }
        }
    }

    private fun handleRiskAnalysis(analysis: FraudAnalysis.Success, transaction: TransactionData) {
        when (analysis.riskLevel) {
            RiskLevel.LOW -> {
                // Proceed with transaction
                showConfirmationDialog(transaction)
            }
            RiskLevel.MEDIUM -> {
                // Require additional verification
                showVerificationDialog(
                    transaction,
                    analysis.verificationNeeded
                )
            }
            RiskLevel.HIGH -> {
                // Block transaction
                showRiskWarning(
                    analysis.suspiciousPatterns,
                    analysis.reasoning
                )
            }
        }
    }

    private fun showRiskWarning(patterns: List<String>, reasoning: String) {
        AlertDialog.Builder(this)
            .setTitle("⚠️ High Risk Transaction")
            .setMessage(buildString {
                append("This transaction has been flagged as high risk.\n\n")
                append("Suspicious patterns:\n")
                patterns.forEach { append("• $it\n") }
                append("\nReasoning:\n$reasoning")
            })
            .setPositiveButton("Understood", null)
            .show()
    }
}
```

### 2. Transaction History Analysis

```kotlin
class TransactionHistoryActivity : AppCompatActivity() {
    fun analyzeTransactionHistory(userId: String) {
        lifecycleScope.launch {
            val transactions = fetchTransactions(userId, 30) // Last 30 days
            
            // Aggregate data
            val avgAmount = transactions.map { it.amount }.average()
            val totalAmount = transactions.sumOf { it.amount }
            val frequency = transactions.size
            
            // Create analysis request
            val analysisRequest = """
                Analyze this transaction history for the last 30 days:
                - Total transactions: $frequency
                - Total amount: $totalAmount ₿
                - Average amount: ${String.format("%.2f", avgAmount)} ₿
                - Transaction pattern: ${analyzePattern(transactions)}
                
                Provide:
                1. Spending patterns
                2. Risk assessment
                3. Recommendations
            """.trimIndent()

            val request = AgbaraAIRequest(
                userId = userId,
                message = analysisRequest
            )

            agbaraClient.processMessage(request) { response ->
                when (response) {
                    is AgbaraAIResponse.Success -> {
                        displayAnalysis(response.data.response)
                    }
                    is AgbaraAIResponse.Error -> {
                        showError(response.error.message)
                    }
                }
            }
        }
    }

    private fun analyzePattern(transactions: List<Transaction>): String {
        // Analyze transaction patterns
        val recent = transactions.take(10)
        val avgRecent = recent.map { it.amount }.average()
        val avgOverall = transactions.map { it.amount }.average()
        
        return when {
            avgRecent > avgOverall * 1.5 -> "Increasing spending"
            avgRecent < avgOverall * 0.5 -> "Decreasing spending"
            else -> "Consistent spending"
        }
    }
}
```

---

## Emergency Features

### 1. SOS Button Integration

```kotlin
class EmergencyActivity : AppCompatActivity() {
    private lateinit var emergencyAI: IkoroEmergencyAI
    private lateinit var fusedLocationClient: FusedLocationProviderClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        agbaraClient = (application as IkorochatApplication).agbaraClient
        emergencyAI = IkoroEmergencyAI(agbaraClient)
        
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)
    }

    fun onSOSButtonClicked(emergencyType: EmergencyType) {
        // Get current location
        fusedLocationClient.lastLocation
            .addOnSuccessListener { location ->
                val locationData = LocationData(
                    address = getAddressFromLocation(location),
                    latitude = location.latitude,
                    longitude = location.longitude,
                    accuracy = location.accuracy,
                    timestamp = getCurrentTimestamp()
                )

                handleEmergency(emergencyType, locationData)
            }
            .addOnFailureListener { exception ->
                // Fallback to cached location
                handleEmergency(emergencyType, getCachedLocation())
            }
    }

    private fun handleEmergency(emergencyType: EmergencyType, location: LocationData) {
        lifecycleScope.launch {
            val situationDescription = when (emergencyType) {
                EmergencyType.MEDICAL -> "Medical emergency - needs immediate attention"
                EmergencyType.FIRE -> "Fire emergency - property damage risk"
                EmergencyType.CRIME -> "Crime in progress - police needed"
                EmergencyType.ACCIDENT -> "Traffic accident - injuries reported"
                EmergencyType.NATURAL_DISASTER -> "Natural disaster - evacuate needed"
                EmergencyType.OTHER -> "Emergency situation - unspecified"
            }

            val response = emergencyAI.handleEmergency(
                userId = getCurrentUserId(),
                emergencyType = emergencyType,
                location = locationData,
                situationDescription = situationDescription
            )

            when (response) {
                is EmergencyResponse.Success -> {
                    displayEmergencyGuide(response)
                    notifyEmergencyContacts(response, location)
                }
                is EmergencyResponse.Error -> {
                    showError(response.error.message)
                }
            }
        }
    }

    private fun displayEmergencyGuide(response: EmergencyResponse.Success) {
        val guide = buildString {
            append("🚨 IMMEDIATE ACTIONS:\n")
            response.immediateActions.forEach { append("• $it\n") }
            
            append("\n🩺 FIRST AID:\n")
            response.firstAidInstructions.forEach { append("• $it\n") }
            
            append("\n📞 CONTACT:\n")
            response.contactInfo.forEach { append("• $it\n") }
            
            append("\n🏥 NEARBY RESOURCES:\n")
            response.nearbyResources.forEach { append("• $it\n") }
            
            append("\n⚠️ SAFETY:\n")
            response.safetyPrecautions.forEach { append("• $it\n") }
        }

        emergencyGuideView.text = guide
    }
}
```

### 2. Emergency Notification System

```kotlin
class EmergencyNotificationService : Service() {
    private lateinit var agbaraClient: AgbaraClient
    private lateinit var emergencyAI: IkoroEmergencyAI

    fun broadcastEmergency(
        emergencyType: EmergencyType,
        location: LocationData,
        description: String
    ) {
        lifecycleScope.launch {
            val response = emergencyAI.handleEmergency(
                userId = getCurrentUserId(),
                emergencyType = emergencyType,
                location = location,
                situationDescription = description
            )

            when (response) {
                is EmergencyResponse.Success -> {
                    // Notify emergency contacts
                    notifyEmergencyContacts(response, location)
                    
                    // Notify nearby users (mesh network)
                    notifyNearbyUsers(response, location)
                    
                    // Log emergency
                    logEmergency(response)
                }
                is EmergencyResponse.Error -> {
                    // Fallback notification
                    sendBasicEmergencyNotification(emergencyType, location)
                }
            }
        }
    }

    private fun notifyEmergencyContacts(
        response: EmergencyResponse.Success,
        location: LocationData
    ) {
        val contacts = fetchEmergencyContacts()
        
        contacts.forEach { contact ->
            val message = buildString {
                append("🚨 EMERGENCY ALERT 🚨\n\n")
                append("Type: ${response.emergencyType}\n")
                append("Location: ${location.address}\n")
                append("Coordinates: ${location.latitude}, ${location.longitude}\n")
                append("\nIMMEDIATE ACTIONS:\n")
                response.immediateActions.forEach { append("• $it\n") }
            }

            sendMessage(contact.phoneNumber, message)
        }
    }

    private fun notifyNearbyUsers(
        response: EmergencyResponse.Success,
        location: LocationData
    ) {
        // Use Ikorochat's mesh network to notify nearby users
        val nearbyUsers = findNearbyUsers(location)
        
        nearbyUsers.forEach { user ->
            sendMeshMessage(
                userId = user.id,
                message = buildString {
                    append("🚨 Emergency Nearby 🚨\n")
                    append("Type: ${response.emergencyType}\n")
                    append("Distance: ${calculateDistance(location, user.location)}m\n")
                    append("Please check if you can help!")
                }
            )
        }
    }
}
```

---

## Creator Economy Features

### 1. Music Production Assistant

```kotlin
class MusicStudioActivity : AppCompatActivity() {
    private lateinit var musicAI: IkoroCreatorAI

    fun analyzeMusicProject(project: MusicProject) {
        lifecycleScope.launch {
            val analysis = musicAI.analyzeMusicProject(
                userId = getCurrentUserId(),
                project = project
            )

            when (analysis) {
                is MusicAnalysis.Success -> {
                    displayMusicAnalysis(analysis)
                }
                is MusicAnalysis.Error -> {
                    showError(analysis.error.message)
                }
            }
        }
    }

    private fun displayMusicAnalysis(analysis: MusicAnalysis.Success) {
        // Display genre suitability
        genreSuitabilityView.text = "Genre Suitability: ${analysis.genreSuitability}/10"

        // Display musical quality
        musicalQualityView.text = "Musical Quality: ${analysis.musicalQuality}/10"

        // Display improvements
        val improvements = analysis.improvements.joinToString("\n• ") { "• $it" }
        improvementsView.text = improvements

        // Display production tips
        val tips = analysis.productionTips.joinToString("\n• ") { "• $it" }
        tipsView.text = tips

        // Display overall score
        overallScoreView.text = "Overall: ${(analysis.overallScore * 100).toInt()}%"
    }

    fun generateMashup(track1: TrackInfo, track2: TrackInfo) {
        lifecycleScope.launch {
            val suggestion = musicAI.generateMashupSuggestion(
                userId = getCurrentUserId(),
                track1 = track1,
                track2 = track2
            )

            when (suggestion) {
                is MashupSuggestion.Success -> {
                    displayMashupSuggestions(suggestion)
                }
                is MashupSuggestion.Error -> {
                    showError(suggestion.error.message)
                }
            }
        }
    }
}
```

### 2. Errand Logistics Optimization

```kotlin
class ErrandActivity : AppCompatActivity() {
    private lateinit var errandAI: IkoroErrandAI

    fun submitErrandRequest(request: ErrandRequest) {
        lifecycleScope.launch {
            val analysis = errandAI.analyzeErrandRequest(
                userId = getCurrentUserId(),
                request = request
            )

            when (analysis) {
                is ErrandAnalysis.Success -> {
                    displayErrandAnalysis(analysis)
                }
                is ErrandAnalysis.Error -> {
                    showError(analysis.error.message)
                }
            }
        }
    }

    private fun displayErrandAnalysis(analysis: ErrandAnalysis.Success) {
        // Display feasibility
        feasibilityView.text = "Feasibility: ${analysis.feasibility}"

        // Display cost range
        costRangeView.text = "Estimated Cost: ${analysis.costRange}"

        // Display recommended runner type
        runnerTypeView.text = "Recommended Runner: ${analysis.recommendedRunnerType}"

        // Display timeline
        timelineView.text = "Estimated Time: ${analysis.timeline}"

        // Display risks
        val risks = analysis.risks.joinToString("\n• ") { "• $it" }
        risksView.text = risks

        // Display optimizations
        val optimizations = analysis.optimizations.joinToString("\n• ") { "• $it" }
        optimizationsView.text = optimizations
    }

    fun optimizeRoute(errands: List<ErrandRequest>) {
        lifecycleScope.launch {
            val optimization = errandAI.optimizeDeliveryRoute(
                userId = getCurrentUserId(),
                errands = errands
            )

            when (optimization) {
                is RouteOptimization.Success -> {
                    displayRouteOptimization(optimization)
                }
                is RouteOptimization.Error -> {
                    showError(optimization.error.message)
                }
            }
        }
    }

    private fun displayRouteOptimization(optimization: RouteOptimization.Success) {
        // Display delivery order
        val order = optimization.deliveryOrder.joinToString(" → ") { "Errand #$it" }
        deliveryOrderView.text = "Optimal Order:\n$order"

        // Display route plan
        routePlanView.text = optimization.routePlan

        // Display total time
        totalTimeView.text = "Total Time: ${optimization.estimatedTotalTime}"

        // Display cost optimizations
        val costOptimizations = optimization.costOptimizations.joinToString("\n• ") { "• $it" }
        costOptimizationsView.text = costOptimizations
    }
}
```

---

## Integration in Ikorochat Application

### Application Class

```kotlin
class IkorochatApplication : Application() {
    lateinit var agbaraClient: AgbaraClient
    lateinit var chatAI: IkoroChatIntelligence
    lateinit var marketAnalyzer: IkoroMarketAnalyzer
    lateinit var transactionAI: IkoroTransactionAI
    lateinit var emergencyAI: IkoroEmergencyAI
    lateinit var creatorAI: IkoroCreatorAI
    lateinit var errandAI: IkoroErrandAI

    override fun onCreate() {
        super.onCreate()

        // Initialize Agbara SDK
        agbaraClient = AgbaraClient.create(
            context = this,
            apiKey = BuildConfig.AGBARA_API_KEY,
            options = {
                enableRemoteAI = true
                enableLocalAI = false
                enableCache = true
                enableOfflineQueue = true
                cacheMaxSize = 50
                logLevel = LogLevel.INFO
            }
        )

        // Set user ID
        val userId = SharedPreferencesManager.getUserId()
        agbaraClient.setUserId(userId)

        // Initialize Ikorochat-specific AI components
        chatAI = IkoroChatIntelligence(agbaraClient)
        marketAnalyzer = IkoroMarketAnalyzer(agbaraClient)
        transactionAI = IkoroTransactionAI(agbaraClient)
        emergencyAI = IkoroEmergencyAI(agbaraClient)
        creatorAI = IkoroCreatorAI(agbaraClient)
        errandAI = IkoroErrandAI(agbaraClient)
    }
}
```

---

**For more examples, see the demo app in `agbara-demo-app/`.**