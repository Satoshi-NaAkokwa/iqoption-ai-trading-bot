package com.agbara.sdk.ikoro

import com.agbara.sdk.AgbaraClient
import com.agbara.sdk.models.*
import kotlinx.coroutines.*

/**
 * Creator Economy AI for Ikorochat
 * Supports music production, DJ mixing, VFX editing, and creative tools
 */
class IkoroCreatorAI(
    private val agbaraClient: AgbaraClient
) {

    suspend fun analyzeMusicProject(
        userId: String,
        project: MusicProject
    ): MusicAnalysis = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Analyze this music project for Ikorochat Creator Studio:\n\n")
            append("=== PROJECT DETAILS ===\n")
            append("Name: ${project.name}\n")
            append("Genre: ${project.genre}\n")
            append("BPM: ${project.bpm}\n")
            append("Key: ${project.key}\n")
            append("Duration: ${project.duration}s\n")
            append("Instruments: ${project.instruments.joinToString(", ")}\n")
            append("Vocals: ${project.hasVocals}\n")
            append("Description: ${project.description}\n")
            
            if (project.lyrics.isNotEmpty()) {
                append("\n=== LYRICS ===\n")
                append(project.lyrics)
            }
            
            append("\n=== ANALYSIS REQUIRED ===\n")
            append("Provide:\n")
            append("1. Genre suitability assessment\n")
            append("2. Musical quality evaluation (1-10)\n")
            append("3. Suggested improvements\n")
            append("4. Production tips\n")
            append("5. Mixing and mastering advice\n")
            append("6. Market potential assessment\n")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            preferredExpert = ExpertType.AUDIO,
            context = mapOf("feature" to "music-analysis")
        )

        try {
            val response = agbaraClient.processMessage(request)
            if (response is AgbaraAIResponse.Success) {
                parseMusicAnalysis(response.data.response, project)
            } else {
                MusicAnalysis.Error(response.error)
            }
        } catch (e: Exception) {
            MusicAnalysis.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun parseMusicAnalysis(response: String, project: MusicProject): MusicAnalysis {
        val genreSuitability = extractRating(response, "genre suitability")
        val musicalQuality = extractRating(response, "musical quality")
        val improvements = extractSection(response, "suggested improvements")
        val productionTips = extractSection(response, "production tips")
        val mixingAdvice = extractSection(response, "mixing and mastering")
        val marketPotential = extractMarketPotential(response)

        return MusicAnalysis.Success(
            projectId = project.id,
            genreSuitability = genreSuitability,
            musicalQuality = musicalQuality,
            improvements = improvements,
            productionTips = productionTips,
            mixingAdvice = mixingAdvice,
            marketPotential = marketPotential,
            overallScore = (genreSuitability + musicalQuality) / 20.0f
        )
    }

    suspend fun generateMashupSuggestion(
        userId: String,
        track1: TrackInfo,
        track2: TrackInfo
    ): MashupSuggestion = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Suggest a creative mashup for these two tracks:\n\n")
            append("=== TRACK 1 ===\n")
            append("Title: ${track1.title}\n")
            append("Artist: ${track1.artist}\n")
            append("BPM: ${track1.bpm}\n")
            append("Key: ${track1.key}\n")
            append("Duration: ${track1.duration}s\n")
            append("Genre: ${track1.genre}\n")
            
            append("\n=== TRACK 2 ===\n")
            append("Title: ${track2.title}\n")
            append("Artist: ${track2.artist}\n")
            append("BPM: ${track2.bpm}\n")
            append("Key: ${track2.key}\n")
            append("Duration: ${track2.duration}s\n")
            append("Genre: ${track2.genre}\n")
            
            append("\nProvide:\n")
            append("1. BPM adjustment recommendations\n")
            append("2. Key compatibility assessment\n")
            append("3. Transition point suggestions\n")
            append("4. Which parts to use from each track\n")
            append("5. Overall mashup concept\n")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            preferredExpert = ExpertType.AUDIO,
            context = mapOf("feature" to "mashup-creation")
        )

        try {
            val response = agbaraClient.processMessage(request)
            if (response is AgbaraAIResponse.Success) {
                parseMashupSuggestion(response.data.response, track1, track2)
            } else {
                MashupSuggestion.Error(response.error)
            }
        } catch (e: Exception) {
            MashupSuggestion.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun parseMashupSuggestion(
        response: String,
        track1: TrackInfo,
        track2: TrackInfo
    ): MashupSuggestion {
        val bpmAdjustment = extractBPMAdjustment(response)
        val keyCompatibility = extractKeyCompatibility(response)
        val transitionPoints = extractTransitionPoints(response)
        val trackParts = extractTrackParts(response)
        val concept = extractSection(response, "Overall mashup concept").joinToString(" ")

        return MashupSuggestion.Success(
            track1Id = track1.id,
            track2Id = track2.id,
            bpmAdjustment = bpmAdjustment,
            keyCompatibility = keyCompatibility,
            transitionPoints = transitionPoints,
            trackParts = trackParts,
            concept = concept,
            confidence = 0.85f
        )
    }

    suspend fun analyzeVFXProject(
        userId: String,
        project: VFXProject
    ): VFXAnalysis = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Analyze this VFX project for Ikorochat Creator Studio:\n\n")
            append("=== PROJECT DETAILS ===\n")
            append("Name: ${project.name}\n")
            append("Type: ${project.type}\n")
            append("Resolution: ${project.resolution}\n")
            append("Duration: ${project.duration}s\n")
            append("Effects: ${project.effects.joinToString(", ")}\n")
            append("Description: ${project.description}\n")
            
            append("\n=== ANALYSIS REQUIRED ===\n")
            append("Provide:\n")
            append("1. Quality assessment (1-10)\n")
            append("2. Rendering recommendations\n")
            append("3. Optimization suggestions\n")
            append("4. Creative improvements\n")
            append("5. Export settings recommendations\n")
        }

        val request = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            preferredExpert = ExpertType.VISION,
            context = mapOf("feature" to "vfx-analysis")
        )

        try {
            val response = agbaraClient.processMessage(request)
            if (response is AgbaraAIResponse.Success) {
                parseVFXAnalysis(response.data.response, project)
            } else {
                VFXAnalysis.Error(response.error)
            }
        } catch (e: Exception) {
            VFXAnalysis.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun parseVFXAnalysis(response: String, project: VFXProject): VFXAnalysis {
        val qualityScore = extractRating(response, "quality assessment")
        val renderingRecommendations = extractSection(response, "Rendering recommendations")
        val optimizationSuggestions = extractSection(response, "Optimization suggestions")
        val creativeImprovements = extractSection(response, "Creative improvements")
        val exportSettings = extractSection(response, "Export settings")

        return VFXAnalysis.Success(
            projectId = project.id,
            qualityScore = qualityScore,
            renderingRecommendations = renderingRecommendations,
            optimizationSuggestions = optimizationSuggestions,
            creativeImprovements = creativeImprovements,
            exportSettings = exportSettings,
            overallScore = qualityScore / 10.0f
        )
    }
}

/**
 * Errand Logistics AI for Ikorochat
 * Supports delivery requests, runner management, and logistics optimization
 */
class IkoroErrandAI(
    private val agbaraClient: AgbaraClient
) {

    suspend fun analyzeErrandRequest(
        userId: String,
        request: ErrandRequest
    ): ErrandAnalysis = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Analyze this errand request for Ikorochat Errand Logistics:\n\n")
            append("=== REQUEST DETAILS ===\n")
            append("Type: ${request.type}\n")
            append("Description: ${request.description}\n")
            append("Pickup Location: ${request.pickupLocation}\n")
            append("Delivery Location: ${request.deliveryLocation}\n")
            append("Distance: ${request.distance}km\n")
            append("Estimated Time: ${request.estimatedTime} minutes\n")
            append("Priority: ${request.priority}\n")
            append("Special Requirements: ${request.specialRequirements}\n")
            append("Budget: ${request.budget} ₿\n")
            
            append("\n=== ANALYSIS REQUIRED ===\n")
            append("Provide:\n")
            append("1. Feasibility assessment\n")
            append("2. Estimated cost range\n")
            append("3. Recommended runner type\n")
            append("4. Delivery timeline\n")
            append("5. Potential risks or challenges\n")
            append("6. Optimization suggestions\n")
        }

        val req = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            context = mapOf("feature" to "errand-analysis")
        )

        try {
            val response = agbaraClient.processMessage(req)
            if (response is AgbaraAIResponse.Success) {
                parseErrandAnalysis(response.data.response, request)
            } else {
                ErrandAnalysis.Error(response.error)
            }
        } catch (e: Exception) {
            ErrandAnalysis.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun parseErrandAnalysis(response: String, request: ErrandRequest): ErrandAnalysis {
        val feasibility = extractFeasibility(response)
        val costRange = extractCostRange(response)
        val runnerType = extractRunnerType(response)
        val timeline = extractTimeline(response)
        val risks = extractSection(response, "Potential risks")
        val optimizations = extractSection(response, "Optimization suggestions")

        return ErrandAnalysis.Success(
            requestId = request.id,
            feasibility = feasibility,
            costRange = costRange,
            recommendedRunnerType = runnerType,
            timeline = timeline,
            risks = risks,
            optimizations = optimizations,
            confidence = 0.88f
        )
    }

    suspend fun optimizeDeliveryRoute(
        userId: String,
        errands: List<ErrandRequest>
    ): RouteOptimization = withContext(Dispatchers.IO) {
        val prompt = buildString {
            append("Optimize the delivery route for these errands:\n\n")
            errands.forEachIndexed { index, errand ->
                append("Errand ${index + 1}:\n")
                append("  Type: ${errand.type}\n")
                append("  Pickup: ${errand.pickupLocation}\n")
                append("  Delivery: ${errand.deliveryLocation}\n")
                append("  Distance: ${errand.distance}km\n")
                append("  Priority: ${errand.priority}\n")
                append("\n")
            }
            
            append("\nProvide:\n")
            append("1. Optimal delivery order\n")
            append("2. Combined route plan\n")
            append("3. Estimated total time\n")
            append("4. Cost optimization\n")
            append("5. Alternative routes\n")
        }

        val req = AgbaraAIRequest(
            userId = userId,
            message = prompt,
            context = mapOf("feature" to "route-optimization")
        )

        try {
            val response = agbaraClient.processMessage(req)
            if (response is AgbaraAIResponse.Success) {
                parseRouteOptimization(response.data.response, errands)
            } else {
                RouteOptimization.Error(response.error)
            }
        } catch (e: Exception) {
            RouteOptimization.Error(
                AgbaraError(ErrorType.UNKNOWN, e.message ?: "Analysis failed")
            )
        }
    }

    private fun parseRouteOptimization(
        response: String,
        errands: List<ErrandRequest>
    ): RouteOptimization {
        val deliveryOrder = extractDeliveryOrder(response)
        val routePlan = extractRoutePlan(response)
        val totalTime = extractTotalTime(response)
        val costOptimization = extractSection(response, "Cost optimization")
        val alternativeRoutes = extractSection(response, "Alternative routes")

        return RouteOptimization.Success(
            deliveryOrder = deliveryOrder,
            routePlan = routePlan,
            estimatedTotalTime = totalTime,
            costOptimizations = costOptimization,
            alternativeRoutes = alternativeRoutes,
            errands = errands,
            confidence = 0.85f
        )
    }
}

// Helper functions for parsing AI responses
private fun extractRating(response: String, label: String): Int {
    val regex = """${label.replace(" ", "\\s+")}[^\d]*(\d+)""".toRegex(RegexOption.IGNORE_CASE)
    val match = regex.find(response)
    return match?.groupValues?.get(1)?.toIntOrNull() ?: 5
}

private fun extractMarketPotential(response: String): String {
    val marketRegex = """market\s+potential[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
    val match = marketRegex.find(response)
    return match?.groupValues?.get(1) ?: "MEDIUM"
}

private fun extractBPMAdjustment(response: String): String {
    val bpmRegex = """bpm\s+adjustment[^\d]*(\d+)""".toRegex(RegexOption.IGNORE_CASE)
    val match = bpmRegex.find(response)
    return match?.groupValues?.get(1) ?: "0"
}

private fun extractKeyCompatibility(response: String): KeyCompatibility {
    val compatRegex = """key\s+compatibility[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
    val match = compatRegex.find(response)
    val compat = match?.groupValues?.get(1)?.uppercase() ?: "MISMATCH"
    
    return when (compat) {
        "COMPATIBLE", "GOOD", "EXCELLENT" -> KeyCompatibility.COMPATIBLE
        "MISMATCH", "POOR", "BAD" -> KeyCompatibility.INCOMPATIBLE
        else -> KeyCompatibility.NEUTRAL
    }
}

private fun extractTransitionPoints(response: String): List<String> {
    val transitionsSection = response.substringAfter("Transition point suggestions:")
        .substringBefore("\n\n")
    return transitionsSection.lines()
        .filter { it.isNotBlank() && it.startsWith("-") }
        .map { it.trim().removePrefix("-").trim() }
}

private fun extractTrackParts(response: String): List<String> {
    val partsSection = response.substringAfter("Which parts to use:")
        .substringBefore("\n\n")
    return partsSection.lines()
        .filter { it.isNotBlank() }
        .map { it.trim() }
}

private fun extractFeasibility(response: String): String {
    val feasRegex = """feasibility[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
    val match = feasRegex.find(response)
    return match?.groupValues?.get(1) ?: "UNCERTAIN"
}

private fun extractCostRange(response: String): String {
    val costRegex = """cost\s+range[^\d]*(\d+\.?\d*)\s*(?:to|-|–)\s*(\d+\.?\d*)""".toRegex(RegexOption.IGNORE_CASE)
    val match = costRegex.find(response)
    return match?.groupValues?.let {
        "${it[1]}-${it[2]} ₿"
    } ?: "50-100 ₿"
}

private fun extractRunnerType(response: String): String {
    val typeRegex = """runner\s+type[^\w]*(\w+)""".toRegex(RegexOption.IGNORE_CASE)
    val match = typeRegex.find(response)
    return match?.groupValues?.get(1) ?: "STANDARD"
}

private fun extractTimeline(response: String): String {
    val timeRegex = """timeline[^\d]*(\d+)\s*(?:hours|minutes|hrs|mins|h|m)""".toRegex(RegexOption.IGNORE_CASE)
    val match = timeRegex.find(response)
    return match?.groupValues?.let { "${it[1]} ${it[2]}" } ?: "30 minutes"
}

private fun extractDeliveryOrder(response: String): List<Int> {
    val orderSection = response.substringAfter("Optimal delivery order:")
        .substringBefore("\n\n")
    return orderSection.lines()
        .filter { it.isNotBlank() }
        .mapNotNull { it.trim().toIntOrNull() }
}

private fun extractRoutePlan(response: String): String {
    val planSection = response.substringAfter("Combined route plan:")
        .substringBefore("\n\n")
    return planSection.trim()
}

private fun extractTotalTime(response: String): String {
    val timeRegex = """total\s+time[^\d]*(\d+)\s*(?:hours|minutes|hrs|mins|h|m)""".toRegex(RegexOption.IGNORE_CASE)
    val match = timeRegex.find(response)
    return match?.groupValues?.let { "${it[1]} ${it[2]}" } ?: "2 hours"
}

// Data classes for Creator Economy
data class MusicProject(
    val id: String,
    val name: String,
    val genre: String,
    val bpm: Int,
    val key: String,
    val duration: Int,
    val instruments: List<String>,
    val hasVocals: Boolean,
    val description: String,
    val lyrics: String = ""
)

data class TrackInfo(
    val id: String,
    val title: String,
    val artist: String,
    val bpm: Int,
    val key: String,
    val duration: Int,
    val genre: String
)

data class VFXProject(
    val id: String,
    val name: String,
    val type: String,
    val resolution: String,
    val duration: Int,
    val effects: List<String>,
    val description: String
)

// Data classes for Errand Logistics
data class ErrandRequest(
    val id: String,
    val type: String,
    val description: String,
    val pickupLocation: String,
    val deliveryLocation: String,
    val distance: Double,
    val estimatedTime: Int,
    val priority: String,
    val specialRequirements: String,
    val budget: Double
)

// Sealed classes for analysis results
sealed class MusicAnalysis {
    data class Success(
        val projectId: String,
        val genreSuitability: Int,
        val musicalQuality: Int,
        val improvements: List<String>,
        val productionTips: List<String>,
        val mixingAdvice: List<String>,
        val marketPotential: String,
        val overallScore: Float
    ) : MusicAnalysis()
    
    data class Error(val error: AgbaraError) : MusicAnalysis()
}

sealed class MashupSuggestion {
    data class Success(
        val track1Id: String,
        val track2Id: String,
        val bpmAdjustment: String,
        val keyCompatibility: KeyCompatibility,
        val transitionPoints: List<String>,
        val trackParts: List<String>,
        val concept: String,
        val confidence: Float
    ) : MashupSuggestion()
    
    data class Error(val error: AgbaraError) : MashupSuggestion()
}

enum class KeyCompatibility {
    COMPATIBLE,
    INCOMPATIBLE,
    NEUTRAL
}

sealed class VFXAnalysis {
    data class Success(
        val projectId: String,
        val qualityScore: Int,
        val renderingRecommendations: List<String>,
        val optimizationSuggestions: List<String>,
        val creativeImprovements: List<String>,
        val exportSettings: List<String>,
        val overallScore: Float
    ) : VFXAnalysis()
    
    data class Error(val error: AgbaraError) : VFXAnalysis()
}

sealed class ErrandAnalysis {
    data class Success(
        val requestId: String,
        val feasibility: String,
        val costRange: String,
        val recommendedRunnerType: String,
        val timeline: String,
        val risks: List<String>,
        val optimizations: List<String>,
        val confidence: Float
    ) : ErrandAnalysis()
    
    data class Error(val error: AgbaraError) : ErrandAnalysis()
}

sealed class RouteOptimization {
    data class Success(
        val deliveryOrder: List<Int>,
        val routePlan: String,
        val estimatedTotalTime: String,
        val costOptimizations: List<String>,
        val alternativeRoutes: List<String>,
        val errands: List<ErrandRequest>,
        val confidence: Float
    ) : RouteOptimization()
    
    data class Error(val error: AgbaraError) : RouteOptimization()
}