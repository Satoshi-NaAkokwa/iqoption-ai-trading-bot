// Igbo Language Client for cultural support
package com.agbara.sdk.igbo

import android.content.Context
import com.agbara.sdk.config.AgbaraConfig
import com.agbara.sdk.models.*
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.Random

class IgboClient(private val config: AgbaraConfig) {

    private val proverbs = listOf(
        IgboProverb(
            text = "Egbe bere ugo bere",
            translation = "Let the kite perch and let the eagle perch",
            meaning = "Everyone deserves their space and rights",
            culturalContext = "Traditional Igbo philosophy of coexistence and mutual respect"
        ),
        IgboProverb(
            text = "Ọkụ mị e gbu n'ụzọ",
            translation = "One finger cannot kill a louse",
            meaning = "Collaboration is necessary for success",
            culturalContext = "Emphasizes the importance of community and working together"
        ),
        IgboProverb(
            text = "Onye isi ihe ọjọọ ga-ahụ ọjọọ",
            translation = "He who sows discord will reap discord",
            meaning = "Actions have consequences",
            culturalContext = "Wisdom about cause and effect in human relationships"
        ),
        IgboProverb(
            text = "Nwata na-amị amị, ọ gba egwú",
            translation = "A child who asks questions will grow wise",
            meaning = "Curiosity leads to knowledge and growth",
            culturalContext = "Value placed on learning and wisdom in Igbo culture"
        ),
        IgboProverb(
            text = "Chi amọọn'ọnụ ya ga-eji we ya",
            translation = "What kills a child is known by the child",
            meaning = "Understand your own strengths and weaknesses",
            culturalContext = "Self-awareness and personal responsibility"
        )
    )

    private val culturalConcepts = mapOf(
        "Chi" to CulturalConcept(
            name = "Chi",
            explanation = "Chi is your personal spiritual guide and destiny in Igbo culture. It represents the individual's connection to the divine and influences their life path, talents, and purpose. Everyone has their own Chi, which is believed to choose them before birth.",
            examples = listOf(
                "Chi gị mụ - Your Chi is great",
                "Chi na-echetegọ - My Chi is supporting me",
                "Chi ọma - Good Chi (good destiny)"
            ),
            relatedConcepts = listOf("Ikenga", "Arụsị", "Ndichie")
        ),
        "Ikenga" to CulturalConcept(
            name = "Ikenga",
            explanation = "Ikenga is the Igbo god of achievement, success, and personal power. Represented as a horned figure, Ikenga symbolizes masculine strength, creativity, and the ability to overcome challenges. It is often carved as a wooden figure displayed in homes.",
            examples = listOf(
                "Ikenga m ji - My Ikenga is strong",
                "Gba Ikenga - Work hard (like Ikenga)"
            ),
            relatedConcepts = listOf("Chi", "Arụsị", "Ozo")
        ),
        "Omenala" to CulturalConcept(
            name = "Omenala",
            explanation = "Omenala refers to the traditional customs, traditions, and way of life of the Igbo people. It encompasses social norms, religious practices, marriage customs, burial rites, and all aspects of cultural heritage that have been passed down through generations.",
            examples = listOf(
                "N'ime omenala - In the tradition",
                "Ọmenala Igbo - Igbo tradition"
            ),
            relatedConcepts = listOf("Ndichie", "Ozo", "Igwebuike")
        ),
        "Ndichie" to CulturalConcept(
            name = "Ndichie",
            explanation = "Ndichie are the revered ancestors in Igbo culture. Ancestors are believed to continue watching over their living descendants, offering guidance, protection, and blessings. They are honored through rituals and are an essential part of Igbo spirituality.",
            examples = listOf(
                "Nne nna - Father/Mother (ancestors)",
                "Ndi ichie - The ancestors"
            ),
            relatedConcepts = listOf("Chi", "Omenala", "Arụsị")
        ),
        "Igwebuike" to CulturalConcept(
            name = "Igwebuike",
            explanation = "Igwebuike translates to 'unity is strength' or 'many hands make light work.' It is a fundamental Igbo principle emphasizing the power of community, cooperation, and collective action in achieving goals and solving problems.",
            examples = listOf(
                "Igwebuike ka ọ bụ - Unity is strength",
                "Onye ọ bụrụ, ọ gbara - Everyone's contribution matters"
            ),
            relatedConcepts = listOf("Omenala", "Ndichie", "Ọtụtụ")
        )
    )

    private val vocabulary = mapOf(
        "Ndeewo" to "Hello, welcome",
        "Kedu" to "How",
        "Kedu ka ị mere" to "How are you",
        "Ọ di mma" to "I am fine",
        "Chineke me" to "God bless you",
        "Dalụ" to "Thank you",
        "Biko" to "Please",
        "Jisie ike" to "Make an effort",
        "Ọfọma" to "Well done",
        "Nna m" to "My father",
        "Nne m" to "My mother",
        "Nwata" to "Child",
        "Nwoke" to "Man",
        "Nwanyị" to "Woman",
        "Obi" to "Home/Community"
    )

    private val random = Random()

    fun getProverb(): IgboProverb {
        return proverbs[random.nextInt(proverbs.size)]
    }

    fun translate(text: String, direction: TranslationDirection): IgboTranslation {
        return when (direction) {
            TranslationDirection.IGBO_TO_ENGLISH -> {
                val translated = vocabulary[text.lowercase()] ?: "Translation not found"
                IgboTranslation(
                    text = translated,
                    originalText = text,
                    direction = direction
                )
            }
            TranslationDirection.ENGLISH_TO_IGBO -> {
                // Reverse lookup
                val translated = vocabulary.entries.find { it.value == text }?.key ?: "Translation not found"
                IgboTranslation(
                    text = translated,
                    originalText = text,
                    direction = direction
                )
            }
        }
    }

    fun explainConcept(conceptName: String): CulturalConcept {
        return culturalConcepts[conceptName] ?: CulturalConcept(
            name = conceptName,
            explanation = "This concept is not yet documented in the Igbo cultural database.",
            examples = emptyList(),
            relatedConcepts = emptyList()
        )
    }

    fun getAllProverbs(): List<IgboProverb> {
        return proverbs.toList()
    }

    fun getAllConcepts(): List<CulturalConcept> {
        return culturalConcepts.values.toList()
    }

    fun getVocabularySize(): Int {
        return vocabulary.size
    }

    fun searchProverb(keyword: String): List<IgboProverb> {
        return proverbs.filter { proverb ->
            proverb.text.contains(keyword, ignoreCase = true) ||
            proverb.translation.contains(keyword, ignoreCase = true) ||
            proverb.meaning.contains(keyword, ignoreCase = true)
        }
    }
}