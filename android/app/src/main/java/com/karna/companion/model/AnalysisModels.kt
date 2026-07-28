package com.karna.companion.model

data class AnalyzeRequest(
    val text: String? = null,
    val urls: List<String> = emptyList(),
)

data class ThreatEvidence(
    val signal: String,
    val explanation: String,
    val weight: Int,
)

data class AnalysisResponse(
    val risk_level: String,
    val risk_score: Int,
    val threat_category: String,
    val evidence: List<ThreatEvidence>,
    val confidence: Double,
    val recommended_action: String,
    val summary: String,
)
