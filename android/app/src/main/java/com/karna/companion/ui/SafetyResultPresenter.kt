package com.karna.companion.ui

import com.karna.companion.model.AnalysisResponse

object SafetyResultPresenter {
    private val actions = setOf("allow", "show_caution", "block", "quarantine")

    fun actionLabel(result: AnalysisResponse): String =
        result.recommended_action.takeIf { it in actions }?.replace('_', ' ') ?: "show caution"
}
