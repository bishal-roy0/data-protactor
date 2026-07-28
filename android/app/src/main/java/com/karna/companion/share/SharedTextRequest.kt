package com.karna.companion.share

import com.karna.companion.model.AnalyzeRequest

object SharedTextRequest {
    private val standaloneUrl = Regex("^https?://\\S+$", RegexOption.IGNORE_CASE)

    fun from(text: String): AnalyzeRequest {
        val trimmed = text.trim()
        return if (standaloneUrl.matches(trimmed)) {
            AnalyzeRequest(urls = listOf(trimmed))
        } else {
            AnalyzeRequest(text = trimmed)
        }
    }
}
